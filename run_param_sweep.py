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
baseline_config = 'configs_renamed_limit/MP6shuttle060km_WTG6shuttle060km.yaml' # shuttle
sweep_config = 'configs_renamed_limit/MP6feeder_060km_WTG6feeder_060km.yaml' # feeder
# sweep_config = 'configs/feeder_freq.yaml'

# Define parameter sweep
wtiv_feeder_position_time_vals = [40, 35, 30, 25, 20, 15, 10, 5] # site_position_time

# Update ORBIT defaults
wtiv_only_position_time = 5        # Time to position a WTIV (wiht no feeder) at each turbine position; default=2
mono_drive_rate = 25                # Rate (m/hr) to drive monopiles; default=20
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

# Define method to run ORBIT and output appropriate variables
def orbit_run(config, param_val=None, LIBRARY=LIBRARY, WEATHER=WEATHER):
    
    config = load_config(config)
    
    mod_config = {
        'install_phases': {
            'MonopileInstallation': '05/01/2010', # Set monopile install start on May 1
            'TurbineInstallation': ('MonopileInstallation', 1)  # Index turbine installation to end of monopile installatino
            }, #https://github.com/WISDEM/ORBIT/blob/electrical-refactor/examples/Example%20-%20Dependent%20Phases.ipynb 
        'turbine': '15MW_generic_4sections'
        }
    
    ## append mod_config to config
    run_config = ProjectManager.merge_dicts(config, mod_config)

    project = ProjectManager(run_config, library_path=LIBRARY, weather=WEATHER)

    if param_val == None:
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
    else:
        project.run(site_position_time = param_val, 
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

    # Collect Results
    installation_times = project.project_time / (8760/12)

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

for vi in wtiv_feeder_position_time_vals:
    i,m,t = orbit_run(sweep_config, param_val=vi)
    install_time += [i]
    mp_time += [m]
    turb_time += [t]  

fig,(ax1,ax2,ax3) = plt.subplots(1,3, figsize=(15,5))
ax1.axhline(y=base_install_time, linestyle='--', label='Shuttle')
ax1.plot(wtiv_feeder_position_time_vals, install_time, label='Feeder')
ax1.set_ylim([0,20])
ax1.set_ylabel('Project installation time, months')
ax1.set_xlabel('Site position time, hours')
ax1.legend()

ax2.axhline(y=base_mp_time, linestyle='--', label='Shuttle')
ax2.plot(wtiv_feeder_position_time_vals, mp_time, label='Feeder')
ax2.set_ylim([0,20])
ax2.set_ylabel('Monopile installation time, months')
ax2.set_xlabel('Site position time, hours')
ax2.legend()

ax3.axhline(y=base_turb_time, linestyle='--', label='Shuttle')
ax3.plot(wtiv_feeder_position_time_vals, turb_time, label='Feeder')
ax3.set_ylim([0,20])
ax3.set_ylabel('Turbine installation time, months')
ax3.set_xlabel('Site position time, hours')
ax3.legend()

fig.savefig('figures/site_position_param_sweep.png', bbox_inches='tight')

