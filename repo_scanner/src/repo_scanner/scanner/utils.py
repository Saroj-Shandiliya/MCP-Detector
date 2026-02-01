import logging
import sys
from rich.logging import RichHandler

def setup_logger(name: str = "repo_scanner", level: int = logging.INFO) -> logging.Logger:
    """Sets up a logger with RichHandler."""
    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True)]
    )
    return logging.getLogger(name)

logger = setup_logger()

def load_config(path: str) -> dict:
    import yaml
    try:
        with open(path, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        logger.error(f"Config file not found: {path}")
        return {}
    except yaml.YAMLError as e:
        logger.error(f"Error parsing config file {path}: {e}")
        return {}
