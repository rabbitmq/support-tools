# Data Collection Form for Tanzu RabbitMQ for Kubernetes Issues that Require Further Investigation/Escalation

If a a Tanzu RabbitMQ for Kubernetes issue needs to be assigned to the Tanzu RabbitMQ for Kubernetes Research and Development team for further investigation and resolution, please answer the questions in this form and submit these answers in the ticket that you are assigning to the research and development to get the issue resolved.

## The Research and Development Team Need the Following Information to Work on the Issue:

1. **What type of product?**
   * Commercial
   * Open source  
   
2. **What is the product version?**
  * **Commercial: What is the Tanzu RabbitMQ for Kubernetes version?** The product versions currently in use are: 1.0, 1.1, 1.2, and 1.3. There will be future versions. 
    Run the following command to get the product version: </br>
    
    ```  
    kubectl get PackageInstall tanzu-rabbitmq -o yaml -n rabbitmq-system | grep "version:" 
    ```
  * **Open source: What are the operator versions and RabbitMQ images being used?**  </br>
    
    Run the following commands to get the operator versions and RabbitMQ images being used: 
    ```
    kubectl get deployment rabbitmq-cluster-operator -n rabbitmq-system -o yaml | grep " image:" 
    kubectl get deployment messaging-topology-operator -n rabbitmq-system -o yaml | grep " image:" 
    kubectl get rabbitmqcluster.rabbitmq.com hello-world -n rabbit-cluster -o yaml | grep " image:"  
    ```
3. **What is the The Kubernetes distribution?**
   Possible options are: TKG, GKE, AKS, EKS, Openshift, Anthos etc
   
5. **What is the Kubernetes version?**
   Run the following command to get the Kubernetes version: 
   
   ```
   kubectl version
   ``` 
6. **Is the issue is related to an Installation/Upgrade procedure?**
   If so, see [Specific Issues during the Installation or Upgrade of the Commercial Tanzu RabbitMQ for Kubernetes Product](#issues-during-install-upgrade). 

7. 
*  
*  If available informations about the deployed operators objects status, description and logs: See section "Operator Informations" below
*  If available informations about the RabbitMQ cluster objects status, description and logs: See section "RabbitMQ server information" below

* Detailed description of the scenario causing the issue:
  *  Is an issue happening during installation/upgrade of the product or running a scenario on a correctly deployed RabbitMQ cluster?
  *  Is the issue happening with a specific scenario: Ex. (standby replication, MQTT, STOMP ecc..)? And is it still reproducible with it? If yes to describe the scenario
  *  Is the issue impacting a specific Kubernetes operator / commercial functionality? (Cluster operator, Mesagging topology operator, Standby operator) or is about a RabbitMQ core functionality?
     
* Some informations about the Kubernetes cluster deployed: Number of nodes, total cores, memory, Network used Calico, CNI, ecc... Storage classes defined and used ecc..
  Commands like this can be useful:
  ```
  kubectl get nodes 
  kubectl describe nodes 
  kubectl get pv
  kubectl get storageclasses 
  ```
## Specific Issues during the Installation or Upgrade of the Commercial Tanzu RabbitMQ for Kubernetes Product
## <a id="issues-during-install-upgrade" class="anchor" href="issues-during-install-upgrade">Specific issues during the Installation or Upgrade of the Commercial Tanzu RabbitMQ for Kubernetes Version</a>

This section concerns problems related to installation/update
Tanzu RabbitMQ is installed through the Carvel toolchain.</br>
https://docs.vmware.com/en/VMware-Tanzu-RabbitMQ-for-Kubernetes/1.3/tanzu-rmq/GUID-installation.html

### Prerequisites to check:

* Versions of the tanzu cluster essential been installed or of the kapp and secretgen controllers. Also cert-manager is necessary so the version of cert-manager used in the Kubernetes cluster.
  You can get the info from the deployment of the kapp, secretgen and cert-manager namespaces like:
  ```
  kubectl describe deployment kapp-controller -n kapp-controller | grep "kapp-controller.carvel.dev/version"
  kubectl describe deploy secretgen-controller -n secretgen-controller | grep "secretgen-controller.carvel.dev/version"
  kubectl describe deployment cert-manager -n cert-manager | grep version
  ```
* Status, description of the replicaset and pods inside the kapp-controller namespace as well as logs of the pods. You can use the following example commands:
  ```
  kubectl get all -n kapp-controller
  kubectl describe replicaset kapp-controller-54fdd6557d -n kapp-controller
  kubectl describe pod kapp-controller-54fdd6557d-782cw -n kapp-controller
  kubectl logs kapp-controller-54fdd6557d-782cw -c kapp-controller -n kapp-controller
  ```
* Status, description of the replicaset and pods inside the secretgen-controller and cert-manager namespace as well as logs of the pods 
  Command to use as an example:
  ```
  kubectl get all -n secretgen-controller
  kubectl describe replicaset secretgen-controller-7995bcbd87 -n secretgen-controller
  kubect logs secretgen-controller-7995bcbd87-kqctv -n secretgen-controller
  ```
* Status, description of the PackageRepository and PackageInstall objects. Yaml definition files of the objects can be very useful as well.
  Command to use as an example:
  ```
  kubectl describe PackageRepository tanzu-rabbitmq-repo
  kubectl get PackageRepository tanzu-rabbitmq-repo -o yaml > tanzu-rabbitmq-repo.yml
  kubectl describe PackageInstall tanzu-rabbitmq-install
  kubectl get PackageInstall tanzu-rabbitmq-install -o yml > tanzu-rabbitmq.yml
  ```

If prerequisites are ok we can continue with the Operator and RabbitMQ server information

## Operator informations

If the prerequisites are fine we may need to inspect the operators objects. Operators are by default installed by the PackageInstall in the namespace rabbitmq-system

* Status, description, definition file of the deployment, replicaset and pods inside rabbitmq-system, and logs of the operator pods.
  Command to use as example:
  ```
  kubectl get all -n rabbitmq-system
  kubectl describe rs rabbitmq-cluster-operator-767c4c7575 -n rabbitmq-system
  kubectl describe deployment rabbitmq-cluster-operator -n rabbitmq-system
  kubectl get deployment rabbitmq-cluster-operator -o yaml >  rabbitmq-cluster-operator-deploy.yml
  kubectl describe pod rabbitmq-cluster-operator-767c4c7575-6bvmp  -n rabbitmq-system
  kubectl describe pod rabbitmq-cluster-operator-767c4c7575-6bvmp  -n rabbitmq-system 
  kubectl logs rabbitmq-cluster-operator-767c4c7575-6bvmp  -n rabbitmq-system >  rabbitmq-cluster-operator.log
  ```

* If the issue is related to specific functionalities of the Messaging topology operator or Standby Operator, the same info are needed for these two operators too.
  ```
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
    
## RabbitMQ server information

This section contains specific checks on the RabbitMQ deployed cluster.

*  Status, description of the statefulset and pods inside the namespace where RabbitMQ is installed, and logs of the rabbitmq cluster.
   Command to use as example:
   ```
   kubectl get all -n rabbitmq-cluster
   kubectl describe statefulset hello-world-server -n rabbitmq-cluster
   kubectl describe pod hello-world-server-0 -n rabbitmq-cluster
   kubectl describe pod hello-world-server-1 -n rabbitmq-cluster
   kubectl describe pod hello-world-server-2 -n rabbitmq-cluster
   kubectl logs hello-world-server-0 -n rabbitmq-cluster > rabbit-server-0.log
   kubectl logs hello-world-server-1 -n rabbitmq-cluster > rabbit-server-1.log
   kubectl logs hello-world-server-2 -n rabbitmq-cluster > rabbit-server-2.log
   ```
*  yaml definition of the rabbitmq cluster.
   Command to use as example:
   ```
   kubectl get rabbitmqcluster.rabbitmq.com rabbit-cluster-name -o yaml > rabbitmq_cluster.yml
   ```
*  For RabbitMQ core specific issue follow this guideline: (https://github.com/rabbitmq/support-tools/blob/master/docs/Reporting_RabbitMQ_Issues.md)
   If the issue is something specific to a RabbitMQ the core guideline must be followed.


