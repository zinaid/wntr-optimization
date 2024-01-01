# WATER NETWORK RESILIENCE TOOL - OPTIMIZATION

We are using GA for performing cost optimization of a water network system.

## MATHEMATICAL FORMULATION

### Decision variables:

Decision variables are diameters $x_i$ for each pipe with index i.

The objective is to minimize the total cost of the pipes while satisfying certain constraints. Decision variables (diameter sizes) are constrained in these sizes:

$lowerBound<=x_i<=upperBound$ where lowerBound is set to 0.1 and upperBound is set to 0.762.

### Objective function:

$MIN f(x) = \sum_{i=1}^{n}{Cost(x_i)\cdot l_i}$

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

### FINAL OBJECTIVE FUNCTION

$MIN f(x) = \sum_{i=1}^{n} Cost(x_i)\cdot l_i +P_{pressure}+P_{resilience}$

## CODE STRUCTURE

networks -> holds INP files of benchmark networks (Net1, Net2, Net3).

main.py -> starting point of our program, where we define thresholds, print starting values of cost, pressures, diameters and mri. Call optimization and then print final values

network.py -> all wntr helper functions that we use, like file include, simulation run, pressure extractions, mri calculation, cost calculation, diameters update and etc.

optimization.py -> definition of optimization algorithm and proces, and definition of an objective function (uses pymoo library for optimization).
