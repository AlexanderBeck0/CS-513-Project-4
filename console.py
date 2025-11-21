import os
import re
from collections.abc import Callable
from functools import update_wrapper
from typing import Any

from graph_manager import GraphManager
from routing import (
    DistanceVectorRouting,
    DistributredLinkStateRouting,
    LinkStateRouting,
    RoutingAlgorithm,
    average_shortest_path,
)


class Command:
    def __init__(
        self,
        name: str,
        func: Callable[[Any], bool],
        usage: str = "",
        description: str = "",
        flags: dict[str, str] = {},
    ):
        self.name = name
        self.usage = usage or f"No usage provided for {name}"
        self.description = description or f"No description provided for {name}"
        self.func = func
        update_wrapper(self, func)
        self.flags = flags

        # https://stackoverflow.com/questions/582056/getting-list-of-parameter-names-inside-python-function#comment29479288_4051447
        self.needs_graph_manager = (
            "graph_manager" in func.__code__.co_varnames[: func.__code__.co_argcount]
        )

    def __call__(self, graph_manager=None, *args: Any, **kwargs: Any) -> Any:
        func_param_names = self.func.__code__.co_varnames[
            : self.func.__code__.co_argcount
        ]

        expected_kwargs = {k: v for k, v in kwargs.items() if k in func_param_names}
        if self.needs_graph_manager:
            return self.func(graph_manager, *args, **expected_kwargs)
        return self.func(*args, **expected_kwargs)


commands: dict[str, Command] = {}


def register_command(command: Command) -> None:
    """Registers a command.

    Args:
        command (Command): The command to register.
    """
    commands[command.name] = command


def add_command(
    name: str, usage: str = "", description: str = "", flags: dict[str, str] = {}
):
    def decorator(func):
        register_command(
            Command(
                name=name, func=func, usage=usage, description=description, flags=flags
            )
        )
        # TODO: If func returns None, have it return False (maybe?)
        return func

    return decorator


def start_console(graph_manager: GraphManager | None = None) -> None:
    print("Team Lord of the Pings | Network Layer Routing")
    shutdown_reason = "Unknown reason"

    if graph_manager is None:
        # Ensure there is always a graph manager
        graph_manager = GraphManager()

    while True:
        try:
            command = input("> ")
            exit_loop = parse_command(command, graph_manager)
            if exit_loop:
                shutdown_reason = "User exited"
                break
        except KeyboardInterrupt:
            # This looks much nicer than the giant trace when doing ctrl + C
            shutdown_reason = "User interrupt"
            break
        except Exception as e:
            shutdown_reason = f"Fatal error: {e}"
    on_shutdown(shutdown_reason)


def parse_command(command: str, graph_manager: GraphManager) -> bool:
    """Parses the passed command and runs the relavent code.
    See README for command usage.

    Args:
        command (str): The command to parse.

    Returns:
        bool: Whether the console should break. Primarily for fatal errors or quitting the terminal.
    """
    first_node, second_node, cost = parse_edge(command)
    if first_node is not None:
        # assertions for type checking. They will ALWAYS pass, so keeping them does no harm.
        assert first_node is not None
        assert second_node is not None
        assert cost is not None
        if isinstance(cost, str) and cost == "-":
            graph_manager.remove_edge(first_node, second_node)
            return False

        assert isinstance(cost, int)
        graph_manager.add_edge(first_node, second_node, cost)
        return False

    # BUG: A B C 1 -> Trys to run "A"
    split_command = command.strip().split()
    if not split_command:
        # Empty command
        return False

    name = split_command[0].lower()
    args = []
    flags = set()

    for part in split_command[1:]:
        if part.startswith("-"):
            for flag in part[1:]:
                flags.add(flag)
        else:
            args.append(part)

    cmd = commands.get(name)

    if cmd:
        flags_kwargs = {flag: True for flag in flags}
        command_result = cmd(graph_manager, *args, **flags_kwargs)
        return bool(command_result)  # Whether to exit the console or not
    else:
        # Unknown command
        print(f"Unknown command '{name}'. Please type 'help' to see commands.")
        return False


@add_command(
    "exit", usage="exit", description="Quits the terminal and ends the program."
)
def exit_cmd() -> bool:
    return True


@add_command(
    "help",
    usage="help [command]",
    description="Shows a help message with all of the console commands.",
)
def help_cmd(*args, **kwargs) -> bool:
    if len(args) == 0:
        print("Availible commands:")
        for item in commands.items():
            print(f"{item[0]} -- {item[1].description}")
        return False

    name = str(args[0]).strip().lower()
    command = commands.get(name)
    if command is None:
        print(f"Unknown command: {name}.")
        return False

    print(f"Help for '{name}':\n")
    print(f"Usage: {command.usage}")
    if command.flags:
        print("Options:")
        for flag, description in command.flags.items():
            print(f"\t{flag}: {description}")
    print(f"Description: {command.description}")
    return False


@add_command("plot", usage="plot", description="Plots the graph.")
def plot_cmd(graph_manager: GraphManager) -> bool:
    graph_manager.plot()
    return False


@add_command(
    "tree",
    usage="tree (root node)",
    description="Shows the dijkstra tree of the root node.",
)
def tree_cmd(graph_manager: GraphManager, root: str = "") -> bool:
    if root == "":
        print("Usage: ", commands["tree"].usage)
        return False
    graph_manager.tree(root)
    return False


@add_command(
    "ls",
    usage="ls (node)",
    description="Calculates and prints routing table using link-state routing algorithm. Output is read destination <- from (cost).",
)
def ls_cmd(graph_manager: GraphManager, node: str = "") -> bool:
    if node == "":
        print("Usage: ", commands["ls"].usage)
        return False
    link_state_routing_alg = LinkStateRouting(graph_manager)
    graph_manager.runs["ls"] += link_state_routing_alg.run(node)
    return False


@add_command(
    "dv",
    usage="dv (node) [-i] [-r]",
    description="Calculates and prints routing table using distance-vector routing algorithm. Output is read destination <- from (cost).",
    flags={"i": "Runs iteratively.", "r": "Resets the distance vectors"},
)
def dv_cmd(graph_manager: GraphManager, node: str = "", i=False, r=False) -> bool:
    if r:
        graph_manager.dvs = {}
        graph_manager.runs["dv"] = 0
        print("Reset distance vectors.")

        # Allow use of dv -r without a node
        if node == "":
            return False

    # dv (no other args)
    if node == "" and not r:
        print("Usage: ", commands["dv"].usage)
        return False

    distance_vector_routing_alg = DistanceVectorRouting(graph_manager)
    graph_manager.runs["dv"] += distance_vector_routing_alg.run(node, iterative=i)
    return False


@add_command(
    "dls",
    usage="dls (node) [-i] [-r]",
    description="Calculates and prints routing table using distributed link-state routing algorithm. Output is read destination <- from (cost).",
    flags={"i": "Runs iteratively.", "r": "Resets the distance vectors"},
)
def dls_cmd(graph_manager: GraphManager, node: str = "", i=False, r=False) -> bool:
    if r:
        graph_manager.graphs = {}
        graph_manager.runs["dls"] = 0
        print("Reset dls graphs.")

        # Allow use of dls -r without a node
        if node == "":
            return False

    # dls (no other args)
    if node == "" and not r:
        print("Usage: ", commands["dls"].usage)
        return False

    distributed_link_state_routing_alg = DistributredLinkStateRouting(graph_manager)
    graph_manager.runs["dls"] += distributed_link_state_routing_alg.run(
        node, iterative=i
    )
    return False


@add_command(
    "file",
    usage="file (file name)",
    description="Reads the file found at file name. Will print an error if the file is not found.",
)
def file_cmd(graph_manager: GraphManager, *args, **kwargs) -> bool:
    """Takes in a str file name and reads it into a graph.

    Returns:
        bool: Whether the terminal should quit.
    """
    if len(args) == 0:
        # No file name
        print("No file name provided!")
        print(f"Usage: {commands.get('file').usage}")  # type: ignore
        return False

    if len(args) > 1:
        # More than one file name
        print(f"Too many arguments for file: '{' '.join(args)}'")
        print(f"Usage: {commands.get('file').usage}")  # type: ignore
        return False

    file_path: str = args[0]
    if not os.path.exists(file_path):
        print(f"Could not find {file_path}. Please ensure you spelled it correctly.")
        return False

    # File exists. Open it.
    graph_edges: list[str] = []
    with open(file_path, "r") as file:
        lines = file.readlines()
        graph_edges = list(map(lambda x: x.strip(), lines))

    # Duplicate code. Could make it into a function, but whatever
    graph_manager.temp_mute()
    start_edge_count = graph_manager.graph.number_of_edges()
    for edge in graph_edges:
        first_node, second_node, cost = parse_edge(edge)
        if first_node is not None:
            # assertions for type checking. They will ALWAYS pass, so keeping them does no harm.
            assert first_node is not None
            assert second_node is not None
            assert cost is not None
            if isinstance(cost, str) and cost == "-":
                graph_manager.remove_edge(first_node, second_node)
                continue

            assert isinstance(cost, int)
            graph_manager.add_edge(first_node, second_node, cost)
    graph_manager.temp_unmute()
    end_edge_count = graph_manager.graph.number_of_edges()
    delta_edge_count = end_edge_count - start_edge_count
    if delta_edge_count > 0:
        print(f"Successfully added {delta_edge_count} edges to the graph!")
    elif delta_edge_count < 0:
        print(f"Succesffully removed {abs(delta_edge_count)} edges from the graph!")
    else:
        print("Number of edges in the graph remains the same!")
    return False


@add_command(
    "centrality",
    usage="centrality",
    description="Used to find the betweenness centrality of the graph.",
)
def centrality_cmd(graph_manager: GraphManager) -> bool:
    import centrality

    betweenness_centrality = centrality.brandes_centrality(graph_manager)
    for k, v in betweenness_centrality.items():
        print(f"{k}: {v:.2f}")
    return False


@add_command(
    "stats",
    usage="stats [-r]",
    description="Used to find the max, min, and average shortest path length.",
    flags={"r": "Resets the statistics saved for the different algorithms."},
)
def stats_cmd(graph_manager: GraphManager, r=False) -> bool:
    if r:
        for k in graph_manager.runs.keys():
            graph_manager.runs[k] = 0
        print("Reset all algorithm statistics.")

    # TODO: Make this take a node as input and give stats of that node
    max_node, min_node, avg_len, dijkstra_len = average_shortest_path(
        graph_manager.graph
    )
    print(
        f"Node with max shortest path length: {max_node} ({dijkstra_len[max_node]:.2f})"
    )
    print(
        f"Node with min shortest path length: {min_node} ({dijkstra_len[min_node]:.2f})"
    )
    print(f"Average shortest path length: {avg_len}")

    print("\nAlgorithm Runs:")
    for algorithm, runs in graph_manager.runs.items():
        print(algorithm.upper(), f": {runs} run{'s' if runs != 1 else ''}")
    return False


def parse_edge(command: str) -> tuple[str, str, int | str] | tuple[None, None, None]:
    """Gets the components of an edge in the form `X Y {cost}`, or None if it is not in that form.

    Args:
        command (str): The command to attempt to extract the edge from.

    Returns:
        Tuple[str, str, int | str] | Tuple[None, None, None]: The edge (X, Y, cost), (X, Y, -), or (None, None, None) if it failed to parse it.
    """
    # TODO: Is the cost allowed to be negative? If so, this needs to be rewritten slightly
    graph_input_regex = r"([A-Z]{1})\s([A-Z]{1})\s([\d]+|-)"
    is_edge_command: re.Match[str] | None = re.search(graph_input_regex, command)
    if is_edge_command is None:
        return (None, None, None)

    # Strips the parsed regex to see if there is text after the graph input
    hanging_command = command.replace(is_edge_command.group(), "")

    if hanging_command != "":
        # Case where input is not just A B 3, but something like A B 3e
        print("Error parsing graph edge.")
        print(f"Input: {command}")
        print(f"Parsed graph node: {is_edge_command.group()}")
        print(f"Command remaining after parsing: {hanging_command}")
        return (None, None, None)

    # No hanging command and regex succeeded. Return the tuple.
    edge: tuple = is_edge_command.groups()
    return (edge[0], edge[1], int(edge[2]) if edge[2] != "-" else edge[2])


def on_shutdown(reason: str = "Unknown reason") -> None:
    """(Currently) a stub for if we want a shutdown behavior (like saving the graph state)"""
    print(f"Closing console. Reasoning: {reason}")


if __name__ == "__main__":
    # Just create a wrapper of main so that I can click run in VS code without having to switch to another file
    import main

    parse_command("file figure1.in", main.manager)
    main.main()
