import os
from typing import Generator, List, Dict
from .utils import logger
from .result import FileData

class FileFilter:
    def __init__(self, languages_config: Dict, max_file_size: int = 100 * 1024):
        self.languages = languages_config
        self.max_file_size = max_file_size
        self.allowed_extensions = set()
        self.special_files = set()
        
        for lang_config in self.languages.values():
            self.allowed_extensions.update(lang_config.get('extensions', []))
            self.special_files.update(lang_config.get('special_files', []))

    def walk_repo(self, root_path: str) -> Generator[FileData, None, None]:
        for root, dirs, files in os.walk(root_path):
            # Skip hidden directories and node_modules/venv
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ('node_modules', 'venv', '__pycache__')]
            
            for file in files:
                file_path = os.path.join(root, file)
                
                # Check extension and filename
                _, ext = os.path.splitext(file)
                if ext not in self.allowed_extensions and file not in self.special_files:
                    continue
                
                # Check size
                try:
                    if os.path.getsize(file_path) > self.max_file_size:
                        logger.debug(f"Skipping large file: {file_path}")
                        continue
                        
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        yield FileData(path=file_path, content=content, extension=ext)
                except Exception as e:
                    logger.warning(f"Error reading file {file_path}: {e}")
