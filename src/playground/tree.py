"""The module contains functions for working with the node tree in Nuke.
"""

from typing import Generator as _Generator

import nuke as _nuke

GenReturn = _Generator[_nuke.Node, _nuke.Node, None]


def all_nodes(start_node: _nuke.Node, expressions: bool = False, history: list[_nuke.Node] | None = None) -> GenReturn:
    """Get all nodes in the tree starting from the given node.

    Example:
        >>> for node in all_nodes(nuke.selectedNode()):
        ...     print(node.fullName())

    Args:
        start_node (nuke.Node): The node to start from.
        expressions (bool, optional): Include expression linked nodes. Defaults to False.
        history (list[nuke.Node], optional): The history of nodes visited. Defaults to None.

    Yields:
        nuke.Node: The nodes in the tree.
    """
    node = start_node
    history = history or []
    if node in history:
        return
    yield node
    history.append(node)
    for input_value in range(node.inputs()):
        if not node.input(input_value):
            continue
        yield from all_nodes(node.input(input_value), expressions=expressions, history=history)  # type: ignore
    if not expressions:
        return
    yield from expression_dependencies(node, history=history)


def expression_dependencies(node: _nuke.Node, history: list | None = None) -> GenReturn:
    """
    Get all nodes that the given node depends on.

    Example:
        >>> for node in expression_dependencies(nuke.selectedNode()):
        ...     print(node.fullName())

    Args:
        node (nuke.Node): The node to get the dependencies from.
        history (list, optional): The history of nodes visited. Defaults to None.

    Yields:
        nuke.Node: The nodes that the given node depends on
    """
    history = history or [node]
    flags = _nuke.EXPRESSIONS
    if not node.dependencies(flags) and not node.dependent(flags):
        return
    for expression in node.dependencies(flags) + node.dependent(flags):
        if expression in history or node == expression:
            continue
        history.append(expression)
        yield from expression_dependencies(expression, history=history)
        yield expression


def extended_all_nodes(start_node: _nuke.Node, history: list[_nuke.Node] | None = None) -> GenReturn:
    """Get all extended nodes in the tree starting from the given node. Include the dependents and dependencies of the
    expression nodes.

    Example:
        >>> for node in extended_all_nodes(nuke.selectedNode()):
        ...     node["tile_color"].setValue(16711935)

    Args:
        start_node (nuke.Node): The node to start from.
        history (list[nuke.Node], optional): The history of nodes visited. Defaults to None.

    Yields:
        nuke.Node: The nodes in the tree.
    """
    flags = _nuke.EXPRESSIONS
    history = history or []
    for node in all_nodes(start_node, history=history):
        # Dont change the yield order or remove the append history
        yield node
        history.append(node)
        # Find the extended dependents instead of checking for expression linked nodes.
        extended_dependents = node.dependent(flags, forceEvaluate=False) + node.dependencies(flags)
        for dependent in extended_dependents:
            if dependent in history:
                continue
            yield from extended_all_nodes(dependent, history=history)


def find_top_node(node: "_nuke.Node", node_input: int = 0, resolve: bool = False) -> _nuke.Node:
    """Find the top node in the tree starting from the given node.

    Example:
        >>> top_node = find_top_node(nuke.selectedNode())
        >>> print(top_node.fullName())
        ... 'Read1'

    Args:
        node (nuke.Node): The node to start from.
        node_input (int, optional): The input to start from. Defaults to 0.
        resolve (bool, optional): Resolve the node if it does not have an input. Defaults to False.

    Returns:
        nuke.Node: The top node in the tree.
    """

    if not node or not node.inputs():
        return node

    next_node = node.input(node_input) or (resolve and node.input(node.inputs() - 1))
    if not next_node:
        return node
    return find_top_node(next_node, node_input=node_input, resolve=resolve)


def tcl_top_node(node: _nuke.Node) -> _nuke.Node:
    """Find the top node in the tree starting from the given node using tcl.

    Example:
        >>> top_node = tcl_top_node(nuke.selectedNode())
        >>> print(top_node.fullName())
        ... 'Read1'

    Note:
        This is extensively faster than the find_top_node function but you are
        limited to not having resolve and input options.


    Args:
        node (nuke.Node): The node to start from.

    Returns:
        nuke.Node: The top node in the tree.
    """
    return _nuke.toNode(_nuke.tcl("topnode", node.name()))
