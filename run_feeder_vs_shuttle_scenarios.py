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



    ### Select an installation step
    phase = 'MonopileInstallation'
    df = pd.DataFrame(project.actions)
    df.phase.unique()
    sub = df.loc[df['phase']==phase]
    # Number of times for every action
    #sub.groupby('action').count()['time']

    # display action and duration
    sub[['action', 'duration']].head(30)
    # groupby a selected action to make it more reeadable and sum it all together
    # .... but some of these are happening at the same time... but if there is only one AHV then it should happen relatively sequentially.. 
    total_monopile_installation_time_if_all_steps_happened_sequentially[i] = sub.groupby('action').sum()['duration'].sum()


    ### to take a look at the vessels
    #df.agent.unique()
    # to take a look at the vessels used in the substructure assembly and tow out:
    #sub[['action','agent','duration']]


    ### Select an installation step
    phase = 'TurbineInstallation'
    df = pd.DataFrame(project.actions)
    df.phase.unique()
    sub = df.loc[df['phase']==phase]
    # Number of times for every action
    #sub.groupby('action').count()['time']

    # display action and duration
    sub[['action', 'duration']].head(30)
    # groupby a selected action to make it more reeadable and sum it all together
    # .... but some of these are happening at the same time... but if there is only one AHV then it should happen relatively sequentially.. 
    total_turbine_installation_time_if_all_steps_happened_sequentially[i] = sub.groupby('action').sum()['duration'].sum()

    print('NOTE:::: you cannot sum all of these and get total project time becuase some of these steps could be happening at the same time, especially if you have multiple vessels.')
    
    names[i] = name


#return project








