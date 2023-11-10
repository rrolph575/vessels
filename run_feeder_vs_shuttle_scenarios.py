"""Primary analysis script."""

__author__ = "Becca Fuchs and Matt Shields"
__copyright__ = "Copyright 2022, National Renewable Energy Laboratory"
__maintainer__ = "Becca Fuchs"
__email__ = "rebecca.fuchs@nrel.gov"


## Using the electrical-refactor branch ##


import numpy as np
import pandas as pd
pd.set_option('display.max_columns', 10)
import os
import openpyxl

from ORBIT import ProjectManager, load_config
from ORBIT.core.library import initialize_library

#initialize_library("data")
DIR = os.path.split(__file__)[0]
LIBRARY= os.path.join(DIR, "library")
print(LIBRARY)
initialize_library(LIBRARY)

WEATHER = pd.read_csv('library/weather/example_weather.csv', parse_dates=['datetime']).set_index('datetime')
num_turbines = 50
#def run():

total_capex = {}
installation_times = {}
installation_capex = {}
capex_breakdown_per_kW = {}
names = {}

total_monopile_installation_time_if_all_steps_happened_sequentially = np.empty(8)
total_turbine_installation_time_if_all_steps_happened_sequentially = np.empty(8)

#for f in ['feeder_strategy_3kits.yaml']:
for i,f in enumerate(os.listdir('configs/')):
    config_yaml_file = os.path.join('configs/', f)
    
    if os.path.isfile(config_yaml_file):
        name, extension = os.path.splitext(f)

    config = load_config(config_yaml_file)
    
    mod_config = {
        'install_phases': ['MonopileInstallation', 'TurbineInstallation'] #https://github.com/WISDEM/ORBIT/blob/electrical-refactor/examples/Example%20-%20Dependent%20Phases.ipynb 
         }
    
    ## append mod_config to config
    run_config = ProjectManager.merge_dicts(config, mod_config)
    
    
    project = ProjectManager(run_config, library_path=LIBRARY, weather=WEATHER)
    project.run()
    
    print(project.detailed_outputs)
    project.detailed_outputs['total_monopile_mass']/num_turbines

    ## Categorize project actions
    df = pd.DataFrame(project.actions)
    action_phases = df['phase']
    print('Phases are: ' + action_phases.unique())
    # df['action'] #### look through dataframe and see if monopile installation happens always before turbine installation !!! 
    

   
    # Collect Results
    total_capex[name] = project.total_capex
    installation_times[name] = project.project_time
    installation_capex[name] = project.installation_capex
    capex_breakdown_per_kW[name] = project.capex_breakdown_per_kw

    ## write to excel file to use as input to gantt chart script
    time_str = pd.to_datetime(WEATHER.index[0])
    df.to_excel('action_logs/' + name + '_' + time_str.strftime('%m_%d_%Y') + '.xlsx', index=False)  
    
    print('\n \n Below summary is for the ' + name + ': \n \n')

    monopiles = df.loc[df["phase"]=="MonopileInstallation"]  # Filter actions table to the MonopileInstallation phase.
    monopile_duration = monopiles['time'].iloc[-1] - monopiles['time'].iloc[0] # Subtract first and last time stamp
    turbines = df.loc[df["phase"]=="TurbineInstallation"]  # Filter actions table to the TurbineInstallation phase.
    turbine_duration = turbines['time'].iloc[-1] - turbines['time'].iloc[0]
 
    total_monopile_installation_time_if_all_steps_happened_sequentially[i] = monopile_duration / (8760/12) # convert from hours to months
    total_turbine_installation_time_if_all_steps_happened_sequentially[i] = turbine_duration / (8760/12) # convert from hours to months
    
    names[i] = name


#return project

print('Monopile installation time (months): ')
print(total_monopile_installation_time_if_all_steps_happened_sequentially)  # Can we simply these variable names?
print('Turbine installation time (months): ')
print(total_turbine_installation_time_if_all_steps_happened_sequentially)





