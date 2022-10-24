# RabbitMQ for Kubernetes diagnostic script

This tool is intended to be a simple script for collecting diagnostic informations: status, object yaml definitions, logs for the RabbitMQ operators and RabbitMQ clusters deployed in Kubernetes. </br>

It is based on this guideline and set of commands: </br> https://github.com/rabbitmq/support-tools/blob/main/docs/Reporting_RabbitMQ_For_Kubernetes_Issues.md </br>

It can be used with both Tanzu RabbitMQ commercial and open source versions. </br>

It can run with 4 options 
* get_k8s_info
* get_carvel_components_info
* get_operators_info
* get_rabbitmq_cluster_info

### Get K8s cluster info:

```
./rabbitmq-k8s-diagnostic-runbook get_k8s_cluster_info ./diagnostics
```

This command returns useful informations on the Kubernetes cluster (version, status of the nodes, status of the storageclasses ecc...) 

### Get specific commercial Carvel components diagnostic info:

```
./rabbitmq-k8s-diagnostic-runbook get_carvel_components_info -n rabbitmq-system  ./diagnostics
```

This command which should be used just if you are running the commercial version of RabbitMQ based on this doc:</br> https://docs.vmware.com/en/VMware-Tanzu-RabbitMQ-for-Kubernetes/1.3/tanzu-rmq/GUID-installation.html </br>
returns informations and logs on the components of the Carvel Suite (kapp, secret-gen controller as well as the PackageRepository and PackageInstall objects used). </br>

It takes in input the namespace where you deployed the PackageRepository and PackageInstall objects. If none is provided then it will search in the default namespace. </br>

Note: kapp, and secretgen controller are supposed to be deployed in the default installation namespaces for these components: kapp and secret-gen namespaces

### Get Operators diagnostic info:

```
./rabbitmq-k8s-diagnostic-runbook get_operators_info -n rabbitmq-system  ./diagnostics
```

This command returns informations and logs on the three RabbitMQ operators: cluster-operator, messaging-topology-operator and standby replication operator (this last one just available in the commercial version). </br>
It takes in input the namespace where the operators are installed, if none is provided will search in the rabbitmq-system. 

### Get RabbitMQ cluster diagnostic info:

```
./rabbitmq-k8s-diagnostic-runbook get_rabbitmq_cluster_info -n rabbitmq-cluster  ./diagnostics
```

Returns informations and logs on the RabbitMQ cluster deployed on the namespace passed (If none specified will search on the default namespace).
You can run it on different namespaces where a RabbitMQ cluster is deployed

### Generated report informations:

the output of the scripts is a set of files containing informations and logs.
For every of the four commands run a subfolder will be created: k8s-cluster, carvel, operators, rabbitmq_cluster
So you will have:

* k8s-cluster/info: Some informations about the Kubernetes cluster (version, status of the nodes, storage classes)
* carvel/info: informations about kapp and secret-gen controller objects as well as .yaml definitions of the PackageRepository and PackageInstall objects
* carvel/logs: logs file for kapp and secretgen-controller pods
* operators/info: Status of the RabbitMQ operator objects as well asyaml definition files of the statefulset
* operators/logs: Logs of operators pods as well as of the secretgen pods.
* rabbitmq_cluster/info: Status of the RabbitMQ cluster objects as well as some .yaml definition files of the statefulset
* rabbitmq_cluster/info: Logs of the RabbitMQ cluster pods

Note: the folder you pass in input will be overwritten. So run the script with an empty or non-existing folder.</br>
You can then zip and send the info to R&D for investigation. </br>
For commercial version you need also to run the option get_carvel_components_info, for OSS is not necessary
