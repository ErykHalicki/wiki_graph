from node import node
from collections import deque
import time
import concurrent.futures
import heapq
import json
import sys

prefix = 'https://en.wikipedia.org/wiki/'

class graph:
    def __init__(self, start_link="",max_workers=100):
        self.root = node(start_link)
        self.max_workers=max_workers
        self.max_iteration=1000000
        self.node_list = []
        self.last_write_index = 0

    def get_neighbor_batch(self, nodes):
        unvisited = deque(nodes)
        searched=0
        visited = set()
        while(len(unvisited) > 0):
            def pop_and_fetch_neighbors():
                current_page = unvisited.popleft()
                if (current_page.link in visited):
                    return
                visited.add(current_page.link)# marks current page as visited so it isnt reexplored
                current_page.get_all_neighbors()# getting all neighbors to the current page
                #print(f"{current_page.link} has {len(current_page.neighbors)} neighbors")

            pool = concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers)
            for i in range(min(len(unvisited), self.max_workers)):
                pool.submit(pop_and_fetch_neighbors)
                searched+=1
            pool.shutdown(wait=True)
            print(f"got {round(searched/len(nodes)*100)}% of all nodes")

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

    def best_first(self, start_link, target_link):#node link is the target link
        target = node(target_link)
        target.get_all_neighbors()

        start = node(start_link)

        visited = set()#used to keep track of links already visited

        current = start
        found = False
        path = []
        print(f"Searching for a path between: {start_link} and {target_link}")
        while not found:
            path.append(current.link)
            if(current.link.lower() == target_link.lower()):
                found = True
                break
            current.get_all_neighbors()
            self.get_neighbor_batch(current.neighbors)
            best_neighbor = current.neighbors[0]
            for neighbor in current.neighbors:
                if(neighbor.link not in visited):
                    neighbor.get_similarity_to(target)
                    if(neighbor.similarity < best_neighbor.similarity):
                        best_neighbor = neighbor
                        print(f"new best: {current.link} -> {neighbor.link}. Distance: {round(neighbor.similarity,2)}\n")
            current = best_neighbor
            visited.add(current.link)
            print(f"clicking {best_neighbor.link}")

        print("Path was:")
        for n in path[:-1]:
            print(n)
            print("  |\n  V")
        print(path[-1])
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

def main():
    g = graph()
    g.best_first(sys.argv[1], sys.argv[2])
    '''
    g.reconstruct("Life.json")
    g.bfs(8)
    g.save(f"{g.root.link}.json")
    path = g.search(sys.argv[2])
    print(path)

    start = node(sys.argv[1])
    target = node(sys.argv[2])

    start.get_all_neighbors()
    target.get_all_neighbors()
    print(f"distance between {sys.argv[1]} and {sys.argv[2]} is {start.get_similarity_to(target)}")
    '''


if __name__ == "__main__":
    if(len(sys.argv) != 3):
        print("please enter 2 Wikipedia topics")
    else:
        main()


