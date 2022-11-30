
import setuptools
import os

from setuptools import setup

def read_file(file):
    with open(file) as f:
        content = f.read()
    return content

setup(
    name="hive-gate",
    version="1.0",
    url="https://github.com/MAIA-KTH/Hive-Gate.git",
    license="GPLv3",
    author="Simone Bendazzoli",
    author_email="simben@kth.se",
    project_urls={
        'Documentation': 'https://maia-kth.github.io/Hive_Gate/',
        'Source': 'https://github.com/MAIA-KTH/Hive_Gate',
        'Tracker': 'https://github.com/MAIA-KTH/Hive_Gate/issues',
    },
    long_description=read_file(os.path.join(os.path.dirname(__file__), "README.md")),
    long_description_content_type="text/markdown",
    description="Python interface to MAIA. It can be used as interface to any Kubernetes-based platform.",
    packages=setuptools.find_packages(),
    package_data={
        "": ["configs/*.yml", "configs/*.json"],
    },
    entry_points={
        "console_scripts": [
            "Hive_Gate_deploy_helm_chart = scripts.Hive_Gate_deploy_helm_chart:main"
        ],
    },
    keywords=["helm","kubernetes","maia","resource deployment"],

)
