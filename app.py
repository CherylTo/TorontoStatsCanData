import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import requests
import geopandas as gpd
import pandas as pd
import json
from flask import Flask
#from flask_cors import CORS
import os
import numpy as np

app = dash.Dash(__name__)

app.css.append_css({'external_url': 'https://cdn.rawgit.com/plotly/dash-app-stylesheets/2d266c578d2a6e8850ebce48fdb52759b2aef506/stylesheet-oil-and-gas.css'})  # noqa: E501
server = app.server
#CORS(server)

if 'DYNO' in os.environ:
    app.scripts.append_script({
        'external_url': 'https://cdn.rawgit.com/chriddyp/ca0d8f02a1659981a0ea7f013a378bbd/raw/e79f3f789517deec58f41251f7dbb6bee72c44ab/plotly_ga.js'  # noqa: E501
    })

accesstoken = 'pk.eyJ1IjoiY2hlcnlsdG8iLCJhIjoiY2pmMDhybjlrMGtqZTJxcWowb3p6cjRlciJ9.xeYztQb94PNAFbC1sMqcHQ'

df = gpd.read_file('verysimplecoords.geojson')

with open('verysimplecoords.geojson','r') as infile:
    coords = json.load(infile)

#sources=[{"type": "FeatureCollection", 'features': [feat]} for feat in coords['features']]

f_income = pd.read_csv('female_income.csv').drop('Unnamed: 0', axis = 1)
m_income = pd.read_csv('male_income.csv').drop('Unnamed: 0', axis = 1)

f_income.columns = ['geo_code', 'Income', 'Government Transfer']
m_income.columns = ['geo_code', 'Income', 'Government Transfer']
f_income['Gender'] = 'female'
m_income['Gender'] = 'male'
ham_income = pd.concat([f_income, m_income])

avg_income = []
for i in ham_income['geo_code'].unique():
    avg_income.append((ham_income[ham_income['geo_code'] == i]['Income'].values[0] + ham_income[ham_income['geo_code'] == i]['Income'].values[1]) / 2)

#lookup df
lookup_df = pd.DataFrame({'geo_code': f_income['geo_code'], 'avg_income': avg_income})

edu = pd.read_csv('education.csv')
edu.columns=['geo_code', 'Gender', 'High School', 'Some College',
             'Some BA', 'BA', 'Masters', 'Medicine', 'PhD']

edu['High School'] = [int(0) if not i.isdigit() else int(i) for i in edu['High School']]
edu['Some College'] = [int(0) if not i.isdigit() else int(i) for i in edu['Some College']]
edu['Some BA'] = [int(0) if not i.isdigit() else int(i) for i in edu['Some BA']]
edu['BA'] = [int(0) if not i.isdigit() else int(i) for i in edu['BA']]
edu['Masters'] = [int(0) if not i.isdigit() else int(i) for i in edu['Masters']]
edu['Medicine'] = [int(0) if not i.isdigit() else int(i) for i in edu['Medicine']]
edu['PhD'] = [int(0) if not i.isdigit() else int(i) for i in edu['PhD']]

employment = pd.read_csv('employment_status.csv')

employment.columns = ['geo_code', 'Gender', 'In Labour Force', 'Not in Labour Force',
                      'Employed', 'Unemployed']

employment['In Labour Force'] = [int(0) if not i.isdigit() else int(i) for i in employment['In Labour Force']]
employment['Not in Labour Force'] = [int(0) if not i.isdigit() else int(i) for i in employment['Not in Labour Force']]
employment['Employed'] = [int(0) if not i.isdigit() else int(i) for i in employment['Employed']]
employment['Unemployed'] = [int(0) if not i.isdigit() else int(i) for i in employment['Unemployed']]

marital = pd.read_csv('marital_status.csv').drop('Unnamed: 0', axis=1)

marital.columns = ['geo_code', 'Married', 'Common Law', 'Not Married or Common Law',
                   'Never Married', 'Separated', 'Divorced', 'Widowed']

marital['Married'] = [int(0) if not i.isdigit() else int(i) for i in marital['Married']]
marital['Common Law'] = [int(0) if not i.isdigit() else int(i) for i in marital['Common Law']]
marital['Not Married or Common Law'] = [int(0) if not i.isdigit() else int(i) for i in marital['Not Married or Common Law']]
marital['Never Married'] = [int(0) if not i.isdigit() else int(i) for i in marital['Never Married']]
marital['Separated'] = [int(0) if not i.isdigit() else int(i) for i in marital['Separated']]
marital['Divorced'] = [int(0) if not i.isdigit() else int(i) for i in marital['Divorced']]
marital['Widowed'] = [int(0) if not i.isdigit() else int(i) for i in marital['Widowed']]

df['DA'] = [int(0) if not i.isdigit() else int(i) for i in df['DA']]

app.layout = html.Div([
        html.H1(children='Hamilton Dissemination Areas'),
        html.H3(children='Filter by Income Range:'),
        html.Div([
                    dcc.RangeSlider(id='my-slider',
                                    min=0,
                                    max=100000,
                                    marks={i:str(i) for i in range(0, 100001, 5000)},
                                    step=5000,
                                    value=[0,30000],
                    ),
                    html.H3(html.Div(id='slider-output-container'))
                    ]),
        html.Div(
            [
                html.Div(
                    [
                        dcc.Graph(id='main-graph')
                    ],
                    className='eight columns',
                    style={'margin-top': '20'}
                ),
                html.Div(
                    [
                        dcc.Graph(id='income-graphic')
                    ],
                    className='four columns',
                    style={'margin-top': '20'}
                ),
            ],
            className='row'
        ),
        html.Div(
            [
                html.Div(
                    [
                        dcc.Graph(id='education-graphic')
                    ],
                    className='four columns',
                    style={'margin-top': '10'}
                ),
                html.Div(
                    [
                        dcc.Graph(id='marital-graphic')
                    ],
                    className='four columns',
                    style={'margin-top': '10'}
                ),
                html.Div(
                    [
                        dcc.Graph(id='employment-graphic')
                    ],
                    className='four columns',
                    style={'margin-top': '10'}
                ),
            ],
            className='row'
        ),
    ])

@app.callback(Output('main-graph', 'figure'),
              [Input('my-slider', 'value')]
)
def update_map(value_list):
    relevant_da = [lookup_df[(lookup_df['avg_income'] >= value_list[0]) & (lookup_df['avg_income'] <= value_list[1])]['geo_code']]
    #just the DA's
    x = relevant_da[0].values

    #filtered df
    filtered_df = df[df['DA'].isin(x)]

    # Load and convert GeoJSON file  -- ADD IF STATMENT HERE
    sources=[{"type": "FeatureCollection", 'features': [feat]} for feat in coords['features']]

     #getting the x and y coords from geojson file
    filtered_df['lon'] = gpd.GeoSeries(filtered_df.centroid).x
    filtered_df['lat'] = gpd.GeoSeries(filtered_df.centroid).y

    layers_array = [
        dict(sourcetype = 'geojson',
                 source =sources[k],
                 below='water',
                 type = 'fill',
                 color = '#adbdd6',
                 opacity=0.5,
                ) for k in range(len(sources))
       ]

    data = go.Data([
        go.Scattermapbox(
            lat=filtered_df['lat'],
            lon=filtered_df['lon'],
            mode='markers',
            marker=dict(color='#b8bcc8',size=6),
            text=[str(s) for s in df['DA']]
        )
    ])
    layout = go.Layout(
        title='Hamilton Dissemination Area Map',
        height=500,
        autosize=True,
        hovermode='closest',
        margin=dict(
            l=35,
            r=35,
            b=35,
            t=35
        ),
        mapbox=dict(
            # layers=layers_array,
            # accesstoken='pk.eyJ1IjoiY2hlcnlsdG8iLCJhIjoiY2pmMDhybjlrMGtqZTJxcWowb3p6cjRlciJ9.xeYztQb94PNAFbC1sMqcHQ',
            accesstoken = 'pk.eyJ1IjoiY2hlcnlsdG8iLCJhIjoiY2poOWhvdXI4MGN1NTNkbWZkYTQ3cTF0ZSJ9.a_31nG7J_8gvzg2CWR6vSw',

            bearing=0,
            center=dict(
                lat=43.2557,
                lon=-79.8711
            ),
            pitch=0,
            zoom=10,
            style='mapbox://styles/cherylto/cjf08sicm4fqr2qp0wf5qhszd'
            #style='light'
        )
    )

    figure = dict(data=data, layout=layout)
    return figure

@app.callback(
    Output('slider-output-container', 'children'),
    [Input('my-slider', 'value')]
)
def update_output(value):
    return 'Minimum income: {}\t\tMaximum income: {}'.format(value[0],value[1])

@app.callback(
    Output('income-graphic', 'figure'),
    [Input('my-slider', 'value')]
)
def update_plot(value_list):
    relevant_da = [lookup_df[(lookup_df['avg_income'] >= value_list[0]) & (lookup_df['avg_income'] <= value_list[1])]['geo_code']]
    #just the DA's
    x = relevant_da[0].values

    #filtered df
    filtered_df = ham_income[ham_income['geo_code'].isin(x)]

    #using the filtered_df to find the mean income for f and m
    f=[]
    m=[]
    for i in range(len(filtered_df)):
        if filtered_df.iloc[i]['Gender'] == 'female':
            f.append(filtered_df.iloc[i]['Income'])
        else:
            m.append(filtered_df.iloc[i]['Income'])


    f_avg = np.mean(f)
    m_avg = np.mean(m)

    return {'data': [go.Bar(x = list(np.unique(ham_income['Gender'].values)),
                y = [f_avg, m_avg],
                marker={'color': ['#FFD700', '#9EA0A1']})
                ],
                'layout': go.Layout(title='Income by Gender',
                                    xaxis={'title': 'Gender'},
                                    yaxis={'title': 'Average Income (k)',
                                           'autorange': False,
                                           'range':[0, 100000]},
                                    height=500,
                                    autosize=True)}

@app.callback(Output('education-graphic', 'figure'),
              [Input('my-slider', 'value')]
)
def update_education(value_list):
    relevant_da = [lookup_df[(lookup_df['avg_income'] >= value_list[0]) & (lookup_df['avg_income'] <= value_list[1])]['geo_code']]
    #just the DA's
    x = relevant_da[0].values

    #filtered df
    filtered_df = edu[edu['geo_code'].isin(x)]

    #female education
    labels = ['High School', 'Some College',
             'Some BA', 'BA', 'Masters', 'Medicine', 'PhD']
    f_values = filtered_df[filtered_df['Gender'] == 'female'][['High School', 'Some College',
             'Some BA', 'BA', 'Masters', 'Medicine', 'PhD']].values.tolist()
    f_avg = [np.average(x) for x in zip(*f_values)]

    #male education
    m_values = filtered_df[filtered_df['Gender'] == 'male'][['High School', 'Some College',
             'Some BA', 'BA', 'Masters', 'Medicine', 'PhD']].values.tolist()
    m_avg = [np.average(x) for x in zip(*m_values)]

    trace1=go.Bar(x=labels,
                  y=f_avg,
                 name='Female')
    trace2=go.Bar(x=labels,
                  y=m_avg,
                  name='Male')
    data=[trace1, trace2]

    return {'data': [trace1, trace2]
            ,
            'layout': go.Layout(title='Education by Gender',
                                xaxis={'title': 'Level of Education'},
                                yaxis={'title': 'Average No. Across Dissemination Areas'}
                                )}

go.Layout(title='Income by Gender',
                                    xaxis={'title': 'Gender'},
                                    yaxis={'title': 'Average Income (k)',
                                           'autorange': False,
                                           'range':[0, 100000]},
                                    height=500,
                                    autosize=True)


@app.callback(
    Output('marital-graphic', 'figure'),
    [Input('my-slider', 'value')]
)
def update_marital(value_list):
    relevant_da = [lookup_df[(lookup_df['avg_income'] >= value_list[0]) & (lookup_df['avg_income'] <= value_list[1])]['geo_code']]
    #just the DA's
    x = relevant_da[0].values

    #filtered df
    filtered_df = marital[marital['geo_code'].isin(x)]

    #marital
    labels = ['Married', 'Common Law', 'Not Married or Common Law',
       'Never Married', 'Separated', 'Divorced', 'Widowed']
    values = filtered_df[labels].values.tolist()
    avg = [np.average(x) for x in zip(*values)]

    return {'data': [go.Pie(labels=labels,
                            values=avg,
                            hole=0.5,
                            marker=dict(colors=['#a2b9bc','#b2ad7f', '#878f99',
                                                '#6b5b95', '#bdcebe', '#FFD700', '#9EA0A1']))
            ],
            'layout': go.Layout(title='Marital Status')}


@app.callback(
    Output('employment-graphic', 'figure'),
    [Input('my-slider', 'value')]
)
def update_employment(value_list):
    relevant_da = [lookup_df[(lookup_df['avg_income'] >= value_list[0]) & (lookup_df['avg_income'] <= value_list[1])]['geo_code']]
    #just the DA's
    x = relevant_da[0].values

    #filtered df
    filtered_df = employment[employment['geo_code'].isin(x)]

    #female employment
    labels = ['In Labour Force', 'Not in Labour Force',
       'Employed', 'Unemployed']
    f_values = filtered_df[filtered_df['Gender'] == 'female'][labels].values.tolist()
    f_avg = [np.average(x) for x in zip(*f_values)]

    #male employment
    m_values = filtered_df[filtered_df['Gender'] == 'male'][labels].values.tolist()
    m_avg = [np.average(x) for x in zip(*m_values)]

    trace1=go.Bar(x=labels,
                  y=f_avg,
                 name='Female')
    trace2=go.Bar(x=labels,
                  y=m_avg,
                  name='Male')
    data=[trace1, trace2]

    return {'data': [trace1, trace2]
            ,
            'layout': go.Layout(title='Employment by Gender',
                                xaxis={'title': 'Employment'},
                                yaxis={'title': 'Average No. Across Dissemination Areas'}
                                )}

go.Layout(title='Income by Gender',
                                    xaxis={'title': 'Gender'},
                                    yaxis={'title': 'Employment'})

if __name__ == '__main__':
    app.run_server(debug=True, threaded=True)
