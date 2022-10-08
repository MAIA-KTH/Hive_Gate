# Cluster Access

## Cluster Access on CLI
To verify the correct cluster access, run:

```
kubectl get pods
```
or:
```
kubectl get svc
```
You should see an output similar to:

```
NAME                      TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)                  AGE
user01-v1-example-hive    ClusterIP   10.99.56.221   <none>        22/TCP,80/TCP,5000/TCP   24d
```

To inspect resources in other namespaces, run:
```
kubectl get pods -n NAMESPACE
```

## Cluster Access on KubeNav

Launch KubeNav and verify the access by checking if some *pods* or *services* can be detected by selecting the corresponding resources on the sidebar.