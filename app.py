#!/usr/bin/python
import requests
import calendar
from datetime import datetime
from collections import defaultdict
import pandas as pd
import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import plotly.express as px


# initialize app

app = dash.Dash(__name__, static_url_path='assets')
server = app.server
app.config.suppress_callback_exceptions = True
app.css.config.serve_locally = True
app.scripts.config.serve_locally = True

def make_weather_table(dtf):

    table = [html.Tr([html.Th(['Day']), html.Th(['Description']),
             html.Th(['Humidyty']), html.Th(['Temperature']),
             html.Th(['Wind']),
             html.Th(['Wind Direction'])])]
    for (index, row) in dtf.iterrows():
        html_row = []
        for i in range(len(row)):
            html_row.append(html.Td([row[i]]))
        table.append(html.Tr(html_row))

    return table


# openweather api call returns pandas dataframe

def api_call(input_value='Lisbon'):
    city = input_value.replace(' ', '').split(' ')[0]
    state = ''
    key = '' 
    r = \
        requests.get('http://api.openweathermap.org/data/2.5/forecast?q={},{}&appid={}&units=metric'.format(city,
                     state, key))
    data = r.json()
    day = [calendar.day_name[datetime.strptime(data['list'][i]['dt_txt'
           ].split(' ')[0], '%Y-%M-%d').weekday()] for i in range(3,
           36, 8)]
    description = [data['list'][i]['weather'][0]['description']
                   for i in range(3, 36, 8)]
    temp = [round(data['list'][i]['main']['temp']) for i in range(3,
            36, 8)]
    wind_speed = [data['list'][i]['wind']['speed'] for i in range(3,
                  36, 8)]
    wind_direction = [data['list'][i]['wind']['deg'] for i in range(3,
                      36, 8)]
    wind_direction = map(degrees_to_cardinal, wind_direction)
    humidity = [data['list'][i]['main']['humidity'] for i in range(3,
                36, 8)]
    df = pd.DataFrame(data={
        'Day': day,
        'Description': description,
        'Temperature': temp,
        'Humidity': humidity,
        'Wind': wind_speed,
        'Wind_direction': wind_direction,
        })

    return df


def degrees_to_cardinal(d):
    dirs = [
        'N',
        'NNE',
        'NE',
        'ENE',
        'E',
        'ESE',
        'SE',
        'SSE',
        'S',
        'SSW',
        'SW',
        'WSW',
        'W',
        'WNW',
        'NW',
        'NNW',
        ]
    ix = int((d + 11.25) / 22.5)
    return dirs[ix % 16]




app.layout = html.Div([  
    html.Div([
        dcc.Location(id='url', refresh=False),
        html.Link(
            rel='stylesheet',
            href='/assets/css/skeleton.min.css'
        ),
        html.Link(
            rel='stylesheet',
            href='/assets/css/dash-drug-discovery-demo-stylesheet.css'
        )
    ]),
    html.Div(id='page-content'),
    
    html.Div([html.H1('Weather Forcast with OpenWeatherMapApi'
             , style={'font-family': 'Dosis', 'font-size': '4.0rem',
             'textAlign': 'center'})]),
    html.Div([html.P('Enter City and country code or just city'),
             html.Div([dcc.Input(id='city_name',
             placeholder='ex Lisbon, prt', value='Lisbon, prt',
             type='text')])]),
    html.Div([html.Div(id='city_id')]),
    html.Div([dcc.Graph(id='weather_graph', style=dict(width='700px'
             ))]),

    ], className='container')  

@app.callback(Output(component_id='city_id',
              component_property='children'),
              [Input(component_id='city_name',
              component_property='value')])
def update_weather(input_value):
    icons = {
        'snow': 'img/snow.png',
        'cloud': 'img/cloudy.png',
        'rain': 'img/rain.png',
        'sunny': 'img/sunny.png',
        'clear sky': 'img/sunny.png',
        'fog': 'img/fog.png',
        }
    df = api_call(input_value)

    temp_icon = ['']
    for (key, value) in icons.items():
        if key in df.Description[0]:
            temp_icon = icons[key]

    input_value = input_value



    app.layout = html.Div([  
        html.H3(input_value, style={'color': '#878787'}),
        html.P(df.Day[0], style={'fontSize': '20px'}),
        html.P(df.Description[0], style={'fontSize': '18px'}),
        html.Div(style={
            'height': '64px',
            'display': 'inline',
            'position': 'relative',
            'width': '64px',
            'margin-top': '-9px',
            }, children=[html.Img(src=temp_icon),
                         html.P("{} °C".format(df.Temperature[0]),
                         style={'fontSize': '36px', 'display': 'inline'
                         })]),
        html.Div(style={'float': 'right', 'fontSize': '20px'},
                 children=[html.P('Humidity: {}%'.format(df.Humidity[0])),
                 html.P('Wind: {} kph'.format(df.Wind[0]))]),
        html.Div(children=[dcc.Graph(id='weather_graph',
                 figure=go.Figure(data=[go.Scatter(x=list(df.Day),
                 y=list(df.Temperature), mode='lines+markers',
                 name='temperature'), go.Scatter(x=list(df.Day),
                 y=list(df.Humidity), mode='lines+markers',
                 name='Humidity'), go.Scatter(x=list(df.Day),
                 y=list(df.Wind), mode='lines+markers', name='wind')],
                 layout=go.Layout(title='Five Day Weather Forcast For {}'.format(input_value),
                 showlegend=True, margin=go.Margin(l=20, r=0, t=40,
                 b=20))))]),
        html.Div([html.Br(), html.Hr(),
                 html.P('Table for {} Weather Information'.format(input_value),
                 style={'textAlign': 'center'}), html.Table(),
                 html.Table(make_weather_table(df))]),
        ])

    return app.layout

# external_css = \
#     ['https://cdnjs.cloudflare.com/ajax/libs/skeleton/2.0.4/skeleton.min.css'
#      , '//fonts.googleapis.com/css?family=Raleway:400,300,600',
#      '//fonts.googleapis.com/css?family=Dosis:Medium',
#      'https://cdn.rawgit.com/plotly/dash-app-stylesheets/0e463810ed36927caf20372b6411690692f94819/dash-drug-discovery-demo-stylesheet.css'
#      ]

# for css in external_css:
#     app.css.append_css({'external_url': css})

@app.server.route('/assets/<path:path>')
def static_file(path):
    static_folder = os.path.join(os.getcwd(), 'assests')
    return send_from_directory(static_folder, path)


if __name__ == '__main__':
    app.run_server(host='0.0.0.0',port=80)
