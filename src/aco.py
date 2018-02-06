import random
import math


class CustomersGraph(object):
    def __init__(self, cost_matrix : list, total_customer: int, number_of_customer_in_first_route: int,
                 total_cost_in_first_route: int):
        self.cost_matrix: cost_matrix
        self.total_customer: total_customer
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

                        is_feasible = ant.any_feasible_node()


        return 0
    
    
class Ant(object):   
    def __init__(self, aco: ACO, customers_graph: CustomersGraph):
        self.aco = aco
        self.customers_graph = customers_graph
        # local increase of pheromone
        self.pheromone_delta = []                                                           
        self.candidate_list = aco.customers
        self.selected_customer = {}
        
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

        return 0

    def update_pheromone_delta(self):
        return 0