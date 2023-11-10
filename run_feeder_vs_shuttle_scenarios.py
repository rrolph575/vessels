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
import matplotlib.pyplot as plt

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
names = []

total_monopile_installation_time_months = np.empty(8)
total_turbine_installation_time_months = np.empty(8)
substructure_installation_cost = np.empty(8)
turbine_installation_cost = np.empty(8)

#for i,f in enumerate(['shuttle_foreign_infreq_close.yaml', 'shuttle_foreign_infreq_far.yaml']):
for i,f in enumerate(os.listdir('configs/')):
    config_yaml_file = os.path.join('configs/', f)
    
    if os.path.isfile(config_yaml_file):
        name, extension = os.path.splitext(f)

    config = load_config(config_yaml_file)
    
    mod_config = {
        'install_phases': ['MonopileInstallation', 'TurbineInstallation'], #https://github.com/WISDEM/ORBIT/blob/electrical-refactor/examples/Example%20-%20Dependent%20Phases.ipynb 
        'turbine': '15MW_generic_4sections'
         }
    
    ## append mod_config to config
    run_config = ProjectManager.merge_dicts(config, mod_config)
    
    
    project = ProjectManager(run_config, library_path=LIBRARY, weather=WEATHER)
    project.run()
    
    #print(project.detailed_outputs)
    project.detailed_outputs['total_monopile_mass']/num_turbines

    ## Categorize project actions
    df = pd.DataFrame(project.actions)
    action_phases = df['phase']
    #print('Phases are: ' + action_phases.unique())
    # df['action'] #### look through dataframe and see if monopile installation happens always before turbine installation !!! 
    

   
    # Collect Results
    total_capex[name] = project.total_capex
    installation_times[name] = project.project_time
    installation_capex[name] = project.installation_capex
    capex_breakdown_per_kW[name] = project.capex_breakdown_per_kw
    substructure_installation_cost[i] = capex_breakdown_per_kW[name].get('Substructure Installation')
    turbine_installation_cost[i] = capex_breakdown_per_kW[name].get('Turbine Installation')

    ## write to excel file to use as input to gantt chart script
    time_str = pd.to_datetime(WEATHER.index[0])
    df.to_excel('action_logs/' + name + '_' + time_str.strftime('%m_%d_%Y') + '.xlsx', index=False)  
    
    #print('\n \n Below summary is for the ' + name + ': \n \n')

    monopiles = df.loc[df["phase"]=="MonopileInstallation"]  # Filter actions table to the MonopileInstallation phase.
    monopile_duration = monopiles['time'].iloc[-1] - monopiles['time'].iloc[0] # Subtract first and last time stamp. Time is in hours
    turbines = df.loc[df["phase"]=="TurbineInstallation"]  # Filter actions table to the TurbineInstallation phase.
    turbine_duration = turbines['time'].iloc[-1] - turbines['time'].iloc[0]
 
    total_monopile_installation_time_months[i] = monopile_duration / (8760/12) # convert from hours to months
    total_turbine_installation_time_months[i] = turbine_duration / (8760/12) # convert from hours to months
    
    names.append(name)
    
    print(name)
    print(df.loc[df['action']=='Transit'].count())
    
    transit_df = df.loc[df['action']=='Transit']
    print('Total transit time for monopile installation '+ name + ':')
    print(transit_df['duration'].sum())
    
#return project

df_install_times_and_cost = pd.DataFrame(data={'Scenario_name': names, 'Monopile_install_time_months': total_monopile_installation_time_months, 'Turbine_install_time_months': total_turbine_installation_time_months, 'Substructure_install_cost': substructure_installation_cost, 'Turbine_install_cost': turbine_installation_cost})

df_install_times_and_cost = df_install_times_and_cost.set_index('Scenario_name')

                                
print(df_install_times_and_cost)
df_install_times_and_cost.to_csv('df_install_times_and_cost.csv')


fig = plt.figure()
df_install_times_and_cost[['Turbine_install_cost', 'Substructure_install_cost']].plot(kind='bar', ax = fig.gca())
plt.legend(loc='center left', bbox_to_anchor = (1.0, 0.5))
fig.savefig('install_cost_comparison.png', bbox_inches='tight')


fig = plt.figure()
df_install_times_and_cost[['Turbine_install_time_months', 'Monopile_install_time_months']].plot(kind='bar', ax = fig.gca())
plt.legend(loc='center left', bbox_to_anchor = (1.0, 0.5))
fig.savefig('install_time_comparison.png', bbox_inches='tight')









