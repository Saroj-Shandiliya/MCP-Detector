import requests
import zipfile
import io
import tempfile
import shutil
import os
from repo_scanner.scanner.utils import logger
from contextlib import contextmanager
from typing import Generator

class RepoFetcher:
    def __init__(self, token: str = None):
        self.token = token

    def _get_headers(self):
        headers = {}
        if self.token:
            headers["Authorization"] = f"token {self.token}"
        return headers

    @contextmanager
    def fetch_repo_zip(self, url: str) -> Generator[str, None, None]:
        """
        Downloads a repo ZIP from GitHub and extracts it to a temporary directory.
        Yields the path to the extracted directory.
        """
        # Convert GitHub URL to zipball URL if needed
        # Expected format: https://github.com/owner/repo or https://api.github.com/repos/owner/repo
        
        if "github.com" in url and not url.endswith(".zip"):
             # Simple heuristic for public web URLs: https://github.com/owner/repo -> https://github.com/owner/repo/archive/refs/heads/main.zip
             # But safer to use API if possible or codeload.
             # Let's assume standard "https://github.com/owner/repo/archive/master.zip" or similar.
             # Better approach: Use the API to get the default branch, but for now we'll rely on the user passing a valid download URL or constructing one.
             # For this step, I'll assume the URL passed IS the download URL or I construct it blindly for main/master.
             # Wait, the requirements say "No git clone... Use ZIP download".
             # I will implement a smarter URL builder in GitHubClient, but here keep it simple.
             pass

        logger.info(f"Downloading repository from {url}...")
        try:
            response = requests.get(url, headers=self._get_headers(), stream=True)
            response.raise_for_status()
            
            with tempfile.TemporaryDirectory() as temp_dir:
                try:
                    with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                        # Security check for zip slip could go here
                        z.extractall(temp_dir)
                        
                        # GitHub zips usually have a top-level folder (repo-branch)
                        # We want to yield that inner folder if it exists
                        contents = os.listdir(temp_dir)
                        if len(contents) == 1 and os.path.isdir(os.path.join(temp_dir, contents[0])):
                            yield os.path.join(temp_dir, contents[0])
                        else:
                            yield temp_dir
                except zipfile.BadZipFile:
                    logger.error("Failed to unzip repository.")
                    raise ValueError("Invalid ZIP file")
        except requests.RequestException as e:
            logger.error(f"Network error downloading repo: {e}")
            raise
