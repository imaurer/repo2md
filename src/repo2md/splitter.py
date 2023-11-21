import os
import dataclasses
from typing import List, Optional

from repo2md import NodeType, Node, logger, SYNTAX_MAP, slugify


class SplitterException(Exception):
    pass


class InputFileSizeException(SplitterException):
    pass


class OutputFileLimitException(SplitterException):
    pass


def calculate_file_byte_size(node: Node, indent_level=0):
    """
    Calculate the number of bytes added by including a file in the document.

    :param node: The file node to be added.
    :param indent_level: The level of indentation in the TOC.
    :return: The number of bytes added.
    """
    byte_count = 0

    # Calculate bytes for the file name in the TOC and header
    file_name = os.path.basename(node.path)
    byte_count += len(file_name.encode())

    # Calculate bytes for the slugified path (used in links)
    slugified_path = slugify(node.path)
    byte_count += len(slugified_path.encode())

    # Indentation bytes in the TOC
    toc_indent = "    " * indent_level
    byte_count += len(toc_indent.encode())

    # Static elements: newpage, newlines, TOC, Next/Prev links
    # Adding bytes for each static element
    byte_count += len("\n\\newpage\n\n".encode())
    byte_count += len(f"## {file_name} {{#{slugified_path}}}\n".encode())
    byte_count += len("[TOC](#toc) ".encode())
    byte_count += len("[PREV](#prev) ".encode())
    byte_count += len("[NEXT](#next)\n\n".encode())

    # Add bytes for content and code block syntax if not markdown
    syntax_type = SYNTAX_MAP.get(
        node.path.split(".")[-1], node.path.split(".")[-1]
    )
    if syntax_type != "markdown":
        # Opening and closing backticks with syntax type
        byte_count += len(f"```{syntax_type}\n".encode())
        byte_count += len("\n```\n".encode())

    # Add bytes of file
    byte_count += node.size

    logger.debug(f"Calculated byte size for '{node}': {byte_count} bytes")
    return byte_count


class NodeTreeSplitter:
    def __init__(
        self, input_root_node: Node, max_file_size: int, max_num_files: int
    ):
        self.input_root_node = input_root_node
        self.max_file_size = max_file_size
        self.max_num_files = max_num_files
        self.output_root_nodes = []
        self.current_size = 0

    def split(self) -> Optional[List[Node]]:
        try:
            self.descend(self.input_root_node, None)
        except SplitterException as e:
            logger.warning(str(e))
            return None
        return self.output_root_nodes

    def start_new_root(self, input_node: Node) -> Node:
        new_output_root = Node(path=input_node.path, type=NodeType.DIR)
        self.output_root_nodes.append(new_output_root)
        self.current_size = 0
        return new_output_root

    def descend(self, input_node: Node, output_node: Optional[Node]):
        if output_node is None:
            output_node = self.start_new_root(input_node)
            for child_node in input_node:
                self.descend(child_node, output_node)

        elif input_node.type == NodeType.FILE:
            node_size = calculate_file_byte_size(input_node)
            if node_size > self.max_file_size:
                raise InputFileSizeException(input_node.path)

            if self.current_size + node_size > self.max_file_size:
                if len(self.output_root_nodes) >= self.max_num_files:
                    raise OutputFileLimitException()

                output_node = self.start_new_root(input_node)
                self.current_size = 0

            output_child_node = dataclasses.replace(input_node, parent=None)
            output_node.add_child(output_child_node)
            self.current_size += node_size

        elif input_node.type == NodeType.DIR:
            new_dir_node = Node(path=input_node.path, type=NodeType.DIR)
            output_node.add_child(new_dir_node)
            for child_node in input_node:
                self.descend(child_node, new_dir_node)
