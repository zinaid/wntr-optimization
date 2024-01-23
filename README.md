# WATER NETWORK RESILIENCE TOOL - OPTIMIZATION

We are performing cost optimization of a water network system using water network resilience tool (WNTR).

## MATHEMATICAL FORMULATION

### Decision variables:

Decision variables are diameters $x_i$ for each pipe with index $i$.

The objective is to minimize the total cost of the pipes while satisfying certain constraints. We also implement removal of some pipes from the network. Those pipes that are redundant are removed from the network, while maintaing the desired constraints.

To achieve this we set diameter sizes in these boundaries: 

$$lowerBound<=x_i<= upperBound $$ 

The variable ```upperBound``` is set according to the used network, but the lower bound is set to 0 (WITH THIS WE ACHIEVE TOTAL REMOVAL OF SOME PIPES). We remove those pipes whose diameter is smaller than ```0.1```:

$$x_i <= x_{min}$$

where ```X_min = 0.1```.

## OBJECTIVE FUNCTION

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

Table 1 is visualized in Figure 1.

<img src="images/diameterCost.png" />

## DECISION VARIABLES

Decision variables are diameters $x_i$ for each pipe with index $i$.

The objective is to minimize the total cost of the pipes while satisfying certain constraints. We also implement the removal of some pipes from the network. Those pipes that are redundant are removed from the network while maintaining the desired constraints.

To achieve this we set diameter sizes in these boundaries:

$$lowerBound<=x_i<= upperBound $$ 

The variable ```upperBound``` is set according to the used network, but the lower bound is set to ```0``` (WITH THIS WE ACHIEVE TOTAL REMOVAL OF SOME PIPES). We remove those pipes whose diameter is smaller than ```0.1```:

$$x_i <= X_{min}$$

where $X_{min} = 0.1$.

## CONSTRAINTS

We have implicit and explicit constraints.

### Implicit constraints:

Implicit system constraints are Conservation of mass and Conservation of energy. They are maintained through the EPANET simulator and because of that they are called implicit constraints.

### Explicit constraints:

Explicit constraints are given and handled by us through our optimization process. The explicit constraints that we use are:

* Pressure demand constraint
* Pipe criticality constraint (Network resilience)
* Network connectivity

These constraints are handled by penalizing the objective function.

If there are some isolated nodes the network doesn't function properly, so we also introduce a <b>Network connectivity penalty</b> for penalizing those solutions that lead to isolated nodes. The network connectivity penalty is set to a high value so that our simulation quickly abandons such solutions.

### PRESSURE CONSTRAINT:

We want to maintain junction pressure levels above minimum pressure for that junction. To obtain minimum pressures we run a simulation before optimization and obtain minimum junction pressures for each node. 

$P_{node} >= P_{min}$.

This is maintained using a penalty function on a minimization objective.

$P_{pressure} = \sum_{node} max(0, P_{min}-P_{node})$

### PIPE CRITICALITY CONSTRAINT:

We perform criticality analysis by doing <b>n+1</b> simulations where we turn off one pipe at a time and calculate a number of impacted junctions by that closure. Finally, we find the total number of impacted junctions and create a penalty function for our cost function. We set a threshold for junctions impacted as maxJunctions, and simJunctions as a total number of impacted junctions. We want to minimize the number of impacted junctions affected through pipe criticality analysis.

$P_{junction} = max(0, maxJunctions - simJunctions)$

Closing some pipes can lead to incorrect operation of the simulation (wntr simulation cannot converge, consumers' needs cannot be met and because of that simulation automatically opens some pipes even though we have previously closed them). We solved that problem with try catch blocks on simulation calls, which catch errors and warnings for each simulation and penalize incorrect simulations with a high penalty.

### FINAL OBJECTIVE FUNCTION

$$MIN f(x) = \sum_{i=1}^{n} Cost(x_i)\cdot l_i +P_{pressure}+P_{resilience}+P_{junction}$$

## CODE STRUCTURE

networks -> holds INP files of networks.

main.py -> starting point of our program, where we define thresholds, print starting values of cost, pressures, diameters and call criticality analysis. Call optimization and then print final values, draw network and perform final criticality analysis.

network.py -> all wntr helper functions that we use, like file include, simulation run, pressure extractions, cost calculation, diameters update, pipe criticality, plotting and etc.

optimization.py -> definition of optimization algorithm and proces, and definition of an objective function (uses pymoo library for optimization).

## EXAMPLES

### NETWORK 1 - MODIFIED 19 PIPES NETWORK

Cost and layout optimization of a 19 pipes network (https://uknowledge.uky.edu/wdst_systems/7/).

The network with it's pressures is shown in Figure 2.

<img src="images/19Pipes.png">

Initial cost is: <b></b>

We want to minimize the cost, remove redundant pipes while maintaining pressures from the Figure 2.

```
```

Convergence plot is shown in Figure 3.

The final network is shown in Figure 4.

<img src="images/19Pipes.png">

Final cost is: <b></b>

Running our network in Epanet2.2 we get no errors.

<img src="images/19Pipes.png">

### NETWORK 2 - 14 PIPES NETWORK