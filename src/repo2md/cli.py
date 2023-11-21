import heapq
import os
import sys

import click
import humanize

from repo2md import (
    Collector,
    Config,
    NodeTreeSplitter,
    logger,
    render_markdown,
)


# Helper function to find largest files
def find_largest_files(root_node, n):
    files = [(node.size, node.path) for node in root_node.file_children]
    return heapq.nlargest(n, files)


@click.command()
@click.argument(
    "repo_path",
    type=click.Path(exists=True),
)
@click.option(
    "--max-size",
    default=512 * 1024 * 1024,
    help="Max size of each Markdown file in bytes.",
)
@click.option(
    "--max-files",
    default=10,
    help="Max number of Markdown files to generate.",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Perform a dry run to display repository stats.",
)
@click.option(
    "--list-largest",
    default=0,
    help="List the largest N files in the repository.",
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Enable verbose output.",
)
@click.option(
    "-q",
    "--quiet",
    is_flag=True,
    help="Suppress output.",
)
def cli(**kwargs):
    config = Config()
    config.update_config(**kwargs)

    collector = Collector(config.repo_path)
    root_node = collector.build_node_tree()

    if config.dry_run:
        print(f"Total size: {humanize.naturalsize(root_node.size)}")
        print(f"Files: {root_node.file_count}")
        print(f"Directories: {root_node.dir_count}")
        sys.exit(0)

    if config.list_largest > 0:
        largest_files = find_largest_files(root_node, config.list_largest)
        for size, path in largest_files:
            print(f"{path}: {humanize.naturalsize(size)}")
        sys.exit(0)

    splitter = NodeTreeSplitter(root_node, config.max_size, config.max_files)
    nodes = splitter.split()

    if nodes is None:
        print("Repository content exceeds the set limits.")
        sys.exit(1)

    output_dir = os.path.join(config.repo_path, "repo2md_output")
    os.makedirs(output_dir, exist_ok=True)

    for index, node in enumerate(nodes):
        render_markdown(node, output_dir, index)

    logger.info("Markdown files generated successfully.")
