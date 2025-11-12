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

### Updating a Graph Edge Cost

Typing `X Y {cost}` will update the cost of the edge between `X` and `Y`.

### Algorithm Commands

1. [ls](#ls)
1. [dv](#dv)

#### ls

Usage: `ls (node)`

Calculates and prints routing table using link-state routing algorithm.

#### dv

Usage: `dv (node)`

Calculates and prints routing table using distance-vector routing algorithm. Runs one iteration at a time, and will output when the distance vectors converge.

### Other Commands

1. [exit](#exit)
1. [help](#help)
1. [file](#file)
1. [plot](#plot)
1. [tree](#tree)
1. [stats](#stats)

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

#### tree

Usage: `tree (root node)`

Plots the Dijkstra spanning tree from the given node.

#### centrality

Usage `centrality`

Used to find the betweenness centrality of the graph.

#### stats

Usage: `stats`

Reports the maximum, minimum, and average length of shortest distance paths.
