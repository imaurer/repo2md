import os

import pytest

from repo2md import (
    Collector,
    Node,
    calculate_file_byte_size,
    NodeType,
    NodeTreeSplitter,
)

REPO_ROOT_PATH = os.path.dirname(os.path.dirname(__file__))


@pytest.fixture
def mock_node():
    return Node(path="/path/to/test.md", type=NodeType.FILE, size=100)


def test_calculate_byte_size_markdown(mock_node):
    mock_node.path = "/path/to/test.md"
    byte_size = calculate_file_byte_size(mock_node)
    assert byte_size == 100 + 117


def test_calculate_byte_size_non_markdown(mock_node):
    mock_node.path = "/path/to/test.py"
    byte_size = calculate_file_byte_size(mock_node)
    assert byte_size == 100 + 117


def test_calculate_byte_size_with_indentation(mock_node):
    byte_size_level_0 = calculate_file_byte_size(mock_node, 0)
    byte_size_level_1 = calculate_file_byte_size(mock_node, 1)
    assert byte_size_level_1 > byte_size_level_0


@pytest.fixture
def sample_node_tree():
    root = Node(path="/tmp/test/")
    root.add_child(Node(path="/tmp/test/sub")).add_child(
        Node(path="/tmp/test/sub/file1.txt", type=NodeType.FILE, size=500)
    )
    root.add_child(
        Node(path="/tmp/test/sub/file2.txt", type=NodeType.FILE, size=500)
    )
    return root


def test_assign_nodes_within_size_limit(sample_node_tree):
    splitter = NodeTreeSplitter(sample_node_tree, 1500, 10)
    output_files = splitter.split()
    assert output_files is not None
    assert len(output_files) == 1
    assert all(file.path == "/tmp/test/" for file in output_files)


def test_maximum_file_limit(sample_node_tree):
    splitter = NodeTreeSplitter(sample_node_tree, 999, 1)
    output_files = splitter.split()
    assert output_files is None  # Expecting to exceed file limit


def test_skip_oversized_node(sample_node_tree):
    child = sample_node_tree.add_child(
        Node(path="/tmp/test/bigfile.txt", type=NodeType.FILE, size=1001)
    )
    assert child.is_file
    splitter = NodeTreeSplitter(sample_node_tree, 1000, 10)
    output_files = splitter.split()
    assert output_files is None  # Oversized node should cause failure


def test_file_incrementation_on_size_exceeds(sample_node_tree):
    splitter = NodeTreeSplitter(sample_node_tree, 1000, 10)
    output_files = splitter.split()
    assert output_files is not None
    assert len(output_files) > 1


def test_build_assign_repo():
    builder = Collector(REPO_ROOT_PATH)
    node = builder.build_node_tree()
    assert node is not None
    assert node.path == "."

    splitter = NodeTreeSplitter(node, 1_000_000, 1)
    output_nodes = splitter.split()

    assert len(output_nodes) == 1
    new_root = output_nodes[0]
    assert new_root.path == node.path

    child = new_root.dir_children[0]
    assert child.path == node.dir_children[0].path
    assert (
        child.file_children[0].path
        == node.dir_children[0].file_children[0].path
    )
