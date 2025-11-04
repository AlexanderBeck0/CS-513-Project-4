import networkx as nx
import matplotlib.pyplot as plt


class GraphManager:
    def __init__(self):
        self.graph = nx.Graph()

    def add_edge(self, node1: str, node2: str, cost: int):
        """Add or update an edge in the graph."""
        self.graph.add_edge(node1, node2, weight=cost)
        print(f"Added/Updated edge {node1}-{node2} with cost {cost}")

    def remove_edge(self, node1: str, node2: str):
        # Possible improvement would be to make this return the removed edge
        if self.graph.has_edge(node1, node2):
            self.graph.remove_edge(node1, node2)
            print(f"Removed edge {node1}-{node2}")
        else:
            print(f"Edge {node1}-{node2} not found.")

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
