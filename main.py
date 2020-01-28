#########################
# Blake Thompson        #
# Student ID: 000898127 #
#########################

from algorithms import *
from data import *

# hard coding these strings is bad practice and should probably have a config file
hub_address = '4001 South 700 East'
package_list = import_package_data('WGUPS Package File.csv')  # import packages to hash table
# import address data, map {Name: Address}, used to refer to street address by location name
address_list = import_address_data('Addresses.csv')

routes_graph = Graph()  # create routes graph object

# the add_vertex method has another loop that checks the edge weight of each other vertex, causing each loop to loop
# again for a runtime of O(V^2) where V is the number of vertices
for address in address_list.table:  # create vertices for each address
    vertex = Vertex(address[1])
    routes_graph.add_vertex(vertex)

import_route_data('WGUPS Distance Table.csv', routes_graph)  # import routes data and create weighted edges

# create 3 truck objects to load packages into, set current address to hub, load all three trucks
truck1 = Truck()
truck1.current_vertex = routes_graph.vertices[hub_address]
truck2 = Truck()
truck2.current_vertex = routes_graph.vertices[hub_address]
truck3 = Truck()
truck3.current_vertex = routes_graph.vertices[hub_address]

load_trucks(package_list, truck1, truck2, truck3)

# we only have 2 drivers, so send the first 2 trucks
truck1.deliver_packages(routes_graph)
truck2.deliver_packages(routes_graph)

# truck 3 will have a start time of the first truck to returns arrival time, allowing the driver to take this truck
truck3.leave_time = get_delivery_time(truck1)  # for better scalability this should test which truck returns first

# this change's the wrong address package's address at roughly 9:50 rather than 10:20. It still delivers after 10:20.
# it's not a great solution, but it does work.
# Any other solution would require an entire re-write of how the program handles time
package_list.search(9).address = '410 S State St'

urgent_packages = []  # in order to make delivery times, mark late packages with deadline urgent for priority delivery
# single for loop operates in O(n) where n is number of packages on the truck, with a max of 16 loops
for package in reversed(truck3.packages):
    if not package.deadline == 'EOD':
        urgent_packages.append(package)
        truck3.packages.remove(package)

# do a swap on truck3.packages and urgent_packages to run delivery algorithm on urgent,
# then swap back for final deliveries
swap_list = truck3.packages
truck3.packages = urgent_packages
truck3.deliver_packages(routes_graph)
truck3.packages = swap_list
truck3.deliver_packages(routes_graph)

# Begin interface runtime
run_program = True
print('#########################')
print('# WGUPS Delivery System #')
print('#########################')

# verify all delivery times for user
print('\nAll packages delivered!')
print('\nID | Deadline | Delivery Time')
print('-----------------------------')
for i in range(1, len(package_list.table) + 1):
    package = package_list.search(i)
    print(package.id, '|', package.deadline, '|', package.delivery_time)

# verify driving distances for user
print('\nTotal Distances')
print('---------------')
print('Truck 1:', round(truck1.miles_driven, 1), 'miles')
print('Truck 2:', round(truck2.miles_driven, 1), 'miles')
print('Truck 3:', round(truck3.miles_driven, 1), 'miles')
print('\nTotal', truck1.miles_driven + truck2.miles_driven + truck3.miles_driven, 'miles')

print('\n*********************************')
while run_program:
    print('\nMENU OPTIONS:\n\n1) Find Package Status\n2) Get All Package Status\n3) Print Driving Distances\n'
          '4) Find Routes\n5) Quit\n')
    print('Enter selection number:', end=' ')
    selection = input()

    if selection == '1':
        print('Enter package ID:', end=' ')
        package_id = input()
        print('Enter current time(HH:mm):', end=' ')
        try:
            time = datetime.datetime.strptime(input(), "%H:%M")
        except:
            print('Invalid time format. Use HH:mm, 24 hour clock')
            continue
        package = package_list.search(int(package_id))
        if package is None:
            print('No package found')
            continue
        else:
            print('\nID, Address, City, Zip Code, Weight, Deadline, Status')
            print(get_package_data(package) + get_package_status(package, time.time()))
    elif selection == '2':
        print('Enter current time(HH:mm):', end=' ')
        try:
            time = datetime.datetime.strptime(input(), "%H:%M")
        except:
            print('\nInvalid time format. Use HH:mm, 24 hour clock')
            continue
        print('\nID, Address, City, Zip Code, Weight, Deadline, Status')
        for i in range(1, len(package_list.table) + 1):
            package = package_list.search(i)
            print(get_package_data(package) + get_package_status(package, time.time()))
        continue
    elif selection == '3':
        print()
        print('Truck 1:', round(truck1.miles_driven, 1), 'miles')
        print('Truck 2:', round(truck2.miles_driven, 1), 'miles')
        print('Truck 3:', round(truck3.miles_driven, 1), 'miles')
        print('\nTotal', truck1.miles_driven + truck2.miles_driven + truck3.miles_driven, 'miles')
    elif selection == '4':
        print('This function will list the most efficient route to every other known address based on input address.')
        print('Enter starting address:', end=' ')
        address = input()
        try:
            vertex_a = routes_graph.vertices[address]
        except:
            print('Invalid Address')
            continue
        dijkstras_algorithm(routes_graph, vertex_a)
        print()
        for v in sorted(routes_graph.vertices.values(), key=operator.attrgetter("name")):
            if v.previous_vertex is None and v is not vertex_a:
                print(vertex_a.name, "to %s: no path exists" % v.name)
            else:
                print(vertex_a.name,
                      "to %s: %s (total distance: %g miles)" % (v.name, get_shortest_path(vertex_a, v), v.distance))
    elif selection == '5':
        run_program = False
    else:
        continue
