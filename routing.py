import heapq

class RoutingAlgorithm:
    """Base class for routing algorithms."""
    def __init__(self, graph_manager):
        self.graph_manager = graph_manager

    def run(self, source: str):
        raise NotImplementedError("Subclasses must implement this method.")


class LinkStateRouting(RoutingAlgorithm):
    """Implements the Link-State (Dijkstra) algorithm."""

    def run(self, source: str):
        graph = self.graph_manager.graph
        if source not in graph.nodes:
            print(f"Node {source} not found in graph.")
            return

        dist = {node: float('inf') for node in graph.nodes}
        prev = {node: None for node in graph.nodes}
        dist[source] = 0

        pq = [(0, source)]
        while pq:
            current_dist, current_node = heapq.heappop(pq)
            if current_dist > dist[current_node]:
                continue
            
            for neighbor, attrs in graph.adj[current_node].items():
                weight = attrs["weight"]
                new_dist = current_dist + weight
                
                if new_dist < dist[neighbor]:
                    dist[neighbor] = new_dist
                    prev[neighbor] = current_node
                    heapq.heappush(pq, (new_dist, neighbor))
        
        results = []
        for node in graph.nodes:
            distance = dist[node]    
            if distance == float('inf'):
                continue
            if node == source:
                via = "-"
            else:
                via = prev[node] 
            results.append((distance, node, via))
        results.sort(key=lambda x: x[0]) 

        print(f"\nRouting Table for node {source} (Sorted by Cost):")
        for distance, node, via in results:
            print(f"{node} {via} {distance}")

class DistanceVectorRouting(RoutingAlgorithm):
    """Stub for Distance-Vector algorithm (to be implemented later)."""
    def run(self, source: str):
        print("Distance Vector algorithm not yet implemented.")
