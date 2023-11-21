import os
from repo2md import SYNTAX_MAP, slugify, NodeType, logger


def render_file_content(node):
    """Renders the content of a file node."""
    syntax_type = SYNTAX_MAP.get(node.extension, node.extension)
    logger.debug(f"Rendering: {node.basename} [{syntax_type}]")
    with open(node.path, "r") as file:
        content = file.read()
    return (
        content
        if syntax_type == "markdown"
        else f"```{syntax_type}\n{content}\n```"
    )


def generate_navigation_links(index, total_files):
    """Generate navigation links for a file section."""
    nav_links = "[TOC](#table-of-contents) | "
    nav_links += f"[PREV](#file-{index - 1}) | " if index > 0 else "PREV | "
    nav_links += (
        f"[NEXT](#file-{index + 1})\n\n"
        if index < total_files - 1
        else "NEXT\n\n"
    )
    return nav_links


def render_toc(node, indent=0):
    """
    Renders the Table of Contents with proper indentation for nested files
    and directories.

    Args:
        node (Node): The node to render in the TOC.
        indent (int): The current indentation level.
    """
    logger.debug(f"TOC Node: {node.path} [indent={indent}]")
    toc = ""

    if node.type == NodeType.DIR:
        if node.basename != ".":
            toc += f"{'    ' * indent}* {node.basename}\n"
        for child in sorted(
            node.file_children + node.dir_children, key=lambda x: x.path
        ):
            toc += render_toc(child, indent + 1)
    else:
        # File: Create a clickable link
        link = slugify(node.path)
        toc += f"{'    ' * indent}* [{node.basename}](#{link})\n"

    return toc


def render_markdown(node, output_directory, index):
    """

    :param node:
    :param output_directory:
    :param index:
    :return:
    """
    markdown_file_path = os.path.join(output_directory, f"output_{index}.md")

    with open(markdown_file_path, "w") as markdown_file:
        markdown_file.write(render_toc(node))
        descend(markdown_file, node)

    return markdown_file_path


def descend(markdown_file, node):
    # Write each file content
    for file_node in node.file_children:
        markdown_file.write("\n\\newpage\n\n")
        file_header = " ".join(
            [
                "##",
                file_node.basename,
                f"{{#{slugify(file_node.path)}}}\n",
            ]
        )
        markdown_file.write(file_header)

        # Navigation links
        nav_links = generate_navigation_links(
            node.file_children.index(file_node), len(node.file_children)
        )
        markdown_file.write(nav_links)

        # File content
        content = render_file_content(file_node)
        markdown_file.write(content)

    for dir_node in node.dir_children:
        descend(markdown_file, dir_node)
