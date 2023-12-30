# WATER NETWORK RESILIENCE TOOL - OPTIMIZATION

We are using GA for performing cost optimization of a water network system.

## MATHEMATICAL FORMULATION

### Decision variables:

Decision variables are diameters $x_i$ for each pipe with index i.

The objective is to minimize the total cost of the pipes while satisfying certain constraints. Decision variables (diameter sizes) are constrained in these sizes:

$lowerBound<=x_i<=upperBound$ where lowerBound is set to 0.1 and upperBound is set to 0.762.

### Objective function:

$MIN f(x) = \sum_{i=1}^{n} Cost(x_i)\cdot l_i$

where $Cost(x_i)$ represents a cost of each pipe, $l_i$ represents a length of a pipe. Pipe cost is directly connected to a diametar size.

Each diemeter size has a specific cost. Cost is given in the Table 1.

### Constraints:

#### Pressure constraint

We also want to maintain junction pressure levels above and below specific thresholds. 

$P_{low}<=P_{node}<=P_{high}$.

This is maintained using a penalty function on a minimization objective.

$P_{low} = \sum_{node}max(0, P_{min}-P_{node})$

$P_{high} = \sum_{node}max(0, P_{node}-P_{max})$

$P_{pressure}=P_{low}+P_{high}$.

#### Resilience constraint

Besides pressure constraints we introduce a resilience constraint where we want to maintain overall resilience of a system above a resilience threshold.

$MRI_{current}>=MRI_{target}$

We are interested in a Modified Resilience Index (MRI). The modified resilience index is the total surplus power available at demand junctions as a percentage of the total minimum required power at demand junctions. The metric can be computed as a timeseries for each junction or as a system average timeseries. We use mean value of a total system average timesires and maintain the resilience metric with another penalty constraint.

$MRI =\frac{∑_{j=1}^N q_j (ha_j − hr_j)}{∑_{j=1}^N q_jhr_j}\times 100$.

Penalty resilience is calculated as:

$P_{resilience}=max(0, MRI_{target}-MRI_{current})$

### FINAL OBJECTIVE FUNCTION

$MIN f(x) = \sum_{i=1}^{n} Cost(x_i)\cdot l_i +P_{pressure}+P_{resilience}$

## CODE STRUCTURE

networks -> holds INP files of benchmark networks (Net1, Net2, Net3).

main.py -> starting point of our program, where we define thresholds, print starting values of cost, pressures, diameters and mri. Call optimization and then print final values

network.py -> all wntr helper functions that we use, like file include, simulation run, pressure extractions, mri calculation, cost calculation, diameters update and etc.

optimization.py -> definition of optimization algorithm and proces, and definition of an objective function (uses pymoo library for optimization).
