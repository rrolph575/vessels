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
initialize_library(LIBRARY)

WEATHER = pd.read_csv('library/weather/vineyard_wind_repr_with_whales.csv', parse_dates=['datetime']).set_index('datetime')
num_turbines = 50

#for i,f in enumerate(['shuttle_foreign_infreq_close.yaml', 'shuttle_foreign_infreq_far.yaml']):

names = []

total_monopile_installation_time_months = []
total_turbine_installation_time_months = []
substructure_installation_cost = []
turbine_installation_cost = []
capex_breakdown_per_kW = []
installation_times = []
time_per_mp = []
time_per_turbine = []

# Update ORBIT defaults
wtiv_feeder_position_time = 60     # Time to position a WTIV and feeder combo at each turbine position; default=2
wtiv_only_position_time = 5        # Time to position a WTIV (with no feeder) at each turbine position; default=2
mono_drive_rate = 25               # Rate (m/hr) to drive monopiles; default=20
mono_release_time = 10             # Time to release monopile from deck
tp_release_time = 10               # Time to release transition piece from deck
tower_section_fasten_time = 2      # Fasten tower section to deck; default = 4
tower_section_release_time = 1     # Release tower section from deck; default=3
tower_section_attach_time = 2      # Attach tower sectin on site; dfault = 6
nacelle_fasten_time = 2            # Fasten nacelle section to deck; default = 4
nacelle_release_time = 1           # Release nacelle sectin on site; dfault = 3
nacelle_attach_time = 2            # Attach nacelle sectin on site; dfault = 6
blade_fasten_time = .75            # Fasten blade section to deck; default = 1.5
blade_release_time = .5            # Release blade sectin on site; dfault = 1
blade_attach_time = 1.5           # Attach bladesectin on site; dfault = 3.5


for i,f in enumerate(os.listdir('configs_renamed_limit/')):
    config_yaml_file = os.path.join('configs_renamed_limit/', f)
    
    if os.path.isfile(config_yaml_file):
        name, extension = os.path.splitext(f)

    config = load_config(config_yaml_file)
    
    mod_config = {
        # 'install_phases': ['MonopileInstallation', 'TurbineInstallation'], #https://github.com/WISDEM/ORBIT/blob/electrical-refactor/examples/Example%20-%20Dependent%20Phases.ipynb 
        'install_phases': {
            'MonopileInstallation': '05/01/2010', # Set monopile install start on May 1
            'TurbineInstallation': ('MonopileInstallation', 1)  # Index turbine installation to end of monopile installatino
            }, 
        'turbine': '15MW_generic_4sections'
        }
    
    ## append mod_config to config
    run_config = ProjectManager.merge_dicts(config, mod_config)
    
    project = ProjectManager(run_config, library_path=LIBRARY, weather=WEATHER)
    if 'feeder' in name:
        project.run(site_position_time = wtiv_feeder_position_time, 
                    mono_drive_rate = mono_drive_rate,
                    mono_release_time = mono_release_time,
                    tp_release_time = tp_release_time,
                    tower_section_fasten_time = tower_section_fasten_time, 
                    tower_section_release_time = tower_section_release_time,
                    tower_section_attach_time = tower_section_attach_time,
                    nacelle_fasten_time = nacelle_fasten_time,
                    nacelle_release_time = nacelle_release_time,
                    nacelle_attach_time = nacelle_attach_time,
                    blade_fasten_time = blade_fasten_time,
                    blade_release_time = blade_release_time,
                    blade_attach_time = blade_attach_time)
    else:
        project.run(site_position_time = wtiv_only_position_time, 
                    mono_drive_rate = mono_drive_rate,
                    mono_release_time = mono_release_time,
                    tp_release_time = tp_release_time,
                    tower_section_fasten_time = tower_section_fasten_time, 
                    tower_section_release_time = tower_section_release_time,
                    tower_section_attach_time = tower_section_attach_time,
                    nacelle_fasten_time = nacelle_fasten_time,
                    nacelle_release_time = nacelle_release_time,
                    nacelle_attach_time = nacelle_attach_time,
                    blade_fasten_time = blade_fasten_time,
                    blade_release_time = blade_release_time,
                    blade_attach_time = blade_attach_time)
    
    #print(project.detailed_outputs)
    project.detailed_outputs['total_monopile_mass']/num_turbines

    ## Categorize project actions
    df = pd.DataFrame(project.actions)
    action_phases = df['phase']
    #print('Phases are: ' + action_phases.unique())
    # df['action'] #### look through dataframe and see if monopile installation happens always before turbine installation !!! 

    # Collect Results
    installation_times += [project.project_time / (8760/12)]
    capex_breakdown_per_kW += [project.capex_breakdown_per_kw]
    substructure_installation_cost += [project.capex_breakdown_per_kw['Substructure Installation']]
    turbine_installation_cost += [project.capex_breakdown_per_kw['Turbine Installation']]

    ## write to excel file to use as input to gantt chart script
    time_str = pd.to_datetime(WEATHER.index[0])
    df.to_excel('action_logs/' + name + '_' + time_str.strftime('%m_%d_%Y') + '.xlsx', index=False) 
    df.to_csv('action_logs_csv/' + name + '_' + time_str.strftime('%m_%d_%Y') + '.csv', index=False)
    
    #print('\n \n Below summary is for the ' + name + ': \n \n')

    monopiles = df.loc[df["phase"]=="MonopileInstallation"]  # Filter actions table to the MonopileInstallation phase.
    monopile_duration = monopiles['time'].iloc[-1] - monopiles['time'].iloc[0] # Subtract first and last time stamp. Time is in hours
    turbines = df.loc[df["phase"]=="TurbineInstallation"]  # Filter actions table to the TurbineInstallation phase.
    turbine_duration = turbines['time'].iloc[-1] - turbines['time'].iloc[0]

    total_monopile_installation_time_months += [monopile_duration / (8760/12)] # convert from hours to months
    total_turbine_installation_time_months += [turbine_duration / (8760/12)] # convert from hours to months

    time_per_mp += [(monopile_duration / 24) / num_turbines]
    time_per_turbine += [(turbine_duration / 24) / num_turbines]

    
    names.append(name)
    
    # print(name)
    # print(df.loc[df['action']=='Transit'].count())
    
    transit_df = df.loc[df['action']=='Transit']
    # print('Total transit time for monopile installation '+ name + ':')
    # print(transit_df['duration'].sum())
    
#return project

df_install_times_and_cost = pd.DataFrame(data={'Scenario_name': names, 
                                            'Total project installation time': installation_times,
                                            'Monopile_install_time_months': total_monopile_installation_time_months, 
                                            'Turbine_install_time_months': total_turbine_installation_time_months, 
                                            'Substructure_install_cost': substructure_installation_cost, 
                                            'Turbine_install_cost': turbine_installation_cost,
                                            'Average time per monopile, days': time_per_mp,
                                            'Average time per turbine, days': time_per_turbine,
                                            'Total install cost': np.array(substructure_installation_cost) + np.array(turbine_installation_cost)})

df_install_times_and_cost = df_install_times_and_cost.set_index('Scenario_name')

                                
print(df_install_times_and_cost)
df_install_times_and_cost.to_csv('df_install_times_and_cost.csv')


fig, ax = plt.subplots()
df_install_times_and_cost[['Substructure_install_cost', 'Turbine_install_cost', 'Total install cost']].plot(kind='barh', ax = fig.gca())
plt.legend(loc='center left', bbox_to_anchor = (0.75, 0.22))
ax.set_xlabel('Cost ($/kW)')
ax.set_ylabel(' ')
ax.set_xlim([0,440])
ax.invert_yaxis()
fig.savefig('install_cost_comparison.png', bbox_inches='tight')


fig, ax = plt.subplots()
df_install_times_and_cost[['Monopile_install_time_months', 'Turbine_install_time_months', 'Total project installation time']].plot(kind='barh', ax = fig.gca())
ax.set_xlabel('Installation Time (months)')
ax.set_ylabel(' ')
plt.legend(loc='center left', bbox_to_anchor = (0.75, 0.22))
ax.set_xlim([0,22])
ax.invert_yaxis()
fig.savefig('install_time_comparison.png', bbox_inches='tight')


# fig, ax = plt.subplots()
# total_install_capex = df_install_times_and_cost[['Turbine_install_cost', 'Substructure_install_cost']].sum(axis=1)
# total_install_capex.plot(kind='barh', ax=fig.gca())
# ax.set_xlabel('Turbine + Substructure Installation Cost ($/kW)')
# ax.set_xlim([0,425])
# ax.invert_yaxis()
# ax.set_ylabel(' ')
# fig.savefig('turbine_plus_substructure_install_cost.png', bbox_inches='tight')








