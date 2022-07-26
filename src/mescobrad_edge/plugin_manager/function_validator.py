import logging
import json
import mescobrad_edge.singleton as singleton



def default_validator(plugin_path:str):
    logging.info("Checking config file for plugin {}".format(plugin_path))
    try:
        plugin_info = {}
        with open(plugin_path + "/" + singleton.PLUGIN_INFO_FILE, 'r') as plugin_info_file:
            plugin_info = json.load(plugin_info_file)
        return True, plugin_info
    except:
        return False, None