import random

class CustomersGraph(object):
    def __init__(self, cost_matrix: list, total_customer: int, number_of_customer_in_first_route: int,
                 total_cost_in_first_route: int):
        self.cost_matrix = cost_matrix
        self.total_customer = total_customer
        self.pheromone_matrix = [[1 / (number_of_customer_in_first_route * total_cost_in_first_route) for j in range(total_customer)]
                          for i in range(total_customer)]


class ACO(object):
    def __init__(self, alpha: int, beta: int, gama: int, M: int, E: int , ITE: int, vehicles: list, customers: list,
                 total_cost_in_first_route: float):
        self.alpha = alpha
        self.beta = beta
        self.gama = gama
        self.M = M
        self.E = E
        self.ITE = ITE
        self.vehicles = vehicles
        self.customers = customers
        self.total_cost_in_first_route = total_cost_in_first_route

    def update_pheromone(self, customer_graph: CustomersGraph, best_cost: float):
        for i, row in enumerate(customer_graph.pheromone_matrix):
            for j, col in enumerate(row):
                customer_graph.pheromone_matrix[i][j] = (1 - self.gama) * customer_graph.pheromone_matrix[i][j]\
                                                        + self.gama / best_cost

    def solve(self, customers_graph: CustomersGraph):
        best_cost = self.total_cost_in_first_route
        best_route = []
        for e in range(self.E):
            ants = [Ant(self, customers_graph, i) for i in range(self.ITE)]
            ite = 1
            for ant in ants:
                ite += 1
                for vehicle in self.vehicles:
                    is_feasible = True
                    route_for_single_vehicle = []
                    if self.vehicles.index(vehicle) != 0:
                        ant.current_customer = self.customers[0] #if it is not the first vehicle, move the ant back to depot
                    while is_feasible:
                        ant.select_next()
                        capacity_remaining = vehicle.get("capacity")
                        delivery_time = 0
                        for node in ant.ant_route:
                            capacity_remaining -= node.get("demand")
                        for i in range(len(ant.ant_route) - 1):
                            from_node = ant.ant_route[i]
                            to_node = ant.ant_route[i+1]
                            delivery_time += ant.customers_graph.cost_matrix[from_node.get("index")][to_node.get("index")]/vehicle.get("velocity")
                        is_feasible = ant.any_feasible_node(capacity_remaining,delivery_time)
                    ant.ant_route_for_all_vehicles.append(ant.ant_route)
                #calcualate current cost for this ant
                for single_route in ant.ant_route_for_all_vehicles:
                    for i in range(len(single_route) - 1):
                        from_node_index = single_route[i].get("index")
                        to_node_index = single_route[i+1].get("index")
                        ant.total_cost += customers_graph.cost_matrix[from_node_index][to_node_index]
                if ant.total_cost < best_cost:
                    best_cost = ant.total_cost
                    best_route = ant.ant_route_for_all_vehicles
                ant.update_pheromone_delta(ite)
            self.update_pheromone(customers_graph, best_cost)
        return best_route

class Ant(object):   
    def __init__(self, aco: ACO, customers_graph: CustomersGraph, start_node_index: int):
        self.aco = aco
        self.customers_graph = customers_graph
        self.total_cost = 0.0
        # local increase of pheromone
        self.pheromone_delta = []
        self.ant_route_for_all_vehicles = []
        self.candidate_list = aco.customers
        self.current_customer = {}
        self.ant_route = [aco.customers[0]]  # dispatch ant from depot
        self.eta = [[0 if i == j else 1/ customers_graph.cost_matrix[i][j] for j in range(customers_graph.total_customer)]
                    for i in range(customers_graph.total_customer)]
        start = aco.customers[start_node_index]
        self.current_customer = start
        self.ant_route.append(start)
        self.candidate_list.remove(start)
        
    def any_feasible_node(self, capacity_remaining: int, delivery_time: int):
        result = False
        for candidate in self.candidate_list:
            if capacity_remaining > candidate.get("index") and delivery_time < candidate.get("closetime"):
                result = True
        return result

    def select_next(self):
        Q0 = 0.9
        denominator = 0
        q = random.uniform(0, 1)
        selected_customer = {}

        for candidate in self.candidate_list:
            i = self.current_customer.get("index")
            j = candidate.get("index")
            denominator += self.customers_graph.pheromone_matrix[i][j] ** self.aco.alpha * self.eta[i][j] ** self.aco.beta

        probabilities = [0 for i in range(self.customers_graph.total_customer)]
        attractiveness = [0 for i in range(self.customers_graph.total_customer)]
        for customer in self.aco.customers:
            try:
                self.candidate_list.index(customer) # test if the candidate list contains this customer
                i = self.current_customer.get("index")
                j = customer.get("index")
                probabilities[customer.get("index")] = self.customers_graph.pheromone_matrix[i][j] ** self.aco.alpha * \
                    self.eta[i][j] ** self.aco.beta / denominator
                attractiveness[customer.get("index")] = self.customers_graph.pheromone_matrix[i][j] ** self.aco.alpha * \
                    self.eta[i][j] ** self.aco.beta
            except ValueError:
                pass #do nothing

        if q > Q0:
            rand = random.random()
            for i, probability in enumerate(probabilities):
                rand -= probability
                if rand <= 0:
                    selected_customer = self.candidate_list[i]
                    break
        else:
            max_attractiveness = max(attractiveness)
            customer_index = attractiveness.index(max_attractiveness)
            selected_customer = self.candidate_list[customer_index]

        self.candidate_list.remove(selected_customer)
        self.ant_route.append(selected_customer)
        self.current_customer = selected_customer

    def update_pheromone_delta(self, ite: int):
        self.pheromone_delta = [[0 for j in range(self.customers_graph.total_customer)] for i in range(self.customers_graph.total_customer)]
        for single_route in self.ant_route_for_all_vehicles:
            for i in range(len(single_route) - 1):

                from_node_index = single_route[i].get("index")
                to_node_index = single_route[i + 1].get("index")

                self.pheromone_delta[from_node_index][to_node_index]\
                    = (1 - self.aco.gama) * self.pheromone_delta[from_node_index][to_node_index]\
                    + self.customers_graph.pheromone_matrix[from_node_index][to_node_index]\
                    * self.aco.gama ** ite