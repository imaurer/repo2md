import logging
from dataclasses import dataclass
from typing import Optional

SYNTAX_MAP = {
    "": "text",
    ".md": "markdown",
    ".py": "python",
    ".rs": "rust",
    ".js": "javascript",
    ".ts": "typescript",
    # todo: add more extensions that need mapping (i.e. not css, java)
}

logger = logging.getLogger("repo2md")


@dataclass
class Config:
    _instance: Optional["Config"] = None

    repo_path: str = "."
    max_size: int = 512 * 1024 * 1024
    max_files: int = 10
    dry_run: bool = False
    list_largest: int = 0
    verbose: bool = False
    quiet: bool = False
    logger: logging.Logger = None

    def __init__(self):
        pass

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
        return cls._instance

    @property
    def logging_level(self):
        level = logging.DEBUG if self.verbose else logging.WARNING
        level = logging.ERROR if self.quiet else level
        return level

    def update_config(self, **kwargs):
        for key, value in kwargs.items():
            if value is not None:
                setattr(self, key, value)
        logger.setLevel(level=self.logging_level)


config = Config()


def slugify(value: str) -> str:
    """Converts strings to a slug format suitable for identifiers."""
    return "".join(char if char.isalnum() else "-" for char in value)
