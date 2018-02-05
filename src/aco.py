import random
import math

class Customers_Graph(object):
    def __init__(self, cost_matrix : list, total_customer: int, number_of_customer_in_first_route: int,
                 total_cost_in_first_route: int):
        self.cost_matrix: cost_matrix
        self.total_customer: total_customer
        self.pheromone = [[1 / (number_of_customer_in_first_route * total_cost_in_first_route) for j in range(total_customer)]
                          for i in range (total_customer)]


class ACO(object):
    def __init__(self, alpha: int, beta: int, gama: int, M: int, E: int , ITE: int, vehicles: list):
        self.alpha = alpha
        self.beta = beta
        self.gama = gama
        self.M = M
        self.E = E
        self.ITE = ITE
        self.vehicles = vehicles

    def update_pheromone(self):
        return 0

    def solve(self, customers_graph: Customers_Graph):
        best_route = []
        for e in range(self.E):
            for vehicle in self.vehicles:
                ants = [Ant(self, customers_graph) for i in range(self.ITE)]
                for ant in ants:
                    pass

        return 0



class Ant(object):
    def __init__(self, aco: ACO, customers_graph: Customers_Graph):
        self.aco = aco
        self.customers_graph = customers_graph
        self.pheromone_delta = [] #local increase of pheromone
        self.candidate_list = []
    def any_feasible_node(self, capacity_remaining: int, delivery_time: int):
        result = False
        for candidate in self.candidate_list:
            if capacity_remaining > candidate.get("index") and delivery_time < candidate.get("closetime"):
                result = True
        return result

    def select_next(self):
        return 0

    def update_pheromone_delta(self):
        return 0