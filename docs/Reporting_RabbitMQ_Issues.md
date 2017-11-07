# Best Practices for reporting RabbitMQ issues

When reporting an issue with RabbitMQ, providing as much information as possible from the following lists will assist the RabbitMQ Core team in determining the issue's root cause.

## Gather Information

The [`rabbitmq-collect-env`](https://raw.githubusercontent.com/rabbitmq/support-tools/master/scripts/rabbitmq-collect-env) script will run commands to gather system information and RabbitMQ logs.

Other necessary information includes the following:

* RabbitMQ version
* Erlang version
* Client library (or libraries) used and versions
* System topology - for each node in the environment, provide the following information:
 * Hostname
 * IP address
 * Cluster membership

If the `rabbitmq_management` plugin is in use, please log into the management dashboard's "Overview" page, expand all sections, and take a screenshot.

## Questions

* When did the issue first occur (including time zone)? 
* Is it a recurring issue? If so, is recurrence regular or intermittent?
* Which protocol(s) are you using? e.g. AMQP / MQTT / STOMP
* What exceptions is the RabbitMQ client returning?
* Which connection / channel / queue / exchange are the exceptions for?
* Is a specific RabbitMQ node failing?
* Are multiple RabbitMQ nodes failing at the same time?
* Is the Erlang VM PID changing?
* Did any `rabbitmqctl` commands fail during the incident? In which way?
* What actions did you take to remedy the failures?
* In which way did the observed behaviour change after your actions?
* Did you restart all RabbitMQ nodes at once or only the affected node(s)?
* Did any RabbitMQ node remain running during restarts?
* If you have a suspicion as to what might be wrong, please describe it

## TODO:

### RMQ General

How many nodes does your RabbitMQ cluster have?
What type of nodes does your RabbitMQ cluster have?
How many connections & channels does your cluster handle?
What protocols do you use? AMQP 0-9-1 / MQTT / STOMP / AMQP 1.0
How many queues does your RabbitMQ cluster have?
How many messages are published / consumed on average and during peaks?
How large are message payloads?
Are the messages published as persistent & queues durable?
Which RabbitMQ client & version are you using?
Please share RabbitMQ logs with us, either from one or all nodes (scrub credentials)
Please share your exported RabbitMQ definitions file with us

### Deployment

How are you deploying RabbitMQ?
Which IaaS is your RabbitMQ cluster deployed to? AWS / GCP / vSphere

### Hardware

Tell us about the type & number of CPUs that your RabbitMQ nodes are using
Tell us about the RAM that your RabbitMQ nodes are using
What network throughput do your RabbitMQ nodes have?
What network throughput do your client nodes have?
If applicable, tell us about the load balancer or proxy that sits in front of RabbitMQ
What network throughput do load balancer/proxy nodes have?
Tells us about the disks that your RabbitMQ nodes are using

