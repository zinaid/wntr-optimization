import wntr
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def readFile(network):
    wn = wntr.network.WaterNetworkModel(network)
    return wn

def saveFile(network, name):
    wntr.network.write_inpfile(network, "networks/new_networks/"+name+"_new.inp", version=2.2)

def runSimulation(wn):
    wn.options.hydraulic.demand_model = 'PDD'
    wn.options.hydraulic.required_pressure = 21.097
    sim = wntr.sim.EpanetSimulator(wn)
    results = sim.run_sim()
    return results

def getPressure(results):
    pressure = results.node['pressure']
    return pressure

def getJunctionPressures(wn, results):
    pressure = results.node['pressure'].loc[:,wn.junction_name_list]
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

def runCriticalityAnalysis(wn, pressure_threshold):
    # Simulation options
    analysis_end_time = 72*3600 
    wn.options.time.duration = analysis_end_time
    wn.options.hydraulic.demand_model = 'PDD'
    wn.options.hydraulic.required_pressure = 17.57
    wn.options.hydraulic.minimum_pressure = 0

    # List of pipes to include in the analysis (we can play with the list)
    pipes = wn.query_link_attribute('diameter', np.greater_equal, 0, 
                                    link_type=wntr.network.model.Pipe)      
    pipes = list(pipes.index)

    # Remove the first pipe from the list (This is for Net1)
    #if pipes:
    #    first_pipe = pipes[0]
    #    pipes.remove(first_pipe)
    
    # We can select specific pipes
    #pipes = ['11', '110', '121']

    # If we want to see details about the list
    #print(pipes)
    #wntr.graphics.plot_network(wn, link_attribute=pipes, 
    #                           title='Pipes included in criticality analysis')

    # Run a preliminary simulation to determine if junctions drop below the 
    # pressure threshold during normal conditions
    sim = wntr.sim.EpanetSimulator(wn)
    results = sim.run_sim()
    min_pressure = results.node['pressure'].loc[:,wn.junction_name_list].min()
    below_threshold_normal_conditions = set(min_pressure[min_pressure < pressure_threshold].index)

    # Run the criticality analysis, closing one pipe for each simulation
    junctions_impacted = {} 
    for pipe_name in pipes:
        #print('Pipe:', pipe_name)     
        
        # Reset the water network model
        wn.reset_initial_values()

        # Add a control to close the pipe
        pipe = wn.get_link(pipe_name)        
        act = wntr.network.controls.ControlAction(pipe, 'status', 
                                                  wntr.network.LinkStatus.Closed)
        cond = wntr.network.controls.SimTimeCondition(wn, '=', '24:00:00')
        ctrl = wntr.network.controls.Control(cond, act)
        wn.add_control('close pipe ' + pipe_name, ctrl)

        try:    
            # Run a PDD simulation
            sim = wntr.sim.EpanetSimulator(wn)
            results = sim.run_sim()
                
            # Extract the number of junctions that dip below the minimum pressure threshold
            min_pressure = results.node['pressure'].loc[:,wn.junction_name_list].min()
            below_threshold = set(min_pressure[min_pressure < pressure_threshold].index)
            
            # Remove the set of junctions that were below the pressure threshold during 
            # normal conditions and store the result
            junctions_impacted[pipe_name] = below_threshold - below_threshold_normal_conditions

        except Exception as e:
            # Identify failed simulations and the reason
            impacted_junctions = None
            print(pipe_name, ' Failed:', e)
            
        # Remove the control
        wn.remove_control('close pipe ' + pipe_name)

    # Extract the number of junctions impacted by low pressure conditions for each pipe closure  
    number_of_junctions_impacted = dict([(k,len(v)) for k,v in junctions_impacted.items()])
    return sum(number_of_junctions_impacted.values())

def checkMinConstraints(wn, results, min_pressure):
    for node_name, node in wn.nodes(wntr.network.Junction):
        if (results.node['pressure'].loc[:, node_name] < min_pressure[node_name]).any():
            return False
    return True

def getStartingPressures(wn, results):
    pressure_min_dict = {}

    for node_name, node in wn.nodes(wntr.network.Junction):
        pressure_min = results.node['pressure'].loc[:, node_name].min()
        pressure_min_dict[node_name] = pressure_min

    pressure_min_series = pd.Series(pressure_min_dict, dtype=float)
    return pressure_min_series

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

def remove_small_diameter_pipes(wn, diameter_threshold):
    removed_pipes = []

    pipes_to_remove = [link_name for link_name, link in wn.links(wntr.network.Pipe) if link.diameter < diameter_threshold]

    for link_name in pipes_to_remove:
        wn.remove_link(link_name)
        removed_pipes.append(link_name)
    
    return removed_pipes

def plot_network_with_consumers(wn, junction_pressures):
    print(junction_pressures)
    fig, ax = plt.subplots()
    for node_name, node in wn.nodes(wntr.network.Junction):
        if node_name in junction_pressures:
            demand = float(junction_pressures[node_name][0])
            ax.annotate(f"{demand:.5f}", (node.coordinates[0], node.coordinates[1]),
                        xytext=(5, -5), textcoords='offset points',
                        fontsize=10, color='red', ha='right', va='top')

    for link_name, link in wn.links(wntr.network.Pipe):
        start_node = wn.get_link(link_name).start_node_name
        end_node = wn.get_link(link_name).end_node_name
        line_width = link.diameter * 3 
        x_start, y_start = wn.nodes[start_node].coordinates
        x_end, y_end = wn.nodes[end_node].coordinates
        ax.plot([x_start, x_end], [y_start, y_end], linewidth=line_width, color='black', marker='')
        ax.text((x_start + x_end) / 2, (y_start + y_end) / 2, link_name, fontsize=10, color='blue', ha='left', va='bottom')
    # Plot nodes as black dots
    for node_name, node in wn.nodes(wntr.network.Junction):
        ax.plot(node.coordinates[0], node.coordinates[1], 'ko')

    plt.tight_layout()
    plt.show()