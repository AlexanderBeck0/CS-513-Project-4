from graph_manager import GraphManager
from routing import LinkStateRouting, DistanceVectorRouting

def main():
    manager = GraphManager()
    edges = [
        ("A", "D", 5),
        ("D", "F", 2),
        ("A", "B", 2),
        ("A", "E", 6),
        ("D", "E", 4),
        ("E", "F", 1),
        ("F", "G", 7),
        ("B", "C", 1),
        ("C", "E", 3),
        ("C", "H", 1),
        ("G", "H", 3),
    ]
    for u, v, w in edges:
        manager.add_edge(u, v, w)

    print("Running Link-State routing from A:")
    ls = LinkStateRouting(manager)
    ls.run("A")

    print("\nRunning Distance-Vector routing from A:")
    dv = DistanceVectorRouting(manager)
    dv.run("A")


if __name__ == "__main__":
    main()
