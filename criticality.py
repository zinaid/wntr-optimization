import numpy as np
import wntr
import copy

def runCriticality(inp):
    wn = wntr.network.WaterNetworkModel(inp)
    wn_copy = copy.deepcopy(wn)
    start_time = 2*3600 # 2 hours
    break_duration = 12*3600 # 12 hours
    total_duration = start_time + break_duration # 14 hours
    minimum_pressure = 3.52
    required_pressure = 14.06 
    min_pipe_diam = 0 

    AED = wntr.metrics.average_expected_demand(wn)
    nzd_junct = AED[AED > 0].index
    wn.options.hydraulic.demand_model = 'PDD'
    wn.options.time.duration = total_duration
    wn.options.hydraulic.minimum_pressure = minimum_pressure
    wn.options.hydraulic.required_pressure = required_pressure
    wn.options.time.report_timestep = 3600 
    wn.options.time.hydraulic_timestep = 3600 
    sim = wntr.sim.WNTRSimulator(wn)
    results = sim.run_sim()
    pressure = results.node['pressure'].loc[start_time::, nzd_junct]
    normal_pressure_below_pmin = pressure.columns[(pressure <minimum_pressure).any()] 

    pipes_of_interest = wn.query_link_attribute('diameter',np.greater_equal, min_pipe_diam)

    analysis_results = {}
    for pipe_name in pipes_of_interest.index:
        wn = wntr.network.WaterNetworkModel(inp)
        wn.options.hydraulic.demand_model = 'PDD'
        wn.options.time.duration = total_duration
        wn.options.hydraulic.minimum_pressure = minimum_pressure
        wn.options.hydraulic.required_pressure = required_pressure
        wn.options.time.report_timestep = 3600 
        wn.options.time.hydraulic_timestep = 3600 
        pipe = wn.get_link(pipe_name)
        #Before adding the control
        #initial_pipe_status = wn.get_link(pipe_name).status
        #print("Initial Pipe Status:", initial_pipe_status)
        act = wntr.network.controls.ControlAction(pipe, 'status', 0)
        cond = wntr.network.controls.SimTimeCondition(wn, 'Above',start_time)
        ctrl = wntr.network.controls.Control(cond, act)
        wn.add_control('close pipe' + pipe_name, ctrl)
        try:
            sim = wntr.sim.WNTRSimulator(wn)
            sim_results = sim.run_sim()
            sim_pressure = sim_results.node['pressure'].loc[start_time::,nzd_junct]
            sim_pressure_below_pmin = sim_pressure.columns[(sim_pressure< minimum_pressure).any()]
            impacted_junctions = set(sim_pressure_below_pmin) - set(normal_pressure_below_pmin)
            # After adding the control
            #pipe_status_after_control = wn.get_link(pipe_name).status
            #print("Pipe Status After Control:", pipe_status_after_control)
        except Exception as e:
            impacted_junctions = None
            print(pipe_name, 'Failed:', e)
        finally:
            analysis_results[pipe_name] = impacted_junctions 
    num_junctions_impacted = {}
    for pipe_name, impacted_junctions in analysis_results.items():
        if impacted_junctions is not None: 
            num_junctions_impacted[pipe_name] = len(impacted_junctions)

    #print(num_junctions_impacted)
    total_sum = sum(num_junctions_impacted.values())

    #number_of_junctions_impacted = dict([(k,len(v)) for k,v in impacted_junctions.items()])
    #total = sum(num_junctions_impacted.values().sum())

    print(total_sum)
    wntr.graphics.plot_network(wn, link_attribute=num_junctions_impacted,
                            node_size=0,link_width=2,link_range=[0,10],
                            link_colorbar_label='JunctionsImpacted',title='Number of junctions impacted by eachpipe closure ('+str(total_sum)+')')
    
    return total_sum
