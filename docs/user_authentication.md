# MAIA User Authentication

After [registering a MAIA account](user_registration.md), follow the instructions provided to [get started](getting_started.md) and correctly authenticate to the MAIA cluster.

## User Login
In order to properly authenticate to the cluster, you need to have a proper configuration YAML file saved in `~/.kube/config`.
This configuration file can be obtained by authentication via the [MAIA login web app](https://loginapp.k8s-maia.com).
A personal ID token is required to authenticate to the cluster. This token is uniquely assigned to each user and stored in the `config` file.

IMPORTANT: Each ID token is valid for only 48 hours, so you will need to re-authenticate every 2 days, either through the [web app](#Authentication via web browser app) or with the [command line](#Authentication with command line)

### Authentication via web browser app
After installing **kubectl**, authenticate through the [MAIA Login](https://loginapp.k8s-maia.com) webpage.
Copy/paste and execute the displayed commands on your shell or either download the full config file and save it as `~/.kube/config`.

NOTE: In Windows systems, `Git Bash` is the recommended shell to execute *Kube* commands.

### Authentication with command line
In order to properly authenticate using the command line, [KubeLogin](https://github.com/int128/kubelogin) needs to be installed first.

You can get the latest binary release for your OS on the GitHub page, and save it as `~/.kube/kubectl-oidc_login`.
After saving it, run ``kubectl oidc-login``. You will be prompted to a webpage where to login with your credentials.
After a successful login, the new ID token will be automatically saved in the *config* file.

## First time Authentication

When you authenticate to the cluster for the first time after the registration, you will need to set your personal namespace as the default.
This is because, by default, Kubernetes assignes the namespace `default` as the current one.
To set your personal namespace as the current one:
```
kubectl config set-context --current --namespace=YOUR_NAMESPACE
```

