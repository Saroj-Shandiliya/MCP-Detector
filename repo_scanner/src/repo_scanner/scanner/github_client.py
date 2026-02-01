import requests
import time
from typing import List, Generator, Optional
from .result import RepoMetadata
from .utils import logger

class GitHubClient:
    BASE_URL = "https://api.github.com"

    def __init__(self, token: str = None):
        self.token = token
        self.session = requests.Session()
        if token:
            self.session.headers.update({"Authorization": f"token {token}"})
        self.session.headers.update({"Accept": "application/vnd.github.v3+json"})

    def _request(self, method: str, endpoint: str, params: dict = None) -> requests.Response:
        url = f"{self.BASE_URL}{endpoint}"
        while True:
            response = self.session.request(method, url, params=params)
            
            # Handle Rate Limiting
            if response.status_code == 403 and "x-ratelimit-remaining" in response.headers:
                remaining = int(response.headers["x-ratelimit-remaining"])
                if remaining == 0:
                    reset_time = int(response.headers["x-ratelimit-reset"])
                    sleep_time = reset_time - int(time.time()) + 1
                    logger.warning(f"Rate limit exceeded. Sleeping for {sleep_time} seconds.")
                    time.sleep(sleep_time)
                    continue
            
            response.raise_for_status()
            return response

    def get_repo_metadata(self, owner: str, repo: str) -> RepoMetadata:
        endpoint = f"/repos/{owner}/{repo}"
        data = self._request("GET", endpoint).json()
        return RepoMetadata(
            name=data["name"],
            owner=data["owner"]["login"],
            full_name=data["full_name"],
            html_url=data["html_url"],
            description=data.get("description"),
            language=data.get("language"),
            stars=data["stargazers_count"],
            default_branch=data["default_branch"],
            updated_at=data["updated_at"]
        )

    def get_user_repos(self, username: str) -> Generator[RepoMetadata, None, None]:
        endpoint = f"/users/{username}/repos"
        yield from self._paginate_repos(endpoint)

    def get_org_repos(self, org: str) -> Generator[RepoMetadata, None, None]:
        endpoint = f"/orgs/{org}/repos"
        yield from self._paginate_repos(endpoint)

    def _paginate_repos(self, endpoint: str) -> Generator[RepoMetadata, None, None]:
        params = {"per_page": 100, "page": 1}
        while True:
            data = self._request("GET", endpoint, params=params).json()
            if not data:
                break
            
            for repo_data in data:
                 yield RepoMetadata(
                    name=repo_data["name"],
                    owner=repo_data["owner"]["login"],
                    full_name=repo_data["full_name"],
                    html_url=repo_data["html_url"],
                    description=repo_data.get("description"),
                    language=repo_data.get("language"),
                    stars=repo_data["stargazers_count"],
                    default_branch=repo_data["default_branch"],
                    updated_at=repo_data["updated_at"]
                )
            
            params["page"] += 1

    def get_archive_url(self, owner: str, repo: str, ref: str = None) -> str:
        # If ref is None, we need to know the default branch. 
        # But efficiently, we usually just want the default.
        # https://api.github.com/repos/OWNER/REPO/zipball/REF
        if ref:
            return f"{self.BASE_URL}/repos/{owner}/{repo}/zipball/{ref}"
        return f"{self.BASE_URL}/repos/{owner}/{repo}/zipball"
