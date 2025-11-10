import matplotlib.pyplot as plt
import networkx as nx

class GraphManager:
    def __init__(self):
        self.graph = nx.Graph()
        self.verbose = True
        self._verbose_state = (
            self.verbose
        )  # used to store whatever verbose is to reverse the verbose state

        self.dvs: dict[str, dict[str, int]] = {}

        self.changes: dict[str, bool] = {}

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

        # Mark nodes as changed
        self.changes[node1] = True
        self.changes[node2] = True

    def remove_edge(self, node1: str, node2: str):
        # Possible improvement would be to make this return the removed edge
        if self.graph.has_edge(node1, node2):
            self.graph.remove_edge(node1, node2)
            self.vprint(f"Removed edge {node1}-{node2}")
            
            # Mark nodes as changed
            self.changes[node1] = True
            self.changes[node2] = True
        else:
            self.vprint(f"Edge {node1}-{node2} not found.")

    def list_edges(self):
        """Print edges with costs."""
        if not self.graph.edges:
            print("Graph is empty.")
            return
        for u, v, w in self.graph.edges(data="weight"):
            print(f"{u} -- {v} (cost: {w})")

    def plot(self):
        """Visualize the graph."""
        pos = nx.spring_layout(self.graph)

        weights = nx.get_edge_attributes(self.graph, "weight")
        nx.draw(self.graph, pos, with_labels=True, node_color="skyblue", node_size=1000)
        nx.draw_networkx_edge_labels(self.graph, pos, edge_labels=weights, rotate=False)
        plt.title("Network Graph")
        plt.show()

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
        nx.draw(dijkstra_tree, pos, with_labels=True, node_color="skyblue", node_size=1000)
        nx.draw_networkx_edge_labels(dijkstra_tree, pos, edge_labels=weights, rotate=False)
        plt.title("Tree")
        plt.savefig("ALEXSVIEW.png")
        plt.show()
