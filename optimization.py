import wntr
import numpy as np
from pymoo.algorithms.soo.nonconvex.ga import GA
from pymoo.optimize import minimize
from pymoo.termination import get_termination
from pymoo.core.problem import ElementwiseProblem
from network import runSimulation, getPipeCost, getPressure, MRI, runCriticalityAnalysis

class WaterNetworkProblem(ElementwiseProblem):

    def __init__(self, wn, min_pressure, max_pressure, resilience_target, junction_target):
        self.wn = wn
        self.min_pressure = min_pressure
        self.max_pressure = max_pressure
        n_var = len(wn.link_name_list)
        self.resilience_target = resilience_target
        self.junction_target = junction_target
        xl = [0.1] * n_var
        xu = [0.762] * n_var
        super().__init__(n_var=n_var, n_obj=1, n_ieq_constr=1, xl=xl, xu=xu)

    def _evaluate(self, x, out):
        for i, (link_name, link) in enumerate(self.wn.links(wntr.network.Pipe)):
            link.diameter = x[i]

        results = runSimulation(self.wn)
        total_cost = getPipeCost(self.wn)
        mri = MRI(self.wn, results, getPressure(results), self.min_pressure)

        pressure_penalty_low = 0.0
        for node_name, node in self.wn.nodes(wntr.network.Junction):
            pressure = results.node['pressure'].loc[:, node_name]
            pressure_penalty_low += np.maximum(0, self.min_pressure - pressure).sum()

        pressure_penalty_high = 0.0
        for node_name, node in self.wn.nodes(wntr.network.Junction):
            pressure = results.node['pressure'].loc[:, node_name]
            pressure_penalty_high += np.maximum(0, pressure - self.max_pressure).sum()

        resilience_penalty = np.maximum(0, self.resilience_target - np.mean(mri))

        # If we want to turn off number of junction impact just comment these simulations
        # and remove junction penalty
        num_impacted_junctions = runCriticalityAnalysis(self.wn, self.min_pressure)
        junction_penalty = np.maximum(0, num_impacted_junctions - self.junction_target)

        total_penalty = pressure_penalty_low + pressure_penalty_high + resilience_penalty + junction_penalty

        objective = total_cost
        out["F"] = np.array([objective])
        out["G"] = np.array([total_penalty])

def optimize_water_network(wn, threshold, max_pressure, resilience_target, junction_target):
    water_network_problem = WaterNetworkProblem(wn, threshold, max_pressure, resilience_target, junction_target)
    termination = get_termination("n_gen", 200)
    algorithm = GA(pop_size=40, eliminate_duplicates=True)
    res = minimize(water_network_problem, algorithm, termination, seed=1, verbose=True, save_history=True)
    return res