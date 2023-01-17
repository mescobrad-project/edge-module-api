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
## Deployment

1. Open terminal (Find a launcher for the terminal by clicking on the Activities item at the top
left of the screen, then type 'terminal'. If you can't find the launcher you can try keyboard shortcut
to start it: Ctrl-Alt-T)

2. Next step is installing Docker. Type next commands one by one in terminal:
    ```
    wget https://get.docker.com
    ```
    ```
    mv index.html get-docker.sh && chmod a+x get-docker.sh
    ```
    ```
    DRY_RUN=1 sudo sh ./get-docker.sh
    ```
    ```
    DRY_RUN=0 sudo sh ./get-docker.sh
    ```
3. Next step is creating folder where all the needed files will be stored and download files. Follow next steps, one by one:
    ```
    mkdir mescobrad-edge
    ```
    ```
    cd mescobrad-edge
    ```
    ```
    wget https://raw.githubusercontent.com/mescobrad-project/edge-module-api/main/docker/docker-compose.yml
    ```
    ```
    wget https://raw.githubusercontent.com/mescobrad-project/edge-module-api/main/docker/edge_module.config
    ```

4. Set credentials for local instance of the MinIO in the downloaded *docker-compose.yml* file:
    * First open *docker-compose.yml* file:
        ```
        nano docker-compose.yml
        ```
    * Instead of empty string, type your credentials for next variables in the open file. Take care that min length of characters for user is 5 and for password is 8:
        ```
        MINIO_ROOT_USER: ""
        ```
        ```
        MINIO_ROOT_PASSWORD: ""
        ```
5. Customize *edge_module.config* file.
    * First open *edge_module.config* file:
        ```
        nano edge_module.config
        ```
    * Set the following variables in the opened file:
        ```
        OBJ_STORAGE_URL_LOCAL=http://mescobrad-edge_minio_1:9000
        ```
        ```
        OBJ_STORAGE_ACCESS_ID_LOCAL - the same username you have chosen in previous step (value of *MINIO_ROOR_USER* from the previous step)
        ```
        ```
        OBJ_STORAGE_ACCESS_SECRET_LOCAL - the same password you have chosen in previous step (value of *MINIO_ROOT_PASSWORD* from the previous step)
        ```
        ```
        OBJ_STORAGE_BUCKET_LOCAL - a bucket name of your choice
        ```

6) Run the *docker-compose.yml*:
    * First login into *registry.opsilab.eng.it*
        ```
        docker login registry.opsilab.eng.it
        ```
    * Run the following command
        ```
        docker-compose -f docker-compose.yml up -d
        ```

7) Run Swagger UI:
    * First download *swagger.yaml* file:
        ```
        wget https://raw.githubusercontent.com/mescobrad-project/edge-module-api/main/src/mescobrad_edge/swagger/swagger.yaml
        ```
    * Open https://editor.swagger.io/ in the browser
    * Import the *swagger.yaml* file downloaded in the previous step. Open File tab within main menu, and choose Import file, and then choose *swagger.yaml* file
    * Be sure that the schemes are set to HTTP. From the drop down menu schemes choose HTTP.
    * Within authorize tab put 'abc' as a token
    * Run *plugins/install_plugin* providing following urls to install. Choose the ones which you need and install each, one by one.
        * Plugins needed to install for using questionnaires anonymisation plugin:
            - https://github.com/mescobrad-project/edge_plugin_upload.git
            - https://github.com/mescobrad-project/edge_plugin_download.git
            - https://github.com/mescobrad-project/questionnaire_anonymisation_plugin.git

        * MRI anonymisation plugin:
            - https://github.com/mescobrad-project/mri_anonymisation_plugin.git

        * EDF anonymisation plugin:
            - https://github.com/mescobrad-project/edf_anonymisation_plugin.git

8) Navigate to each plugin folder under */var/lib/docker/volumes/plugins* and change data within *plugin.config* file. For example:
    ```
    cd var/lib/docker/volumes/plugins/mri_anonymisation_plugin
    ```
    ```
    nano plugin.config
    ```
    When file is updated, save and close file. Continue in the same way for all the others installed plugins.

Note: All the variables which contain *LOCAL* within name, reference to the local instance of MinIO, otherwise reference to the data lake instance

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