import wntr
import numpy as np
from pymoo.algorithms.soo.nonconvex.ga import GA
from pymoo.optimize import minimize
from pymoo.termination import get_termination
from pymoo.core.problem import ElementwiseProblem
from network import runSimulation, getPipeCost, runCriticalityAnalysis, remove_small_diameter_pipes
import copy
import networkx as nx

class WaterNetworkProblem(ElementwiseProblem):

    def __init__(self, wn, min_pressure, junction_target, diameter_threshold):
        self.wn = wn
        self.min_pressure = min_pressure
        n_var = len(wn.link_name_list)
        self.junction_target = junction_target
        self.diameter_threshold = diameter_threshold
        xl = [0.0] * n_var
        xu = [0.762] * n_var
        super().__init__(n_var=n_var, n_obj=1, n_ieq_constr=1, xl=xl, xu=xu)

    def _evaluate(self, x, out):
        wn_copy = copy.deepcopy(self.wn)

        for i, (link_name, link) in enumerate(wn_copy.links(wntr.network.Pipe)):
            link.diameter = x[i]

        remove_small_diameter_pipes(wn_copy, self.diameter_threshold)
        total_cost = getPipeCost(wn_copy)

        G = wn_copy.to_graph()
        uG = G.to_undirected()

        connectivity_penalty = 0.0
        pressure_penalty_low = 0.0
        if nx.is_connected(uG) is True:
            connectivity_penalty = 0.0
            results = runSimulation(wn_copy)

            pressure_penalty_low = 0.0
            for node_name, node in wn_copy.nodes(wntr.network.Junction):
                pressure = results.node['pressure'].loc[:, node_name].min()
                pressure_penalty_low += np.maximum(0, self.min_pressure[node_name] - pressure).sum()

                # If we want to turn off number of junction impact just comment these simulations
                # and remove junction penalty
                #num_impacted_junctions = runCriticalityAnalysis(self.wn, self.min_pressure)
                #junction_penalty = np.maximum(0, num_impacted_junctions - self.junction_target)
        else:
            connectivity_penalty = 100.0

        total_penalty = pressure_penalty_low + connectivity_penalty

        objective = total_cost
        out["F"] = np.array([objective])
        out["G"] = np.array([total_penalty])

def optimize_water_network(wn, threshold, junction_target, diameter_threshold):
    water_network_problem = WaterNetworkProblem(wn, threshold, junction_target, diameter_threshold)
    termination = get_termination("n_gen", 400)
    algorithm = GA(pop_size=20, eliminate_duplicates=True)
    res = minimize(water_network_problem, algorithm, termination, seed=1, verbose=True, save_history=True)
    return res
