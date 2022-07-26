from pathlib import Path

ROOT_DIR = str(Path(__file__).parent)
PLUGIN_FOLDER_PATH="plugins/"
PLUGIN_INFO_FILE="plugin.info.json"
MAX_PLUGIN_SCAN_ATTEMPT=5
plugin_manager = None