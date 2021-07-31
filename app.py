import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
from utils import predict_price
import yfinance as yf
from datetime import datetime as dt
from dash.exceptions import PreventUpdate

app = dash.Dash(__name__,external_stylesheets=[dbc.themes.BOOTSTRAP],
               meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0'}])
server = app.server

app.title = 'iStocks Research'

all_company = ['AAPL','KOLD','UNF','MSFT']

CONTENT_STYLE = {
    "margin-left": "2rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

sidebar = html.Div([

    html.H2("Pick A Stock !!", className="display-4",style={'padding-top':'5px'}),
    html.Hr(),
    html.Br(),
    dcc.Dropdown(
        id='stock_code',
        options=[{'label': i, 'value': i} for i in all_company],
        # value='AAPL'
    ),
    html.Br(),
    html.Br(),
    html.Div([
        dcc.DatePickerRange(id='my-date-picker-range',
                        min_date_allowed=dt(1995, 8, 5),
                        max_date_allowed=dt.now(),
                        initial_visible_month=dt.now(),
                        end_date=dt.now().date()),
        html.Br(),
        html.Br(),
        dbc.Button(id='show_data_submit', n_clicks=0, children='Show Data',
        outline=True, color="info", className="mr-1"),
    ],style={'text-align':'center'}),
    html.Br(),
    html.Br(),
    html.Div([
        dbc.Button(id='stock_forecast_submit', n_clicks=0, children='Predict',
        outline=True, color="dark")
    ],style={'text-align':'center'}),
    html.Br(),
])

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Linkedin", target='_blank', href="https://www.linkedin.com/in/jasmine-parween-393282200/")),
        dbc.NavItem(dbc.NavLink("Github", target='_blank', href="https://github.com/JasmineParween/Stock-price-analyzer")),
    ],
    brand="iStocks Reasearch",
    brand_href="#",
    # color="primary",
    className='navbar navbar-expand-sm bg-dark navbar-dark w-100',
    dark=True
    )

data_graph = html.Div(id='data_graph',style=CONTENT_STYLE)
predict_graph = html.Div(id='predict_graph',style=CONTENT_STYLE)

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            sidebar,
        ],sm=3,style={"background-color":"lavender"},
        ),

        dbc.Col([
            dbc.Row([
                navbar,
            ],className='d-flex flex-column flex-fill flex-wrap'),

            dbc.Row([
                dbc.Col([
                    dcc.Loading(
                        id="loading-1",
                        children=html.Div([
                                html.Img(id="logo"),
                                ],className="header",style=CONTENT_STYLE), 
                        type='dot',
                        color='#FFFFFF',
                    )
                ],sm=2),
                dbc.Col([
                    dcc.Loading(
                        id="loading-2",
                        children= html.Div([
                                html.P(id="c_name")],className="header",
                                style={"left": 0,"margin-top": '4rem','FONT-WEIGHT': 400,'font-size':' xx-large',
                                'font-family': 'fangsong'}), 
                        type='dot',
                        color='#FFFFFF',
                    )
                    
                ],sm=3),
            ],justify='start'),

            dbc.Row([
                dcc.Loading(
                    id="loading-3",
                    children= html.Div([], id="company_data",className="bg-white",style=CONTENT_STYLE),
                    type="cube",
                )
               
            ]),
            dbc.Row([
                dcc.Loading(
                    id="loading-4",
                    children= data_graph,
                    type="graph",
                ) 
            ],className='justify-content-center'),
            dbc.Row([
                dcc.Loading(
                    id="loading-5",
                    children= predict_graph,
                    type="graph",
                    style={'padding-bottom':'100px'}
                ) 
            ],className='justify-content-center'),

        ],sm=9)
        
    ],style={'height':'100vh'}),

],fluid=True)

about_me = '''Hey, Folks! If you came this far for me, so why not Give it a shot !!. 
                Go Ahead pick a stock of your wish, Get the company info.select date range and then view the data.
                Want some signals for tomorrow ?? Go Ahead Click ON Predict BUtton'''

@app.callback(
    Output(component_id='logo', component_property='src'),
    Output(component_id='c_name', component_property='children'),
    Output(component_id='company_data', component_property='children'),
    Output(component_id='show_data_submit', component_property='n_clicks'),
    Output(component_id='stock_forecast_submit', component_property='n_clicks'),
    Input(component_id='stock_code', component_property='value')
    )
def update_company_data(stock_code):
    if stock_code == None:
        return '','Jasmine Parween',about_me,0,0
    pfizer = yf.Ticker(stock_code)
    c_data = pfizer.info
    return c_data['logo_url'],c_data['shortName'],c_data['longBusinessSummary'],0,0

@app.callback(
    Output(component_id='data_graph', component_property='children'),
    Input(component_id='show_data_submit', component_property='n_clicks'),
    Input(component_id='my-date-picker-range', component_property='start_date'),
    Input(component_id='my-date-picker-range', component_property='end_date'),
    State(component_id='stock_code', component_property='value')
    )
def update_data_graph(n, start_date, end_date, val):
    if n == 0:
        return [""]
    if val == None:
        raise PreventUpdate
    else:
        if start_date != None:
            df = yf.download(val, str(start_date), str(end_date))
        else:
            df = yf.download(val,period='60d')
    df.reset_index(inplace=True)
    fig = px.line(df,
                  x="Date",
                  y=["Close", "Open"],
                  title="Closing and Openning Price vs Date")
    return [dcc.Graph(figure=fig)]

@app.callback(
    Output(component_id='predict_graph', component_property='children'),
    Input(component_id='stock_forecast_submit', component_property='n_clicks'),
    State(component_id='stock_code', component_property='value')
    )
def update_output_div(n,val):
    if n == 0:
        return [""]
    if val == None:
        raise PreventUpdate
    else:
        fig = predict_price(val, 5)
        return [dcc.Graph(figure=fig)]



if __name__ == '__main__':
    app.run_server()