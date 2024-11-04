from node import node
from collections import deque
import time
import concurrent.futures
import heapq
import json
import sys

prefix = 'https://en.wikipedia.org/wiki/'

class graph:
    def __init__(self, start_link="",max_workers=10):
        self.root = node(start_link)
        self.max_workers=max_workers
        self.max_iteration=1000000
        self.node_list = []
        self.last_write_index = 0

    def bfs(self, node, max_depth):
        visited = set()
        unvisited_set = set()
        unvisited = deque()
        unvisited.append(node)
        iteration = 0
        while (unvisited[0].depth <= max_depth
               and iteration < self.max_iteration):
            # removes the next page to be explored from the unvisited queue
            def pop_and_fetch_neighbors():
                current_page = unvisited.popleft()
                if (current_page.link in visited):
                    return
                visited.add(current_page.link)# marks current page as visited so it isnt reexplored
                self.node_list.append(current_page)
                current_page.get_all_neighbors()# getting all neighbors to the current page

                unvisited_neighbors = [neighbor for neighbor in current_page.neighbors if neighbor.link not in visited and neighbor.link not in unvisited_set]
                unvisited.extend(unvisited_neighbors)
                unvisited_neighbor_links = [neighbor.link for neighbor in unvisited_neighbors]
                unvisited_set.update(unvisited_neighbor_links)
                #print(f"{current_page.link}")
                # print(f"Depth: {current_page.depth}")
                # print(f"\t{len(unvisited_neighbors)} / {len(current_page.neighbors)} or {100.0 * len(unvisited_neighbors)/len(current_page.neighbors)}%  neighbors are unvisited in current page")

            pool = concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers)
            for i in range(min(len(unvisited), self.max_workers)):
                pool.submit(pop_and_fetch_neighbors)

            pool.shutdown(wait=True)
            iteration += self.max_workers
            #print(f"\tLength of unvisited page list at iteration {iteration} is {len(unvisited)}")
        #print("Done BFS")

    def heuristic(self, node, target):
        #this function calculates the estiamted distance between 2 concepts
        #if the return value is low, the 2 links are similar, so we should continue out search in that direction

        #using inverse jaccard similarity of the neighboring node links

        

        node_links, target_links = set([neighbor.link for neighbor in node.neighbors]), set([neighbor.link for neighbor in target.neighbors])
        intersection = node_links.intersection(target_links)
        union = node_links.union(target_links)
        #since we are using inverse jaccard similarity, a high similarity results in a lower score, i.e a lower distance
        return len(union) / len(intersection) / 1000. if intersection else 1

    def a_star(self, start_link, target_link):#node link is the target link
        #same steps as dijkstra's, but add heuristic, and make it online

        target = node(target_link)
        target.get_all_neighbors()

        start = node(start_link)
        start.distance = 0

        visited = set()
        heap = list()

        heapq.heappush(heap,start)

        current = start

        while (current.link != target_link
               and heap != []
               and current.distance != 10000000):
            current = heapq.heappop(heap)
            print(f"{current.link} Distance: {current.distance}")
            if (current in visited):
                continue
            current.get_all_neighbors()
            for neighbor in current.neighbors:
                if (current.distance + 1 < neighbor.distance):
                    print(f"Evaluating {current.link} -> {neighbor.link}")
                    neighbor.get_all_neighbors()
                    neighbor.distance = current.distance + 1 + self.heuristic(neighbor, target)
                    neighbor.parent = current
                    heapq.heappush(heap, neighbor)
            visited.add(current)

        path = []
        if (current.link == target_link):
            print("found target node!")
            while (current != self.root):
                path.append(current.link)
                current = current.parent
            path.append(self.root.link)
            path.reverse()
        else:
            print("couldnt find target node!")
        return path


    def dijkstras(self, node_link):
        # create a set of unvisited nodes
        # assign every node a distance from start (inf)
        # set current node to be the one with the smallest distance (min heap / prio queue)
        # check if the node was already explored (current.link in visited), if not continue
        # update the distance of all UNVISITED neighbor nodes to be min(neighbor.distance,current.distance + 1)
        # if the new distance is smaller than the old distance, reinsert it into the heap
        # continue until the unvisited heap is empty

        visited = set()
        heap = list(self.node_list)
        self.root.distance = 0
        heapq.heapify(heap)

        current = self.root

        while (current.link != node_link
               and heap != []
               and current.distance != 1000):
            current = heapq.heappop(heap)
            #print(f"Link: {current.link} Distance: {current.distance}")
            if (current in visited):
                continue
            for neighbor in current.neighbors:
                if (current.distance + 1 < neighbor.distance):
                    neighbor.distance = current.distance + 1
                    neighbor.parent = current
                    heapq.heappush(heap, neighbor)
            visited.add(current)

        path = []
        if (current.link == node_link):
            print("found target node!")
            while (current != self.root):
                path.append(current.link)
                current = current.parent
            path.append(self.root.link)
            path.reverse()
        else:
            print("couldnt find target node!")
        return path

    def search(self, node_link):
        return self.dijkstras(node_link)
    
    def save(self, file):
        json_list = [{"link" : n.link, 
                     "neighbors" :[neighbor.link for neighbor in n.neighbors]} 
                     for n in self.node_list]
        f = open(file, "w")
        f.write(json.dumps(json_list))
        f.close()

    def reconstruct(self, file):
        f = open(file, "r")
        json_list = json.loads(f.read())

        node_map = dict()

        for n in json_list:
            node_map[n["link"]] = node(n["link"])
            for i in n["neighbors"]:
                node_map[i] = node(i)

        for n in json_list:
            self.node_list.append(node_map[n["link"]])
            for i in n["neighbors"]:
                node_map[n["link"]].neighbors.append(node_map[i])
        if self.root.link in node_map:
            self.root = node_map[self.root.link]
        else:
            print(f"Couldnt find node {self.root.link}, defaulting to {self.node_list[0].link} for root")
            self.root = self.node_list[0]


if __name__ == "__main__":
    g = graph(start_link=sys.argv[1], max_workers=50)
    #g.reconstruct("Life.json")
    #g.bfs(8)
    #g.save(f"{g.root.link}.json")
    #path = g.search(sys.argv[2])
    #print(path)

    g.a_star(sys.argv[1], sys.argv[2])

    start = node(sys.argv[1])
    target = node(sys.argv[2])

    start.get_all_neighbors()
    target.get_all_neighbors()

    print(f"distance between {sys.argv[1]} and {sys.argv[2]} is {g.heuristic(start, target)}")

