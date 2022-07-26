import logging
import os
import json
from threading import Lock
import shutil
from xmlrpc.client import Boolean

from mescobrad_edge.singleton import ROOT_DIR

PLUGIN_LIST_PATH = "plugin_manager/.config/plugin_list.json"
plugin_list_mutex = Lock()

class PluginManager():

    def __init__(self, plugin_folder_path, plugin_downloader, plugin_validation_func, plugin_conf_func) -> None:
        # Set plugin_list config
        self.plugin_list_path = PLUGIN_LIST_PATH
        # Set plugin folder path
        self.plugin_folder_path = plugin_folder_path
        # Set plugin validation function
        self.plugin_validation_func = plugin_validation_func
        # Set plugin configuration function
        self.plugin_conf_func = plugin_conf_func
        # Set plugin downloader
        self.plugin_downloader = plugin_downloader

        # Load plugin list in memory
        self.plugin_list = {}


        self.plugin_list = self.__load_plugin_list__()
        self.__update_plugin_conf_file__()

    def __load_plugin_list__(self):
        in_memory_plugin_list = {}

        # List folders within plugin folder
        persisted_plugin_dict = [ '/'.join(f.path.split(self.plugin_folder_path)[1:]) for f in os.scandir(ROOT_DIR + '/' + self.plugin_folder_path) if f.is_dir() ]
        
        logging.debug("Plugins in the local config file: {}".format(persisted_plugin_dict))
        
        # For each plugin
        for plugin_id in persisted_plugin_dict:
            logging.info("Validating plugin {} ".format(plugin_id))
            # Validate plugin (if True the function returns also the plugin info, otherwise None )
            is_valid, plugin_info = self.__validate_plugin__(plugin_id)
            if is_valid:
                logging.info("Plugin {} is valid, extracting plugin_info".format(plugin_id))
                # If valid, add to the in-memory array
                in_memory_plugin_list[plugin_id] = plugin_info
            else:
                logging.info("Plugin {} is not valid, uninstalling".format(plugin_id))
                # If not, uninstall it
                self.uninstall_plugin(plugin_id)

        logging.info("Plugins correctly loaded: {}".format(list(in_memory_plugin_list.keys()))) 

        return in_memory_plugin_list

    def __update_plugin_conf_file__(self):
        # Re-Write plugin list file
        with open(ROOT_DIR + '/' + self.plugin_list_path, 'w') as persisted_plugin_json:
            json.dump(self.plugin_list, persisted_plugin_json)

    def __validate_plugin__(self, plugin_id):
        plugin_path = ROOT_DIR + "/" + self.plugin_folder_path + plugin_id
        logging.info("Validating plugin at {}".format(plugin_path))
        # Return True or False
        return self.plugin_validation_func(plugin_path)

    def list_plugins(self) -> dict:
        return self.plugin_list

    def get_plugin_info(self, plugin_id) -> dict:
        return self.plugin_list[plugin_id] if plugin_id in self.plugin_list.keys()  else None

    def download_plugin(self, plugin_id, plugin_repo) -> Boolean:
        try:
            # Download plugin
            self.plugin_downloader.download(plugin_repo, "{}/{}/{}".format(ROOT_DIR, self.plugin_folder_path, plugin_id))
            return True
        except:
            logging.error("Impossible to download plugin {} at url {}".format(plugin_id, plugin_repo))
            return False


    def delete_plugin_folder(self, plugin_id) -> None:
        # Delete plugin folder recursively
        shutil.rmtree(ROOT_DIR + "/" +self.plugin_folder_path + plugin_id, ignore_errors=True)

    def install_plugin(self, plugin_id) -> None:
        # Validate plugin
        is_valid, plugin_info = self.__validate_plugin__(plugin_id)
        if is_valid:
            logging.info("{} is a valid plugin".format(plugin_id))
            # Update the plugin list file
            # Lock on general plugin list file
            with plugin_list_mutex:
                # Write plugin_info
                self.plugin_list[plugin_id] = plugin_info
                self.__update_plugin_conf_file__()
        else:
            logging.info("{} is not a valid plugin".format(plugin_id))
            self.delete_plugin_folder(plugin_id)

    def configure_plugin(self, plugin_id, configurations) -> None:
        # Lock on specific plugin conf file
        self.plugin_conf_func(plugin_id, configurations)

    def uninstall_plugin(self, plugin_id) -> None:
        # Lock on general plugin list file
        with plugin_list_mutex:
            self.plugin_list.pop(plugin_id, None)    
            self.__update_plugin_conf_file__()
