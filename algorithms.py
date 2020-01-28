import datetime
import operator
from data import HashTable, Package
import csv


# 2 separate for loops for O(n + n) = O(n)
def import_package_data(file_path):
    package_file = open(file_path, 'r')
    package_file.seek(0)
    # get number of packages for the day from the file to create that many indexes in our list
    num_packages = -1  # start at -1 to account for top line
    for line in package_file:
        num_packages += 1

    package_list = HashTable(num_packages)  # create Hash Table
    package_file.seek(0)  # return to the top line of the file, byte 0
    reader = csv.DictReader(package_file)

    # create package objects
    for item in reader:
        id = item['PackageID']
        address = item['Address']
        city = item['City']
        state = item['State']
        zip_code = item['Zip']
        deadline = item['Deadline']
        weight = item['Weight']
        notes = item['Notes']

        package = Package(id, address, city, state, zip_code, deadline, weight, notes)
        package_list.insert(int(id), package)

    package_file.close()
    return package_list


# 2 separate for loops for O(n + n) = O(n)
def import_address_data(file_path):
    address_file = open(file_path)
    address_file.seek(0)
    num_addresses = 0
    for line in address_file:
        num_addresses += 1

    address_list = HashTable(num_addresses)
    address_file.seek(0)

    for line in address_file:
        x = line.split(',')
        address_list.insert(x[0], x[1].strip('\n'))

    address_file.close()
    return address_list


# 2 separate for loops for O(n + n) = O(n)
def import_route_data(file_path, graph):
    routes_file = open(file_path)
    reader = csv.DictReader(routes_file)

    for line in reader:
        vertex_a = line.pop('start')
        for entry in line.items():
            vertex_b = entry[0]
            if entry[1] == '':
                continue
            else:
                weight = float(entry[1])
            graph.add_edge(vertex_a, vertex_b, weight)

    routes_file.close()


# Dijkstra's algorithm implemented and adapted from:
# C950: Data Structures and Algorithms II home > 6.12: Python: Dijkstra's shortest path
# Algorithm operates in O(n) time complexity
def dijkstras_algorithm(graph, start_vertex):
    for vertex in graph.vertices.values():  # reset all distances to inf
        vertex.distance = float('inf')
        vertex.previous_vertex = None  # possibly not needed, but ensures no bugs in pred vertex

    unvisited_vertices = []
    for vertex in graph.vertices.values():  # place all vertices in the queue
        unvisited_vertices.append(vertex)

    start_vertex.distance = 0  # set start vertex distance 0 distance from itself

    while len(unvisited_vertices) > 0:  # keep looping until we have checked each vertex
        current_shortest_index = 0

        for i in range(1, len(unvisited_vertices)):  # loop through unvisited_vertices, find next closest
            if unvisited_vertices[i].distance < unvisited_vertices[current_shortest_index].distance:
                current_shortest_index = i
        current_vertex = unvisited_vertices.pop(current_shortest_index)  # move to next closest vertex

        for adj_vertex in graph.vertices.values():
            distance = graph.edges[graph.edge_indices[current_vertex.name]][graph.edge_indices[adj_vertex.name]]
            alternate_path_distance = current_vertex.distance + distance

            if alternate_path_distance < adj_vertex.distance:
                adj_vertex.distance = alternate_path_distance
                adj_vertex.previous_vertex = current_vertex


def get_shortest_path(start_vertex, end_vertex):
    # Start from end_vertex and build the path backwards.
    path = ''
    current_vertex = end_vertex
    while current_vertex is not start_vertex:
        path = ' -> ' + str(current_vertex.name) + path
        current_vertex = current_vertex.previous_vertex
    path = start_vertex.name + path
    return path


def parse_time(time):
    if time == 'EOD':
        return time
    else:
        time = datetime.datetime.strptime(time, "%I:%M %p")
        return datetime.datetime.strftime(time, "%H:%M")


def get_delivery_time(truck):
    time_on_truck = truck.miles_driven / 18
    return truck.leave_time + datetime.timedelta(hours=time_on_truck)


def get_package_status(package, time):
    if time < package.truck.leave_time.time():
        return 'AT HUB'
    elif time < package.delivery_time:
        return 'IN TRANSIT'
    else:
        return 'DELIVERED: ' + str(package.delivery_time)


def get_package_data(package):
    return package.id + ', ' + \
           package.address + ', ' + \
           package.city + ', ' + \
           package.zip_code + ', ' + \
           package.weight + ' lbs, ' + \
           package.deadline + ', '


# This entire function feels way too specific. Ideally we would have a set of standard codes for special instructions,
# as well as a database of addresses. It seems like on a small scale, human sorting is the more efficient way of
# loading packages, which I have attempted to represent with this code. In order to scale this up, I think the algorithm
# would need to be written with some more specific parameters as well as the ability to take user input.
def load_trucks(package_list, truck1, truck2, truck3):
    # create a separate list to sort packages by zip code
    packages_by_zip = []
    for i in package_list.table:
        packages_by_zip.append(i[1])
    packages_by_zip.sort(key=operator.attrgetter('zip_code'))

    # we iterate over the lists in reverse to prevent removal causing an index skip
    for i in reversed(packages_by_zip):
        # load and remove any that can only be on truck 2
        if i.notes == 'Can only be on truck 2':
            truck2.load_truck(i)
            packages_by_zip.remove(i)
        # load and remove any that have been delayed to truck 3
        elif i.notes == 'Delayed on flight---will not arrive to depot until 9:05 am':
            truck3.load_truck(i)
            packages_by_zip.remove(i)
        elif i.notes == 'Wrong address listed':
            truck3.load_truck(i)
            packages_by_zip.remove(i)
        # load and remove any early deliveries to truck 1
        elif not i.deadline == 'EOD':
            truck1.load_truck(i)
            packages_by_zip.remove(i)

    # load any other duplicate address packages onto truck 1
    # the runtime complexity here gets a little hairy. this block loops once for each package on the truck, max of 16,
    # then once more for each remaining package giving us O(n^2)
    for i in truck1.packages:
        for j in reversed(packages_by_zip):
            if j.address == i.address:
                if len(truck1.packages) < 16:
                    truck1.load_truck(j)
                    packages_by_zip.remove(j)

    truck_list = [truck2, truck3]  # we only want the early deliveries on truck1, so leave out of this list

    # put like zip codes with already loaded zip codes
    # here we need to loop through each unloaded package for each package in each truck. It could probably be written
    # better as it is currently an O(n^3) loop. By this point, most of the other packages have been loaded so runtime
    # should hopefully stay low.
    for truck in truck_list:
        for package in truck.packages:
            for unloaded_package in reversed(packages_by_zip):
                if unloaded_package.zip_code == package.zip_code:
                    truck.load_truck(unloaded_package)
                    packages_by_zip.remove(unloaded_package)

    # load the remaining packages on truck3 so driver of truck 2 can get back and take out truck3 early deliveries
    for i in reversed(packages_by_zip):
        if len(truck3.packages) < 16:
            truck3.load_truck(i)
            packages_by_zip.remove(i)

    # check for any stray packages
    if packages_by_zip:
        for i in reversed(packages_by_zip):
            truck2.load_truck(i)
            packages_by_zip.remove(i)