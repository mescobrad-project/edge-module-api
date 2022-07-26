from ast import parse
from urllib.parse import urlparse
from mescobrad_edge.plugin_manager.plugin_downloader import PluginDownloader
from git import Repo

class GitHubDownloader(PluginDownloader):

    def __init__(self) -> None:
        super().__init__()
        self.VALID_URL = "github.com"

    def validate_url(self, url):
        # from urlparse import urlparse  # Python 2
        parsed_uri = urlparse(url)
        return parsed_uri.netloc == self.VALID_URL

    def download(self, url, destination):
        if self.validate_url(url):
            Repo.clone_from(url, destination)
        else:
            raise Exception("URL is not valid")

