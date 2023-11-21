import os
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional


class NodeType(str, Enum):
    FILE = "FILE"
    DIR = "DIR"


@dataclass
class Node:
    path: str
    type: NodeType = NodeType.DIR
    size: int = 0
    file_count: int = 0
    dir_count: int = 0
    file_children: List["Node"] = field(default_factory=list)
    dir_children: List["Node"] = field(default_factory=list)
    parent: Optional["Node"] = None

    def __repr__(self):
        return f"{self.path} [{self.type.value}]"

    def __iter__(self):
        yield from self.file_children
        yield from self.dir_children

    @property
    def extension(self):
        return os.path.splitext(self.path)[-1]

    @property
    def basename(self):
        return os.path.basename(self.path)

    @property
    def is_dir(self):
        return self.type == NodeType.DIR

    @property
    def is_file(self):
        return self.type == NodeType.FILE

    def add_child(self, child: "Node"):
        if child is not None:
            if child.is_dir:
                self.dir_children.append(child)
            else:
                self.file_children.append(child)
            child.parent = self
        return child
