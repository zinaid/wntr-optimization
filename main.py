import numpy as np
import matplotlib.pyplot as plt
from optimization import optimize_water_network
from network import readFile, saveFile, plot_network_with_consumers, remove_small_diameter_pipes, getJunctionPressures, getStartingPressures, getMinPressure, runSimulation, getPipeCost, getPressure, getMaxPressure, checkMinConstraints, updateSolution, printOptimalSolution
from criticality import runCriticality

if __name__ == "__main__":
    print("####Program starts####") 

    network_name = "Anytown"
    wn = readFile("networks/"+network_name+".inp")

    print("####Initial readings####")

    print("Initial pipe cost: ", getPipeCost(wn))
    junction_target = runCriticality("networks/"+network_name+".inp")
    pipe_diameters = wn.query_link_attribute('diameter')
    print("Initial Pipe Diameters:")
    print(pipe_diameters)

    print("####Initial simulation starting####")
    results = runSimulation(wn)
    print("Initial minimum pressures for nodes")
    starting_pressures = getStartingPressures(wn, results)
    print(getStartingPressures(wn, results))

    pressure = getPressure(results)
    junction_pressures = getJunctionPressures(wn, results)

    print("Starting list of pressures for whole network:")
    print(getPressure(results))
    print("Starting list of Junction(consumers) pressures:")
    print(getJunctionPressures(wn, results))

    print("Maximum pressure: ", getMaxPressure(junction_pressures))
    print("Minimum pressure: ", getMinPressure(junction_pressures))

    plot_network_with_consumers(wn, junction_pressures)

    # Setting thresholds
    min_pressure = starting_pressures
    diameter_threshold = 0.1

    print("####Starting optimization####")
    res = optimize_water_network(wn, min_pressure, junction_target, diameter_threshold)
    n_evals = np.array([e.evaluator.n_eval for e in res.history])
    opt = np.array([e.opt[0].F for e in res.history])

    plt.title("Convergence")
    plt.plot(n_evals, opt, "--")
    plt.yscale("log")
    plt.show()

    printOptimalSolution(res)

    #Creating a final network
    updateSolution(wn, res)
    remove_small_diameter_pipes(wn, diameter_threshold)
    results = runSimulation(wn)
    print("Final cost:", getPipeCost(wn))
    print("Final list of pressures for whole network:")
    pressure = getPressure(results)
    print(pressure)

    if(checkMinConstraints(wn, results, min_pressure)):
        print("Minimum pressure constraints are satisfied.")
    else:
        print("Minimum pressure constraints are not satisfied.")

    junction_pressures = getJunctionPressures(wn, results)
    print("Final list of Junction(consumers) pressures:")
    print(junction_pressures)

    network_name_to_save = network_name+"_newWithoutCA.inp"
    saveFile(wn, network_name_to_save)
    final_junction= runCriticality("networks/new_networks/"+network_name_to_save+"")

    plot_network_with_consumers(wn, junction_pressures)
    
