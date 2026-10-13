#!/usr/bin/env python3
# CircuitViewer4 - github.com/daniSoares08
# Open source (MIT License): free to use, copy, modify and redistribute.
"""Fundamental mesh/loop basis derived from a topology element graph.

This intentionally uses a graph-only spanning-tree cycle basis. It does not
try to trace planar faces or inspect drawing coordinates, which keeps the
result stable for the generated CircuitViewer4 topology records.
"""

from collections import deque


class MeshError(Exception):
    pass


def _active_nodes(elements):
    nodes = set()
    for elem in elements:
        nodes.add(elem["na"])
        nodes.add(elem["nb"])
    return nodes


def _edge_sign(elem, u, v):
    if elem["na"] == u and elem["nb"] == v:
        return 1
    if elem["na"] == v and elem["nb"] == u:
        return -1
    raise MeshError("edge does not connect traversal endpoints")


def _path_to_root(node, parent):
    path = []
    while node is not None:
        path.append(node)
        node = parent[node]
    return path


def _tree_path(start, end, parent, parent_edge, elements):
    """Return tree edges/signs for the directed path start -> end."""
    start_path = _path_to_root(start, parent)
    end_path = _path_to_root(end, parent)
    start_pos = {node: i for i, node in enumerate(start_path)}

    lca = None
    end_lca_pos = None
    for i, node in enumerate(end_path):
        if node in start_pos:
            lca = node
            end_lca_pos = i
            break
    if lca is None:
        raise MeshError("tree path not found")

    out = []

    node = start
    while node != lca:
        edge_idx = parent_edge[node]
        prev = parent[node]
        out.append((edge_idx, _edge_sign(elements[edge_idx], node, prev)))
        node = prev

    down_nodes = list(reversed(end_path[:end_lca_pos]))
    node = lca
    for child in down_nodes:
        edge_idx = parent_edge[child]
        out.append((edge_idx, _edge_sign(elements[edge_idx], node, child)))
        node = child

    return out


def _loop_nodes(loop, elements):
    nodes = set()
    for edge_idx, _sign in loop:
        elem = elements[edge_idx]
        nodes.add(elem["na"])
        nodes.add(elem["nb"])
    return nodes


def _assert_closed_walk(loop, elements):
    if not loop:
        raise MeshError("empty loop")

    current = None
    first = None
    for edge_idx, sign in loop:
        elem = elements[edge_idx]
        if sign == 1:
            u, v = elem["na"], elem["nb"]
        elif sign == -1:
            u, v = elem["nb"], elem["na"]
        else:
            raise MeshError("mesh edge sign must be +1 or -1")

        if current is None:
            first = u
        elif current != u:
            raise MeshError("loop is not a connected directed walk")
        current = v

    if current != first:
        raise MeshError("loop does not close")


def fundamental_meshes(topo):
    """Return a deterministic fundamental loop basis for a derived topology.

    topo is a dict as returned by topology.derive_topology(). The return value
    is a list of meshes; each mesh is a list of (element_index, sign) pairs.
    element_index indexes topo["elements"], and sign is +1 when traversing the
    element in its na->nb direction or -1 for nb->na.

    Raises MeshError when the element graph is disconnected or has no
    independent loops.
    """
    elements = topo.get("elements", [])
    if not elements:
        raise MeshError("topology has no elements")

    nodes = _active_nodes(elements)
    if not nodes:
        raise MeshError("topology has no incident nodes")

    root = 0 if 0 in nodes else min(nodes)
    adjacency = {node: [] for node in nodes}
    for idx, elem in enumerate(elements):
        na, nb = elem["na"], elem["nb"]
        if na == nb:
            raise MeshError("element %d is a self-loop" % idx)
        adjacency.setdefault(na, []).append((idx, nb))
        adjacency.setdefault(nb, []).append((idx, na))

    for edges in adjacency.values():
        edges.sort(key=lambda item: item[0])

    parent = {root: None}
    parent_edge = {root: None}
    tree_edges = set()
    queue = deque([root])

    while queue:
        node = queue.popleft()
        for edge_idx, other in adjacency[node]:
            if other in parent:
                continue
            parent[other] = node
            parent_edge[other] = edge_idx
            tree_edges.add(edge_idx)
            queue.append(other)

    if set(parent) != nodes:
        missing = sorted(nodes - set(parent))
        raise MeshError("element graph is disconnected; unreachable nodes %r" % missing)

    loop_count = len(elements) - len(nodes) + 1
    if loop_count <= 0:
        raise MeshError("element graph has no independent loops")

    chord_edges = [idx for idx in range(len(elements)) if idx not in tree_edges]
    if len(chord_edges) != loop_count:
        raise AssertionError("cycle rank mismatch: chords=%d rank=%d" %
                             (len(chord_edges), loop_count))

    meshes = []
    for chord_idx in chord_edges:
        chord = elements[chord_idx]
        # Define each fundamental loop as: chord na->nb, then the tree path
        # from chord nb back to chord na. This makes the returned sequence a
        # directed closed walk and keeps the chord as the first item.
        loop = [(chord_idx, 1)]
        loop.extend(_tree_path(chord["nb"], chord["na"], parent,
                               parent_edge, elements))
        _assert_closed_walk(loop, elements)
        meshes.append((min(_loop_nodes(loop, elements)), chord_idx, loop))

    meshes.sort(key=lambda item: (item[0], item[1]))
    result = [loop for _min_node, _chord_idx, loop in meshes]

    if len(result) != loop_count:
        raise AssertionError("mesh count mismatch: got=%d rank=%d" %
                             (len(result), loop_count))
    return result
