import os

import matplotlib.pyplot as plt
import networkx as nx


class GraphManager:
    def __init__(self):
        self.graph = nx.Graph()
        self.verbose = True
        self._verbose_state = (
            self.verbose
        )  # used to store whatever verbose is to reverse the verbose state

        self.runs = {"ls": 0, "dls": 0, "dv": 0}

        self.dvs: dict[str, dict[str, int]] = {}

        self.graphs: dict[str, nx.Graph] = {}

    def temp_mute(self) -> None:
        # Silence the verbosity, while keeping the previous mute state
        # This is so if verbose is already off, it won't enable it after unmuting
        self._verbose_state = self.verbose
        self.verbose = False

    def temp_unmute(self) -> None:
        self.verbose = self._verbose_state

    def vprint(self, *values: object) -> None:
        """Only prints when self.verbose is True"""
        if self.verbose:
            print(*values)

    def add_edge(self, node1: str, node2: str, cost: int):
        """Add or update an edge in the graph."""
        self.graph.add_edge(node1, node2, weight=cost)
        self.vprint(f"Added/Updated edge {node1}-{node2} with cost {cost}")

    def remove_edge(self, node1: str, node2: str):
        # Possible improvement would be to make this return the removed edge
        if self.graph.has_edge(node1, node2):
            self.graph.remove_edge(node1, node2)
            self.vprint(f"Removed edge {node1}-{node2}")
        else:
            self.vprint(f"Edge {node1}-{node2} not found.")

    def list_edges(self):
        """Print edges with costs."""
        if not self.graph.edges:
            print("Graph is empty.")
            return
        for u, v, w in self.graph.edges(data="weight"):
            print(f"{u} -- {v} (cost: {w})")

    def plot(self, file_name: str = ""):
        """Visualize the plot.

        Args:
            file_name (str, optional): The name of the file to save to. Will not be saved if no name is provided. Defaults to "".
        """
        pos = nx.spring_layout(self.graph)

        weights = nx.get_edge_attributes(self.graph, "weight")
        nx.draw(self.graph, pos, with_labels=True, node_color="skyblue", node_size=1000)
        nx.draw_networkx_edge_labels(self.graph, pos, edge_labels=weights, rotate=False)
        plt.title("Network Graph")
        if file_name:
            directory = os.path.dirname(file_name)

            if directory:
                os.makedirs(directory, exist_ok=True)

            if os.path.exists(file_name):
                response = input(
                    f"File with name '{file_name}' already exists. Replace? (Y/N) "
                ).lower()
                if response[0] != "y":
                    plt.show()
                    return
            plt.savefig(file_name)
        plt.show()

    def save_plot(self, file_name: str) -> None:
        directory = os.path.dirname(file_name)

        if directory:
            os.makedirs(directory, exist_ok=True)

        if os.path.exists(file_name):
            response = input(
                f"File with name '{file_name}' already exists. Replace? (Y/N) "
            ).lower()
            if response[0] != "y":
                return

        # Exact same thing as plot, but doesn't show the plot.
        # In fact, it is DUPLICATE CODE.
        pos = nx.spring_layout(self.graph)

        weights = nx.get_edge_attributes(self.graph, "weight")
        nx.draw(self.graph, pos, with_labels=True, node_color="skyblue", node_size=1000)
        nx.draw_networkx_edge_labels(self.graph, pos, edge_labels=weights, rotate=False)
        plt.title("Network Graph")
        if file_name:
            plt.savefig(file_name)

    def tree(self, root: str) -> None:
        from routing import dijkstra

        dijkstra_results = dijkstra(root, self.graph)

        # Construct graph from dijkstra_results
        dijkstra_tree = nx.Graph()
        dijkstra_tree.add_node(root)

        for distance, node, via in dijkstra_results:
            if via is None or via == "-":
                continue
            if node not in dijkstra_tree.nodes:
                dijkstra_tree.add_node(node)
            if via not in dijkstra_tree.nodes:
                dijkstra_tree.add_node(via)
            dijkstra_tree.add_edge(via, node, weight=distance)

        pos = nx.bfs_layout(dijkstra_tree, start=root)
        weights = nx.get_edge_attributes(dijkstra_tree, "weight")
        nx.draw(
            dijkstra_tree, pos, with_labels=True, node_color="skyblue", node_size=1000
        )
        nx.draw_networkx_edge_labels(
            dijkstra_tree, pos, edge_labels=weights, rotate=False
        )
        plt.title("Spanning Tree")
        plt.show()

    def save_to_file(self, filename: str) -> None:
        directory = os.path.dirname(filename)

        if directory:
            os.makedirs(directory, exist_ok=True)

        if os.path.exists(filename):
            response = input(
                f"File with name '{filename}' already exists. Replace? (Y/N) "
            ).lower()
            if response[0] != "y":
                return

        # Replace the file
        with open(filename, "w") as file:
            for u, v, data in self.graph.edges(data=True):
                file.write(f"{u} {v} {data['weight']}\n")
