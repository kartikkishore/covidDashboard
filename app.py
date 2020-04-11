from datetime import datetime

import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go

# Get Data
confirmed = pd.read_csv(
    'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv')
recovered = pd.read_csv(
    'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv')
death = pd.read_csv(
    'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv')

# Find dates
assert (len(confirmed.columns) == len(death.columns) == len(recovered.columns))
dates = []
for d in confirmed.columns:
    try:
        datetime.strptime(d, '%m/%d/%y')
        dates.append(d)
    except ValueError:
        continue


# Helper Functions
def updateDF(df, newDF, dates):
    for date in dates:
        if len(newDF) == 0:
            newDF = df.groupby(['Country/Region'])[date].apply(sum).reset_index().copy()
        else:
            temp = df.groupby(['Country/Region'])[date].apply(sum).reset_index().copy()
            newDF = pd.merge(left=newDF, right=temp, on=['Country/Region'], how='left')
    return newDF


def getCountryTimeData(df, cn):
    return df[df['Country/Region'] == cn].values.flatten()[1:].tolist()


# Process data by country - Aggregating states and provinces into country
newConfirmed = pd.DataFrame()
confirmed = updateDF(df=confirmed, newDF=newConfirmed, dates=dates)
print('*\n')

newDeath = pd.DataFrame()
death = updateDF(df=death, newDF=newDeath, dates=dates)
print('*\n')

newRecovered = pd.DataFrame()
recovered = updateDF(df=recovered, newDF=newRecovered, dates=dates)
print('*\n')

print('**** Data processing done, bringing up server ****\n\n')

#################
### DASHBOARD ###
#################

# Stylesheet
bootstrap = [
    'https://codepen.io/chriddyp/pen/bWLwgP.css',
    {
        'href': 'https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css',
        'rel': 'stylesheet',
        'integrity': 'sha384-MCw98/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO',
        'crossorigin': 'anonymous'
    }
]

# Create DASH instance
app = dash.Dash(__name__, external_stylesheets=bootstrap)
app.title = 'COVID-19 DASHboard'

###################
### HTML LAYOUT ###
###################

app.layout = html.Div([
    html.Div(
        [html.H1('COVID-19 DASHBOARD', style={'fontSize': 72}),
         html.P('Coronavirus disease (COVID-19) is an infectious disease caused by a new virus. The disease causes respiratory illness (like the flu) with symptoms such as a cough, fever, and in more severe cases, difficulty breathing.')],
        className='jumbotron text-center', style={'color': 'white', 'background-color': 'black'}),

    html.Div([
        html.Div(className='col-sm-4'),
        html.Div(dcc.Dropdown(options=[{'label': cn, 'value': cn} for cn in confirmed['Country/Region']],
                              id='countryDropdown',
                              value='China'),
                 className='col-sm-4'),
        html.Div([html.Button(id='countryConfirmedButton', n_clicks=0, children='submit', className='center')],
                 className='col-sm-4')
    ], className='row'),

    html.Div([
        html.Div([dcc.Graph(id='countryGraphConfirm')], className='col-sm-4'),
        html.Div([dcc.Graph(id='countryGraphRecovered')], className='col-sm-4'),
        html.Div([dcc.Graph(id='countryGraphDeath')], className='col-sm-4')
    ], className='row')
])


#######################
### CALLBACK CONFIG ###
#######################


@app.callback(dash.dependencies.Output(component_id='countryGraphConfirm', component_property='figure'),
              [dash.dependencies.Input(component_id='countryConfirmedButton', component_property='n_clicks')],
              [dash.dependencies.State(component_id='countryDropdown', component_property='value')])
def getChartFigure(n_clicks, input_value):
    countryTimeline = go.Scatter(x=dates,
                                 y=getCountryTimeData(df=confirmed, cn=input_value),
                                 name='Timeline',
                                 line=dict(color='#f2a600'))
    data = [countryTimeline]
    layout = dict(title='COVID-19 CONFIRMED CASES', showlegend=False)

    fig = dict(data=data, layout=layout)
    return fig


@app.callback(dash.dependencies.Output(component_id='countryGraphDeath', component_property='figure'),
              [dash.dependencies.Input(component_id='countryConfirmedButton', component_property='n_clicks')],
              [dash.dependencies.State(component_id='countryDropdown', component_property='value')])
def getChartFigure(n_clicks, input_value):
    countryTimeline = go.Scatter(x=dates,
                                 y=getCountryTimeData(df=death, cn=input_value),
                                 name='Timeline',
                                 line=dict(color='#f44242'))
    data = [countryTimeline]
    layout = dict(title='COVID-19 DEATHS', showlegend=False)

    fig = dict(data=data, layout=layout)
    return fig


@app.callback(dash.dependencies.Output(component_id='countryGraphRecovered', component_property='figure'),
              [dash.dependencies.Input(component_id='countryConfirmedButton', component_property='n_clicks')],
              [dash.dependencies.State(component_id='countryDropdown', component_property='value')])
def getChartFigure(n_clicks, input_value):
    countryTimeline = go.Scatter(x=dates,
                                 y=getCountryTimeData(df=recovered, cn=input_value),
                                 name='Timeline',
                                 line=dict(color='#00e30b'))
    data = [countryTimeline]
    layout = dict(title='COVID-19 RECOVERED', showlegend=False)

    fig = dict(data=data, layout=layout)
    return fig


if __name__ == '__main__':
    app.run_server(debug=False)
