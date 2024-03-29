# Data Collection Form for VMware RabbitMQ for Kubernetes Issues that Require Further Investigation/Escalation

If a VMware RabbitMQ for Kubernetes issue needs to be assigned to the VMware RabbitMQ for Kubernetes Research and Development team for further investigation and resolution, please answer the questions in this form and submit these answers in the ticket that you are assigning to the research and development to get the issue resolved.

## The Research and Development Team Need the Following Information to Work on the Issue

### What is the product type?

   * Commercial
   * Open source  

### What is the product version?
#### Commercial: what product version is used?

The product versions currently in use are: 1.0, 1.1, 1.2, and 1.3. There will be future versions.

Run the following command to get the product version:

``` shell
kubectl get PackageInstall tanzu-rabbitmq -o yaml -n rabbitmq-system | grep "version:"
```

#### Open source: What are the operator versions and RabbitMQ images being used?

Run the following commands to get the operator versions and RabbitMQ images being used:

``` shell
kubectl get deployment rabbitmq-cluster-operator -n rabbitmq-system -o yaml | grep " image:"
kubectl get deployment messaging-topology-operator -n rabbitmq-system -o yaml | grep " image:"
kubectl get rabbitmqcluster.rabbitmq.com hello-world -n rabbit-cluster -o yaml | grep " image:"
```

### What is the The Kubernetes distribution?

Possible options are: TKG, GKE, AKS, EKS, Openshift, Anthos, etc.
   
### What is the Kubernetes version?
   
Run the following command to get the Kubernetes version:
   
``` shell
kubectl version
```

### Is the issue related to the installation or upgrade of the product?

To investigate and provide further information, see [Specific Issues during the Installation of the Commercial Tanzu RabbitMQ for Kubernetes  Product](#issues-during-install-upgrade).

### Is the issue related to the deployed operators?

To investigate and provide further information (status, description and logs) about the deployed operators, see [Retrieving Information about the Deployed Operators](#retrieve-operator-details).

### Is the issue related to the RabbitMQ cluster object(s)?

To investigate and provide further information (status, description and logs) about the RabbitMQ cluster object(s), see [Retrieving Information about the RabbitMQ Cluster](#retrieve-cluster-information).


### Provide a detailed description of the scenario causing the issue

by answering the following questions

 * Is an issue happening during installation or upgrade of the product or running a scenario on a correctly deployed RabbitMQ cluster?
 * Is the issue happening with a specific scenario such as standby replication, MQTT, STOMP? If the answer is yes, please see the next question otherwise skip the next question.
 * Can the issue still be reproduced with this specific scenario? If the answer is yes, provide as much detail as possible about this scenario including any logs.
 * Is the issue impacting a specific Kubernetes Operator (Cluster Operator, Messaging Topology Operator, and Standby Replication Operator) or is the issue impacting RabbitMQ core functionality?
     
To retrieve useful informations about the Kubernetes cluster that is deployed such as the number of nodes, the total number of cores,
cpu and memory usage, the network (Calico, CNI, or others), and the storage classes that are in use, run the following commands:

``` shell
kubectl get nodes
kubectl describe nodes
kubectl get storageclasses
kubectl describe storageclasses
kubectl top node
kubectl top pod --all-namespaces
```

## <a id="issues-during-install-upgrade" class="anchor" href="issues-during-install-upgrade">Specific issues during the Installation of the Commercial Tanzu RabbitMQ for Kubernetes Version</a>

If the issue is related to the [installation of the Tanzu RabbitMQ for Kubernetes commercial product using the Carvel toolchain](https://docs.vmware.com/en/VMware-Tanzu-RabbitMQ-for-Kubernetes/1.3/tanzu-rmq/GUID-installation.html), check the following:

### Check the Prerequites are Complete and cert-manager is Installed

**Important:**  Some example commands are used in this section. Before running the commands, edit the required parameters and values in these commands based on your own specific environment.

Verify that the Tanzu Cluster Essentials package is installed on the Kubernetes cluster and the `kapp-controller` and `secretgen-controller` Kubernetes controllers are installed and running. Also, verify that `cert-manager` is installed on the Kubernetes cluster.

You can to get deployment information for the  `kapp-controller` and `secretgen-controller` controllers and `cert-manager` by running the following commands:

``` shell
kubectl describe deployment kapp-controller -n kapp-controller | grep "kapp-controller.carvel.dev/version"
kubectl describe deploy secretgen-controller -n secretgen-controller | grep "secretgen-controller.carvel.dev/version"
kubectl describe deployment cert-manager -n cert-manager | grep version
```

To get status information and a description of the replicaset and the pods running inside the `kapp-controller` controller as well as review the logs, run the following commands.

``` shell
kubectl get all -n kapp-controller
kubectl describe replicaset kapp-controller-54fdd6557d -n kapp-controller
kubectl describe pod kapp-controller-54fdd6557d-782cw -n kapp-controller
kubectl logs kapp-controller-54fdd6557d-782cw -c kapp-controller -n kapp-controller
```

To get status information and a description of the replicaset and the pods running inside the `secretgen-controller` controller as well as review the logs, run the following commands:

``` shell
kubectl get all -n secretgen-controller
kubectl describe replicaset secretgen-controller-7995bcbd87 -n secretgen-controller
kubect logs secretgen-controller-7995bcbd87-kqctv -n secretgen-controller
```

To get the status, description of the `PackageRepository` and `PackageInstall` objects, and review the Yaml definition files of these objects, run the following commands:

``` shell
kubectl describe PackageRepository tanzu-rabbitmq-repo
kubectl get PackageRepository tanzu-rabbitmq-repo -o yaml > tanzu-rabbitmq-repo.yml
kubectl describe PackageInstall tanzu-rabbitmq-install
kubectl get PackageInstall tanzu-rabbitmq-install -o yaml > tanzu-rabbitmq.yml
```

If the prerequisites are ok, next, check the Operator and RabbitMQ server information.

## <a id="retrieve-operator-details" class="anchor" href="retrieve-operator-details">Retrieving Information about the Deployed Operators</a>

**Important:**  Example commands are used in this section. Before running the commands, edit the required parameters and values in these commands based on your own specific environment. 

If the prerequisites are ok, next, complete checks on the Operators. By default, Operators are installed by the `PackageInstall` object in the `rabbitmq-system` namespace.

To get the status, description, and definition file for the deployed Cluster Operator, information about the replicaset and the pods running inside
the `rabbitmq-system` namespace, and to review the logs for the Cluster Operator pods, run the following commands.

``` shell
kubectl get all -n rabbitmq-system
kubectl describe rs rabbitmq-cluster-operator-767c4c7575 -n rabbitmq-system
kubectl describe deployment rabbitmq-cluster-operator -n rabbitmq-system
kubectl get deployment rabbitmq-cluster-operator -o yaml >  rabbitmq-cluster-operator-deploy.yml
kubectl describe pod rabbitmq-cluster-operator-767c4c7575-6bvmp  -n rabbitmq-system
kubectl describe pod rabbitmq-cluster-operator-767c4c7575-6bvmp  -n rabbitmq-system
kubectl logs rabbitmq-cluster-operator-767c4c7575-6bvmp  -n rabbitmq-system >  rabbitmq-cluster-operator.log
```

If the issue reported is related to a Messaging topology operator or Standby Replication Operator scenario we need informations for these operators too.
To get the status, description, and definition file for the deployed Messaging Topology Operator or Standby Replication Operator, information about the replicaset and the pods running inside the `rabbitmq-system` namespace, and to review the logs for the Messaging Topology Operator or Standby Replication Operator pods, run the following commands.

``` shell
kubectl describe rs messaging-topology-operator-678ff579dd -n rabbitmq-system
kubectl describe deployment messaging-topology-operator -n rabbitmq-system
kubectl get deployment messaging-topology-operator -o yaml >  rabbitmq-messaging-topology-operator-deploy.yml
kubectl describe pod messaging-topology-operator-678ff579dd-7597g  -n rabbitmq-system
kubectl logs messaging-topology-operator-678ff579dd-7597g  -n rabbitmq-system >  messaging-topology-operator.log
kubectl describe rs standby-replication-operator-545c66cb66 -n rabbitmq-system
kubectl describe deployment standby-replication-operator  -n rabbitmq-system
kubectl get deployment standby-replication-operator -o yaml >  rabbitmq-standby-replication-operator-deploy.yml
kubectl describe pod standby-replication-operator-545c66cb66-cskph   -n rabbitmq-system
kubectl logs standby-replication-operator-545c66cb66-cskph   -n rabbitmq-system >  rabbitmq-standby-operator.log
```

If you are using the messaging topology operator with Cert Manager to manage certificates and you are having issues with TLS connections or certificates it may be a good idea to check the status of the cert-manager namespace objects too with the usual kubectl get/describe command on the objects: deployments, pods and check the logs of the pods too to see if there are issues.

``` shell
kubectl get all -n cert-manager
kubectl get logs -l app.kubernetes.io/instance=cert-manager -n cert-manager
```

## <a id="retrieve-cluster-information" class="anchor" href="retrieve-cluster-information">Retrieving Information about the RabbitMQ Cluster</a>

**Important:**  Example commands are used in this section. Before running the commands, edit the required parameters and values in these commands based on your own specific environment. 

This section contains specific checks on the RabbitMQ deployed cluster.

To get the status, description of the statefulset and pods running inside the namespace where RabbitMQ is installed, and the logs for the RabbitMQ cluster, run the following commands:

``` shell
kubectl get all -n rabbitmq-cluster
kubectl describe statefulset hello-world-server -n rabbitmq-cluster
kubectl describe pod hello-world-server-0 -n rabbitmq-cluster
kubectl describe pod hello-world-server-1 -n rabbitmq-cluster
kubectl describe pod hello-world-server-2 -n rabbitmq-cluster
kubectl logs hello-world-server-0 -n rabbitmq-cluster > rabbit-server-0.log
kubectl logs hello-world-server-1 -n rabbitmq-cluster > rabbit-server-1.log
kubectl logs hello-world-server-2 -n rabbitmq-cluster > rabbit-server-2.log
```

Some informations about the status of the persistent volume/persistent volume claims can be useful too.
Command to use as example (if the broker is deployed in the rabbitmq-system namespace):

``` shell
kubectl get pv -n rabbitmq-system
kubectl get pvc -n rabbitmq-system
```


To get the yaml definition for the RabbitMQ cluster, run the following command:
Command to use as example:

``` shell
kubectl get rabbitmqcluster.rabbitmq.com rabbit-cluster-name -o yaml > rabbitmq_cluster.yml
```

## <a id="retrieve-operator-details" class="anchor" href="retrieve-operator-details">Diagnostic tool</a>
We developed a (still experimental) tool in order to collect all these informations based on the commands of this documentation which can be found here: </br>

https://github.com/rabbitmq/support-tools/tree/main/scripts/rabbitmq-k8s-runbook 
</br>

Note: If the issue is specific to the RabbitMQ core deployment, you must follow the [Best Practices for reporting RabbitMQ issues](https://github.com/rabbitmq/support-tools/blob/master/docs/Reporting_RabbitMQ_Issues.md) guidelines.


