import os

import pathspec

from repo2md import Collector

TEST_PATH = os.path.dirname(__file__)
REPO_ROOT_PATH = os.path.dirname(TEST_PATH)
EMPTY_DIR_PATH = os.path.join(TEST_PATH, "empty_dir")
IGNORE_FILE_PATH = os.path.join(REPO_ROOT_PATH, ".repo2md_ignore")


def test_read_ignore_file_exists():
    builder = Collector(REPO_ROOT_PATH)
    patterns = builder.read_ignore_file()
    assert isinstance(patterns, pathspec.PathSpec)


def test_read_ignore_file_not_exists():
    collector = Collector("/non_existing_path")
    assert collector.matches_ignore_pattern("~/.git/file.txt")


def test_matches_ignore_pattern_match():
    builder = Collector(REPO_ROOT_PATH)
    assert builder.matches_ignore_pattern("test.log")


def test_matches_ignore_pattern_no_match():
    builder = Collector(REPO_ROOT_PATH)
    assert not builder.matches_ignore_pattern("test.py")


def test_build_node_tree_empty():
    builder = Collector(EMPTY_DIR_PATH)
    root_node = builder.build_node_tree()
    assert root_node is None  # Empty directory should return None


def test_build_node_tree_non_empty():
    builder = Collector(TEST_PATH)
    node = builder.build_node_tree()
    assert node.path == "."
    assert node.file_count == 5
    assert node.dir_count == 0


def test_plan_valid_root():
    builder = Collector(REPO_ROOT_PATH)
    node = builder.build_node_tree()
    assert node is not None
    assert node.path == "."
    assert node.parent is None
    assert node.dir_count == 2
    assert node.file_count == 7

    for child in node:
        assert child.parent == node


def test_plan_invalid_root():
    builder = Collector("/non_existing_path")
    node = builder.build_node_tree()
    assert node is None  # Invalid path should return None
