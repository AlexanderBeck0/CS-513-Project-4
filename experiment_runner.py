import random
import string
from tqdm import tqdm

from console import file_cmd, parse_command
from graph_manager import GraphManager
from routing import (
    DistanceVectorRouting,
    DistributredLinkStateRouting,
    LinkStateRouting,
)


def main():
    manager = GraphManager()
    file_cmd(manager, "figure1.in")

    print("Running Link-State routing from A:")
    ls = LinkStateRouting(manager)
    ls.run("A")

    print("\nRunning Distance-Vector routing from A:")
    dv = DistanceVectorRouting(manager)
    dv.run("A")

    print("\nRunning Distributed Link-State routing from A:")
    dls = DistributredLinkStateRouting(manager)
    dls.run("A")


def generate_random_graph(
    max_num_nodes: int, edge_prob: float, max_cost: int = 10, silent: bool = True
) -> GraphManager:
    manager = GraphManager()
    if silent:
        manager.temp_mute()
    # num_nodes = random.randint(3, max_num_nodes)
    num_nodes = max_num_nodes
    nodes = random.sample(string.ascii_uppercase, num_nodes)
    for i in range(num_nodes):
        for j in range(i + 1, num_nodes):
            if random.random() < edge_prob:
                cost = random.randint(1, max_cost)
                manager.add_edge(nodes[i], nodes[j], cost)
    if silent:
        manager.temp_unmute()
    return manager


def get_parse_wrapper(manager: GraphManager):
    return lambda cmd: parse_command(cmd, manager)


def parse_factory():
    manager = GraphManager()
    parse = get_parse_wrapper(manager)
    return parse, manager


def print_header(header: str, sep: str = "-", num_sep: int = 5):
    print("\n" + sep * 5 + header + sep * 5)


def changing_cost_dv():
    print_header("Chaning Cost DV", num_sep=6)
    parse, manager = parse_factory()
    file_cmd(manager, "figure1.in")
    print_header("Adding A-J (cost 9)")
    parse("dv A")

    print_header("Adding A-J (cost 9)")
    parse("A J 9")
    parse("dv A")

    print_header("Adding C J 1")
    parse("C J 1")
    parse("dv A")

    print_header("Changing C J 1 -> C J ")
    print("(Should make shortest path from A -> J be 9 instead of 4)")
    parse(
        "C J 999",
    )
    parse("dv A")


def time_to_converge():
    print_header("Time to Converge", num_sep=6)
    parse, manager = parse_factory()
    file_cmd(manager, "figure1.in")
    parse("dv A")
    parse("dls A -r")


def simple_run():
    print_header("Simple Run", num_sep=6)
    parse, _ = parse_factory()
    print_header("Adding Edges")
    parse("A D 5")
    parse("D F 2")
    parse("A B 2")
    parse("A E 6")
    parse("D E 4")
    parse("E F 1")
    parse("F G 7")
    parse("B C 1")
    parse("C E 3")
    parse("C H 1")
    parse("G H 3")
    parse("H I 2")
    parse("I J 4")
    parse("G J 5")
    parse("plot")

    print_header("Running Link-State routing from A:")
    parse("ls A")
    parse("tree A")

    print_header("Removing Edges")
    parse("A D -")
    parse("D F -")
    parse("G J -")
    parse("plot")

    print_header("Running Distance-Vector routing after removing edges:")
    parse("dv A")
    parse("tree A")


def count_to_infinity():
    parse, _ = parse_factory()
    print_header("Count-to-infinity test", num_sep=6)
    print_header("Straight line")
    parse("A B 1")
    parse("B C 1")
    parse("C D 1")

    # Run dv until completion
    parse("dv A")

    # Remove C-D
    parse("C D -")

    # Show that running dv A iteratively counts to infinity
    parse("dv A -i")
    parse("dv A -i")
    parse("dv A -i")
    parse("dv A -i")


def batch_gather_statistics(n=100, save_graphs: bool = False, save_plots: bool = False) -> None:
    """Generates `n` random graphs and gathers the statistics of them.

    Args:
        n (int, optional): Number of random graphs to generate. Defaults to 100.
        save_graphs (bool, optional): Flag for whether the graphs should be saved. Defaults to False.
        save_plots (bool, optional): Flag for whether the plots should be saved. Defaults to False.
    """
    graphs: list[GraphManager] = []
    for i in tqdm(range(0, n)):
        graphs.append(generate_random_graph(26, 0.075, 50))

        if save_graphs:
            graphs[i].save_to_file(f"out/graphs/{i}.in")
        if save_plots:
            graphs[i].save_plot(f"out/plots/{i}.png")


if __name__ == "__main__":
    # main()
    # randomgraph = generate_random_graph(26, 0.075, 50)
    # randomgraph.save_to_file("random_graph.in")
    # randomgraph.save_plot("random_graph.png")
    batch_gather_statistics(100, True, True)
    # Finished
    # count_to_infinity()
