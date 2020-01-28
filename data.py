from enum import Enum
import datetime
import algorithms


class Package:
    def __init__(self, id, address, city, state, zip_code, deadline, weight, notes):
        self.id = id
        self.address = address
        self.city = city
        self.state = state
        self.zip_code = zip_code
        self.deadline = deadline
        self.weight = weight
        self.notes = notes
        self.status = Status.AT_HUB
        self.delivery_time = None
        self.truck = None


class Status(Enum):
    AT_HUB = 1
    IN_TRANSIT = 2
    DELIVERED = 3


class Truck:
    def __init__(self):
        self.driver = None
        self.packages = []
        self.package_count = 0  # variable to track when the truck is empty and can return
        self.miles_driven = 0
        self.current_vertex = None
        self.leave_time = datetime.datetime(100, 1, 1, 8, 0, 0)
        self.status = Status.AT_HUB

    def load_truck(self, package):
        if len(self.packages) < 16:
            self.packages.append(package)
            self.package_count += 1
            package.truck = self

    # calling dijkstra's algorithm includes 3 separate for loops for O(n + n + n), or O(n). Adding the next 2 loops in
    # this method give us O(n + n +n) again for O(n)
    def deliver_packages(self, routes_graph):
        self.status = Status.IN_TRANSIT
        while self.packages:
            next_delivery_distance = float('inf')
            next_delivery_vertex = None
            algorithms.dijkstras_algorithm(routes_graph, self.current_vertex) # find the shortest distance to each vertex
            for package in self.packages: # loop through package list, find next closest delivery
                next_vertex = routes_graph.vertices[package.address]
                if next_vertex.distance < next_delivery_distance:
                    next_delivery_vertex = next_vertex
                    next_delivery_distance = next_vertex.distance
            self.miles_driven += next_delivery_vertex.distance  # add next vertex distance to total miles driven
            self.current_vertex = next_delivery_vertex
            for package in reversed(self.packages):  # deliver all packages in truck bound for current address
                if package.address == self.current_vertex.name:
                    package.status = Status.DELIVERED
                    package.delivery_time = algorithms.get_delivery_time(self).time()
                    self.packages.remove(package)
                    self.package_count -= 1
            if self.package_count == 0:  # if empty return to the hub
                next_delivery_vertex = routes_graph.vertices['4001 South 700 East']  # this should be populated from a config file
                self.miles_driven += next_delivery_vertex.distance


class EmptyBucket:  # empty bucket class for use in hash table with no values or methods
    pass


# linear search hash table implemented and adapted from:
# Zybooks C950: Data Structures and Algorithms II > 7.8: Python: Hash tables
class HashTable:
    def __init__(self, initial_capacity):
        self.EMPTY_SINCE_START = EmptyBucket()
        self.EMPTY_AFTER_REMOVAL = EmptyBucket()

        self.table = [self.EMPTY_SINCE_START] * initial_capacity

    def hash_function(self, key):
        hashed_key = 0
        if type(key) == int:  # if our key is already an int, use it for the hash
            hashed_key = key
        else:  # else add the ascii values of each character together for the hash
            for char in key:  # this loop adds some runtime as O(n) where n is the number of characters
                hashed_key += ord(char)
        return hashed_key % len(self.table)

    # this exercise had unique keys for the requirements, so collision handling wasn't completely necessary,
    # however adding collision handling allows for better future scaling and maintainability
    # runtime on insert and search are O(1)
    def insert(self, key, value):
        bucket = self.hash_function(key)
        buckets_probed = 0
        while buckets_probed < len(self.table):
            if type(self.table[bucket]) is EmptyBucket:
                self.table[bucket] = (key, value)
                return True

            bucket = (bucket + 1) % len(self.table)
            buckets_probed = buckets_probed + 1

        return False

    def search(self, key):
        bucket = self.hash_function(key)
        buckets_probed = 0
        while self.table[bucket] is not self.EMPTY_SINCE_START and buckets_probed < len(self.table):
            if self.table[bucket][0] == key:
                return self.table[bucket][1]

            bucket = (bucket + 1) % len(self.table)
            buckets_probed = buckets_probed + 1

        return None


# Graph and Vertex classes are used for our routes table. Implemented and adapted from:
# Zybooks C950: Data Structures and Algorithms II home > 6.12: Python: Dijkstra's shortest path
class Vertex:
    def __init__(self, name):
        self.name = name
        self.distance = float('inf')
        self.previous_vertex = None


# adding a vertex takes place in O(n) where n is the number of vertices
# adding an edge is O(1)
class Graph:
    vertices = {}
    edges = []
    edge_indices = {}

    def add_vertex(self, vertex):
        if isinstance(vertex, Vertex) and vertex.name not in self.vertices:
            self.vertices[vertex.name] = vertex  # adds vertex to vertices dict using {vertex name: object}
            for row in self.edges:
                row.append(0)
            self.edges.append([0] * (len(self.edges) + 1))
            self.edge_indices[vertex.name] = len(self.edge_indices)
            return True
        else:
            return False

    def add_edge(self, vertex_a, vertex_b, weight):
        if vertex_a in self.vertices and vertex_b in self.vertices:
            self.edges[self.edge_indices[vertex_a]][self.edge_indices[vertex_b]] = weight
            self.edges[self.edge_indices[vertex_b]][self.edge_indices[vertex_a]] = weight
            return True
        else:
            return False
