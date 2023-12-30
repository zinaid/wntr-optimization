import numpy as np
import matplotlib.pyplot as plt
from optimization import optimize_water_network
from network import readFile, runSimulation, getPipeCost, getPressure, getMaxPressure, checkMinConstraints, checkMaxConstraints, updateSolution, printOptimalSolution, MRI

if __name__ == "__main__":
    print("Program starts")
    wn = readFile()
    print("Initial pipe cost: ", getPipeCost(wn))
    # Initial pipe diameters
    pipe_diameters = wn.query_link_attribute('diameter')
    print("Initial Pipe Diameters:")
    print(pipe_diameters)

    print("Initial simulation starting")
    results = runSimulation(wn)
    pressure = getPressure(results)
    print("Initial list of pressures:")
    print(getPressure(results))
    print("Initial maximum pressure: ", getMaxPressure(pressure))
    
    min_pressure = 0
    max_pressure = 100
    resilience_target = 10
    
    print("Initial network MRI: ", np.mean(MRI(wn, results, pressure, min_pressure)))

    # Optimization
    res = optimize_water_network(wn, min_pressure, max_pressure, resilience_target)
    
    n_evals = np.array([e.evaluator.n_eval for e in res.history])
    opt = np.array([e.opt[0].F for e in res.history])

    plt.title("Convergence")
    plt.plot(n_evals, opt, "--")
    plt.yscale("log")
    plt.show()

    printOptimalSolution(res)

    # Updating network and running simulation
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
    print(np.mean(MRI(wn, results, pressure, resilience_target)))
