import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

############### Part I: Import Data ###############
# Read Data; Use Cache so that it doesn't load separately every time
@st.cache
def importdata():
    # store the data somewhere online; there are size limits which can be an issue, but GitHub is a good option
    return pd.read_csv("https://raw.githubusercontent.com/h3mps/fonrealwebapp/master/fon-REAL-data.csv")

# call function to import the data
df = importdata()

############### Part II: Inputs ###############
# Inputs: Normalization, Item, Province
# Once selection made, filter data so that it just includes these things

# Normalization
data = df[~df.normalization.str.contains("Nominal dollars")]
NORMS = list(data['normalization'].unique())
NORM_SELECTED = st.selectbox('Select Unit', NORMS, index = 0)
mask_norms = data['normalization'].isin([NORM_SELECTED])
data = data[mask_norms]

# Item
ITEMS = list(data['fonitem'].unique())
ITEMS_SELECTED = st.multiselect('Select Items (max. 5)', ITEMS, default=["Total revenue"])
mask_items = data['fonitem'].isin(ITEMS_SELECTED)
data = data[mask_items]

# Provinces
PROVS = list(data['provname'].unique())
PROVABBS = list(data['provabb'].unique())
PROVS_SELECTED = st.multiselect('Select Government', PROVS, default=["Federal government"])
mask_provs = data['provname'].isin(PROVS_SELECTED)
data = data[mask_provs]

############### Part IV: Create Figure ###############
# Province Color Scheme; Use for setting colors and text colors in the graphs
# These were meant to correspond to the province identity, so hopefully the order doesn't change much (currently alphabetical)
provcollist = ['olive', 'coral', 'lightseagreen', 'red', 'gold', 'magenta', 'slategray', 'peru', 'chocolate', 'dodgerblue', 'rosybrown', 'firebrick', 'forestgreen', 'midnightblue', 'goldenrod', 'yellow']
provfontlist = ['white', 'black', 'white', 'white', 'black', 'white', 'white', 'black', 'black', 'white', 'white', 'white', 'white', 'white', 'black', 'black']
itemmarkerlist = ['square', 'circle-open', 'triangle-up', 'diamond-open', 'hexagram']

# Create Figure Function
def addlines(fig):
    # Filter the data to only include what is desired
    for p in PROVS_SELECTED:
        # Find the index of the province in the list and assign the desired colors and abbreviation to it
        colindxp = PROVS.index(p)
        provcol = provcollist[colindxp]
        provfontcol = provfontlist[colindxp]
        provabb = PROVABBS[colindxp]
        # Filter the data to only include this province
        datalpp = data[data['provname'].isin([p])]
        # I distinguish between the units here because I want to format the hover text differently for each (% vs. M/B/T)
        # This could be eliminated easily
        for i in ITEMS_SELECTED:
            datalpi = datalpp[datalpp['fonitem'].isin([i])]
            if len(ITEMS_SELECTED) == 1:
                fig.add_trace(go.Scatter(x=datalpi['date'], y=datalpi['val'], mode='lines', line=dict(color=provcol, width=2),
                                        customdata=datalpi[['provname', 'fonitem', 'normalization']], name= provabb +', '+ i,
                                        hovertemplate = "Prov: %{customdata[0]} <br>Item: %{customdata[1]} <br>Unit: %{customdata[2]} <br>Year: %{x}<extra></extra>",
                                        hoverlabel=dict(font_color=provfontcol)))
            else:
                colindxi2 = ITEMS_SELECTED.index(i)
                itemmark = itemmarkerlist[colindxi2]
                fig.add_trace(go.Scatter(x=datalpi['date'], y=datalpi['val'], mode='lines+markers',
                                 line=dict(color=provcol, width=1.5), marker=dict(symbol=itemmark, size=8),
                                         customdata=datalpi[['provname', 'fonitem', 'normalization']], name=provabb + ', ' + i,
                                         hovertemplate="Prov: %{customdata[0]} <br>Item: %{customdata[1]} <br>Unit: %{customdata[2]} <br>Year: %{x}<extra></extra>",
                                        hoverlabel=dict(font_color=provfontcol)))

    return fig

# create the figure here
fig = go.Figure()
# What is nice about creating the function is that now I can call it with any type of line I want

fig = addlines(fig)

############### Part V: Format Figure Layout ###############
# axes
fig.update_yaxes(title_text=NORM_SELECTED)
fig.update_xaxes(title_text='Year')

# title
if len(ITEMS_SELECTED) == 1 and len(PROVS_SELECTED) == 1:
    fig.update_layout(title="Government REAL Data <br>" + ITEMS_SELECTED[0] + ' for ' + PROVS_SELECTED[0])
if len(ITEMS_SELECTED) == 1 and len(PROVS_SELECTED) > 1:
    fig.update_layout(title="Government REAL Data <br>" + ITEMS_SELECTED[0] + ' for Selected Governments')
if len(ITEMS_SELECTED) > 1 and len(PROVS_SELECTED) == 1:
    fig.update_layout(title="Government REAL Data <br>" + 'Selected Items for ' + PROVS_SELECTED[0])
if len(ITEMS_SELECTED) > 1 and len(PROVS_SELECTED) > 1:
    fig.update_layout(title="Government REAL Data <br>" + 'Selected Items for Selected Governments')

# elements of figure: title, template, grid, size
fig.update_layout(
    template = "simple_white",
    legend_title_text='',
    height=600,
    width=800,
    yaxis=dict(rangemode='tozero', showgrid=True, zeroline=True),
    xaxis=dict(showgrid=True),
    showlegend=True,
    legend=dict(x=0, y=-0.5),
    hoverlabel=dict(
        font_size=14,
    )
)

# add FON logo
fig.layout.images = [dict(
    source="https://raw.githubusercontent.com/h3mps/t1webapp/master/fon-icon.png",
    xref="paper", yref="paper",
    x=1, y=-0.5,
    sizex=0.25, sizey=0.25,
    xanchor="right", yanchor="bottom"
)]

############### Part VI: Publish Chart ###############
# Streamlit display Plotly chart function
# the use_container_width command is something to consider in conjunction with the height and width variables as well
# as the legend location, since the legend makes the chart area shrink as it gets larger
st.plotly_chart(fig, use_container_width=True)