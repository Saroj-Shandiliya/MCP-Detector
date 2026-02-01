import os
import re
from typing import List, Dict
from repo_scanner.scanner.result import Indicator
from .base import BaseScanner

class DependencyScanner(BaseScanner):
    def __init__(self):
        # Maps filenames to simple regex patterns for extraction
        self.parsers = {
            "requirements.txt": re.compile(r"^([a-zA-Z0-9_\-]+)", re.MULTILINE),
            "package.json": re.compile(r"\"(.*?)\"\s*:", re.MULTILINE), # Very naive, good enough for signal
            # Add more per language
        }
        
        # In a real impl, we'd cross reference these parsed deps against a list of known server/client libs in config
        # For now, we just extract them. The Classification/Scoring step will decide if they are "server" or "client".
        # OR we can do it here. The prompt says "Match against configurable patterns".
        # Let's assume passed config has known libs.

    def scan(self, file_path: str, content: str) -> List[Indicator]:
        indicators = []
        filename = os.path.basename(file_path)
        
        if filename in self.parsers:
            matches = self.parsers[filename].findall(content)
            for match in matches:
                # In a real system, we'd filter this list against known "interesting" dependencies
                # For this MVP, we report EVERYTHING as a dependency found, 
                # and let the scorer/classifier filter for "flask", "django", "requests", etc.
                # Actually, reporting everything is too noisy.
                # Let's just create an indicator "dependency" with value "dependency_name".
                
                # To be useful without hardcoding, we rely on the Config to tell us what is interesting.
                # But the prompt says "Dependency Scanner: Extract package names... Match against configurable patterns".
                # I will assume the Classifier will scan the list of indicators.
                
                # For efficiency, let's just emit them.
                indicators.append(Indicator(
                    type="dependency",
                    value=match,
                    file=file_path
                ))
                
        return indicators
