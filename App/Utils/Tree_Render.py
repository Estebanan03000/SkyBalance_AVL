"""Render AVL and BST structures as images for the frontend."""

import matplotlib.pyplot as plt
import networkx as nx
import base64
from io import BytesIO


class TreeRenderer:
    """
    Utility class to render a tree (AVL or BST) as an image.

    Nodes are colored based on their state:
    - Red: Critical nodes (depth penalty applied)
    - Blue: Normal nodes

    Returns a base64 encoded image for frontend usage.
    """

    def __init__(self, tree):
        """
        Initialize renderer with a tree instance.

        Parameters
        ----------
        tree : AVL or BST
            The tree structure to render
        """
        self._tree = tree

    def render(self):
        """
        Render the tree as an image and return it as base64.

        Returns
        -------
        str
            Base64 encoded PNG image
        """
        G = nx.DiGraph()
        root = self._tree._root

        if root is None:
            return None

        # ---------------------------
        # Build graph recursively
        # ---------------------------
        def add_edges(node):
            if node is None:
                return

            node_id = node.getValue()
            G.add_node(node_id)

            if node.getLeftChild():
                left_id = node.getLeftChild().getValue()
                G.add_edge(node_id, left_id)
                add_edges(node.getLeftChild())

            if node.getRightChild():
                right_id = node.getRightChild().getValue()
                G.add_edge(node_id, right_id)
                add_edges(node.getRightChild())

        add_edges(root)

        # ---------------------------
        # Layout (tree-like)
        # ---------------------------
        pos = self._hierarchy_pos(G, root.getValue())

        # ---------------------------
        # Node coloring
        # ---------------------------
        colors = []
        for node_id in G.nodes():
            flight = self._tree.search(node_id)

            # If node has depth penalty → red
            if hasattr(flight, "getIsCritical") and flight.getIsCritical():
                colors.append("red")
            else:
                colors.append("skyblue")

        # ---------------------------
        # Draw graph
        # ---------------------------
        plt.figure(figsize=(10, 6))
        nx.draw(
            G,
            pos,
            with_labels=True,
            node_color=colors,
            node_size=1000,
            font_size=10
        )

        # ---------------------------
        # Convert to base64
        # ---------------------------
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)

        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')

        buffer.close()
        plt.close()

        return image_base64

    def _hierarchy_pos(self, G, root, width=1., vert_gap=0.2, vert_loc=0):
        """
        Create a hierarchical layout for the tree.

        Parameters
        ----------
        G : networkx graph
        root : root node id

        Returns
        -------
        dict
            Node positions
        """
        pos = {}

        def _hierarchy(node, left, right, vert_loc):
            pos[node] = ((left + right) / 2, vert_loc)
            neighbors = list(G.successors(node))

            if neighbors:
                dx = (right - left) / len(neighbors)
                nextx = left

                for neighbor in neighbors:
                    _hierarchy(neighbor, nextx, nextx + dx, vert_loc - vert_gap)
                    nextx += dx

        _hierarchy(root, 0, width, vert_loc)
        return pos