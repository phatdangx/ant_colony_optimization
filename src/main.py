import math
import random
import re
import time

from src.aco import ACO, CustomersGraph

is_visited = []


def distance(customer1: dict, customer2: dict):

    if customer1["index"] == customer2["index"]:
        return 0
    else:
        lat1 = customer1['x']
        lat2 = customer2['x']
        long1 = customer1['y']
        long2 = customer2['y']
        try:
            cost1 = math.cos(math.radians(90-lat1))
            cost2 = math.cos(math.radians(90-lat2))
            sin1 =  math.sin(math.radians(90-lat1))
            sin2 =  math.sin(math.radians(90-lat2))
            cos_delta = math.cos(math.radians(long1-long2))
            temp = cost1 * cost2 + sin1 * sin2 * cos_delta
            if temp > 1:
                temp = 1
            result = math.acos(temp)*6371
            return result
        except Exception as e:
            print(e)


def find_shortest_path(customers: list, vehicle_capacity: int):
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
    route_list.append(customers[0])
    return route_list


def create_corresponding_graph(vehicles: list, customers: list):
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
    cost_matrix = []

    with open('../data/vehicle.txt') as f1:
        for line in f1.read().splitlines():
            line.rstrip('\n')
            line.rstrip('\t')
            vehicle = re.split(r'\t+', line)
            vehicles.append(dict(index=int(vehicle[0]), capacity=int(vehicle[1]), velocity=float(vehicle[2]),
                                 cost=float(vehicle[3])))
    with open('../data/customer.txt') as f2:
        for line in f2.read().splitlines():
            customer = re.split(r'\t+', line)
            customers.append(dict(index=int(customer[0]), x=float(customer[1]), y=float(customer[2]),
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
    vehicle_count = 0
    for single_route in initial_route_list:
        for i in range(len(single_route)):
            if i < len(single_route) - 1:
                total_cost_in_first_route = total_cost_in_first_route + distance(single_route[i], single_route[i+1]) * vehicles[vehicle_count].get("cost")
        vehicle_count += 1

    # Store the distance between 2 customer in a n x n matrix
    total_customer = len(customers)
    for i in range(total_customer):
        row = []
        for j in range(total_customer):
            row.append(distance(customers[i], customers[j]))
        cost_matrix.append(row)
    for i in range(total_customer):
        for j in range(total_customer):
            if cost_matrix[i][j] == 0 and i != j:
                print(i)
                print(j)
                print("--")
    total_vehicle = len(vehicles)
    index_list_special_vehicles = [6,7,8]
    aco = ACO(1, 1, 1, total_vehicle, 500, total_customer, vehicles, customers, total_cost_in_first_route, initial_route_list,index_list_special_vehicles)
    customers_graph = CustomersGraph(cost_matrix, total_customer, number_of_customer_in_first_route, total_cost_in_first_route)
    best_route = aco.solve(customers_graph)

    print("\n*********** FIRST ROUTE ***********\n")
    for single_route in initial_route_list:
        for item in single_route:
            print(item.get("index"), end=" ", flush=True)
        print("\n")

    print("\n*********** SOLUTION ***********\n")
    for single_route in best_route:
        for item in single_route:
            print(item.get("index"), end=" ", flush=True)
        print("\n")

    total_cost_in_final_route = 0
    vehicle_count = 0
    for single_route in best_route:
        for i in range(len(single_route)):
            if i < len(single_route) - 1:
                total_cost_in_final_route = total_cost_in_final_route + distance(single_route[i], single_route[i+1]) * vehicles[vehicle_count].get("cost")
        vehicle_count += 1
    print("TOTAL COST IN THE FINAL ROUTE: ", total_cost_in_final_route)
    print("\n")
    number_of_customer_in_best_route = 0
    for single_route in best_route:
        for item in single_route:
            if item.get("index") != 0:
                number_of_customer_in_best_route += 1
    print("TOTAL CUSTOMER IN THE FINAL ROUTE: ", number_of_customer_in_best_route)
    print("\n")

start_time = time.time()
main()
print("RUNNING TIME: ", (time.time() - start_time))