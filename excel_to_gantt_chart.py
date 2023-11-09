# -*- coding: utf-8 -*-
"""
Created on Tue Oct  3 13:52:02 2023

@author: Ashesh Sharma, edited by R. Fuchs

This reads in the action logs (saved as xlsx files) that are produced in run_feeder_vs_shuttle_scenarios.py and turns it into a gantt chart.

"""


import datetime as dt
import matplotlib.pyplot as plt
# plt.rcParams["font.family"] = "Times New Roman"
font = {'family' : 'Arial',
        'size'   : 10}
plt.rc('font', **font)
import numpy as np
import pandas as pd
import textwrap



# problem parameters
strategy = 'feeder_strategy_6kits'  # 'feeder_strategy_3(6)kits', 'shuttle_strategy_foreign(american)WTIV_3(6)kits'
start_date  = '10/21/2009'
start_date = pd.to_datetime(start_date)
plot_based_on = 'agent'

# read excel sheet and drop irrelevant stuff
df = pd.read_excel(strategy + '_' + start_date.strftime('%m_%d_%Y') + '.xlsx')
df = df.drop('cost_multiplier', axis=1)
df = df.drop('level', axis=1)
#df = df.drop('phase_name', axis=1)

# sort based on time
df = df.sort_values('time', ascending=True)
df = df.reset_index(drop = True)

# create a new column converting time to date-time
start_date_list = []
end_date_list = []
for idx in range(0, df.shape[0]):
    end_date_list.append(start_date + pd.DateOffset(hours=df.loc[idx].at['time'])) #specify the number of hours and add it to start_date
    start_date_list.append(start_date + pd.DateOffset(hours=df.loc[idx].at['time']) \
                           - pd.DateOffset(hours=df.loc[idx].at['duration'])) #specify the number of hours and add it to start_date

# add dates column to the data frame 
df.insert(loc = 5, column = 'start_date', value = start_date_list)
df.insert(loc = 6, column = 'end_date', value = end_date_list)

# create additional data for gantt charts
df['days_to_start'] = (df['start_date'] - df['start_date'].min()).dt.days
df['days_to_end'] = (df['end_date'] - df['start_date'].min()).dt.days
df['phase_duration'] = df['days_to_end'] - df['days_to_start'] + 1



################################# Change the name of Agents / actions #################################

if 'WTIV' in strategy:
    for idx in range(0, df.shape[0]):
        if df.at[idx, 'phase'] == 'MonopileInstallation' and df.at[idx, 'action'] != 'Delay':
            df.at[idx, 'agent'] = 'WTIV for Monopile Installation'
        elif df.at[idx, 'phase'] == 'TurbineInstallation' and df.at[idx, 'action'] != 'Delay':
            df.at[idx, 'agent'] = 'WTIV for Turbine Installation'
        elif df.at[idx, 'action'] == 'Delay':
            df.at[idx, 'agent'] = 'Delay: Weather'

if 'feeder' in strategy:
    for idx in range(0, df.shape[0]):
        # Monopile installation
        if df.at[idx, 'phase'] == 'MonopileInstallation' and df.at[idx, 'action'] != 'Delay' and df.at[idx, 'agent'] == 'WTIV':
            df.at[idx, 'agent'] = 'WTIV for Monopile Installation'
        elif df.at[idx, 'phase'] == 'MonopileInstallation' and df.at[idx, 'action'] != 'Delay' and 'Feeder' in df.at[idx, 'agent']:
            df.at[idx, 'agent'] = 'Feeder for Monopile Installation'
        # Turbine Installation
        elif df.at[idx, 'phase'] == 'TurbineInstallation' and df.at[idx, 'action'] != 'Delay' and df.at[idx, 'agent'] == 'WTIV':
            df.at[idx, 'agent'] = 'WTIV for Turbine Installation'
        elif df.at[idx, 'phase'] == 'TurbineInstallation' and df.at[idx, 'action'] != 'Delay' and 'Feeder' in df.at[idx, 'agent']:
            df.at[idx, 'agent'] = 'Feeder for Turbine Installation'
        # Weather delays for all actions
        elif df.at[idx, 'action'] == 'Delay':
            df.at[idx, 'agent'] = 'Delay: Weather'    
    
    
################################# Plot based on Phases/Agents #################################
df[plot_based_on] = df[plot_based_on].str.wrap(30)

if 'WTIV' in strategy:
    agent_dic = ['WTIV for Monopile Installation', 'WTIV for Turbine Installation', 'Delay: Weather']
if 'feeder' in strategy:
    agent_dic = ['WTIV for Monopile Installation', 'Feeder for Monopile Installation', 'WTIV for Turbine Installation', 'Feeder for Turbine Installation', 'Delay: Weather']
wrapped_agent_dic = [textwrap.fill(phrase, width=30) for phrase in agent_dic]

# assign colors for phases/agents
def color(row):
    if plot_based_on == 'agent':
        if 'WTIV' in strategy:
            c_dict = {wrapped_agent_dic[0]:'#EEEE00', wrapped_agent_dic[1]:'#EE0000', wrapped_agent_dic[2]:'#8B0000'}
        if 'feeder' in strategy:
            c_dict = {wrapped_agent_dic[0]:'#EEEE00', wrapped_agent_dic[1]:'#EE0000', wrapped_agent_dic[2]:'#8B0000', wrapped_agent_dic[3]:'#7FFF00', wrapped_agent_dic[4]:'#66CD00'}
        return c_dict[row['agent']]

df['color'] = df.apply(color, axis=1)

fig, ax = plt.subplots(1, figsize=(8,7))
ax.barh(y=df[plot_based_on], width=df['phase_duration'], left=df['days_to_start'], color=df.color)


num_x_labels = 5
day_spacing = int(((df['end_date'].max() - df['start_date'].min()).days)/num_x_labels)
xticks = np.arange(0, df['days_to_end'].max()+1, day_spacing)
ax.set_xticks(xticks)
ax.set_xlabel("Days elapsed since the start of installation", fontdict=dict(weight='bold'), fontsize=12)
# xticks_labels = pd.date_range(start=df['start_date'].min(), end=df['end_date'].max()).strftime("%m/%d/%y")
# ax.set_xticklabels(xticks_labels[::day_spacing])

plt.gca().invert_yaxis()
fig.subplots_adjust(left=0.32)

ax.set_title(strategy)
plt.savefig('figures/' + strategy + '.png', bbox_inches = 'tight')
plt.show()

