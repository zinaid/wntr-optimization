import wntr
import pandas as pd
import numpy as np

def readFile():
    wn = wntr.network.WaterNetworkModel('networks/Net2.inp')
    return wn

def runSimulation(wn):
    wn.options.hydraulic.demand_model = 'PDD'
    wn.options.hydraulic.required_pressure = 1
    sim = wntr.sim.EpanetSimulator(wn)
    results = sim.run_sim()
    return results

def getPressure(results):
    pressure = results.node['pressure']
    return pressure

def getMaxPressure(pressure):
    return pressure.max().max()

def getMinPressure(pressure):
    return pressure.min().min()

def getPipeCost(wn, pipe_cost=None):
    pipeCost = 0

    if pipe_cost is None:
        diameter = [4, 6, 8, 10, 12, 14, 16, 18, 20, 24, 28, 30] # inch
        diameter = np.array(diameter) * 0.0254  # m
        cost = [8.31, 10.10, 12.10, 12.96, 15.22, 16.62, 19.41, 22.20, 24.66, 35.69, 40.08, 42.60]
        diameter_cost = pd.Series(cost, diameter)

    for link_name, link in wn.links(wntr.network.Pipe):
        idx = np.argmin([np.abs(diameter_cost.index - link.diameter)])
        pipeCost = pipeCost + diameter_cost.iloc[idx] * link.length
        
    return pipeCost

def MRI(wn, results, pressure, threshold):
    junction_names = wn.junction_name_list
    elevations = wn.query_node_attribute('elevation')
    junction_elevations = pd.Series(elevations, index=junction_names)
    junction_demands = results.node['demand'].loc[:, junction_names]

    junction_pressure = results.node['pressure'].loc[:, junction_names]
    Pstar = threshold
    mri = wntr.metrics.modified_resilience_index(junction_pressure, junction_elevations, Pstar, demand=junction_demands, per_junction=False)
    return mri

def checkMinConstraints(wn, results, min_pressure):
    for node_name, node in wn.nodes(wntr.network.Junction):
        if (results.node['pressure'].loc[:, node_name] < min_pressure).any():
            return False
    return True

def checkMaxConstraints(wn, results, max_pressure):
    for node_name, node in wn.nodes(wntr.network.Junction):
        if (results.node['pressure'].loc[:, node_name] > max_pressure).any():
            return False
    return True

def printOptimalSolution(res):
    print("Optimal Solutions:")
    for solution in res.X:
        print(solution)

def updateSolution(wn, res):
    for i, link_name in enumerate(wn.link_name_list):
        link = wn.get_link(link_name)
        link.diameter = res.X[i]
