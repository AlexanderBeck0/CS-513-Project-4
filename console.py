import re
from typing import Any
from graph_manager import GraphManager
from collections.abc import Callable
from functools import update_wrapper


class Command:
    def __init__(
        self,
        name: str,
        func: Callable[[Any], bool],
        usage: str = "",
        description: str = "",
    ):
        self.name = name
        self.usage = usage or f"No usage provided for {name}"
        self.description = description or f"No description provided for {name}"
        self.func = func
        update_wrapper(self, func)

        # https://stackoverflow.com/questions/582056/getting-list-of-parameter-names-inside-python-function#comment29479288_4051447
        self.needs_graph_manager = (
            "graph_manager" in func.__code__.co_varnames[: func.__code__.co_argcount]
        )

    def __call__(self, graph_manager=None, *args: Any, **kwds: Any) -> Any:
        if self.needs_graph_manager:
            return self.func(graph_manager, *args, **kwds)
        return self.func(*args, **kwds)


commands: dict[str, Command] = {}


def register_command(command: Command) -> None:
    """Registers a command.

    Args:
        command (Command): The command to register.
    """
    commands[command.name] = command


def add_command(name: str, usage: str = "", description: str = ""):
    def decorator(func):
        register_command(
            Command(name=name, func=func, usage=usage, description=description)
        )
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

    split_command = command.strip().split()
    if not split_command:
        # Empty command
        return False

    name = split_command[0].lower()
    args = split_command[1:]

    cmd = commands.get(name)

    if cmd:
        command_result = cmd(graph_manager, *args)
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

    print(f"Help for {name}:\n")
    print(f"Usage: {command.usage}")
    print(f"Description: {command.description}")
    return False


@add_command("ls")
def ls_cmd(graph_manager: GraphManager) -> bool:
    graph_manager.list_edges()
    return False


@add_command("plot", usage="plot", description="Plots the graph.")
def plot_cmd(graph_manager: GraphManager) -> bool:
    graph_manager.plot()
    return False


@add_command("dv")
def dv_cmd() -> bool:
    print("dv is not yet implemented.")
    return False


@add_command(
    "file",
    usage="file (file name)",
    description="Reads the file found at file name. Will print an error if the file is not found.",
)
def file_cmd() -> bool:
    print("file is not yet implemented.")
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

    main.main()
