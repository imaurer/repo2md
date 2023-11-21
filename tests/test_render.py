import tempfile
import os

from repo2md import (
    Collector,
    render_markdown,
)

REPO_ROOT_PATH = os.path.dirname(os.path.dirname(__file__))


def test_build_assign_and_render():
    builder = Collector(REPO_ROOT_PATH)
    node = builder.build_node_tree()
    assert node is not None
    assert node.path == "."

    with tempfile.TemporaryDirectory() as tmp_dir:
        render_markdown(node, tmp_dir, 0)
        assert os.listdir(tmp_dir) == ["output_0.md"]

        md_path = os.path.join(tmp_dir, "output_0.md")
        assert os.path.isfile(md_path)

        md_output = open(md_path, "r").read()
