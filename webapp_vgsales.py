import pandas as pd
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import plotly.express as px
import plotly.graph_objects as go
import os

# Load the dataset

current_directory = os.path.dirname(os.path.abspath(__file__))

# Construct the full path to the CSV file in the same directory
csv_file_path = os.path.join(current_directory, "vgsales_clean.csv")

# Read the CSV file
data = pd.read_csv(csv_file_path)

years = sorted(data['Year'].unique())

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

# Styling parameters
graph_style = {
    #'plot_bgcolor': 'rgba(0,0,0,0)',
    'paper_bgcolor': 'rgba(0,0,0,0.9)',
    'font': {'size': 10},  # Set the font size here
    #'xaxis': {'gridcolor': '#dedede'},
    #'yaxis': {'gridcolor': '#dedede'}
}


app.layout = dbc.Container(fluid=True, children=[
    html.Div([
        dcc.Slider(
            id='year_slider',  # Unique ID for the desktop slider
            min=min(years),
            max=max(years),
            value=min(years),  # Default value
            marks={str(year): str(year) for year in years},
            step=None,  # This makes the slider snap to the available years
            className='desktop-slider'
        ),  # Added missing comma here
        dcc.Dropdown(
            id='year_dropdown_mobile',  # Unique ID for the mobile dropdown
            options=[{'label': year, 'value': year} for year in years],
            value=min(years),  # Default value
            className='mobile-dropdown'
        )  # Removed unnecessary properties that are not applicable to Dropdown
    ], className='sticky-slider', style={'width': '90%', 'margin': '10px auto'}),

    dbc.Row([                  
        dbc.Col([          
            dcc.Graph(id='genre_Console_heatmap',className='shadow', style={'height': '540px'}),
            dcc.Graph(id='top_games_graph',className='shadow', style={'height': '300px'}),  
                  
        ], lg=4, md=12, sm=12, style={'margin': '0', 'padding': '0'}),

        dbc.Col([
            dcc.Graph(id='region_sales_radar',className='shadow', style={'height': '420px'}),
            dcc.Graph(id='pub_sales_graph',className='shadow', style={'height': '420px'}),
        ], lg=3, md=12, sm=12, style={'margin': '0', 'padding': '0'}),
            
        dbc.Col([         
            dcc.Graph(id='Console_sales_graph',className='shadow', style={'height': '280px'}),
            dcc.Graph(id='sales_trend_graph',className='shadow', style={'height': '280px'}), 
            dcc.Graph(id='genre_sales_bubble',className='shadow', style={'height': '280px'}),         
        ], lg=5, md=12, sm=12, style={'margin': '0', 'padding': '0'}),             
    ])

])

# Sales ------------------

@app.callback(
    Output('sales_trend_graph', 'figure'),
    [Input('year_slider', 'value'), 
     Input('year_dropdown_mobile', 'value')]
)
def update_sales_trend(slider_value, dropdown_value):
   # Determine which input triggered the callback
    ctx = dash.callback_context

    # Set a default year if neither input has been triggered yet
    if not ctx.triggered:
        selected_year = min(years)
    else:
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

        # Use the value from the triggered input
        if trigger_id == 'year_slider':
            selected_year = slider_value
        elif trigger_id == 'year_dropdown_mobile':
            selected_year = dropdown_value
        else:
            selected_year = min(years)

    yearly_data = data[data['Year'] == selected_year]

    # Group by Genre and sum up sales
    genre_sales = yearly_data.groupby('Genre')[['NA', 'EU', 'JP', 'Other']].sum().reset_index()

    # Custom labels for hover information
    labels = {'value': 'Units Sold (M)', 'variable': 'Region'}

    fig = px.bar(genre_sales, x='Genre', y=['NA', 'EU', 'JP', 'Other'],
                 title='Number of Units Sold by Genre', template='plotly_dark', labels=labels)

    fig.update_layout(yaxis_title='Units Sold (M)', **graph_style)
    return fig

@app.callback(
    Output('Console_sales_graph', 'figure'),
    [Input('year_slider', 'value'), 
     Input('year_dropdown_mobile', 'value')]
)
def update_Console_sales(slider_value, dropdown_value):
    # Determine which input triggered the callback
    ctx = dash.callback_context

    # Set a default year if neither input has been triggered yet
    if not ctx.triggered:
        selected_year = min(years)
    else:
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

        # Use the value from the triggered input
        if trigger_id == 'year_slider':
            selected_year = slider_value
        elif trigger_id == 'year_dropdown_mobile':
            selected_year = dropdown_value
        else:
            selected_year = min(years)

    yearly_data = data[data['Year'] == selected_year]

    Console_sales = yearly_data.groupby('Console')[['NA', 'EU', 'JP', 'Other']].sum().reset_index()

    # Custom labels for hover information
    labels = {'value': 'Units Sold (M)', 'variable': 'Region'}

    # Use the correct column name here based on whether you've renamed 'Console' to 'Console'
    fig = px.bar(Console_sales, x='Console', y=['NA', 'EU', 'JP', 'Other'],
                 title='Number of Units Sold by Console', template='plotly_dark', labels=labels)
    
    fig.update_layout(yaxis_title='Units Sold (M)', **graph_style)
    return fig

@app.callback(
    Output('top_games_graph', 'figure'),
    [Input('year_slider', 'value'), 
     Input('year_dropdown_mobile', 'value')]
)
def update_Console_sales(slider_value, dropdown_value):
    # Determine which input triggered the callback
    ctx = dash.callback_context

    # Set a default year if neither input has been triggered yet
    if not ctx.triggered:
        selected_year = min(years)
    else:
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

        # Use the value from the triggered input
        if trigger_id == 'year_slider':
            selected_year = slider_value
        elif trigger_id == 'year_dropdown_mobile':
            selected_year = dropdown_value
        else:
            selected_year = min(years)

    yearly_data = data[data['Year'] == selected_year]

    # Group by game name and sum the global sales
    aggregated_sales = yearly_data.groupby('Name')['Global_Sales'].sum().reset_index()

    # Find the top-selling games
    top_games = aggregated_sales.nlargest(5, 'Global_Sales')

    labels = {'Global_Sales': 'Units Sold (M)'}

    # Create a horizontal bar chart
    fig = px.bar(top_games, x='Global_Sales', y='Name', orientation='h', 
                 title='Top Selling Games', template='plotly_dark')
    
    # Optionally, you can customize the axis labels
    fig.update_layout(xaxis_title='Units Sold (M)', yaxis_title='Game', **graph_style)
    return fig


#Distribution -----------------------------------

@app.callback(
    Output('pub_sales_graph', 'figure'),
    [Input('year_slider', 'value'), 
     Input('year_dropdown_mobile', 'value')]
)
def update_pub_sales(slider_value, dropdown_value):
    # Determine which input triggered the callback
    ctx = dash.callback_context

    # Set a default year if neither input has been triggered yet
    if not ctx.triggered:
        selected_year = min(years)
    else:
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

        # Use the value from the triggered input
        if trigger_id == 'year_slider':
            selected_year = slider_value
        elif trigger_id == 'year_dropdown_mobile':
            selected_year = dropdown_value
        else:
            selected_year = min(years)

    # Filter data by the selected year first
    yearly_data = data[data['Year'] == selected_year]

    #hover_data = {'Parent': False,'labels': False,}

    labels = {'Global_Sales': 'Units Sold (M)','id':'Publisher','labels':'Label'}

    # Then group by Console and sum up regional sales
    top_publishers = yearly_data.groupby('Publisher')['Global_Sales'].sum().reset_index().sort_values(by='Global_Sales', ascending=False).head(10)

    # Creating a bar chart for Console sales

    fig = px.treemap(top_publishers, path=['Publisher'], 
                     values='Global_Sales', 
                     title='Global Publisher Sales Distribution',
                     template='plotly_dark', 
                     #hover_data=hover_data, 
                     labels=labels)
    fig.update_layout(**graph_style)
    return fig

@app.callback(
    Output('region_sales_radar', 'figure'),
    [Input('year_slider', 'value'), 
     Input('year_dropdown_mobile', 'value')]
)
def update_region_sales_radar(slider_value, dropdown_value):
    # Determine which input triggered the callback
    ctx = dash.callback_context

    # Set a default year if neither input has been triggered yet
    if not ctx.triggered:
        selected_year = min(years)
    else:
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

        # Use the value from the triggered input
        if trigger_id == 'year_slider':
            selected_year = slider_value
        elif trigger_id == 'year_dropdown_mobile':
            selected_year = dropdown_value
        else:
            selected_year = min(years)

    yearly_data = data[data['Year'] == selected_year]
    
    # Summing up sales by region
    region_sales = yearly_data[['NA', 'EU', 'JP', 'Other']].sum().reset_index()
    region_sales.columns = ['Region', 'Sales']

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=region_sales['Sales'],
        theta=region_sales['Region'],
        fill='toself'
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, region_sales['Sales'].max()]
            )),
        title='Region Sales Distribution',template='plotly_dark'
    )

    fig.update_layout(**graph_style)

    return fig

# Additional Chart types  ---------------------------------------------------------


# Example: Bubble Chart for Genre Sales with Bubble Size representing number of releases
@app.callback(
    Output('genre_sales_bubble', 'figure'),
    [Input('year_slider', 'value'), 
     Input('year_dropdown_mobile', 'value')]
)
def update_genre_sales_bubble(slider_value, dropdown_value):
    # Determine which input triggered the callback
    ctx = dash.callback_context

    # Set a default year if neither input has been triggered yet
    if not ctx.triggered:
        selected_year = min(years)
    else:
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

        # Use the value from the triggered input
        if trigger_id == 'year_slider':
            selected_year = slider_value
        elif trigger_id == 'year_dropdown_mobile':
            selected_year = dropdown_value
        else:
            selected_year = min(years)

    yearly_data = data[data['Year'] == selected_year]
    genre_data = yearly_data.groupby('Genre').agg({'Global_Sales': 'sum', 'Name': 'count'}).reset_index()

    # Use custom data for hover information
    hover_data = {'Name': False,  # Disable default hoverinfo for 'Name'
                  'Released Games': genre_data['Name']}  # Add new hoverinfo with custom label
    
    labels = {'Global_Sales': 'Units Sold (M)'}

    fig = px.scatter(genre_data, x='Genre', y='Global_Sales', size='Name',
                     title='Genre Sales and Number of Releases',
                     template='plotly_dark', 
                     hover_data=hover_data,
                     labels=labels)

    fig.update_layout(**graph_style)
    return fig

# Example: Heatmap of Sales by Genre and Console
@app.callback(
    Output('genre_Console_heatmap', 'figure'),
    [Input('year_slider', 'value'), 
     Input('year_dropdown_mobile', 'value')]
)
def update_genre_Console_heatmap(slider_value, dropdown_value):
    # Determine which input triggered the callback
    ctx = dash.callback_context

    # Set a default year if neither input has been triggered yet
    if not ctx.triggered:
        selected_year = min(years)
    else:
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

        # Use the value from the triggered input
        if trigger_id == 'year_slider':
            selected_year = slider_value
        elif trigger_id == 'year_dropdown_mobile':
            selected_year = dropdown_value
        else:
            selected_year = min(years)
    
    labels = {'color': 'Units Sold (M)'}

    yearly_data = data[data['Year'] == selected_year]

    heatmap_data = yearly_data.pivot_table(index='Genre', columns='Console', values='Global_Sales', aggfunc='sum').fillna(0)
   
    fig = px.imshow(heatmap_data, title='Sales Heatmap by Genre and Console',template='plotly_dark', labels=labels)
    fig.update_layout(**graph_style)
    return fig

application = app.server

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)