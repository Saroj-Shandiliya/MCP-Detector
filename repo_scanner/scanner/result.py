from datetime import datetime
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field

class Indicator(BaseModel):
    type: str # 'keyword', 'dependency', 'ast', 'filename'
    value: str
    file: Optional[str] = None
    line: Optional[int] = None
    context: Optional[str] = None
    score: float = 0.0
    classification: Optional[str] = None # SERVER, CLIENT

class ScanResult(BaseModel):
    repository: str
    classification: str = "UNKNOWN" # SERVER, CLIENT, PROTOCOL_RELATED, UNKNOWN
    confidence: float = 0.0
    indicators: List[Indicator] = []
    languages_detected: List[str] = []
    files_scanned: int = 0
    commit_sha: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class RepoMetadata(BaseModel):
    name: str
    owner: str
    full_name: str
    html_url: str
    description: Optional[str] = None
    language: Optional[str] = None
    stars: int = 0
    default_branch: str = "main"
    updated_at: str

class FileData(BaseModel):
    path: str
    content: str
    extension: str
