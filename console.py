import sys
import re


def start_console() -> None:
    print("Team Lord of the Pings | Network Layer Routing")
    shutdown_reason = "Unknown reason"

    while True:
        try:
            command = input("> ")
            exit_loop = parse_command(command)
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


def parse_command(command: str) -> bool:
    """Parses the passed command and runs the relavent code.
    See README for command usage.

    Args:
        command (str): The command to parse.

    Returns:
        bool: Whether the console should break. Primarily for fatal errors or quitting the terminal.
    """
    first_node, second_node, cost = parse_edge(command)
    if first_node is not None:
        # Has an edge. Handle it.
        # TODO: Add or remove edge
        print("Adding/removing edges is not yet implemented")
        return False

    # first_node, second_node, and cost will all be None
    # Do this for type checker to know this for a fact
    # Not necessary at all but I'm the one writing this code >:D
    assert first_node is None
    assert second_node is None
    assert cost is None

    # Main switch statement
    if command.lower().startswith("exit"):
        return True
    elif command.lower().startswith("ls"):
        print("ls is not yet implemented.")
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

    return True


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
    assert sys.version_info[0] == 3  # Ensure python 3
    assert sys.version_info[1] >= 11  # Ensure version >= 3.11

    # TODO: Parse passed arguments as input (?)
    # Need to decide if we are going to accept that or not
    start_console()
