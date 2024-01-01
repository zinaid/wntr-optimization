# WATER NETWORK RESILIENCE TOOL - OPTIMIZATION

We are performing cost optimization of a water network system using water network resilience tool (WNTR).

## MATHEMATICAL FORMULATION

### Decision variables:

Decision variables are diameters $x_i$ for each pipe with index $i$.

The objective is to minimize the total cost of the pipes while satisfying certain constraints. Decision variables (diameter sizes) are constrained in these boundaries:

$lowerBound<=x_i<=upperBound$ where lowerBound is set to 0.1 and upperBound is set to 0.762.

### Objective function:

$$MIN f(x) = \sum_{i=1}^{n}{Cost(x_i)\cdot l_i}$$

where $Cost(x_i)$ represents a cost of each pipe, $l_i$ represents a length of a pipe. Pipe cost is directly connected to a diametar size.

Each diemeter size has a specific cost. Cost is given in the Table 1.

<table border="1">
  <tr>
    <th>Diameter (in)</th>
    <th>Diameter (m)</th>
    <th>Annual Cost ($/m/yr)</th>
  </tr>
  <tr>
    <td>4</td>
    <td>0.102</td>
    <td>8.31</td>
  </tr>
  <tr>
    <td>6</td>
    <td>0.152</td>
    <td>10.10</td>
  </tr>
  <tr>
    <td>8</td>
    <td>0.203</td>
    <td>12.10</td>
  </tr>
  <tr>
    <td>10</td>
    <td>0.254</td>
    <td>12.96</td>
  </tr>
  <tr>
    <td>12</td>
    <td>0.305</td>
    <td>15.22</td>
  </tr>
  <tr>
    <td>14</td>
    <td>0.356</td>
    <td>16.62</td>
  </tr>
  <tr>
    <td>16</td>
    <td>0.406</td>
    <td>19.41</td>
  </tr>
  <tr>
    <td>18</td>
    <td>0.457</td>
    <td>22.20</td>
  </tr>
  <tr>
    <td>20</td>
    <td>0.508</td>
    <td>24.66</td>
  </tr>
  <tr>
    <td>24</td>
    <td>0.610</td>
    <td>35.69</td>
  </tr>
  <tr>
    <td>28</td>
    <td>0.711</td>
    <td>40.08</td>
  </tr>
  <tr>
    <td>30</td>
    <td>0.762</td>
    <td>42.60</td>
  </tr>
</table>

### Constraints:

We have implicit and explicit constraints.

<b>Implicit system constraints:</b> Conservations of mass and energy are maintained through EPANET simulator and because of that they are called implicit constraints

<b>Explicit constraints</b>

#### Pressure constraint



We also want to maintain junction pressure levels above and below specific thresholds. 

$P_{low}<=P_{node}<=P_{high}$.

This is maintained using a penalty function on a minimization objective.

$P_{low} = \sum_{node} max(0, P_{min}-P_{node})$

$P_{high} = \sum_{node} max(0, P_{node}-P_{max})$

$P_{pressure}=P_{low}+P_{high}$.

#### Resilience constraint

Besides pressure constraints we introduce a resilience constraint where we want to maintain overall resilience of a system above a resilience threshold.

$MRI_{current}>=MRI_{target}$

We are interested in a Modified Resilience Index (MRI). The modified resilience index is the total surplus power available at demand junctions as a percentage of the total minimum required power at demand junctions. The metric can be computed as a timeseries for each junction or as a system average timeseries. We use mean value of a total system average timesires and maintain the resilience metric with another penalty constraint.

$MRI =\frac{∑_{j=1}^N q_j (ha_j − hr_j)}{∑_{j=1}^N q_jhr_j}\times 100$.

Penalty resilience is calculated as:

$P_{resilience}=max(0, MRI_{target}-MRI_{current})$

#### Pipe criticality constraint

We perform criticality analysis by doing <b>n+1</b> simulations where we turn off one pipe at a time and calculate number of impacted junctions by that closure. Finally we find a total number of impacted junctions and create a penalty function for our cost function. We set a threshold for junctions impacted as maxJunctions, and simJunctions as a total number of impacted junctions. We want to minimize the number of impacted junctions affected through pipe criticality analysis.

$P_{junction} = max(0, maxJunctions - simJunctions)$

### FINAL OBJECTIVE FUNCTION

$$MIN f(x) = \sum_{i=1}^{n} Cost(x_i)\cdot l_i +P_{pressure}+P_{resilience}+P_{junction}$$

## CODE STRUCTURE

networks -> holds INP files of benchmark networks (Net1, Net2, Net3).

main.py -> starting point of our program, where we define thresholds, print starting values of cost, pressures, diameters and mri. Call optimization and then print final values

network.py -> all wntr helper functions that we use, like file include, simulation run, pressure extractions, mri calculation, cost calculation, diameters update and etc.

optimization.py -> definition of optimization algorithm and proces, and definition of an objective function (uses pymoo library for optimization).

## EXAMPLE 1 - NET3 without pipe criticality analyis

Cost optimization of Net3 using GA with population number 40 and 200 iterations. 

$$MIN f(x) = \sum_{i=1}^{n} Cost(x_i)\cdot l_i +P_{pressure}+P_{resilience}$$

n = 100.

### Visualization of network

### Initial costs and descriptions

Initial pipe cost:  1597669.9039680003

Maximum pressure:  93.34697

Minimum pressure:  -0.6586714

Initial MRI:  6.677407434255322

### Thresholds

Minimum pressure: 0

Maximum pressure: 94

MRI: 6

### Convergence plot

### Final results and constraint checks

## EXAMPLE 2 - NET1 with pipe criticality analysis

Cost optimization of Net1 with GA and population size = 20 and number of iterations = 80.

$$MIN f(x) = \sum_{i=1}^{n} Cost(x_i)\cdot l_i +P_{pressure}+P_{resilience}+P_{junction}$$

### Visualization of network

We have not included first pipe (Pipe number 10) in our analysis because that is the critical pipe that when turned affects all other pipes (Start of the network).

### Initial costs and descriptions

Initial pipe cost:  <b>282367.08576000005</b>

Initial Pipe Diameters:

10     0.4572

11     0.3556

12     0.2540

21     0.2540

22     0.3048

31     0.1524

110    0.4572

111    0.2540

112    0.3048

113    0.2032

121    0.2032

122    0.1524

Maximum pressure:  94.18104

Minimum pressure:  0.0

Initial junction impact: 0

Initial MRI:  0.3748347853772069

### Thresholds: 

Minimum pressure: 3.0

Maximum pressure: 100

Resilience target: 0.35

Number of impacted junctions: 0

### Convergence plot:

### Final results and constraints check:








