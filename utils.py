import yfinance as yf
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
import numpy as np
from sklearn.svm import SVR
from datetime import date, timedelta
import plotly.express as px
import plotly.graph_objects as go

def predict_price(stock_code,n_days):
    df = yf.download(stock_code, period='60d')
    df.reset_index(inplace=True)
    df['Day'] = df.index

    days = list()
    for i in range(len(df.Day)):
        days.append([i])
    X = days
    Y = df[['Close']]
    x_train, x_test, y_train, y_test = train_test_split(X,Y,test_size=0.1,shuffle=False)
    gsc = GridSearchCV(
        estimator=SVR(kernel='rbf'),
        param_grid={
            'C': [0.001, 0.01, 0.1, 1, 100, 1000],
            'epsilon': [
                0.0001, 0.0005, 0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1, 5, 10,
                50, 100, 150, 1000
            ],
            'gamma': [0.0001, 0.001, 0.005, 0.1, 1, 3, 5, 8, 40, 100, 1000]
        },
        cv=5,
        scoring='neg_mean_absolute_error',
        verbose=0,
        n_jobs=-1)
    grid_result = gsc.fit(x_train, y_train.values.ravel())
    best_params = grid_result.best_params_
    best_svr = SVR(kernel='rbf',
                C=best_params["C"],
                epsilon=best_params["epsilon"],
                gamma=best_params["gamma"],
                max_iter=-1)

    rbf_svr = best_svr
    rbf_svr.fit(x_train, y_train.values.ravel())

    output_days = list()
    n_days =5
    for i in range(1,n_days+1):
        output_days.append([i + x_test[-1][0]])
    dates = []
    current = date.today()
    for i in range(n_days):
        current += timedelta(days=1)
        dates.append(current)
    
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=rbf_svr.predict(output_days),
            mode='lines+markers',
            name='data'))
    fig.update_layout(
        title="Predicted Close Price of next " + str(n_days) + " days"+" for "+str(stock_code),
        xaxis_title="Date",
        yaxis_title="Closed Price",
        # legend_title="Legend Title",
    )

    return fig
