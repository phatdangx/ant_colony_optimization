import random
import math


class CustomersGraph(object):
    def __init__(self, cost_matrix : list, total_customer: int, number_of_customer_in_first_route: int,
                 total_cost_in_first_route: int):
        self.cost_matrix = cost_matrix
        self.total_customer = total_customer
        self.pheromone_matrix = [[1 / (number_of_customer_in_first_route * total_cost_in_first_route) for j in range(total_customer)]
                          for i in range(total_customer)]


class ACO(object):
    def __init__(self, alpha: int, beta: int, gama: int, M: int, E: int , ITE: int, vehicles: list, customers: list):
        self.alpha = alpha
        self.beta = beta
        self.gama = gama
        self.M = M
        self.E = E
        self.ITE = ITE
        self.vehicles = vehicles
        self.customers = customers

    def update_pheromone(self):
        return 0

    def solve(self, customers_graph: CustomersGraph):
        best_route = []
        for e in range(self.E):
            ants = [Ant(self, customers_graph) for i in range(self.ITE)]
            for ant in ants:
                for vehicle in self.vehicles:
                    is_feasible = True
                    while is_feasible:
                        ant.select_next()
                        is_feasible = ant.any_feasible_node()


        return 0
    
    
class Ant(object):   
    def __init__(self, aco: ACO, customers_graph: CustomersGraph):
        self.aco = aco
        self.customers_graph = customers_graph
        # local increase of pheromone
        self.pheromone_delta = []                                                           
        self.candidate_list = aco.customers
        self.current_customer = {}
        self.eta = [[0 if i == j else 1/ customers_graph.cost_matrix[i][j] for j in range(customers_graph.total_customer)]
                    for i in range(customers_graph.total_customer)]
        start = aco.customers[random.randint(0,customers_graph.total_customer - 1)]
        self.current_customer = start
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
                if rand <=0:
                    selected_customer = self.candidate_list[i]
                    break
        else:
            max_attractiveness = max(attractiveness)
            customer_index = attractiveness.index(max_attractiveness)
            selected_customer = self.candidate_list[customer_index]

        self.candidate_list.remove(selected_customer)
        self.current_customer = selected_customer



    def update_pheromone_delta(self):
        return 0