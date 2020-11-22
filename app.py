#%% libraries
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State
import dash_table
import pandas as pd
import numpy as np

import plotly.express as px
import plotly.io as pio

pio.renderers.default = 'browser'


#%% football field generator
def generate_field():

    #data
    grid_data_x = [10, 10, 10, 20, 20, 30, 30, 40, 40, 50, 50, 60, 60, 70, 70, 80,
                   80, 90, 90, 100, 100, 110, 110, 120, 0, 0, 120, 120]

    grid_data_y = [0, 0, 53.3, 53.3, 0, 0, 53.3, 53.3, 0, 0, 53.3, 53.3, 0, 0, 53.3,
                   53.3, 0, 0, 53.3, 53.3, 0, 0, 53.3, 53.3, 53.3, 0, 0, 53.3]

    # define figure
    fig = go.Figure()

    # layout
    fig.add_trace(
        go.Scatter(x=grid_data_x, y=grid_data_y, mode='lines', line={'color': '#000000'}, showlegend=False,
                   hoverinfo='skip')
    )

    # yard numbers
    for x in range(20, 110, 10):
        numb = x
        if x > 50:
            numb = 120 - x
        fig.add_trace(
            go.Scatter(
                x=[x],
                y=[5],
                text=str(numb - 10),
                mode='text',
                textposition='middle center',
                textfont={'size': 24},
                showlegend=False,
                hoverinfo='skip'
            )
        )
        fig.add_trace(
            go.Scatter(
                x=[x],
                y=[53.3 - 5],
                text=str(numb - 10),
                mode='text',
                textposition='middle center',
                showlegend=False,
                textfont={'size': 24},
                hoverinfo='skip'
            )
        )

    # hashes
    for x in range(11, 110):
        for y in [[0.4, 0.7], [53.0, 52.5], [22.91, 23.57], [29.73, 30.39]]:
            fig.add_trace(
                go.Scatter(
                    x=[x, x],
                    y=y,
                    mode='lines',
                    showlegend=False,
                    line={'color': '#000000'},
                    hoverinfo='skip'
                )
            )

    # plot layout
    fig.update_layout(
        xaxis={
            'showgrid': False,
            'zeroline': False,
            'visible': False
        },
        yaxis={
            'showgrid': False,
            'zeroline': False,
            'visible': False
        },
        height=600,
        plot_bgcolor='#FFFFFF'
    )

    return fig


#%% app config
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

#%% frames datadata
df_plys = pd.read_pickle('./data/all_weeks.pickle')
df_plys['gamePlayId'] = df_plys['gameId'] + df_plys['playId']
get_coords = lambda x: [(idx, ) + i for idx, i in enumerate(x.exterior.coords)] if x is not None else np.nan
df_plys['polygon'] = df_plys['polygon'].apply(get_coords)
df_plys['openness'] = df_plys['openness'].astype('float').round(4) * 100


# polygons
df_poly = df_plys[['gameId', 'playId', 'event', 'nflId', 'polygon']].explode('polygon')
f = ~df_poly['polygon'].isna()
df_poly.loc[f, 'order'] = df_poly.loc[f, 'polygon'].apply(lambda x: x[0])
df_poly.loc[f, 'x'] = df_poly.loc[f, 'polygon'].apply(lambda x: x[1])
df_poly.loc[f, 'y'] = df_poly.loc[f, 'polygon'].apply(lambda x: x[2])
df_poly.dropna(inplace=True)
df_poly.pop('polygon')

#%% players catalog
df_players = pd.read_csv('./data/players.csv')

#%% play summary data
df_plays = pd.read_csv('./data/plays.csv')
df_plays['playLabel'] = 'Q' + df_plays['quarter'].astype('str') + ' ' + df_plays['gameClock']

#%% game summary data
df_games = pd.read_csv('./data/games.csv')
df_games['gameLabel'] = df_games['gameDate'] + ' ' + df_games['homeTeamAbbr'] + ' vs ' + df_games['visitorTeamAbbr']


#%% quarterback data
# load
df_qbs = pd.read_csv('./data/openness.csv')

# top n quarterbacks in the 4th quartile
df_include_in_top = df_plys\
    .loc[df_plys['position']=='QB']\
    .groupby('nflId', as_index=False)\
    .agg({'gamePlayId': 'nunique'})

df_include_in_top = df_include_in_top.loc[df_include_in_top['gamePlayId']>440]

n = 10
f = (df_qbs['event']=='pass_forward')&(df_qbs['targetedReceiver']==1)
df_top_n = \
    df_players[['nflId', 'displayName']]\
    .rename(columns={'displayName': 'displayName_QB'})\
    .merge(df_qbs.loc[f], on='displayName_QB')\
    .merge(df_include_in_top[['nflId']], on='nflId')\
    .groupby('displayName_QB', as_index=False)\
    .agg({'openness': 'mean'})\
    .nlargest(n, 'openness')\
    .rename(columns={'openness': 'Avg. Target Openness', 'displayName_QB': 'displayName'})

# get id for top n quarterbacks
df_top_n = \
    df_players[['nflId', 'displayName']]\
    .merge(df_top_n, on='displayName')\
    .sort_values('Avg. Target Openness', ascending=False)


# total plays per top player
df_n_plays = df_plys\
    .loc[df_plys['event']=='pass_forward']\
    .merge(df_top_n[['nflId']], on='nflId')\
    .groupby('nflId', as_index=False)\
    .agg({'gamePlayId': 'nunique'})\
    .rename(columns={'gamePlayId': 'Total Plays'})

df_nc_plays = df_plys\
    .loc[df_plys['event']=='pass_forward']\
    .merge(df_plays.loc[df_plays['passResult']=='C', ['gameId', 'playId']], on=['gameId','playId'])\
    .merge(df_top_n[['nflId']], on='nflId')\
    .groupby('nflId', as_index=False)\
    .agg({'gamePlayId': 'nunique'})\
    .rename(columns={'gamePlayId': 'Complete Plays'})

df_top = df_top_n\
    .merge(df_n_plays, on='nflId')\
    .merge(df_nc_plays, on='nflId')\
    [['displayName', 'Total Plays', 'Complete Plays', 'Avg. Target Openness']]

#%% top 10 table
def plot_top_10():
    # copy data
    df_tmp = df_top.copy()

    # generate table
    table = dash_table.DataTable(
        id='tab1_top_10',
        columns=[{"name": i, "id": i} for i in df_tmp.columns],
        data=df_tmp.to_dict('records')
    )
    return table

#%% play parameters
playId = 75
gameId = 2018090600
frameId = 36

#%% filter data
f = (df_plys['playId']==playId) &\
    (df_plys['gameId']==gameId) &\
    (df_plys['frameId']==frameId)
df_ply = df_plys.loc[f]

#%% applayout

app.layout = html.Div(children=[
    html.H1(children='Quarterback Openness Visualization'),
    dcc.Tabs(
        id='tabs',
        value='tab-1',
        children=[
            dcc.Tab(label='Leaderboard', value='tab-1'),
            dcc.Tab(label='Plays', value='tab-2')
        ]
    ),
    html.Div(
        id='tab_content'
    )
])


#%% callbacks

@app.callback(
    Output('tab_content', 'children'),
    [Input('tabs', 'value')]
)
def render_content(tab):
    if tab == 'tab-1':
        return html.Div([
            html.H3('Top 10 Quarterbacks'),
            html.P('The quarterbacks (QBs) were ranked by the average openness of the targeted player per play. Only quarterbacks in the 4th quartile by number of plays, QBs with more than 440 plays, were included for the rank.'),
	    plot_top_10(),
            html.H3('Compare Quarterbacks'),
	    html.H5('Avg. EPA vs Avg. Openness'),
            dcc.Dropdown(
                id='tab1_flt_boxplot',
                options=[{'label': i, 'value': i} for i in
                         np.unique(df_plys.loc[df_plys['position'] == 'QB', 'displayName'])],
                multi=True,
                placeholder='Select Quarterback(s)'
            ),
            dcc.Graph(
                id='tab1_boxplot'
            )
        ])
    elif tab == 'tab-2':
        return html.Div([
            html.Div([
                html.Label('Quarterback'),
                dcc.Dropdown(
                    id='det_flt_player',
                    options=[{'label': i, 'value': i} for i in
                             np.unique(df_plys.loc[df_plys['position'] == 'QB', 'displayName'])],
                    placeholder='Select Quarterback'
                )
            ], className='three columns'),
            html.Div([
                html.Label('Game'),
                dcc.Dropdown(
                    id='det_flt_game',
                    placeholder='Select Game'
                )
            ], className='three columns'),
            html.Div([
                html.Label('Play'),
                dcc.Dropdown(
                    id='det_flt_play',
                    placeholder='Select Play'
                )
            ], className='three columns'),
            html.Div([
                html.Label('Event'),
                dcc.Dropdown(
                    id='det_flt_event',
                    placeholder='Select Event'
                )
            ], className='three columns'),
            html.Div([
                html.Div([
                    html.H3('Play Detail'),
                    dash_table.DataTable(
                        id='tab2_play_summary',
                        style_data={
                            'whiteSpace': 'normal',
                            'height': 'auto',
                        }
                    )
                ], className='four columns'),
                html.Div([
                    html.H3('Play Openness Plot'),
                    dcc.Graph(
                        id='det_play_openness'

                    )
                ], className='eight columns')
            ])
        ])


@app.callback(
    Output('det_flt_game', 'options'),
    [Input('det_flt_player', 'value')]
)
def update_tab2_game_filter(displayName):
    # get plays from game
    games = df_plys\
        .loc[df_plys['displayName']==displayName, ['gameId']]\
        .merge(df_games, on='gameId')\
        [['gameId', 'gameLabel']]\
        .drop_duplicates()

    options = [{'label': i.gameLabel, 'value': i.gameId} for i in games.itertuples()]

    return options

@app.callback(
    Output('det_flt_play', 'options'),
    [Input('det_flt_game', 'value')]
)
def update_tab2_play_filter(gameId):
    # get plays from game
    plays = df_plays\
        .loc[df_plays['gameId']==int(gameId), ['gameId', 'playId', 'playLabel']]\
        .drop_duplicates()\
        .dropna(subset=['playLabel'])

    options = [{'label': i.playLabel, 'value': i.playId} for i in plays.itertuples()]

    return options

@app.callback(
    Output('det_flt_event', 'options'),
    Input('det_flt_play', 'value'),
    State('det_flt_game', 'value')
)
def update_tab2_event_filter(playId, gameId):
    # get plays from game
    events = np.unique(df_plys.loc[(df_plys['gameId']==int(gameId))&(df_plys['playId']==int(playId)), 'event'])
    options = [{'label': event, 'value': event} for event in events]

    return options

@app.callback(
    Output('tab1_boxplot', 'figure'),
    [Input('tab1_flt_boxplot', 'value')]
)
def update_tab1_boxplot(quarterBacks):
    if len(quarterBacks)==0:
        return go.Figure()
    else:
        # get quarterbacks and play data
        f = (df_qbs['displayName_QB'].isin(quarterBacks)) & (df_qbs['targetedReceiver']==1) & (df_qbs['event']=='pass_forward')
        df_tmp = df_qbs\
            .loc[f, ['displayName_QB', 'gameId', 'playId', 'openness']]\
            .merge(df_plays[['gameId', 'playId', 'epa']], on=['gameId', 'playId'])\
            .rename(columns={'displayName_QB': 'displayName'})

        # compute avg openness and epa per player
        df_tmp = df_tmp\
            .groupby('displayName', as_index=False)\
            .agg({'openness': 'mean', 'epa': 'mean'})

        # melt average columns
        df_tmp = df_tmp.melt(id_vars='displayName', value_vars=['openness', 'epa'], var_name='metric', value_name='value')

        # generate plot
        colors = {'openness': '#33b5e5', 'epa': '#ffbb33'}
        fig = px.scatter(df_tmp, x='displayName', y='value', color='metric', color_discrete_map=colors)

        fig.update_traces(marker={'size': 15})

        fig.update_layout(
            xaxis={'title': 'Quarterbacks'},
	    yaxis={'title': 'Value'}
        )
        return fig

@app.callback(
    [Output('tab2_play_summary', 'data'), Output('tab2_play_summary', 'columns')],
    [Input('det_flt_event', 'value')],
    [State('det_flt_game', 'value'), State('det_flt_play', 'value')]
)
def update_tab2_play_summary(event, gameId, playId):
    play_filter = (df_plays['gameId'] == gameId) & (df_plays['playId'] == playId)
    cols = ['quarter', 'down', 'yardsToGo', 'possessionTeam', 'epa', 'passResult', 'playDescription']
    df_tmp = df_plays.loc[play_filter, cols].T.reset_index()

    data = df_tmp.to_dict('records')
    columns = [{"name": str(i), "id": str(i)} for i in df_tmp.columns]

    return data, columns

@app.callback(
    Output('det_play_openness', 'figure'),
    [Input('det_flt_event', 'value')],
    [State('det_flt_game', 'value'), State('det_flt_play', 'value')]
)
def update_det_play_openness(event, gameId, playId):
    #print(gameId, playId)
    # play data
    play_filter = \
        (df_plys['gameId']==gameId) &\
        (df_plys['playId']==playId) &\
        (df_plys['event']==event)
    df_ply = df_plys.loc[play_filter].copy()
    f = ~df_ply['openness'].isna()
    df_ply.loc[f, 'openness_str'] = df_ply.loc[f, 'openness'].apply(lambda x: f'{x:0.2f}') + '%'

    # yardline data
    yd_filter = (df_plays['gameId'] == gameId) & (df_plays['playId'] == playId)
    yard_line = df_plays.loc[yd_filter, 'absoluteYardlineNumber'].to_list()[0]

    # offensive team
    possession = df_plays.loc[(df_plays['gameId']==gameId)&(df_plays['playId']==playId), 'possessionTeam'].to_list()[0]
    home = df_games.loc[(df_games['gameId']==gameId), 'homeTeamAbbr'].to_list()[0]
    off_team = 'home' if possession==home else 'away'
    def_team = 'away' if possession==home else 'home'
    df_ply.loc[df_ply['team']==off_team, 'possession'] = 'offense'
    df_ply.loc[df_ply['team']==def_team, 'possession'] = 'defense'

    # polygon data
    poly_filter = \
        (df_poly['gameId']==gameId) &\
        (df_poly['playId']==playId) &\
        (df_poly['event']==event)
    df_polygons = df_poly.loc[poly_filter].merge(df_ply[['nflId', 'openness', 'openness_str']], on='nflId').copy()
    df_polygons.sort_values(['openness', 'order'], ascending=False, inplace=True)

    # rotate if play direction is to the left
    if df_ply['playDirection'].to_list()[0]=='left':
        df_ply['x'] = 120 - df_ply['x']
        df_ply['y'] = 160/3 - df_ply['y']
        yard_line = 120 - yard_line
        df_polygons['x'] = 120 - df_polygons['x']
        df_polygons['y'] = 160/3 - df_polygons['y']

    # create figure
    fig = generate_field()

    # plot initial yard line
    fig.add_shape(
        type='line',
        x0=yard_line,
        x1=yard_line,
        y0=0,
        y1=160/3,
        layer='above',
        line={'color': '#9e9e9e', 'width': 3}
    )

    # plot players
    f = df_ply['displayName'] != 'Football'
    colors = {'offense': '#33b5e5', 'defense': '#ff4444'}
    for poss in ['offense', 'defense']:
        df_tmp = df_ply.loc[(f) & (df_ply['possession']==poss)]
        fig.add_trace(
            go.Scatter(
                x=df_tmp['x'],
                y=df_tmp['y'],
                text='Player ' + df_tmp['displayName'] + '<br>' + 'Openness: ' + df_tmp['openness_str'],
                name=poss,
                mode='markers',
                marker={'size': 15, 'color': colors[poss]}
            )
        )

    # plot football
    df_tmp = df_ply.loc[~f]
    fig.add_trace(
        go.Scatter(
            x=df_tmp['x'],
            y=df_tmp['y'],
            name='Football',
            mode='markers',
            marker={'size': 15, 'color': '#00C851'}
        )
    )

    # plot polygons
    for player in df_polygons['nflId'].unique():
        df_tmp = df_polygons.loc[df_polygons['nflId']==player]
        #print(df_tmp)
        if df_tmp['openness'].isna().all():
            line={'width': 1, 'color': '#000000'}
            showlegend=False
            name=None
        else:
            line = {'width': 3}
            showlegend=True
            name = df_tmp['openness_str'].to_list()[0]

        #print(line, showlegend, name)
        fig.add_trace(
            go.Scatter(
                x=df_tmp['x'],
                y=df_tmp['y'],
                mode='lines',
                line=line,
                showlegend=showlegend,
                name=name
            )
        )

    fig.update_layout(
        legend_title_text='Teams and Openness %'
    )

    return fig

#%%
if __name__ == '__main__':
    app.run_server(debug=False)
