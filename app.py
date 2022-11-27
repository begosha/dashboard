import pandas as pd
import plotly
import plotly.graph_objects as go
from dash import Dash, html, dcc, Input, Output


layout = plotly.graph_objs.Layout(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font_color="white"
)


### utils
def add_leading_zeros_to_time_periods(x: str) -> str:
    h_mh_m = x.split('h')
    h_m = h_mh_m[1].split('-')

    del h_mh_m[1]
    h_mh_m[1:1] = h_m  # h_mh_m -> h_m_h_m
    h_m_h_m = h_mh_m

    h_m_h_m[0] = h_m_h_m[0].zfill(2)
    h_m_h_m[2] = h_m_h_m[2].zfill(2)

    return "{}h{}-{}h{}".format(*h_m_h_m)

df = pd.read_excel("dashboard.xlsx")

df['Time_Period'] = df['Time_Period'].apply(add_leading_zeros_to_time_periods)
df_success = df[df['Outcome'] == 'Success']
df_failure = df[df['Outcome'] == 'Failure']


def task1() -> None:
    """
    We want to see this data in a graph with a time series legend.
    Then we want to see in the same graph the ratio of success /total calls as a function of date.
    """
    total_calls = df.groupby('Date')['Outcome'].count()
    success_calls = df_success.groupby('Date')['Outcome'].count()
    fail_calls = df_failure.groupby('Date')['Outcome'].count()
    success_ratio = success_calls / total_calls * 100

    # Initialize figure
    fig = go.Figure()

    # Adding bars
    fig.add_trace(go.Scatter(
        x=total_calls.index,
        y=total_calls.values,
        mode='lines+markers',
        name='Number of all calls',
    ))
    fig.add_trace(go.Scatter(
        x=success_calls.index,
        y=success_calls.values,
        mode='lines+markers',
        name='Number of success calls',
    ))
    fig.add_trace(go.Scatter(
        x=fail_calls.index,
        y=fail_calls.values,
        mode='lines+markers',
        name='Number of fail calls',
    ))
    fig.add_trace(go.Scatter(
        x=success_ratio.index,
        y=success_ratio.values,
        mode='lines+markers',
        name='Ratio of calls',
    ))
    fig["layout"]["title"] = "Ratio of success/total calls by date"
    fig["layout"]["xaxis"]["title"] = "Date"
    fig["layout"]["yaxis"]["title"] = "Number of calls"
    fig["layout"]["legend_title"] = "Options"

    fig._layout = layout
    return fig


def task2() -> None:
    """
    We want to see another graph that presents the success and failure by State in the form of a bar graph.
    """

    total_calls = df.groupby('State', as_index=False)['Outcome'].count()
    success_calls = df_success.groupby('State', as_index=False)['Outcome'].count()
    fail_calls = df_failure.groupby('State', as_index=False)['Outcome'].count()

    df_merged = total_calls.merge(success_calls, how='left', on='State', suffixes=('', '_Success'))
    df_merged = df_merged.merge(fail_calls, how='left', on='State', suffixes=('', '_Failure'))

    fig = go.Figure(data=[
        go.Bar(name='Success', x=df_merged['State'], y=df_merged['Outcome_Success']),
        go.Bar(name='Success', x=df_merged['State'], y=df_merged['Outcome_Failure']),
    ])

    return fig


def task3() -> None:
    """
    We want to know the number of succes by Time_Period.
    """
    success_calls = df_success.groupby('Time_Period')['Outcome'].count()

    fig = go.Figure()

    # Adding bars
    fig.add_trace(go.Scatter(
        x=success_calls.index,
        y=success_calls.values,
        mode='lines+markers',
        name='Number of success calls',
    ))

    fig["layout"]["title"] = "Ratio of success/time"
    fig["layout"]["xaxis"]["title"] = "Time Period"
    fig["layout"]["yaxis"]["title"] = "Number of calls"
    fig["layout"]["legend_title"] = "Options"

    fig._layout = layout
    return fig


def task4() -> None:
    """
    We want to see a piechart that displays failure-success-timeout as a percentage.
    """
    failed_success_count = df.groupby("Outcome")["Outcome"].count()
    fig = go.Figure(data=[go.Pie(labels=failed_success_count.index, values=failed_success_count.values)])
    fig["layout"]["title"] = "Success vs Failure"
    fig["layout"]["legend_title"] = "Call outcome"
    fig._layout = layout

    return fig


def task5() -> None:
    """
    -We also want to see a double piechart that displays the total number of actions/ State and number of success / state.
    """
    total_calls = df.groupby('State')['Outcome'].count()
    total_success = df[df['Outcome'] == 'Success'].groupby('State')['Outcome'].count()

    trace1 = go.Pie(
        hole=0.5,
        sort=False,
        direction='clockwise',
        labels=total_success.index,
        values=total_success.values.flatten(),
        textposition='inside',
        marker={'line': {'color': 'white', 'width': 1}}
    )

    trace2 = go.Pie(
        hole=0.7,
        sort=False,
        direction='clockwise',
        values=total_calls.values.flatten(),
        labels=total_calls.index,
        textinfo='label',
        textposition='outside',
        marker={'colors': ['green', 'red', 'blue'],
                'line': {'color': 'white', 'width': 1}}
    )

    fig = go.FigureWidget(data=[trace1, trace2])
    return fig


def task6() -> None:
    """
    We want to see at the end which state was the most ' successful ' in share ratios.
    """
    total_calls = df.groupby('State')['Outcome'].count().reset_index()
    success_calls = df[df['Outcome'] == 'Success'].groupby('State')['Outcome'].count().reset_index()

    dfm = pd.merge(total_calls, success_calls, on='State').fillna(0)
    dfm['ratio'] = dfm['Outcome_y'] / dfm['Outcome_x']
    best = dfm['ratio'].max()
    print('best ratio is ', best)
    best = dfm.loc[dfm['ratio'].idxmax()]
    print('best state is', best)


function_pointers = {
    "success_fail_by_date": task1,
    "success_fail_by_state": task2,
    "success_fail_piechart": task4,
    "double_piechart": task5,
    "success_timeperiod": task3,
    "most_success": task6,
}

app = Dash(__name__)

app.layout = html.Div([

    html.H1("Web Application Dashboards with Dash", style={'text-align': 'center'}),

    dcc.Dropdown(id="slct_chart",
                 options=[
                     {"label": "Ratio of success/total calls by date", "value": "success_fail_by_date"}, # we could read it from the data
                     {"label": "Ratio of success/total calls by state", "value": "success_fail_by_state"},
                     {"label": "Piechart with failure-success-timeout percentage", "value": "success_fail_piechart"},
                     {"label": "Double Piechart", "value": "double_piechart"},
                     {"label": "Ratio of success/time period", "value": "success_timeperiod"},
                 ],
                 multi=False,
                 value="success_fail_by_date",
                 style={'width': "40%"}
                 ),

    html.Div(id='output_container', children=[]),
    html.Br(),
    dcc.Graph(id='my_map', figure={})
])

@app.callback(
    [Output(component_id='output_container', component_property='children'),
     Output(component_id='my_map', component_property='figure')],
    [Input(component_id='slct_chart', component_property='value')]
)
def update_graph(option_slctd):
    container = "The year chosen by user was: {}".format(option_slctd)
    fig = function_pointers[option_slctd]()
    return container, fig


if __name__ == "__main__":
    app.run_server(debug=True)