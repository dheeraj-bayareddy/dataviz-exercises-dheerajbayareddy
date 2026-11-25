#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 24 19:33:35 2026

@author: dina.deifallah
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path


# Page configuration, title and data source
st.set_page_config(page_title="World Happiness Report", page_icon="🌐", layout='wide')
st.title("🌍 World Happiness Dashboard")
st.caption("Source: World Happiness Report 2023 | Kaggle")

# Data Ingestion
DATA = Path(__file__).parent.parent / "data" / "world_happiness_2023.csv"
df = pd.read_csv(DATA)

df.columns = ['Country','Region','Score','GDP','Social_Support',
              'Life_Expectancy','Freedom','Generosity','Corruption']

# Side bar filters
with st.sidebar:
    st.header("Filters")
    regions = ['All Regions'] + sorted(df['Region'].unique().tolist())
    selected_region = st.selectbox("Region", regions)
    top_n = st.slider("Show top N", 5, 25, 15)
    

# filter data by region and top_n
filtered = df if selected_region == 'All Regions' else df[df['Region'] == selected_region]
top = filtered.nlargest(top_n, 'Score').sort_values('Score')

# KPI row 
col1, col2, col3 = st.columns(3)
col1.metric("Countries", len(filtered))
col2.metric("Avg Score", f"{filtered['Score'].mean():.2f}",
            f"{filtered['Score'].mean()-df['Score'].mean():+.2f} vs global")
col3.metric("Happiest", filtered.nlargest(1,'Score')['Country'].values[0])

st.divider()

# create top bar chart
fig = px.bar(top, x='Score', y='Country', orientation='h',
             labels={'Score': 'Happiness Score (0–10)', 'Country': ''},
             template='plotly_white', title=f'Happiest {top_n} Countries in 2023 - {selected_region}')

fig.update_layout(title_font=dict(family='Arial', size=13, color='slategrey'),
                  xaxis=dict(range=[0, 8.0]))


st.plotly_chart(fig, width='stretch', height=600) 

# New chart: each country compared to the global average (diverging colours)
global_avg = df['Score'].mean()
filtered = filtered.assign(Diff=filtered['Score'] - global_avg).sort_values('Diff')

fig2 = px.bar(filtered, x='Diff', y='Country', orientation='h',
              color='Diff', color_continuous_scale='RdBu', color_continuous_midpoint=0,
              labels={'Diff': 'Difference from global average', 'Country': ''},
              template='plotly_white', title='Countries above (blue) and below (red) the global average')

fig2.add_vline(x=0, line_dash='dash')
fig2.add_annotation(x=0, y=1, yref='paper', yanchor='bottom', yshift=5,   # label sits ABOVE the bars
                    showarrow=False, text=f'Global average = {global_avg:.2f}')

fig2.update_layout(margin=dict(t=80),                  
                   height=max(400, 20 * len(filtered)),    
                   yaxis=dict(dtick=1))                    
st.plotly_chart(fig2, width='stretch')

st.divider()
st.caption("Built with Streamlit + Plotly")