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

###################
### HTML LAYOUT ###
###################

app.layout = html.Div([
    html.Div(html.H1('DASHBOARD'), className='jumbotron text-center',
             style={'color': 'white', 'background-color': 'black'}),
    html.Div([
        html.Div(className='col-sm-3'),
        html.Div(dcc.Dropdown(options=[{'label': cn, 'value': cn} for cn in confirmed['Country/Region']],
                              id='countryDropdown',
                              value='China'),
                 className='col-sm-6'),
        html.Div([html.Button(id='countryConfirmedButton', n_clicks=0, children='submit', className='center')],
                 className='col-sm-3')
    ], className='row'),

    html.Div([
        html.Div(className='col-sm-3'),
        html.Div([dcc.Graph(id='countryGraph')],
                 className='col-sm-6'),
        html.Div(className='col-sm-3')
    ], className='row')
])

#######################
### CALLBACK CONFIG ###
#######################


@app.callback(dash.dependencies.Output(component_id='countryGraph', component_property='figure'),
              [dash.dependencies.Input(component_id='countryConfirmedButton', component_property='n_clicks')],
              [dash.dependencies.State(component_id='countryDropdown', component_property='value')])
def getChartFigure(n_clicks, input_value):
    countryTimeline = go.Scatter(x=dates,
                                 y=getCountryTimeData(df=confirmed, cn=input_value),
                                 name='Timeline',
                                 line=dict(color='#f44242'))
    data = [countryTimeline]
    layout = dict(title='COVID-19 CONFIRMED CASES', showlegend=False)

    fig = dict(data=data, layout=layout)
    return fig


if __name__ == '__main__':
    app.run_server(debug=False)
