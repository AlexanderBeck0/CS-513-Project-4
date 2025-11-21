# Introduction

This handout provides more details on the report to go with the final course project you are
currently working on. As indicated in the project handout: 

“The final report should be a well-presented technical report discussing your project (in pdf format). If your project is primarily a programming effort, you should explain how the program works, give specific sample runs and analyze the results. The report should be 5-10 pages in length, although may be less if you do the standard project. If your project team is more than one person then the report should indicate what each person did on the project.”

Again, the final project and report are due Friday, December 12, 2025.

# Report Details

In addition to the overview provided above, your report needs to address each of the following questions. You are encouraged to explicitly use this format in organizing your report.

## What is your name(s)?

Team Lord of the Pings consists of: Alexander Beck, Jack Rothenberg

## Individual Contributions

- Alexander Beck
  - Console
  - Centrality & Stats
  - Tree plotting
  - Graph creation from file/console

- Jack Rothenberg
  - Link-state routing
  - Dijsktra
  - Graph manager
  - Network plotting

- Shared
  - Distributed link-state routing
  - Distance-vector routing
  - Report
  - Experiments
  - Analysis

## What project did you select?

We selected the standard network layer routing project.

## Describe the work did you do on the project including any deviations from the description if you chose standard project.

For this project we created a kernel to simulate several different routing algorithms for the analysis of sparse networks. We created and analyzed 3 different routing algorithms along with several visualization and analysis tools.

The kernel itself does not accept any command args, but is done by parsing standard input. It is made in a modular way that allows for easy creation of commands. The commands are parsed after checking for a graph addition/deletion (using the form "A B 10" or "A B -"). The command parser has commands for routing algorithms (talked about in the next paragraph), commands for visualizing the created graph, and commands for graph analysis. There are also flags you can pass to certain commands, such as "-i" to make the distance-vector algorithm run iteratively, or "-r" to reset the distance vectors.

When running the kernel using "help" or "help ls" will show information and usage about a command. To input a file of edges, run "file filename". You can exit the kernel by doing Ctrl + C or typing the "exit" command. Adding an edge is as simple as typing "A B 4", and removing it can be done through "A B -". Nodes are only single characters and costs must be positive integers.

The first algorithm is the link-state routing algorithm, which utilizes Dijkstra's algorithm on a centralized system. The link-state routing algorithm is called by using the "ls" command with the given node as the root node to calculate from (ls A). The second is the distance-vector routing algorithm, which utilizes every node keeping its own table and sharing information with its neighbors in a decentralized fashion. The distance-vector routing algorithm is called using the "dv" command with the given node as the root node to calculate from (dv A). This algorithm allows for the "-i" argument, which indicates that the algorithm should run incrementally (dv A -i). The third is a combination of the two and combines the usage of the optimal Dijkstra's algorithm on a decentralized system by having each node build and share its own graph based on the information shared by its neighbors and runs Dijkstra's on that graph. We are calling it the distributed link-state routing algorith and it is called by using the "dls" command with the given node as the root node to calculate from. Similar to the "dv" command, this can also be ran with the "-i" parameter for iterative running.

In addition to the routing algorithms, we created several tools for analysis and visualization. For visualization, we created the "plot" and "tree" commands. The "plot" command plots the graph as constructed with the given nodes and costs. The "tree" command which plots a minimum spanning tree with the inputted node as the root node for the network graph (tree A). For analysis, we created the commands "centrality" and "stats". The "centrality" command calculates the betweenness of every node in the graph and prints the nodes with their betweenness, allowing us to see which nodes are most central to the network. The "stats" command prints the node with the maximum, minimum, and average shortest path lengths found in the graph.

## What are the results you obtained? As appropriate, it is important you include sample output demonstrating functionality/results of your project

dense_graph:

  - DV in 8
  - DLS in 4

## What went well on the project?

Some aspects of the project that went particularly well were the simulated kernel, visualizations, and experiment runner. The simulated kernel was set up such that it was very easy for us to add various commands as we were experimenting making the integration simple. The visualizations show the graph with the nodes in labeled circles and the edge weights all labeled nicely. It was fairly simple to implement, but made it so much easier to visualize and debug the code regarding the graph inputs. Seeing the physical graph made it easier to double check the routing algorithms. The tree visualization is very clean since it shows the plot in a similar way to the full network graph but spread out, and it also helped validate the results from the routing algorithms. The experiment runner allowed us to easily run various tests with different graphs in different scenarios without having to manually type it all out in our console one by one, searching through all of the prints and similar.

## What did you learn?

Throughout the development of this project, and running the various experiments, we gained hands-on knowlege expanding upon what we discussed in class. While implementing the distance-vector routing algorithm, it was fascinating to see the same count to infinity problem. As mentioned before, we origionally thought it was a mistake, but after analyzing the algorithm it makes total sense that the cost to reach an isolated node continues to climb due to the back and forth (in)corrections from each nodes' neighbors. Also with the distance-vector algorithm, it was extremely interesting to see the delayed response time when a cost is increased as opposed to decreased. This follows what we discussed in class with how good news spreads fast but bad news spreads slowly.

Another thing we learned was that, despite having completely different algorithms, both the link-state and distance-vector routing algorithms converged to the same shortest paths. This behavior is actually quite simple, since both algorithms find the shortest path, the only difference being the knowledge available at the start.

Finally, we learned that distributed systems are much harder to work with than centralized ones. Neither of us had much experience with distributed systems, and working with the behavior mentioned above was hard to debug, especially when count-to-infinity exists (and we don't know that it is normal for distance-vector routing!).

## What was hard?

When writing the distance-vector routing algorithm, we had the counting-to-infinity issue. This caused us to think that our implementation was incorrect, and so we spent a lot of time debugging and came to the conclusion that we needed to start over. Instead of using dictionaries, we tried having each node store a graph of how it sees the network. It was quite an elegant solution, but we later realized that it was no longer the distance-vector routing algorithm, but rather a distributed link-state routing algorithm. We also learned that our initial implementation was correct after counting-to-infinity was discussed in class.

## What, if anything, did you do beyond the standard project description (if you based your project on it)?

We added a command parser that supports arguments and flags. It also is built using python decorators, which means that you simply put "@add_command" on top of a function definition and it will add it to the list of commands. It even automatically adds it to the "help" command with its description, usage, and any arguments.

We also added a "centrality" and "stats" command. They were added because we thought it would make for an interesting report exploring how important certain nodes were for the found shortest paths.

The Distributed Link-State routing algorithm was added after a failed attempt at the distance vector algorithm. Instead of replacing it with the correct "dv" command, we simply made a "dls" command.

## What, if anything, did you not complete that was in the basic project description or your initial design?

While we completed everything that was mentioned in the basic project description and our initial design, we did not complete the optional stretch goal of having the link-state routing algorithm run iteratively. However, we were able to accomplish this iterative style of running in both the distance-vector routing algorithm and our custom distributed link-state routing algorithm.