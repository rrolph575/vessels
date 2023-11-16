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

WEATHER = pd.read_csv('library/weather/example_weather.csv', parse_dates=['datetime']).set_index('datetime')
num_turbines = 50

names = []

total_monopile_installation_time_months = []
total_turbine_installation_time_months = []
substructure_installation_cost = []
turbine_installation_cost = []
capex_breakdown_per_kW = []
installation_times = []

# Select baseline config and config to sweep over
baseline_config = 'configs/shuttle_amer_freq.yaml'
sweep_config = 'configs/feeder_freq.yaml'

# Define parameter sweep
site_position_vals = [40, 35, 30, 25, 20, 15, 10, 5] # site_position_time

# Define method to run ORBIT and output appropriate variables
def orbit_run(config, param_val=None, LIBRARY=LIBRARY, WEATHER=WEATHER):
    
    config = load_config(config)
    
    mod_config = {
        'install_phases': {
            'MonopileInstallation': '05/01/2010', 
            'TurbineInstallation': ('MonopileInstallation', 1)
            }, #https://github.com/WISDEM/ORBIT/blob/electrical-refactor/examples/Example%20-%20Dependent%20Phases.ipynb 
        'turbine': '15MW_generic_4sections'
        }
    
    ## append mod_config to config
    run_config = ProjectManager.merge_dicts(config, mod_config)

    project = ProjectManager(run_config, library_path=LIBRARY, weather=WEATHER)
    if param_val == None:
        project.run()
    else:
        project.run(site_position_time = param_val)

    # Collect Results
    installation_times = project.project_time / (8760/12)
    capex_breakdown_per_kW = project.capex_breakdown_per_kw
    substructure_installation_cost = project.capex_breakdown_per_kw['Substructure Installation']
    turbine_installation_cost = project.capex_breakdown_per_kw['Turbine Installation']

    df = pd.DataFrame(project.actions)
    monopiles = df.loc[df["phase"]=="MonopileInstallation"]  # Filter actions table to the MonopileInstallation phase.
    monopile_duration = monopiles['time'].iloc[-1] - monopiles['time'].iloc[0] # Subtract first and last time stamp. Time is in hours
    turbines = df.loc[df["phase"]=="TurbineInstallation"]  # Filter actions table to the TurbineInstallation phase.
    turbine_duration = turbines['time'].iloc[-1] - turbines['time'].iloc[0]

    total_monopile_installation_time_months = monopile_duration / (8760/12)  # convert from hours to months
    total_turbine_installation_time_months = turbine_duration / (8760/12)  # convert from hours to months
    
    return installation_times, total_monopile_installation_time_months, total_turbine_installation_time_months

# Run baseline
base_install_time, base_mp_time, base_turb_time = orbit_run(baseline_config)

# Loop over parameter values
install_time = []
mp_time = []
turb_time = []

for vi in site_position_vals:
    i,m,t = orbit_run(sweep_config, param_val=vi)
    install_time += [i]
    mp_time += [m]
    turb_time += [t]  

fig,(ax1,ax2,ax3) = plt.subplots(1,3, figsize=(15,5))
ax1.axhline(y=base_install_time, linestyle='--', label='Shuttle')
ax1.plot(site_position_vals, install_time, label='Feeder')
ax1.set_ylim([0,20])
ax1.set_ylabel('Project installation time, months')
ax1.set_xlabel('Site position time, hours')
ax1.legend()

ax2.axhline(y=base_mp_time, linestyle='--', label='Shuttle')
ax2.plot(site_position_vals, mp_time, label='Feeder')
ax2.set_ylim([0,20])
ax2.set_ylabel('Monopile installation time, months')
ax2.set_xlabel('Site position time, hours')
ax2.legend()

ax3.axhline(y=base_turb_time, linestyle='--', label='Shuttle')
ax3.plot(site_position_vals, turb_time, label='Feeder')
ax3.set_ylim([0,20])
ax3.set_ylabel('Turbine installation time, months')
ax3.set_xlabel('Site position time, hours')
ax3.legend()

fig.savefig('figures/site_position_param_sweep.png', bbox_inches='tight')

