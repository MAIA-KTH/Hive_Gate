#!/usr/bin/env python

import json
import datetime
import subprocess
from argparse import ArgumentParser, RawTextHelpFormatter
from pathlib import Path
from textwrap import dedent

TIMESTAMP = "{:%Y-%m-%d_%H-%M-%S}".format(datetime.datetime.now())

DESC = dedent(
    """
    Script to deploy the Hive_Gate helm chart to a Kubernetes cluster. The target cluster is specified by ``kube_config_file``,
    while the configuration file for the chart is specified with ``config_file``.
    """  # noqa: E501
)
EPILOG = dedent(
    """
    Example call:
    ::
        {filename}  --config-file /PATH/TO/config_file.json --kube-config-file /HOME_FOLDER/.kube/config
    """.format(  # noqa: E501
        filename=Path(__file__).stem
    )
)


def get_arg_parser():
    pars = ArgumentParser(description=DESC, epilog=EPILOG, formatter_class=RawTextHelpFormatter)

    pars.add_argument(
        "--kube-config-file",
        type=str,
        required=False,
        default=None,
        help="Configuration file used to specify the Kubernetes context. Default to: ``~/.kube/config``",
    )

    pars.add_argument(
        "--config-file",
        type=str,
        required=True,
        help="JSON configuration file used to generate the custom values used in the Helm chart.",
    )

    return pars


def generate_custom_helm_values(config_dict):
    value_list = []
    additional_commands = []
    value_list.append("image.repository={}".format(config_dict['docker_image']))
    value_list.append("image.tag={}".format(config_dict['tag']))

    value_list.append("extraVolumeMounts[0].name=dshm")
    value_list.append("extraVolumeMounts[0].mountPath=/dev/shm")
    volume_mounts_index = 1

    value_list.append("resources.requests.memory={}".format(config_dict['memory_size']))
    value_list.append("resources.requests.cpu={}".format(config_dict['cpu']))

    value_list.append("resources.limits.memory={}".format(config_dict['memory_size']))
    value_list.append("resources.limits.cpu={}".format(config_dict['cpu']))

    extra_env_index = 0
    if 'gpu_request' in config_dict and int(config_dict["gpu_request"]) > 0:
        value_list.append("resources.limits.nvidia\\\.com/gpu={}".format(config_dict["gpu_request"]))
        value_list.append("gpus={}".format(config_dict["gpu_request"]))

    if 'persistent_volume' in config_dict:
        for idx, persistent_volume in enumerate(config_dict['persistent_volume']):
            for persistent_volume_key in persistent_volume:
                value_list.append("persistentVolume[{}].{}={}".format(idx, persistent_volume_key,
                                                                      config_dict['persistent_volume'][idx][
                                                                          persistent_volume_key]))

    if 'user_secret' in config_dict:
        value_list.append("extraEnv[{}].name=n_users".format(extra_env_index))
        value_list.append("extraEnv[{}].value=\"{}a\"".format(extra_env_index, str(len(config_dict['user_secret']))))
        extra_env_index += 1
        if len(config_dict['user_secret']) == 1:
            for user_secret_param in config_dict['user_secret_params']:
                value_list.append("extraEnv[{}].name={}".format(extra_env_index, user_secret_param))
                value_list.append(
                    "extraEnv[{}].valueFrom.secretKeyRef.key={}".format(extra_env_index, user_secret_param))
                value_list.append("extraEnv[{}].valueFrom.secretKeyRef.name={}".format(extra_env_index,
                                                                                       config_dict['user_secret'][0]))
                extra_env_index += 1
        else:
            for user_id, user in enumerate(config_dict['user_secret']):
                for idx, user_secret_param in enumerate(config_dict['user_secret_params']):
                    value_list.append("extraEnv[{}].name={}_{}".format(extra_env_index, user_secret_param, user_id))
                    value_list.append(
                        "extraEnv[{}].valueFrom.secretKeyRef.key={}".format(extra_env_index, user_secret_param))
                    value_list.append("extraEnv[{}].valueFrom.secretKeyRef.name={}".format(extra_env_index, user))
                    extra_env_index += 1

    if 'nfs_volume_mounts' in config_dict:
        for idx, extra_nfs_volume in enumerate(config_dict['nfs_volume_mounts']):
            value_list.append("extraNFSVolumes[{}].name={}".format(idx, extra_nfs_volume))
            value_list.append(
                "extraNFSVolumes[{}].hostPath={}".format(idx, config_dict['nfs_volume_mounts'][extra_nfs_volume][0]))
            value_list.append("extraNFSVolumes[{}].server={}".format(idx, config_dict['nfs_server']))

            value_list.append("extraVolumeMounts[{}].name={}".format(idx + volume_mounts_index, extra_nfs_volume))
            value_list.append("extraVolumeMounts[{}].mountPath={}".format(idx + volume_mounts_index,
                                                                          config_dict['nfs_volume_mounts'][
                                                                              extra_nfs_volume][1]))
            if len(config_dict['nfs_volume_mounts'][extra_nfs_volume]) > 2 and \
                    config_dict['nfs_volume_mounts'][extra_nfs_volume][2] == "readOnly":
                value_list.append("extraVolumeMounts[{}].readOnly=true".format(idx + volume_mounts_index
                                                                               ))

        volume_mounts_index += len(config_dict['nfs_volume_mounts'])

    if 'host_volume_mounts' in config_dict:
        for idx, extra_host_volume in enumerate(config_dict['host_volume_mounts']):
            value_list.append("extraHostVolumes[{}].name={}".format(idx, extra_host_volume))
            value_list.append(
                "extraHostVolumes[{}].hostPath={}".format(idx, config_dict['host_volume_mounts'][extra_host_volume][0]))

            value_list.append("extraVolumeMounts[{}].name={}".format(idx + volume_mounts_index, extra_host_volume))
            value_list.append("extraVolumeMounts[{}].mountPath={}".format(idx + volume_mounts_index,
                                                                          config_dict['host_volume_mounts'][
                                                                              extra_host_volume][1]))
            if len(config_dict['host_volume_mounts'][extra_host_volume]) > 2 and \
                    config_dict['host_volume_mounts'][extra_host_volume][2] == "readOnly":
                value_list.append("extraVolumeMounts[{}].readOnly=true".format(idx + volume_mounts_index
                                                                               ))
        volume_mounts_index += len(config_dict['host_volume_mounts'])

    if 'env_variables' in config_dict:
        for env_variable in config_dict["env_variables"]:
            value_list.append("extraEnv[{}].name={}".format(extra_env_index, env_variable))
            value_list.append(
                "extraEnv[{}].value={}".format(extra_env_index, config_dict['env_variables'][env_variable]))
            extra_env_index += 1

    if 'mount_files' in config_dict:
        for idx, mount_file in enumerate(config_dict["mount_files"]):
            print(mount_file)
            value_list.append("extraVolumeMounts[{}].name={}".format(idx + volume_mounts_index, mount_file))
            value_list.append("extraVolumeMounts[{}].mountPath={}".format(idx + volume_mounts_index,
                                                                          config_dict['mount_files'][mount_file][1]))
            additional_commands.append(
                "kubectl create configmap -n {} {} --from-file={}".format(config_dict["namespace"], mount_file,
                                                                          config_dict['mount_files'][mount_file][0]))
            value_list.append("extraConfigMapVolumes[{}].name={}".format(idx, mount_file))
            value_list.append("extraConfigMapVolumes[{}].configMapName={}".format(idx, mount_file))
            value_list.append("extraConfigMapVolumes[{}].configMapFile={}".format(idx, Path(
                config_dict['mount_files'][mount_file][0]).name))
            value_list.append("extraConfigMapVolumes[{}].configMapPath={}".format(idx, Path(
                config_dict['mount_files'][mount_file][0]).name))

        volume_mounts_index += len(config_dict['mount_files'])

    if 'ports' in config_dict:
        value_list.append("serviceEnabled=True")
        if 'service_type' in config_dict:
            value_list.append("service.type={}".format(config_dict['service_type']))
        else:
            value_list.append("service.type=ClusterIP")
        for idx, port in enumerate(config_dict['ports']):

            value_list.append("service.ports[{}].port={}".format(idx, config_dict['ports'][port][0]))
            value_list.append("service.ports[{}].targetPort={}".format(idx, config_dict['ports'][port][0]))
            value_list.append("service.ports[{}].name={}".format(idx, port))
            if 'service_type' in config_dict and config_dict['service_type'] != "ClusterIP":
                value_list.append("service.ports[{}].nodePort={}".format(idx, config_dict['ports'][port][1]))
    else:
        value_list.append("serviceEnabled=False")

    if "ingress" in config_dict:
        value_list.append("ingress.enabled=True")
        value_list.append("ingress.tls=True")
        value_list.append("ingress.host={}".format(config_dict["ingress"]["host"]))
        value_list.append("ingress.port={}".format(config_dict["ingress"]["port"]))

    if "node_selector" in config_dict:
        value_list.append("nodeSelected={}".format(config_dict["node_selector"]))

    if "gpu_selector" in config_dict:
        for gpu_selection in config_dict["gpu_selector"]:
            value_list.append("gpuSelected.{}={}".format(gpu_selection, config_dict["gpu_selector"][gpu_selection]))

    return ",".join(value_list), additional_commands


def main():
    parser = get_arg_parser()

    arguments = vars(parser.parse_args())

    config_file = arguments["config_file"]

    with open(config_file) as json_file:
        config_dict = json.load(json_file)

    sshProcess = subprocess.Popen(["sh"],
                                  stdin=subprocess.PIPE,
                                  stdout=subprocess.PIPE,
                                  universal_newlines=True,
                                  bufsize=0)

    helm_values, additional_commands = generate_custom_helm_values(config_dict)
    if len(additional_commands) > 0:
        for additional_command in additional_commands:
            subprocess.run(additional_command)

    if arguments["kube_config_file"] == None:
        arguments["kube_config_file"] = Path.home().joinpath(".kube", "config")

    sshProcess.stdin.write(
        "helm upgrade --install {} --namespace={} --kubeconfig={} hive-gate/hive-gate --set {}\n".format(
            config_dict["chart_name"], config_dict["namespace"], arguments['kube_config_file'], helm_values))
    sshProcess.stdin.close()
    for line in sshProcess.stdout:
        if line == "END\n":
            break
        print(line, end="")


if __name__ == "__main__":
    main()
