import os
import pathspec

from typing import Optional

from repo2md import Node, NodeType, logger

IGNORE_FILE_NAMES = [".repo2md_ignore", ".gitignore"]


class Collector:
    """
    A class for collecting and organizing file and directory nodes from a
    specified root path.

    Attributes:
        root_path (str): The root directory from which the node tree is built.
        ignore_spec (pathspec.PathSpec): File & directory patterns to ignored.

    Methods:
        read_ignore_file(): Reads ignore patterns from specified ignore files.
        matches_ignore_pattern(path, ignore_patterns): Checks if a given path
            matches any of the ignore patterns.
        process_directory(dirpath): Processes a directory and its contents,
            creating a Node structure.
        build_node_tree(): Builds the entire node tree from the root path.
    """

    def __init__(self, root_path: str):
        """
        Initializes the Collector with a given root path.

        Args:
            root_path (str): The root directory path from which the node tree
                will be built.
        """
        self.root_path = root_path
        self.ignore_spec = self.read_ignore_file()
        logger.debug(f"Ignore patterns: {self.ignore_spec.patterns}")

    def read_ignore_file(self) -> pathspec.PathSpec:
        """
        Reads ignore patterns from .repo2md_ignore or .gitignore files located
        in the root path.

        Returns:
            pathspec.PathSpec: A PathSpec object with compiled ignore patterns.
        """
        patterns = [".git/"]

        for ignore_file_name in IGNORE_FILE_NAMES:
            ignore_file_path = os.path.join(self.root_path, ignore_file_name)
            if os.path.exists(ignore_file_path):
                with open(ignore_file_path, "r") as file:
                    patterns += file.readlines()
                break

        logger.debug(f"Compiled patterns: {patterns}")
        return pathspec.PathSpec.from_lines("gitwildmatch", patterns)

    def matches_ignore_pattern(self, path: str) -> bool:
        """
        Determines if a given path matches any of the ignore patterns.

        Args:
            path (str): The path to check against ignore patterns.

        Returns:
            bool: True if the path matches any of the ignore patterns,
                  False otherwise.
        """
        return self.ignore_spec.match_file(path)

    def relpath(self, path: str) -> str:
        """
        Calculates the relative path from the root_path to the given path.

        Args:
            path (str): The absolute path for which the relative path is required.

        Returns:
            str: The relative path from the root_path to the given path.
        """
        return os.path.relpath(path, self.root_path)

    def process_directory(self, dirpath: str) -> Optional[Node]:
        """
        Processes a directory and its contents, creating a Node for the
        directory.

        Recursively processes each subdirectory and file within the directory,
        ignoring those that match the ignore patterns.

        Args:
            dirpath (str): The path of the directory to process.

        Returns:
            Optional[Node]: A Node representing the directory and its contents,
                or None if the directory is ignored.
        """
        if self.matches_ignore_pattern(dirpath):
            return None

        current_node = Node(path=self.relpath(dirpath), type=NodeType.DIR)
        try:
            for entry in os.scandir(dirpath):
                if entry.is_dir():
                    subdir_node = self.process_directory(entry.path)
                    if subdir_node:
                        subdir_node.parent = current_node
                        current_node.dir_children.append(subdir_node)
                        current_node.dir_count += 1
                        current_node.size += subdir_node.size
                elif entry.is_file():
                    if not self.matches_ignore_pattern(entry.path):
                        file_size = os.path.getsize(entry.path)
                        file_node = Node(
                            path=self.relpath(entry.path),
                            type=NodeType.FILE,
                            size=file_size,
                            parent=current_node,
                        )
                        current_node.file_children.append(file_node)
                        current_node.size += file_size
                        current_node.file_count += 1
        except (FileNotFoundError, PermissionError) as e:
            logger.warning(f"Error accessing {dirpath}: {e}")

        if current_node.file_count == 0 and current_node.dir_count == 0:
            return None

        return current_node

    def build_node_tree(self) -> Node:
        """
        Builds the entire node tree starting from the root path.

        Returns:
            Node: The root node of the generated node tree.
        """
        return self.process_directory(self.root_path)
