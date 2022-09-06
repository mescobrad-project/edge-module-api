import logging
import mescobrad_edge.singleton as singleton
import watchdog.events
import time

import mescobrad_edge.singleton as singleton

class PluginHandler(watchdog.events.PatternMatchingEventHandler):
    def __init__(self, plugin_folder):
        # Set the patterns for PatternMatchingEventHandler
        watchdog.events.PatternMatchingEventHandler.__init__(self, ignore_directories=False, case_sensitive=False)
        self.plugin_folder_path = f"{plugin_folder}/"

    def on_created(self, event):
        if event.is_directory:

            # WAITING FOR FILE TRANSFER
            file = None
            attempt = 0
            config_path=event.src_path + "/" + singleton.PLUGIN_INFO_FILE
            while file is None and attempt < singleton.MAX_PLUGIN_SCAN_ATTEMPT:
                try:
                    file = open(config_path)
                except OSError:
                    file = None
                    logging.debug("Waiting for the plugin config file at {}".format(config_path))
                    attempt+=1
                    time.sleep(3)
                    continue

            logging.info("New folder detected - % s" % event.src_path)
            plugin_id = event.src_path.replace(f"{singleton.ROOT_DIR}/{self.plugin_folder_path}", '', 1).split('/')[0]
            logging.info("Checking if %s is a valid plugin" % plugin_id)
            singleton.plugin_manager.install_plugin(plugin_id)

    def on_deleted(self, event):
        if event.is_directory:
            logging.info("Watchdog received deleted folder - % s" % event.src_path)
            plugin_id = event.src_path.replace(f"{singleton.ROOT_DIR}/{self.plugin_folder_path}", '', 1).split('/')[0]
            logging.info("checking if %s was a valid plugin" % plugin_id)
            singleton.plugin_manager.uninstall_plugin(plugin_id)