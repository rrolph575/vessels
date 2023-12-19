# -*- coding: utf-8 -*-
"""
Created on Tue Nov 14 09:44:47 2023

@author: rrolph
"""

import pandas as pd
import os


# Load file
ifile = 'action_logs_csv/MP4feeder_060km_WTG3feeder_060km_10_21_2009_FeederPosTime50.csv'
# Read file
df = pd.read_csv(os.path.join(os.getcwd(),ifile))

df_MonopileInstallation = df.loc[df['phase']=='MonopileInstallation']
df_MonopileInstallation.loc[df_MonopileInstallation['action']=='Delay']

delay_monopile = df_MonopileInstallation.loc[df_MonopileInstallation['action']=='Delay']['duration'].sum()
print('Total delay for monopile installation' , delay_monopile)



total_project_delay = df.loc[df['action']=='Delay']['duration'].sum()
print('Total project delay', total_project_delay)
