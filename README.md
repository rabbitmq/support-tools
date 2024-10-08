# RabbitMQ Support and Troubleshooting Extras

This repository contains tools that are not yet ready to
be included into RabbitMQ distribution, cannot be a plugin
or cannot ship with RabbitMQ for any other reason:

* [`rabbitmq-collect-env` - Linux/POSIX](./scripts/rabbitmq-collect-env):
 collects RabbitMQ and selected OS logs, system-level metrics and other
 environment information (iostat, kernel limits and similar) that is not always
 directly related to RabbitMQ but can provide additional insights about the
 overall state of the node

* [`rabbitmq-collect-env.ps1` - Windows](./scripts/rabbitmq-collect-env.ps1):
 collects RabbitMQ logs, system-level information and other environment
 information that can provide additional insights about the overall state of the
 node

## Copyright & License

(c) VMware, Inc or its affiliates. 2007-2023

See LICENSE.
