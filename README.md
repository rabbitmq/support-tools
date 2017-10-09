# RabbitMQ Support and Troubleshooting Extras

This repository contains tools that are not yet ready to
be included into RabbitMQ distribution, cannot be a plugin
or cannot ship with RabbitMQ for any other reason:

* [rabbitmq-collect-env](./scripts/rabbitmq-collect-env): collects RabbitMQ
 and selected OS logs, system-level metrics and other environment information
 (iostat, kernel limits and similar) that is not always directly related to
 RabbitMQ but can provide additional insights about the overall state of the
 node

* [rebalance-queue-masters](./scripts/rebalance-queue-masters): given a
 RabbitMQ cluster with unevenly spread queue masters, this script will
 rebalance queue masters evenly, across all RabbitMQ nodes in the cluster

## Copyright & License

(c) Pivotal Software, Inc. 2007-2017.

See LICENSE.
