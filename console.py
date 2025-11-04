import re
from graph_manager import GraphManager


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

    if command.lower().startswith("exit"):
        return True
    elif command.lower().startswith("help"):
        help()
        return False
    elif command.lower().startswith("ls"):
        graph_manager.list_edges()
        return False
    elif command.lower().startswith("plot"):
        graph_manager.plot()
        return False
    elif command.lower().startswith("dv"):
        print("dv is not yet implemented.")
        return False
    elif command.lower().startswith("file"):
        print("file is not yet implemented.")
        return False
    else:
        print("Unknown command. Please try again.")
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


def help() -> None:
    # TODO: Implement help message
    print("Help message not yet implemented.")
    ...


def on_shutdown(reason: str = "Unknown reason") -> None:
    """(Currently) a stub for if we want a shutdown behavior (like saving the graph state)"""
    print(f"Closing console. Reasoning: {reason}")
