#!/usr/bin/env python3
import os
import logging

LOGLEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(level=LOGLEVEL)

import time
import watchdog.observers
import connexion

from swagger_server.plugin_manager.plugin_manager import PluginManager
from swagger_server.plugin_manager.event_handler import PluginHandler
from swagger_server.plugin_manager.function_validator import default_validator
from swagger_server.plugin_manager.github_downloader import GitHubDownloader
from swagger_server import encoder

import swagger_server.singleton as singleton

def __init_observer__(plugin_folder_path):
    event_handler = PluginHandler(plugin_folder_path)
    # Init observer
    observer = watchdog.observers.Observer()
    # Init scheduler
    observer.schedule(event_handler, path=singleton.ROOT_DIR + '/' + plugin_folder_path, recursive=False)
    # Start observing
    logging.info("Starting watching folder {} for new plugins".format(singleton.ROOT_DIR + '/' + plugin_folder_path))
    observer.start()


def main():
    app = connexion.App(__name__, specification_dir='./swagger/')
    app.app.json_encoder = encoder.JSONEncoder
    app.add_api('swagger.yaml', arguments={'title': 'MES-CoBraD Edge module API'}, pythonic_params=True)

    plugin_downloader = GitHubDownloader()
    singleton.plugin_manager = PluginManager(singleton.PLUGIN_FOLDER_PATH, plugin_downloader, default_validator, None)
    __init_observer__(singleton.PLUGIN_FOLDER_PATH)

    app.run(port=8080)



if __name__ == '__main__':
    main()
