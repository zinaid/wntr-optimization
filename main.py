import numpy as np
import matplotlib.pyplot as plt
from optimization import optimize_water_network
from network import readFile, runSimulation, getPipeCost, getPressure, getMaxPressure, checkMinConstraints, checkMaxConstraints, updateSolution, printOptimalSolution, MRI, runCriticalityAnalysis

if __name__ == "__main__":
    print("Program starts")
    wn = readFile()
    print("Initial pipe cost: ", getPipeCost(wn))
    # Extract initial pipe diameters
    pipe_diameters = wn.query_link_attribute('diameter')

    # Print the initial pipe diameters
    print("Initial Pipe Diameters:")
    print(pipe_diameters)
    print("Initial simulation starting")
    results = runSimulation(wn)
    pressure = getPressure(results)
    print("Starting list of pressures:")
    print(getPressure(results))
    print("Maximum pressure: ", getMaxPressure(pressure))

    # This needs to be adapted for a network    
    min_pressure = 0.1
    max_pressure = 68
    resilience_target = 0.3
    
    print("Initial MRI: ", np.mean(MRI(wn, results, pressure, min_pressure)))

    junction_max = runCriticalityAnalysis(wn, min_pressure)
    print("Initial junction impact:", junction_max)
    # We set junction target to be the same as the initial network junction impact
    junction_target = junction_max
    res = optimize_water_network(wn, min_pressure, max_pressure, resilience_target, junction_target)
    n_evals = np.array([e.evaluator.n_eval for e in res.history])
    opt = np.array([e.opt[0].F for e in res.history])

    plt.title("Convergence")
    plt.plot(n_evals, opt, "--")
    plt.yscale("log")
    plt.show()

    printOptimalSolution(res)

    updateSolution(wn, res)
        
    results = runSimulation(wn)
    
    print("Final cost:", getPipeCost(wn))
        
    print("Ending list of pressures:")
    pressure = getPressure(results)
    print(pressure)

    if(checkMinConstraints(wn, results, min_pressure)):
        print("Minimum pressure constraints are satisfied.")
    else:
        print("Minimum pressure constraints are not satisfied.")

    print(getMaxPressure(pressure))
    
    if(checkMaxConstraints(wn, results, max_pressure)):
        print("Maximum pressure constraints are satisfied.")
    else:
        print("Maximum pressure constraints are not satisfied.")
        
    print("Final MRI:")
    print(np.mean(MRI(wn, results, pressure, min_pressure)))

    final_junction = runCriticalityAnalysis(wn, min_pressure)
    print("Final junction impact:", final_junction)
