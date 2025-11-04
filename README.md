# CS 513 Project 4

## Installation

1. (Optional) Create a virtual environment using `python -m venv .venv`
    - Activate the virual environment if you installed it.
1. `pip install -r requirements.txt`

## Basic Usage

Start the program with `python main.py`.

### Adding a Graph Node

Simply type `X Y {cost}`. A node is represented as a single capital letter, and the given cost is an integer. Specifying `Y X {cost}` is equivalent.

### Removing a Graph Node

Typing `X Y -` will remove the edge between `X` and `Y`. It will keep `X` and `Y`. If no such edge exists, it will ignore the command.

### Algorithm Commands

1. [ls](#ls)
1. [dv](#dv)

#### ls

TODO: Write documentation on usage of `ls`.

#### dv

TODO: Write documentation on usage of `dv`.

### Other Commands

1. [exit](#exit)
1. [help](#help)
1. [file](#file)
1. [plot](#plot)

#### exit

Usage: `exit`

Quits the terminal and ends the program.

#### help

Usage: `help [command]`

Shows a help message with all of the console commands.

#### file

Usage: `file (file name)`

Reads the file found at file name. Will print an error if the file is not found.

#### plot

Usage: `plot`

Plots the graph.
