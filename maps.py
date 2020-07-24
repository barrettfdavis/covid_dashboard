"""
Author: Barrett F. Davis
Affiliation: Purdue University, School of Biomedical Engineering
Contact: davis797@purdue.edu

About: 
    
A COVID-19 case visualizer based on the Indiana State Department of
Health's (ISDH) COVID-19 county-wide test, case and death trends information. 
Visualizer uses population data and a rolling, 14-day sum of county-by-county
confirmed COVID-19 cases to estimate the number of actively infected people. 

Links: https://hub.mph.in.gov/dataset/covid-19-county-wide-test-case-and-death-trends/resource/afaa225d-ac4e-4e80-9190-f6800c366b58


Future Work: 

Not all testing centers operate at full capacity, 7-days a week. Nor does every 
county test at an appropriate level (e.g. testing to a <10% positive rate).
However the numbers of confirmed cases per capita are well-correlated between
neighboring counties. Taking advantage of this correlation, it may be worth 
using neighboring counties as an additional estimator for true infection rates
or trends in infection rate. 
"""

import plotly.express as px
import plotly.offline

from pylab import cm
import matplotlib

import pandas as pd
import numpy as np

import json

##############################################################################
#
# LOAD DATA
#
##############################################################################

df_data = pd.read_excel('covid_report_county_date.xlsx')
dict_pop  = pd.read_csv('IN_county_population.csv',index_col=0, squeeze=True).to_dict()

with open('json_indiana.json') as geofile:
    json_indiana = json.load(geofile)
    
##############################################################################
#
# PROCESS DATA
#
##############################################################################
    
df_data['POPULATION'] = [dict_pop[i] for i in df_data['COUNTY_NAME']]

ROLLING = df_data.groupby('COUNTY_NAME')['COVID_COUNT'].transform(lambda x: x.rolling(14, 1).sum())
df_data['ROLLING_PER_100K'] = 1e5*ROLLING/df_data['POPULATION']


##############################################################################
#
# DEFINE DISCRETE BINS
#
##############################################################################

bins = [0,10,25,50,100,250,500,550]
mid_bins = bins[:-1] + np.diff(bins)/2 # used to place legend ticks


class_str = [] # define legend ticks
for idx,j in enumerate(bins[:-2]): 
    class_str.append('  ' + str(j) + '-' + str(bins[idx+1]-1))

class_str.append('  '+ str(bins[-2])+'+')

##############################################################################
#
# DEFINE COLOR-MAPPING
#
##############################################################################

color_list = []
cmap = cm.get_cmap('cividis', len(bins)-1)
for i in range(cmap.N):
    
    rgb = cmap(i)[:3]
    color = matplotlib.colors.rgb2hex(rgb)
    
    color_list.append([bins[i]/bins[-1],color])
    color_list.append([bins[i+1]/bins[-1], color])

colorbar = dict(title=None,tickvals=mid_bins, ticktext= class_str)
coloraxis = dict(cmax=bins[-1],cmin=bins[0], colorbar=colorbar)

##############################################################################
#
#  CONSTRUCT CHOROPLETH (MAP)
#
##############################################################################

fig = px.choropleth(df_data,
                    geojson = json_indiana,
                    locations = "COUNTY_NAME", 
                    projection="mercator",
                    
                    featureidkey='properties.NAME',
                    color="ROLLING_PER_100K", 
                    color_continuous_scale=color_list,
                    
                    hover_data=['DATE','COUNTY_NAME','ROLLING_PER_100K',
                                'COVID_COUNT','POPULATION'],
                    
                    animation_frame="DATE"
                    )

fig.update_layout(
    title_text = '14-Day Cumulative COVID-19 Cases per 100,000 Residents',
    coloraxis=coloraxis
    )

fig.update_geos(fitbounds="locations", visible=True
                )

##############################################################################
#
#  CREATE LOCAL FIGURE DISPLAY
#
##############################################################################


plotly.offline.plot(fig,filename='IndianaCOVID.html')

