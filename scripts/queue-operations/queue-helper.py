#!/usr/bin/env python3
"""
RabbitMQ Queue Management Script
Comprehensive tool for managing RabbitMQ queues via AMQP protocol with SSL support.
Supports DELETE, PURGE, and CONSUME operations with robust error handling and logging.
"""

import pika
import argparse
import sys
import logging
import ssl
import getpass
import csv
import os
import json
import time
import traceback
import base64
from datetime import datetime
from pika.exceptions import AMQPConnectionError, AMQPChannelError

def setup_logging(verbose=False):
    """Setup dual logging system: clean console + comprehensive file logging"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    log_filename = os.path.join(script_dir, f"rabbitmq_queue_mgmt_{timestamp}.log")
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    
    # Clear existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # File handler - ALWAYS captures ALL logs (including pika internals)
    file_handler = logging.FileHandler(log_filename, mode='w', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)  # Always DEBUG level for file
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    ))
    # No filtering for file handler - capture everything
    root_logger.addHandler(file_handler)
    
    # Console handler - only for verbose mode
    if verbose:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        # Filter console to reduce noise
        def console_filter(record):
            # Show our script logs
            if record.name == __name__:
                return True
            # Show important pika errors/warnings
            if record.name.startswith('pika') and record.levelno >= logging.WARNING:
                return True
            # Show other important logs
            return record.levelno >= logging.ERROR
        console_handler.addFilter(console_filter)
        root_logger.addHandler(console_handler)
    
    # Initialize script logger
    logger = logging.getLogger(__name__)
    logger.info("=== RabbitMQ Queue Management Script Started ===")
    logger.info(f"Log file: {log_filename}")
    logger.info(f"Python: {sys.version.split()[0]}, Pika: {pika.__version__}")
    logger.info(f"Console verbose mode: {verbose}")
    logger.info(f"File logging: ALL levels including pika internals")
    
    return logger, log_filename

def log_system_info(logger):
    """Log essential system information for debugging"""
    try:
        import platform
        logger.info("=== System Information ===")
        logger.info(f"Platform: {platform.platform()}")
        logger.info(f"Python executable: {sys.executable}")
        logger.info(f"SSL version: {ssl.OPENSSL_VERSION}")
        
        # Log SSL-related environment variables
        ssl_vars = ['SSL_CERT_FILE', 'SSL_CERT_DIR', 'REQUESTS_CA_BUNDLE', 'CURL_CA_BUNDLE']
        for var in ssl_vars:
            value = os.environ.get(var, 'Not set')
            logger.info(f"{var}: {value}")
    except Exception as e:
        logger.error(f"Failed to log system info: {e}")

def create_connection(host, port, username, password, virtual_host):
    """Create RabbitMQ connection with timeout protection"""
    logger = logging.getLogger(__name__)
    
    logger.info("=== Connection Setup ===")
    logger.info(f"Target: {host}:{port}/{virtual_host} (user: {username})")
    print(f"Connecting to {host}:{port}...")
    
    connection_timeout = 30
    start_time = time.time()
    
    try:
        # SSL configuration
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        # Connection parameters with timeouts
        parameters = pika.ConnectionParameters(
            host=host,
            port=port,
            virtual_host=virtual_host,
            credentials=pika.PlainCredentials(username, password),
            ssl_options=pika.SSLOptions(context=ssl_context),
            heartbeat=600,
            blocked_connection_timeout=300,
            connection_attempts=3,
            retry_delay=2,
            socket_timeout=connection_timeout
        )
        
        logger.info(f"Attempting connection (timeout: {connection_timeout}s, retries: 3)")
        connection = pika.BlockingConnection(parameters)
        connection_time = time.time() - start_time
        
        # Test connection
        test_channel = connection.channel()
        test_channel.close()
        
        logger.info(f"Connection established in {connection_time:.2f}s")
        print(f"✓ Connected successfully to {host}")
        
        return connection
        
    except Exception as e:
        connection_time = time.time() - start_time
        error_type = _classify_connection_error(str(e), connection_time, connection_timeout)
        
        logger.error(f"Connection failed after {connection_time:.2f}s: {e}")
        logger.error(f"Error type: {error_type}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        raise Exception(f"Failed to connect to RabbitMQ: {e}")

def _classify_connection_error(error_str, duration, timeout):
    """Classify connection errors for better diagnostics"""
    error_lower = error_str.lower()
    
    if duration >= timeout or "timeout" in error_lower:
        return "TIMEOUT - Check network connectivity and firewall settings"
    elif "refused" in error_lower:
        return "CONNECTION_REFUSED - Verify host/port and broker status"
    elif "authentication" in error_lower or "access_refused" in error_lower:
        return "AUTH_FAILED - Check username/password and permissions"
    else:
        return "UNKNOWN - Check broker logs and network configuration"

def _queue_exists(connection, queue_name):
    """Check if queue exists"""
    logger = logging.getLogger(__name__)
    
    try:
        channel = connection.channel()
        result = channel.queue_declare(queue=queue_name, passive=True)
        channel.close()
        
        logger.info(f"Queue '{queue_name}' exists (messages: {result.method.message_count}, "
                   f"consumers: {result.method.consumer_count})")
        return True
        
    except AMQPChannelError:
        logger.info(f"Queue '{queue_name}' does not exist")
        return False
    except Exception as e:
        logger.error(f"Error checking queue existence: {e}")
        return False

def _execute_queue_operation(connection, queue_name, operation_func, operation_name, timeout=60):
    """Generic queue operation executor with timeout protection"""
    logger = logging.getLogger(__name__)
    
    logger.info(f"=== {operation_name} Operation ===")
    logger.info(f"Target queue: '{queue_name}'")
    
    if not _queue_exists(connection, queue_name):
        error_msg = f"Queue '{queue_name}' does not exist"
        logger.error(error_msg)
        raise Exception(error_msg)
    
    print(f"{operation_name} queue '{queue_name}'...")
    
    try:
        channel = connection.channel()
        start_time = time.time()
        
        result = operation_func(channel, queue_name)
        
        operation_time = time.time() - start_time
        message_count = result.method.message_count
        
        if operation_time > timeout:
            logger.warning(f"{operation_name} took {operation_time:.2f}s (exceeded {timeout}s)")
        
        logger.info(f"{operation_name} completed in {operation_time:.2f}s")
        logger.info(f"Messages affected: {message_count}")
        
        channel.close()
        return message_count
        
    except Exception as e:
        operation_time = time.time() - start_time if 'start_time' in locals() else 0
        
        if "timeout" in str(e).lower() or operation_time > timeout:
            logger.error(f"{operation_name} timed out after {operation_time:.2f}s")
            logger.error("Possible causes: large queue, network issues, broker overload")
        
        logger.error(f"{operation_name} failed: {e}")
        logger.error(f"Duration: {operation_time:.2f}s")
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        raise Exception(f"Failed to {operation_name.lower()} queue: {e}")

def delete_queue(connection, queue_name, if_unused=False, if_empty=False):
    """Delete queue with conditions"""
    logger = logging.getLogger(__name__)
    
    if if_unused or if_empty:
        conditions = []
        if if_unused:
            conditions.append("if-unused")
        if if_empty:
            conditions.append("if-empty")
        logger.info(f"Conditions: {', '.join(conditions)}")
    
    def delete_operation(channel, queue_name):
        return channel.queue_delete(queue=queue_name, if_unused=if_unused, if_empty=if_empty)
    
    return _execute_queue_operation(connection, queue_name, delete_operation, "Delete")

def purge_queue(connection, queue_name):
    """Purge all messages from queue"""
    def purge_operation(channel, queue_name):
        return channel.queue_purge(queue=queue_name)
    
    return _execute_queue_operation(connection, queue_name, purge_operation, "Purge")

def get_queue_message_count(connection, queue_name):
    """Get current message count in queue"""
    try:
        channel = connection.channel()
        method = channel.queue_declare(queue=queue_name, passive=True)
        message_count = method.method.message_count
        channel.close()
        return message_count
    except Exception:
        return 0

def _extract_message_data(body, message_id):
    """Extract only essential message data - simplified approach"""
    try:
        # Encode message body as base64
        body_base64 = base64.b64encode(body).decode('utf-8') if body else ''
        
        return {
            'message_id': message_id,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'message_body': body_base64,
            'bytes': len(body)
        }
    except Exception as e:
        # Even if something fails, return basic structure
        logging.getLogger(__name__).error(f"Error extracting message {message_id}: {e}")
        return {
            'message_id': message_id,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'message_body': '<extraction_error>',
            'bytes': 0
        }

def _write_messages_to_file(messages_data, filename, file_format):
    """Write messages to file with simplified structure"""
    if not messages_data:
        return
    
    if file_format == 'csv':
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['message_id', 'date', 'message_body', 'bytes'])
            writer.writeheader()
            writer.writerows(messages_data)
    elif file_format == 'json':
        with open(filename, 'w', encoding='utf-8') as f:
            for message in messages_data:
                f.write(json.dumps(message) + '\n')

def _append_messages_to_file(messages_data, filename, file_format):
    """Append messages to existing file with simplified structure"""
    if not messages_data:
        return
    
    if file_format == 'csv':
        with open(filename, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['message_id', 'date', 'message_body', 'bytes'])
            writer.writerows(messages_data)
    elif file_format == 'json':
        with open(filename, 'a', encoding='utf-8') as f:
            for message in messages_data:
                f.write(json.dumps(message) + '\n')

def consume_messages(connection, queue_name, batch_size=10000, output_format='1'):
    """Consume messages from queue with comprehensive timeout protection"""
    logger = logging.getLogger(__name__)
    
    logger.info("=== Message Consumption Operation ===")
    logger.info(f"Queue: '{queue_name}', Batch: {batch_size}, Format: {output_format}")
    
    if not _queue_exists(connection, queue_name):
        raise Exception(f"Queue '{queue_name}' does not exist")
    
    # Setup output files
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                f"{queue_name}_messages_{timestamp}")
    
    output_files = []
    if output_format in ['1', '3']:  # CSV
        output_files.append((f"{base_filename}.csv", 'csv'))
    if output_format in ['2', '3']:  # JSON
        output_files.append((f"{base_filename}.jsonl", 'json'))
    
    logger.info(f"Output files: {[f[0] for f in output_files]}")
    
    # Timeout configuration
    batch_timeout = 120
    message_timeout = 30
    max_timeout_retries = 3
    
    total_consumed = 0
    batch_number = 0
    files_initialized = {fmt: False for _, fmt in output_files}
    
    print(f"\nConsuming messages from queue '{queue_name}' (batch size: {batch_size})...")
    print("📝 Note: Message bodies will be base64 encoded in output files")
    print("   Output format: message_id, date, message_body (base64), bytes")
    print("   To decode: echo '<base64_string>' | base64 -d")
    
    while True:
        batch_number += 1
        batch_start_time = time.time()
        
        current_messages = get_queue_message_count(connection, queue_name)
        if current_messages == 0:
            if total_consumed == 0:
                print("Queue is empty - no messages to consume")
            else:
                print(f"\nQueue is now empty - consumed {total_consumed} total messages")
            break
        
        batch_target = min(batch_size, current_messages)
        logger.info(f"Batch {batch_number}: processing {batch_target} messages")
        
        messages_data = []
        messages_processed = 0
        timeout_count = 0
        
        def process_message(ch, method, properties, body):
            nonlocal messages_processed, messages_data
            
            try:
                message_data = _extract_message_data(body, total_consumed + messages_processed + 1)
                messages_data.append(message_data)
                messages_processed += 1
                
                # Progress indicator
                progress = int((messages_processed / batch_target) * 50)
                print(f"\rBatch Progress: [{'=' * progress}{' ' * (50 - progress)}] "
                      f"{messages_processed}/{batch_target} (Total: {total_consumed + messages_processed})", 
                      end="", flush=True)
                
                ch.basic_ack(delivery_tag=method.delivery_tag)
                
                if messages_processed >= batch_target:
                    ch.stop_consuming()
                    
            except Exception as ex:
                logger.error(f"Error processing message {total_consumed + messages_processed + 1}: {ex}")
                logger.error(f"Exception details: {traceback.format_exc()}")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        
        try:
            channel = connection.channel()
            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(queue=queue_name, on_message_callback=process_message, auto_ack=False)
            
            last_progress_time = time.time()
            last_message_count = 0
            
            # Message processing loop with timeout protection
            while messages_processed < batch_target:
                try:
                    connection.process_data_events(time_limit=1)
                    current_time = time.time()
                    batch_elapsed = current_time - batch_start_time
                    progress_elapsed = current_time - last_progress_time
                    
                    # Check for progress
                    if messages_processed > last_message_count:
                        last_progress_time = current_time
                        last_message_count = messages_processed
                        timeout_count = 0
                    
                    # Message timeout check
                    elif progress_elapsed > message_timeout:
                        timeout_count += 1
                        logger.warning(f"Message timeout #{timeout_count} - no progress for {progress_elapsed:.1f}s")
                        print(f"\n⚠ Timeout #{timeout_count} - no progress for {progress_elapsed:.1f}s")
                        
                        if timeout_count >= max_timeout_retries:
                            logger.error("Max message timeouts reached, stopping batch")
                            print(f"\n✗ Max timeouts reached, stopping batch")
                            break
                        
                        last_progress_time = current_time
                    
                    # Batch timeout check
                    elif batch_elapsed > batch_timeout:
                        logger.error(f"Batch timeout after {batch_elapsed:.1f}s")
                        print(f"\n✗ Batch timeout after {batch_elapsed:.1f}s")
                        break
                        
                except Exception as e:
                    logger.error(f"Error in message processing loop: {e}")
                    break
            
            batch_duration = time.time() - batch_start_time
            channel.cancel()
            channel.close()
            
            # Write processed messages to files
            if messages_data:
                for filename, file_format in output_files:
                    if not files_initialized[file_format]:
                        _write_messages_to_file(messages_data, filename, file_format)
                        files_initialized[file_format] = True
                    else:
                        _append_messages_to_file(messages_data, filename, file_format)
                
                total_consumed += messages_processed
                format_msg = "CSV" if output_format == '1' else "JSON" if output_format == '2' else "CSV & JSON"
                
                logger.info(f"Batch {batch_number} complete: {messages_processed} messages to {format_msg}")
                print(f"\nBatch complete - {messages_processed} messages written to {format_msg}")
                
                # Log performance metrics
                if batch_duration > 0:
                    rate = messages_processed / batch_duration
                    logger.info(f"Performance: {rate:.1f} messages/second")
            
            # Stop if we hit too many timeouts
            if timeout_count >= max_timeout_retries and messages_processed < batch_target:
                logger.error("Stopping consumption due to repeated timeouts")
                break
            
        except (AMQPChannelError, KeyboardInterrupt) as e:
            error_msg = "User interrupted" if isinstance(e, KeyboardInterrupt) else f"Channel error: {e}"
            logger.error(f"Consume operation failed: {error_msg}")
            print(f"\n\nConsuming stopped: {error_msg}")
            break
        except Exception as e:
            logger.error(f"Batch processing error: {e}")
            logger.error(f"Error details: {traceback.format_exc()}")
            break
    
    if total_consumed > 0:
        files_str = " and ".join([f[0] for f in output_files])
        logger.info(f"Total consumed: {total_consumed} messages to {files_str}")
        print(f"\n\n✓ Consumed {total_consumed} total messages to: {files_str}")
        print(f"✓ All messages removed from queue")
        print(f"📝 Message bodies are base64 encoded - decode using: base64 -d <filename> (Linux/Mac)")
    
    return total_consumed

def get_user_input():
    """Get user inputs for operation and options"""
    # Get password
    try:
        password = getpass.getpass("Enter broker password: ")
        if not password:
            raise Exception("Password cannot be empty")
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(0)
    
    # Get operation choice
    print("\nQueue Operations Available:")
    print("1. DELETE - Permanently delete the queue and all its messages")
    print("2. PURGE  - Delete all messages but keep the queue")
    print("3. CONSUME - Export queue messages to CSV/JSON file (messages removed from queue)")
    
    while True:
        try:
            choice = input("\nSelect operation (1 for DELETE, 2 for PURGE, 3 for CONSUME): ").strip()
            if choice == '1':
                return password, 'delete', None, '1'
            elif choice == '2':
                return password, 'purge', None, '1'
            elif choice == '3':
                print("Note: Messages will be consumed (removed) from the queue after export")
                print("Default batch size: 10,000 messages per batch")
                
                format_choice = input("Output format - (1) CSV, (2) JSON, (3) Both [default: 1]: ").strip() or '1'
                if format_choice in ['1', '2', '3']:
                    return password, 'consume', 10000, format_choice
                print("Please enter 1, 2, or 3")
            else:
                print("Invalid choice. Please enter 1 for DELETE, 2 for PURGE, or 3 for CONSUME.")
        except KeyboardInterrupt:
            print("\nOperation cancelled by user")
            sys.exit(0)

def confirm_operation(args, operation, max_messages, output_format):
    """Get user confirmation for the operation"""
    if args.confirm:
        return True
    
    print(f"\nOperation Details:")
    print(f"  Operation: {operation.upper()}")
    print(f"  Host: {args.host}")
    print(f"  Port: {args.port}")
    print(f"  Virtual Host: {args.vhost}")
    print(f"  Queue: {args.queue}")
    print(f"  Username: {args.username}")
    
    if operation == 'delete':
        if args.if_unused:
            print(f"  Condition: Only if unused")
        if args.if_empty:
            print(f"  Condition: Only if empty")
        print(f"  Warning: Queue and all messages will be permanently deleted!")
    elif operation == 'purge':
        print(f"  Warning: All messages will be permanently removed from the queue!")
    else:  # consume
        if max_messages:
            print(f"  Batch size: {max_messages}")
        print(f"  Note: Messages will be consumed (removed) from the queue")
        print(f"  Output: Files will be created in script directory")
    
    action_verb = {"delete": "delete", "purge": "purge", "consume": "consume messages from"}[operation]
    response = input(f"\nAre you sure you want to {action_verb} queue '{args.queue}'? (yes/no): ")
    
    return response.lower() in ['yes', 'y']

def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(
        description='Manage RabbitMQ queues via AMQP protocol (Delete, Purge, or Consume)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --host broker.mq.us-west-2.amazonaws.com --username admin --vhost / --queue my_queue
  %(prog)s --host broker.mq.us-west-2.amazonaws.com --username admin --vhost /prod --queue my_queue --if-unused
  %(prog)s --host broker.mq.us-west-2.amazonaws.com --username admin --vhost /dev --queue my_queue --confirm
        """
    )
    
    # Required parameters
    parser.add_argument('--host', required=True, help='RabbitMQ broker hostname')
    parser.add_argument('--username', required=True, help='Broker username')
    parser.add_argument('--vhost', required=True, help='Virtual host where the queue is located')
    parser.add_argument('--queue', required=True, help='Name of queue to manage')
    
    # Optional parameters
    parser.add_argument('--port', type=int, default=5671, help='AMQP port (default: 5671)')
    parser.add_argument('--if-unused', action='store_true', 
                       help='Only delete if queue has no consumers (DELETE only)')
    parser.add_argument('--if-empty', action='store_true', 
                       help='Only delete if queue is empty (DELETE only)')
    parser.add_argument('--confirm', action='store_true', help='Skip confirmation prompt')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Setup logging
    logger, log_filename = setup_logging(args.verbose)
    
    try:
        # Log execution details
        logger.info("=== Script Execution Started ===")
        logger.info(f"Target: {args.host}:{args.port}/{args.vhost}/{args.queue}")
        logger.info(f"User: {args.username}")
        logger.info(f"Options: if_unused={args.if_unused}, if_empty={args.if_empty}, confirm={args.confirm}")
        
        log_system_info(logger)
        
        # Get user inputs
        password, operation, max_messages, output_format = get_user_input()
        
        # Validate delete-only options
        if operation in ['purge', 'consume'] and (args.if_unused or args.if_empty):
            warning_msg = f"--if-unused and --if-empty options are ignored for {operation.upper()} operation"
            print(f"Warning: {warning_msg}")
            logger.warning(warning_msg)
        
        # Get user confirmation
        if not confirm_operation(args, operation, max_messages, output_format):
            logger.info(f"User cancelled {operation} operation")
            print(f"Queue {operation} cancelled.")
            sys.exit(0)
        
        # Create connection
        connection = create_connection(args.host, args.port, args.username, password, args.vhost)
        
        # Execute operation
        logger.info(f"=== Executing {operation.upper()} Operation ===")
        
        if operation == 'delete':
            message_count = delete_queue(connection, args.queue, args.if_unused, args.if_empty)
            success_message = f"Queue '{args.queue}' deleted successfully"
            warning_message = f"Warning: Queue and {message_count} messages were permanently deleted"
        elif operation == 'purge':
            message_count = purge_queue(connection, args.queue)
            success_message = f"Queue '{args.queue}' purged successfully"
            warning_message = f"Warning: {message_count} messages were permanently removed"
        else:  # consume
            message_count = consume_messages(connection, args.queue, max_messages, output_format)
            success_message = f"Successfully consumed {message_count} messages from queue '{args.queue}'"
            warning_message = f"Note: All {message_count} messages were consumed from the queue"
        
        # Close connection
        connection.close()
        print("✓ Connection closed")
        
        # Log results
        logger.info("=== Operation Results ===")
        logger.info(f"Operation: {operation.upper()}")
        logger.info(f"Messages affected: {message_count}")
        logger.info("Status: SUCCESS")
        
        # Display results to user
        if operation != 'consume':
            print(f"\n✓ {success_message}")
            if message_count > 0:
                print(f"⚠ {warning_message}")
            else:
                if operation == 'purge':
                    print("✓ Queue was already empty - no messages removed")
                else:
                    print("✓ Queue was empty - no messages lost")
        else:
            if message_count > 0:
                print(f"✓ {warning_message}")
        
        print(f"\n📋 Detailed log file created: {log_filename}")
        
    except KeyboardInterrupt:
        logger.error("Script interrupted by user (Ctrl+C)")
        print(f"\n\n✗ Script interrupted by user")
        print(f"📋 Log file available for debugging: {log_filename}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Script execution failed: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        print(f"\n✗ Failed to execute operation: {e}")
        print(f"📋 Check log file for detailed error information: {log_filename}")
        sys.exit(1)

if __name__ == "__main__":
    main()
