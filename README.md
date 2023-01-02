# Deploy Custom Environments in MAIA

[![Build](https://github.com/MAIA-KTH/Hive_Gate/actions/workflows/build.yaml/badge.svg)](https://github.com/MAIA-KTH/Hive_Gate/actions/workflows/build.yaml)

To create custom environments and deploy applications in MAIA (including pods, services and ingresses) 
a Helm chart is available: [Hive_Gate](https://maia-kth.github.io/Hive_Gate/).

With the **Hive_Gate** chart it is possible to deploy any *Docker Image* as a Pod, expose the required ports as services, mount persistent volumes on the specified locations and optionally create Ingress resources to expose the application to the external traffic using the HTTPS protocol.

To add the chart to Helm, run:
```
helm repo add hive-gate https://maia-kth.github.io/Hive_Gate/
helm repo update
```

## Custom Helm values

A number of custom parameters can be specified for the Helm chart, including the Docker image to deploy, the port to expose, etc.

The custom configuration is set in a JSON configuration file, following the conventions described below.

### General Configuration

#### Namespace [Required]
Specify the Cluster Namespace where to deploy the resources
```json
{
  "namespace": "NAMESPACE_NAME"
}
```
#### Chart Name [Required]
Specify the Helm Chart Release name
```json
{
  "chart_name": "Helm_Chart_name"
}
```
#### Docker image [Required]
To specify the Docker image to deploy
```json
{
  "docker_image": "DOCKER_IMAGE"
}
```
In case of a custom Docker image, provide the docker build context ( the folder path containing the *Dockerfile* and all the required files), and the corresponding custom
 image name. The built Docker image is pushed to the private docker registry.
```json
{
  "docker_image": {
    "context_folder": "/PATH/TO/MY/DOCKER_CONTEXT",
    "image_name": "my-custom-image"
  }
}
```
#### Requested Resources [Required]
To request resources (RAM,CPU and optionally GPU).
```json
{
  "memory_size" : "REQUESTED_RAM_SIZE",
  "cpu" : "REQUESTED_CPUs"
}
```

Optionally, to request GPU usage:
```json
{
  "gpu_request" : "NUMBER_OF_GPUs"
}
```
#### Services
To specify which ports (and corresponding services) can be reached from outside the pod.
```json
{
  "ports" : {
    "SERVICE_NAME_1": ["PORT_NUMBER"],
    "SERVICE_NAME_2": ["PORT_NUMBER"]
  }
}

```
The default *Service Type* is **ClusterIP**. To expose a service as a type **NodePort**:
```json
{
  "service_type": "NodePort",
  "ports" : {
    "SERVICE_NAME_1": ["PORT_NUMBER", "NODE_PORT_NUMBER"],
    "SERVICE_NAME_2": ["PORT_NUMBER", "NODE_PORT_NUMBER"]
  }
}

```
#### Persistent Volumes
2 different types of persistent volumes are available: **hostPath** (local folder) and **nfs** (shared nfs folder).
For each of these types, it is possible to request a Persistent Volume via a Persistent Volume Claim, or to directly reference the folder in the host/nfs server to mount.

Direct access:
```json
{
  "host_volume_mounts": 
  {
    "host-folder_1": ["/host/folder/path_1", "/mount/path_1","readOnly"],
    "host-folder_2": ["/host/folder/path_2", "/mount/path_2"]
  },
  "nfs_server": "NFS_SERVER_IP",
  "nfs_volume_mounts": 
  {
    "nfs-folder_1": ["/nfs/folder/path_1", "/mount/path_1","readOnly"],
    "nfs-folder_2": ["/nfs/folder/path_2", "/mount/path_2"]
  }
}
```
The *"readOnly"* options can be added to specify the mounted folder as read-only.

Request PVC:

```json
{
  "persistent_volume" : 
  [
    {
      "mountPath": "/mount/path_1",
      "size": "VOLUME_SIZE",
      "access_mode": "ACCESS_TYPE",
      "pvc_type": "STORAGE_CLASS"
    },
    {
      "mountPath": "/mount/path_2",
      "size": "VOLUME_SIZE",
      "access_mode": "ACCESS_TYPE",
      "pvc_type": "STORAGE_CLASS"
    }
  ]
}
```
**"STORAGE_CLASS"** can be any of the storage classes available on the cluster: 
```
kubectl get sc
```
#### Mounted files
Single files can be mounted inside the Pod. First, a ConfigMap including the file is created, and then it is mounted into the Pod.

```json
{
  "mount_files":
  {
    "file_name": ["/local/file/path","/file/mount/path"]
  }
}
```

#### Node Selection
To optionally select which node in the cluster to use for deploying the application.
```json
{
  "node_selector": "NODE_NAME"
}
```

#### GPU Selection
To optionally select which available GPUs in the cluster to request. `type` and `vram` attribute can be specified (only one of them is needed, both can be included).
Example: `type: "RTX-2070-Super"`, `vram: "8G"`
```json
{
  "gpu_selector": {
    "type": "GPU_TYPE",
    "vram": "VRAM_SIZE"
  }
}
```

#### Ingress
Used to create an Ingress resources to access the application at the specified port by using an HTTPS address.
IMPORTANT! The specified DNS needs to be active and connected to the cluster DNS (**".k8s-maia.com"**)

```json
{
  "ingress": 
  {
    "host": "SUBDOMAIN.k8s-maia.com",
    "port": "SERVICE_PORT"
  }
}
```


#### Environment variables
To add environment variables, used during the creation and deployment of the pod (i.e., environment variables to specify for the Docker Image).
```json
{
  "env_variables": 
  {
    "KEY_1": "VAL_1",
    "KEY_2": "VAL_2"
  }
}
```

### Hive Docker Configuration

#### User info
When deploying Hive-based applications, it is possible to create single-multiple user account in the environment.
For each of the users, *username*, *password* *email*, and, optionally, an *ssh public key* are required.
This information is stored inside Secrets:
```
USER_1_SECRET:
    user: USER_1
    password: pw
    email: user@email.com
    ssh_publickey [Optional]: "ssh-rsa ..." 
```
To provide the user information to the Pod:
```json
{
  "user_secret" : 
  [ 
    "user-1-secret",
    "user-2-secret"
  ],
  "user_secret_params" : ["user","password","email", "ssh_publickey"]
}
```

## Configuration File Example

```json
{
  "namespace": "machine-learning",
  "chart_name": "jupyterlab-1-v1",
  "docker_image": "jupyter/scipy-notebook",
  "tag" : "latest",
  "memory_size" : "4Gi",
  "cpu" : "5000m",
  "ports" : {
    "jupyter": [8888]
  },
  "persistent_volume" :
  [
    {
      "mountPath": "/home/jovyan",
      "size": "100Gi",
      "access_mode": "ReadWriteOnce",
      "pvc_type": "local-hostpath"
    }
  ]
}
```

## Deploy Charts

To deploy an Helm Hive Chart, first create a config file according to the specific requirements (as described [above](#Custom Helm values)).
Then install the **Hive_Gate** package running:
```
pip install hive-gate
```
Or download the executable file:

[Hive_Gate_deploy_helm_chart (Windows .exe)](https://github.com/MAIA-KTH/Hive_Gate/releases/download/v1.0/Hive_Gate_deploy_helm_chart.exe)

[Hive_Gate_deploy_helm_chart (Ubuntu)](https://gits-15.sys.kth.se/MAIA/Hive_Gate/releases/download/v1.1/Hive_Gate_deploy_helm_chart)

Finally:
```
Hive_Gate_deploy_helm_chart --config-file /PATH/TO/CONFIG/FILE
```