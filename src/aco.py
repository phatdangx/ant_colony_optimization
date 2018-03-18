import random

class CustomersGraph(object):
    def __init__(self, cost_matrix: list, total_customer: int, number_of_customer_in_first_route: int,
                 total_cost_in_first_route: int):
        self.cost_matrix = cost_matrix
        self.total_customer = total_customer
        self.global_pheromone = [[1 / (number_of_customer_in_first_route * total_cost_in_first_route) for j in range(total_customer)]
                          for i in range(total_customer)]
        self.number_of_customer_in_first_route = number_of_customer_in_first_route


class ACO(object):
    def __init__(self, alpha: int, beta: int, gama: int, M: int, E: int , ITE: int, vehicles: list, customers: list,
                 total_cost_in_first_route: float, initial_route_list: list, index_list_special_vehicles: list):
        self.alpha = alpha
        self.beta = beta
        self.gama = gama
        self.M = M
        self.E = E
        self.ITE = ITE
        self.vehicles = list(vehicles)
        self.customers = list(customers)
        self.total_cost_in_first_route = total_cost_in_first_route
        self.initial_route_list = list(initial_route_list)
        self.index_list_special_vehicles = list(index_list_special_vehicles)

    def update_global_pheromone(self, customer_graph: CustomersGraph, best_cost: float, local_pherommone_of_ant: list):
        for i, row in enumerate(customer_graph.global_pheromone):
            for j, col in enumerate(row):
                customer_graph.global_pheromone[i][j] = local_pherommone_of_ant[i][j] + self.gama / best_cost
    def update_global_pheromone_by_maximum_customer_route(self, customer_graph: CustomersGraph,maximum_customer: int, maximum_customer_route: list):
        for single_route in maximum_customer_route:
            for i in range(len(single_route) - 1):
                from_node_index = single_route[i].get("index")
                to_node_index = single_route[i + 1].get("index")
                customer_graph.global_pheromone[from_node_index][to_node_index] = customer_graph.global_pheromone[from_node_index][to_node_index] + self.gama/maximum_customer

    def should_continue_check (self, current_maximum_customer, last_maximum_customer, current_count):
        should_continue = True
        percentage = round(current_maximum_customer / last_maximum_customer, 2)
        if percentage <= 1.05:
            current_count += 1

        if current_count == 5:
            should_continue = False

        if percentage > 1.05:
            current_count = 0
            last_maximum_customer = current_maximum_customer

        return should_continue, current_count, last_maximum_customer

    def solve(self, customers_graph: CustomersGraph):
        best_cost = self.total_cost_in_first_route
        best_route = []
        best_route_with_maximum_customer = list(self.initial_route_list)
        maximum_customer = customers_graph.number_of_customer_in_first_route
        is_updated = False
        last_maximum_customer = 0
        current_count = 0
        current_iteration = 0
        for e in range(self.E):
            ants = [Ant(self, customers_graph, i) for i in range(1, self.ITE)]
            ant_of_best_route = ants[0]
            ite = 0
            for ant in ants:
                ite += 1
                for vehicle in self.vehicles:
                    is_feasible = True
                    if self.vehicles.index(vehicle) != 0:
                        ant.current_customer = self.customers[0]  # if it is not the first vehicle, move the ant back to depot
                        ant.ant_route = [self.customers[0]]

                    if len(ant.candidate_list) == 0:
                        is_feasible = False
                    while is_feasible:
                        if vehicle.get("index") in self.index_list_special_vehicles and len(ant.candidate_list_for_special_vehicles) != 0:
                            if len(ant.ant_route) > 1:
                                if ant.ant_route[1].get("demand") > 20:
                                    ant.candidate_list.append(ant.ant_route[1])
                                    ant.ant_route.remove(ant.ant_route[1])
                                    break
                            ant.select_next_for_special()
                            capacity_remaining = vehicle.get("capacity")
                            delivery_time = 0
                            for node in ant.ant_route:
                                capacity_remaining -= node.get("demand")
                            for i in range(len(ant.ant_route) - 1):
                                from_node = ant.ant_route[i]
                                to_node = ant.ant_route[i+1]
                                delivery_time += ant.customers_graph.cost_matrix[from_node.get("index")][to_node.get("index")]/vehicle.get("velocity")
                            if capacity_remaining < 0 or delivery_time > ant.current_customer.get("closetime"):
                                ant.candidate_list.append(ant.current_customer)
                                ant.candidate_list_for_special_vehicles.append(ant.current_customer)
                                ant.ant_route.remove(ant.current_customer)
                                break
                            is_feasible = ant.any_feasible_node(capacity_remaining, delivery_time)
                        else:
                            ant.select_next()
                            capacity_remaining = vehicle.get("capacity")
                            delivery_time = 0
                            for node in ant.ant_route:
                                capacity_remaining -= node.get("demand")
                            for i in range(len(ant.ant_route) - 1):
                                from_node = ant.ant_route[i]
                                to_node = ant.ant_route[i+1]
                                delivery_time += ant.customers_graph.cost_matrix[from_node.get("index")][to_node.get("index")]/vehicle.get("velocity")
                            if capacity_remaining < 0 or delivery_time > ant.current_customer.get("closetime"):
                                ant.candidate_list.append(ant.current_customer)
                                ant.ant_route.remove(ant.current_customer)
                                break
                            is_feasible = ant.any_feasible_node(capacity_remaining, delivery_time)
                    # After finish the its route, current vehicle move back to the depot --> add depot to the end of the route
                    ant.ant_route.append(self.customers[0])
                    ant.ant_route_for_all_vehicles.append(ant.ant_route)

                # calculate current total cost for this ant
                vehicle_count = 0
                for single_route in ant.ant_route_for_all_vehicles:
                    for i in range(len(single_route) - 1):
                        from_node_index = single_route[i].get("index")
                        to_node_index = single_route[i+1].get("index")
                        ant.total_cost += customers_graph.cost_matrix[from_node_index][to_node_index] * self.vehicles[vehicle_count].get("cost")
                    vehicle_count += 1
                ant.update_local_pheromone(ite)
                if ant.total_cost < best_cost:
                    best_cost = ant.total_cost
                    best_route = list(ant.ant_route_for_all_vehicles)
                    ant_of_best_route.local_pheromone = list(ant.local_pheromone)

                #Detect whether the ant route has more customer
                number_of_customer_in_ant_route = 0
                for single_route in ant.ant_route_for_all_vehicles:
                    for item in single_route:
                        if item.get("index") != 0:
                            number_of_customer_in_ant_route += 1

                if number_of_customer_in_ant_route >= maximum_customer:
                    best_route_with_maximum_customer.clear()
                    best_route_with_maximum_customer = list(ant.ant_route_for_all_vehicles)
                    maximum_customer = number_of_customer_in_ant_route
                    best_cost = ant.total_cost
                    is_updated = True

            if e >= 11:
                should_continue, current_count, last_maximum_customer = self.should_continue_check(maximum_customer, last_maximum_customer, current_count)
                if not should_continue:
                    current_iteration = e
                    break
            if e == 10:
                last_maximum_customer = maximum_customer

            self.update_global_pheromone(customers_graph, best_cost, ant_of_best_route.local_pheromone)
            self.update_global_pheromone_by_maximum_customer_route(customers_graph,maximum_customer, best_route_with_maximum_customer )

        print("\n***********\n")
        print("STOP AT ITERATION: ", current_iteration)
        print("\n***********\n")

        if is_updated:
            return best_route_with_maximum_customer
        else:
            return best_route


class Ant(object):   
    def __init__(self, aco: ACO, customers_graph: CustomersGraph, start_node_index: int):
        self.aco = aco
        self.customers_graph = customers_graph
        self.total_cost = 0.0
        # local increase of pheromone
        self.local_pheromone = [[0 for j in range(self.customers_graph.total_customer)] for i in range(self.customers_graph.total_customer)]
        self.ant_route_for_all_vehicles = []
        self.candidate_list = list(self.aco.customers[1:])
        self.current_customer = {}
        self.ant_route = [aco.customers[0]]  # dispatch ant from depot
        self.eta = [[0 if i == j else 1 / customers_graph.cost_matrix[i][j] for j in range(customers_graph.total_customer)]
                    for i in range(customers_graph.total_customer)]
        start = aco.customers[start_node_index]
        self.current_customer = start
        self.ant_route.append(start)
        self.candidate_list.remove(start)

        # build candidate list for special vehicles
        self.candidate_list_for_special_vehicles = []
        for candidate in self.candidate_list:
            if candidate.get("demand") < 20 and self.customers_graph.cost_matrix[0][candidate.get("index")] < 4:
                self.candidate_list_for_special_vehicles.append(candidate)

        #preference to the global pheromone
        for i in range(self.customers_graph.total_customer):
            for j in range(self.customers_graph.total_customer):
                self.local_pheromone[i][j] = self.customers_graph.global_pheromone[i][j]
        
    def any_feasible_node(self, capacity_remaining: int, delivery_time: int):
        result = False
        if len(self.candidate_list) > 0:
            for candidate in self.candidate_list:
                if capacity_remaining > candidate.get("index") and delivery_time < candidate.get("closetime"):
                    result = True
        return result

    def find_element_by_index(self, input_list: list, index: int):
        for i in range(len(input_list)):
            if input_list[i].get("index") == index:
                return input_list[i]

    def select_next(self):
        Q0 = 0.9
        denominator = 0
        q = random.uniform(0, 1)
        selected_customer = {}

        for candidate in self.candidate_list:
            i = self.current_customer.get("index")
            j = candidate.get("index")
            denominator += self.customers_graph.global_pheromone[i][j] ** self.aco.alpha * self.eta[i][j] ** self.aco.beta

        probabilities =  [0 for i in range(self.customers_graph.total_customer)]
        attractiveness = [0 for i in range(self.customers_graph.total_customer)]
        for customer in self.aco.customers:
            try:
                self.candidate_list.index(customer)  # test if the candidate list contains this customer
                i = self.current_customer.get("index")
                j = customer.get("index")
                probabilities[customer.get("index")] = self.customers_graph.global_pheromone[i][j] ** self.aco.alpha * \
                    self.eta[i][j] ** self.aco.beta / denominator
                attractiveness[customer.get("index")] = self.customers_graph.global_pheromone[i][j] ** self.aco.alpha * \
                    self.eta[i][j] ** self.aco.beta
            except ValueError:
                pass #do nothing

        if q > Q0:
            rand = random.random()
            for i, probability in enumerate(probabilities):
                rand -= probability
                if rand <= 0:
                    selected_customer = self.find_element_by_index(self.candidate_list, i)
                    break
        else:
            max_attractiveness = max(attractiveness)
            customer_index = attractiveness.index(max_attractiveness)
            selected_customer = self.find_element_by_index(self.candidate_list, customer_index)

        self.candidate_list.remove(selected_customer)
        if len(self.candidate_list_for_special_vehicles) != 0:
            try:
                self.candidate_list_for_special_vehicles.index(selected_customer)
                self.candidate_list_for_special_vehicles.remove(selected_customer)
            except ValueError:
                pass
        self.ant_route.append(selected_customer)
        self.current_customer = selected_customer

    def select_next_for_special(self):
        Q0 = 0.9
        denominator = 0
        q = random.uniform(0, 1)
        selected_customer = {}

        for candidate in self.candidate_list_for_special_vehicles:
            i = self.current_customer.get("index")
            j = candidate.get("index")
            denominator += self.customers_graph.global_pheromone[i][j] ** self.aco.alpha * self.eta[i][j] ** self.aco.beta

        probabilities =  [0 for i in range(self.customers_graph.total_customer)]
        attractiveness = [0 for i in range(self.customers_graph.total_customer)]
        for customer in self.aco.customers:
            try:
                self.candidate_list_for_special_vehicles.index(customer)  # test if the candidate list contains this customer
                i = self.current_customer.get("index")
                j = customer.get("index")
                probabilities[customer.get("index")] = self.customers_graph.global_pheromone[i][j] ** self.aco.alpha * \
                    self.eta[i][j] ** self.aco.beta / denominator
                attractiveness[customer.get("index")] = self.customers_graph.global_pheromone[i][j] ** self.aco.alpha * \
                    self.eta[i][j] ** self.aco.beta
            except ValueError:
                pass #do nothing

        if q > Q0:
            rand = random.random()
            for i, probability in enumerate(probabilities):
                rand -= probability
                if rand <= 0:
                    selected_customer = self.find_element_by_index(self.candidate_list_for_special_vehicles, i)
                    break
        else:
            max_attractiveness = max(attractiveness)
            customer_index = attractiveness.index(max_attractiveness)
            selected_customer = self.find_element_by_index(self.candidate_list_for_special_vehicles, customer_index)

        self.candidate_list.remove(selected_customer)
        self.candidate_list_for_special_vehicles.remove(selected_customer)
        self.ant_route.append(selected_customer)
        self.current_customer = selected_customer

    def update_local_pheromone(self, ite: int):
        for single_route in self.ant_route_for_all_vehicles:
            for i in range(len(single_route) - 1):

                from_node_index = single_route[i].get("index")
                to_node_index = single_route[i + 1].get("index")

                self.local_pheromone[from_node_index][to_node_index]\
                    = (1 - self.aco.gama) * self.local_pheromone[from_node_index][to_node_index]\
                    + self.customers_graph.global_pheromone[from_node_index][to_node_index]\
                    * self.aco.gama ** ite