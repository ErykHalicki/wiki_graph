#code in this file was written by chatGPT 

from node import node
from collections import deque
import plotly.graph_objects as go
import networkx as nx

prefix = 'https://en.wikipedia.org/wiki/'

class Graph:
    def __init__(self, start_link):
        self.start_link = start_link
        self.root = node(start_link)
        self.G = nx.DiGraph()  # Initialize the directed graph

    def bfs(self, max_depth):
        visited = set()
        unvisited_set = set()
        unvisited = deque()
        unvisited.append(self.root)
        iteration = 0
        
        while unvisited and unvisited[0].depth < max_depth:
            current_page = unvisited.popleft()
            visited.add(current_page.link)
            current_page.get_all_neighbors()

            # Get unvisited neighbors
            unvisited_neighbors = [
                neighbor for neighbor in current_page.neighbors
                if neighbor.link not in visited and neighbor.link not in unvisited_set
            ]
            unvisited.extend(unvisited_neighbors)

            # Update the graph
            self.G.add_node(current_page.link)  # Add the current node
            for neighbor in unvisited_neighbors:
                self.G.add_edge(current_page.link, neighbor.link)  # Add directed edge

            # Prepare the visualization
            if(iteration % 50 == 0):
                self.update_visualization()

            # Output stats
            unvisited_neighbor_links = [neighbor.link for neighbor in unvisited_neighbors]
            unvisited_set.update(unvisited_neighbor_links)
            print(f"{current_page.link} Stats: ")
            print(f"Depth: {current_page.depth}")
            print(f"\t{len(unvisited_neighbors)} / {len(current_page.neighbors)} or {100.0 * len(unvisited_neighbors)/len(current_page.neighbors)}% neighbors are unvisited in current page")
            print(f"\tLength of unvisited page list at iteration {iteration} is {len(unvisited)}")
            iteration += 1
        
        # Final visualization
        self.update_visualization()
        self.fig.show()

    def update_visualization(self):
        # Calculate positions for nodes
        pos = nx.spring_layout(self.G, k=2.0)
        edge_x = []
        edge_y = []

        # Prepare edges
        for edge in self.G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])

        # Create edge trace
        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=0.5, color='#888'),
            hoverinfo='none',
            mode='lines'
        )

        # Create node trace
        node_x = []
        node_y = []
        for node in self.G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)

        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            text=list(self.G.nodes()),
            hoverinfo='text',
            marker=dict(showscale=False, size=10, color='#6175c1', line_width=2)
        )

        # Clear existing data and update traces
        self.fig = go.Figure()  # Create a new figure for each update
        self.fig.add_trace(edge_trace)
        self.fig.add_trace(node_trace)

        # Update layout if needed (e.g., titles, axes)
        self.fig.update_layout(title='Real-Time BFS Visualization', showlegend=False)

        # Save the figure as an HTML file
        self.fig.write_html("bfs_visualization.html")
        print("Graph updated and saved to bfs_visualization.html")

if __name__ == "__main__":
    g = Graph("Dog")
    g.bfs(5)

