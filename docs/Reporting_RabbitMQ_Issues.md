# Best Practices for reporting RabbitMQ issues

When reporting an issue with RabbitMQ, providing as much information as possible will assist the RabbitMQ Core team in determining the issue's root cause.

## Gather Information

The [`rabbitmq-collect-env`](https://raw.githubusercontent.com/rabbitmq/support-tools/master/scripts/rabbitmq-collect-env) script will run commands to gather system information and RabbitMQ logs. At the root of the archive created by this script will be a file called `overview` which contains some important information. *Note:* this script is **NOT** compatible with Windows systems.

If the script can't be run, use `rabbitmqctl` commands to get information like policies, environment and report.

Other _absolutely necessary_ information includes the following:

* RabbitMQ version
* Erlang version
* Client library (or libraries) used and versions
* System topology - for every server running RabbitMQ, provide the following information:
    * Hostname
    * IP address
    * Cluster membership
    * Node type (disc, ram)

## General Questions

### Essential Information

Answering these questions usually pinpoints the root cause of an issue.

* How long did the RabbitMQ environment work correctly before the issue started?
* When did the issue first occur (including time zone)? 
* What changed on or about the same time as when the issue started? _ANY_ changes must be noted:
  * Software versions (including operating system patches)
  * Environment changes - networking, firewalls
  * Client application changes - AMQP library version, client application updates
  * Client application workload - did it increase or decrease outside of the normal range?
* Is the issue recurring? If so, is recurrence regular or intermittent?

### Other Information

* Which protocol(s) are being used? e.g. AMQP / MQTT / STOMP
* What exceptions are being returned via the RabbitMQ client library?
* Which connection / channel / queue / exchange are the exceptions for?
* Is a specific RabbitMQ node failing?
* Are multiple RabbitMQ nodes failing at the same time?
* Is the Erlang VM PID changing? (`beam.smp` process)
* Did any `rabbitmqctl` commands fail during the incident? In which way?
* What actions were taken to remedy the failures?
* In which way did the observed behaviour change after these remedies?
* Were all RabbitMQ nodes restarted at once or only the affected node(s)?
* Did any RabbitMQ node remain running during restarts?
* Is the issue limited to certain queues?
* Is the issue limited to certain exchanges?
* Does the issue involve Federated queues or exchanges?
  * If Federation is involved, what is the topology?
  * If queue Federation is involved, where are messages published and consumed?
* How many connections & channels does the cluster handle?
* How many queues does the RabbitMQ cluster have?
* How many messages are published / consumed on average and during peaks?
* How large are message payloads?
* Are the messages published as persistent & queues durable?

### Deployment

* How is RabbitMQ deployed?
* On which IaaS is the RabbitMQ cluster deployed? AWS / GCP / vSphere / bare-metal
* What network throughput do the RabbitMQ nodes have?
* What network throughput do the client nodes have?
* If applicable, provide details about the load balancer or proxy that sits between RabbitMQ and clients.
* What network throughput do load balancer/proxy nodes have?
* What kind of disks are the RabbitMQ using, and, if known, expected throughput?
