# -*- coding: utf-8 -*-
"""
Created on Tue Nov 14 09:44:47 2023

@author: rrolph
"""

import pandas as pd
import os

name = 'shuttle_amer_freq'

# Load file
ifile = 'action_logs_csv/' + name + '_10_21_2009.csv'
# Read file
df = pd.read_csv(os.path.join(os.getcwd(),ifile))

df_MonopileInstallation = df.loc[df['phase']=='MonopileInstallation']
df_MonopileInstallation.loc[df_MonopileInstallation['action']=='Delay']

total_delay = df_MonopileInstallation.loc[df_MonopileInstallation['action']=='Delay']['duration'].sum()
print(total_delay)


total_delay_not_enough_vessels = df_MonopileInstallation.loc[df_MonopileInstallation['action']=='Delay: Not enough vessels for monopiles']['duration'].sum()
print(total_delay_not_enough_vessels)


name = 'shuttle_foreign_freq_far'# Load file
ifile = 'action_logs_csv/' + name + '_10_21_2009.csv'
# Read file
df = pd.read_csv(os.path.join(os.getcwd(),ifile))

df_MonopileInstallation = df.loc[df['phase']=='MonopileInstallation']
df_MonopileInstallation.loc[df_MonopileInstallation['action']=='Delay']

total_delay = df_MonopileInstallation.loc[df_MonopileInstallation['action']=='Delay']['duration'].sum()
print(total_delay)

total_delay_not_enough_vessels = df_MonopileInstallation.loc[df_MonopileInstallation['action']=='Delay: Not enough vessels for monopiles']['duration'].sum()
print(total_delay_not_enough_vessels)
