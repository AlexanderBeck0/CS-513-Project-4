import random
import string
from tqdm import tqdm
import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
from centrality import brandes_centrality

from console import file_cmd, parse_command
from graph_manager import GraphManager
import seaborn as sns
from routing import (
    DistanceVectorRouting,
    DistributredLinkStateRouting,
    LinkStateRouting,
    average_shortest_path
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
    max_num_nodes: int, max_edge_prob: float, max_max_cost: int = 10, silent: bool = True
) -> tuple[GraphManager, float, int]:
    manager = GraphManager()
    if silent:
        manager.temp_mute()
    num_nodes = random.randint(3, max_num_nodes)
    edge_prob = random.uniform(0.01, max_edge_prob)
    max_cost = random.randint(1, max_max_cost)
    # num_nodes = max_num_nodes
    nodes = random.sample(string.ascii_uppercase, num_nodes)
    for i in range(num_nodes):
        manager.graph.add_node(nodes[i])
        for j in range(i + 1, num_nodes):
            if random.random() < edge_prob:
                cost = random.randint(1, max_cost)
                manager.add_edge(nodes[i], nodes[j], cost)
    if silent:
        manager.temp_unmute()
    return (manager, edge_prob, max_cost)


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
    edge_probs = []
    max_costs = []
    print("Generating graphs...")
    for i in tqdm(range(0, n)):
        gm, edge_prob, max_cost = generate_random_graph(26, 0.1, 50)
        graphs.append(gm)
        edge_probs.append(edge_prob)
        max_costs.append(max_cost)
        if save_graphs:
            graphs[i].save_to_file(f"out/graphs/{i}.in", overwrite=True)
        if save_plots:
            graphs[i].save_plot(f"out/plots/{i}.png", overwrite=True)

    print("Running DV on all graphs...")
    for i in tqdm(range(0, n)):
        # Silence the output of dv
        original_stdout = sys.stdout
        try:
            sys.stdout = open(os.devnull, 'w')
            parse = get_parse_wrapper(graphs[i])
            parse("dv " + random.choice(list(graphs[i].graph.nodes)))
        finally:
            sys.stdout = original_stdout

    print("Running DLS on all graphs...")
    for i in tqdm(range(0, n)):
        # Silence the output of dv
        original_stdout = sys.stdout
        try:
            sys.stdout = open(os.devnull, 'w')
            parse = get_parse_wrapper(graphs[i])
            parse("dls " + random.choice(list(graphs[i].graph.nodes)))
        finally:
            sys.stdout = original_stdout

    print("Running ls on all graphs...")
    for i in tqdm(range(0, n)):
        # Silence the output of dv
        original_stdout = sys.stdout
        try:
            sys.stdout = open(os.devnull, 'w')
            parse = get_parse_wrapper(graphs[i])
            parse("ls " + random.choice(list(graphs[i].graph.nodes)))
        finally:
            sys.stdout = original_stdout
    
    print("Getting centrality of graphs...")
    centralities = []
    for i in tqdm(range(0, n)):
        centralities.append(brandes_centrality(graphs[i]))
        
    # Get all the statistics of all the graphs
    print("Aggregating results...")
    rows = []

    for i in tqdm(range(0, n)):
        graph_manager = graphs[i]
        max_node, min_node, avg_len, dijkstra_len = average_shortest_path(
            graph_manager.graph
        )
        num_nodes = graphs[i].graph.number_of_nodes()
        centrality = centralities[i]
        max_centrality = max(centrality.values())
        mean_centrality = sum(centrality.values())/len(centrality)

        rows.append({
            "max_sp": dijkstra_len[max_node],
            "min_sp": dijkstra_len[min_node],
            "avg_sp": avg_len,
            "nodes": num_nodes,
            "edge_prob": edge_probs[i],
            "max_cost": max_costs[i],
            "max_b_cent": max_centrality,
            "mean_b_cent": mean_centrality,
            **graph_manager.runs,
        })

    df = pd.DataFrame(rows)
    print(df)
    
    # Calculate correlation matrix
    correlation_matrix = df.corr()
    print("\nCorrelation Matrix:")
    print(correlation_matrix)
    
    directory = os.path.dirname("out/_")

    if directory:
        os.makedirs(directory, exist_ok=True)

    # Corr heatmap     
    plt.figure(figsize=(8, 6))
    sns.heatmap(correlation_matrix, annot=True, cmap="coolwarm", center=0, 
                square=True, linewidths=1)
    plt.title("Correlation Matrix of Graph Statistics")
    plt.tight_layout()
    plt.savefig("out/correlation_heatmap.png", dpi=300)
    # plt.show()
    
    directory = os.path.dirname("out/pairplots/_")

    if directory:
        os.makedirs(directory, exist_ok=True)
    # Create scatter plots for top correlations
    for col1 in df.columns:
        for col2 in df.columns:
            if col1 < col2:
                plt.figure(figsize=(8, 6))
                plt.scatter(df[col1], df[col2], alpha=0.6)
                plt.xlabel(col1)
                plt.ylabel(col2)
                plt.title(f'{col1} vs {col2}')
                plt.tight_layout()
                plt.savefig(f'out/pairplots/scatter_{col1}_vs_{col2}.png', dpi=300)
                plt.close()
            
if __name__ == "__main__":
    # main()
    # randomgraph = generate_random_graph(26, 0.075, 50)
    # randomgraph.save_to_file("random_graph.in")
    # randomgraph.save_plot("random_graph.png")
    batch_gather_statistics(10000, False, False)
    # Finished
    # count_to_infinity()
