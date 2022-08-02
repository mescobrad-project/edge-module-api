# Edge Module API

Choose and leave only one of the following badge

![REPO-TYPE](https://img.shields.io/badge/repo--type-backend-critical?style=for-the-badge&logo=github)


This repository contains the backend of the edge-module. It's intended to be deployed locally at the edge of the MES-CoBraD platform.

Such set of APIs allows the communications between the Edge module UI (Deployed within the MES-CoBraD platform) and the edge module functionalities. 

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

- Python 3.7
- Git

### Installing

A step by step series of examples that tell you how to get a development env running

Install docker on you dev machine

```
https://docs.docker.com/get-docker/
```

Run the following command to initializate a Python 3.7 environment

```
docker run --name python-dev --env-file dev.env -v "$(pwd)/src:/usr/src/" -d python:3.7-slim tail -f /dev/null && docker exec -it python-dev /bin/sh

```

Install Git
```
apt-get update
apt-get install git

```

Install Dependencies
```
pip3 install --no-cache-dir -r requirements.txt

```

## Built With

* [Connexion](https://connexion.readthedocs.io/en/latest/) - a framework built on top of Flask that automagically handles HTTP requests based on OpenAPI Specification
* [Pip](https://pip.pypa.io/en/stable/) - Dependency Management

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](tags). 

## Authors

* **Danilo Trombino** - *SW & Data Engineer* - [trowdan](https://github.com/trowdan)

See also the list of [contributors](contributors) who participated in this project.