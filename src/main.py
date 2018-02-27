import math
import random

from src.aco import ACO, CustomersGraph

is_visited = []

def distance(customer1: dict, customer2: dict):
    return math.sqrt((customer1['x'] - customer2['x']) ** 2 + (customer1['y'] - customer2['y']) ** 2)

def find_shortest_path(customers: list , vehicle_capacity: int):
    depot = customers[0]
    route_list = []

    # Always set the depot as visited
    global is_visited
    is_visited[0] = 1
    capacity_increase = 0
    min_distance = distance(depot, customers[1])
    route_list.append(depot)
    while 1:
        for customer in customers:
            if customer.get("index") != depot.get("index") and is_visited[customer.get("index") == 0]:
                depot_to_customer = distance(depot, customer)
                if depot_to_customer <= min_distance:
                    min_distance = depot_to_customer
                    temp_visited_customer = customer
        capacity_increase = capacity_increase + temp_visited_customer.get("demand")
        if capacity_increase > vehicle_capacity:
            break
        if is_visited[temp_visited_customer.get("index")] == 1 :
            continue
        route_list.append(temp_visited_customer)
        is_visited[temp_visited_customer.get("index")] = 1
        depot = temp_visited_customer
    return route_list


def create_corresponding_graph(vehicles: list, customers: list):
    vehicles = vehicles
    customers = customers
    initial_route_list = []
    for vehicle in vehicles:
        initial_route = find_shortest_path(customers, vehicle.get("capacity"))
        for item in initial_route:
            if item.get("index") != 0:
                customers.remove(item)
        initial_route_list.append(initial_route)
        if len(customers) == 1:
            break
    return initial_route_list


def main():
    # Declare variable
    vehicles = []
    customers = []
    initial_route_list = []
    cost_matrix = []

    with open('../data/vehicle.txt') as f1:
        for line in f1.read().splitlines():
            line.rstrip('\n')
            vehicle = line.split(' ')
            vehicles.append(dict(index=int(vehicle[0]), capacity=int(vehicle[1]), velocity=float(vehicle[2]),
                                 cost=int(vehicle[3])))
    with open('../data/customer.txt') as f2:
        for line in f2.read().splitlines():
            customer = line.split(' ')
            customers.append(dict(index=int(customer[0]), x=int(customer[1]), y=int(customer[2]),
                                  demand=int(customer[3]), opentime=int(customer[4]), closetime=int(customer[5])))

    # Initial the value of visited customer. 0 stands for not visited
    global is_visited
    is_visited = [0 for i in range(len(customers))]

    # Create corresponding graph
    customers_parameter = list(customers)
    initial_route_list = create_corresponding_graph(vehicles, customers_parameter)

    # Calculate number of customer and the total cost after creating corresponding graph
    number_of_customer_in_first_route = 0
    for single_route in initial_route_list:
        for item in single_route:
            if item.get("index") != 0:
                number_of_customer_in_first_route += 1
    total_cost_in_first_route = 0
    for single_route in initial_route_list:
        for i in range(len(single_route)):
            if i < len(single_route) - 1:
                total_cost_in_first_route = total_cost_in_first_route + distance(single_route[i], single_route[i+1])

    # Store the distance between 2 customer in a n x n matrix
    total_customer = len(customers)
    for i in range(total_customer):
        row = []
        for j in range(total_customer):
            row.append(distance(customers[i], customers[j]))
        cost_matrix.append(row)

    total_vehicle = len(vehicles)
    index_list_special_vehicles = [1, 2]
    aco = ACO(1, 1, 1, total_vehicle, 100, total_customer, vehicles, customers, total_cost_in_first_route, initial_route_list,index_list_special_vehicles)
    customers_graph = CustomersGraph(cost_matrix, total_customer, number_of_customer_in_first_route, total_cost_in_first_route)
    best_route = aco.solve(customers_graph)

    for single_route in best_route:
        for item in single_route:
            print(item.get("index"))
        print("---")


main()