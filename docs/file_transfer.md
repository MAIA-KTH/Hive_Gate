# File Transfer on MAIA

Two alternative are made available for file sharing in MAIA cluster: by using the native *kubectl* option or by using the *SSH* file transfer protocol.

## File Transfer with Kubectl

To transfer files from a pod in the remote server to a local folder, run:
```
kubectl cp NAMESPACE/POD_NAME:/REMOTE/FOLDER /LOCAL/FOLDER
```
Or alternatively, to copy local files into the pod on the remote server:
```
kubectl cp /LOCAL/FOLDER NAMESPACE/POD_NAME:/REMOTE/FOLDER
```

## File Transfer via SSH
In case of an established SSH connection with the pod (as described in [SSH Access](resources_access.md#SSH Access)), the SSH file transfer command can be used:
```
scp -P local_SSH_port username@localhost:/REMOTE/FOLDER /LOCAL/FOLDER
scp -P local_SSH_port /LOCAL/FOLDER username@localhost:/REMOTE/FOLDER 
```