import dash
from dash.dependencies import Output, Input, State
from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
import numpy as np

Club = 'Manchester_United'
League = 'English_Premier_League'
Club1 = 'Manchester_City'
League1 = 'English_Premier_League'
categories = ['pace', 'shooting', 'passing', 'dribbling', 'defending', 'physic']

 
def parsecsv():
    df=pd.read_csv("./data-sets/players_22.csv")
    df = df[['short_name', 'player_positions', 'club_name', 'league_name','league_level', 'nationality_name', 'club_joined', 'overall' ,'potential', 'wage_eur', 'age', 'pace', 'shooting', 'passing', 'dribbling', 'defending', 'physic']]
    df = df.query('league_level == 1')
    df = df[(df['league_name'] == 'French Ligue 1') | (df['league_name'] == 'German 1. Bundesliga') | (df['league_name'] == 'Spain Primera Division') | (df['league_name'] == 'English Premier League') | (df['league_name'] == 'Italian Serie A')]
    df['league_name'] = df['league_name'].str.replace(' ', '_')
    df['club_name'] = df['club_name'].str.replace(' ', '_')

    return df

# import and parse csv
df = parsecsv()
df_allpositions = (
    df.assign(positions=df['player_positions'].str.split(','))
    .explode('positions')
    .reset_index(drop=True)
)
ddLeagues = df["league_name"].unique()
df_allpositions['positions'] = df_allpositions['positions'].str.replace(' ', '')
all_positions = df_allpositions['positions'].unique()

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
app.layout = html.Div(
    [
        html.H2('FIFA23 Club Comparison', style={'paddingLeft':'20px', 'paddingTop':'20px'}),
        html.Div([
            html.P('League:'),
            dcc.Dropdown(
                id="dropdown_league",
                value=League,
                options=ddLeagues
            ),
        ], className="dash-bootstrap"),
        html.Div([
            html.P('Club:'),
            dcc.Dropdown(
                id="dropdown_team",
                value=Club
            ),
        ], className="dash-bootstrap"),
        html.Div([
            html.P('Other League:'),
            dcc.Dropdown(
                id="dropdown_league1",
                value=League1,
                options=ddLeagues
            ),
        ], className="dash-bootstrap"),
        html.Div([
            html.P('Other Club:'),
            dcc.Dropdown(
                id="dropdown_team1",
                value=Club1
            ),
        ], className="dash-bootstrap"),
        html.Div([
            html.P('Positions:'),
            dcc.Dropdown(
                id="dropdown_positions",
                multi=True,
                options=all_positions
            ),
        ], className="dash-bootstrap"),
        html.Div([
            html.P('Player:'),
            dcc.Dropdown(
                id="dropdown_players"
            ),
        ], className="dash-bootstrap"),
        html.Div(
            [      
                dcc.Loading(
                    id="loading-1",
                    children=[
                        html.Div([
                            html.P('Score: ', style=dict(padding='10px', opacity=0.5)),
                            html.P(id='score_team', style=dict(marginRight='50px', padding='10px', color='blue')),
                            html.H3(id='label_team', style=dict(color='blue')),
                            html.P('VS', style=dict(padding='10px')),
                            html.H3(id='label_team1', style=dict(color='lightseagreen')),  
                            html.P('Score: ', style=dict(padding='10px', marginLeft='50px', opacity=0.5)),
                            html.P(id='score_team1', style=dict(padding='10px', color='lightseagreen'))  
                        ], style=dict(display="flex", width="100%", justifyContent='center', alignCenter ='center'))
                    ],
                    type="circle"
                )                
            ],
        ),
        html.Strong(html.Label(id="graphError")),
        html.Div(
            [
                html.Div(
                    [
                        dcc.Loading(
                            id="loading-2",
                            children=[dcc.Graph(id="scatter_team", animate=False, responsive=True)],
                            type="circle"
                        )
                    ],
                    style=dict(width="34%", height='100%', padding='15px')
                ),
                html.Div(
                    [
                        dcc.Loading(
                            id="loading-3",
                            children=[dcc.Graph(id="radar_team", animate=False, responsive=True)],
                            type="circle"
                        )
                    ],
                    style=dict(width="66%", height='100%', padding='15px')
                ),                          
            ],
            style=dict(display="flex", width="100%", height='80vh'),
        ),
        html.Div(
            [
                html.Div(id="table1", style=dict(padding="30px")),
                html.Div(id="table2", style=dict(padding="30px"))
            ],
            style=dict(display="flex", width="100%", height='100%')
        )
    ]
)

@app.callback(
    [ 
        Output('scatter_team',  "figure"),
        Output('radar_team',  "figure"),
        Output("table1", "children"),
        Output("table2", "children"),
        Output("dropdown_team", "options"),
        Output("dropdown_team1", "options"),
        Output("dropdown_players", "options"),
        Output("dropdown_team", "value"),
        Output("dropdown_league", "value"),
        Output("dropdown_team1", "value"),
        Output("dropdown_league1", "value"),
        Output("label_team", "children"),
        Output("label_team1", "children"),
        Output("score_team", "children"),
        Output("score_team1", "children"),
        Output("graphError", "children")
    ],
    [
        Input("dropdown_team", "value"),
        Input("dropdown_team1", "value"),
        Input("dropdown_league", "value"),
        Input("dropdown_league1", "value"),
        Input("dropdown_players", "value"),
        Input("dropdown_positions", "value")
    ]
)
def updateLine(
    ddv_club,
    ddv_club1,
    ddv_league,
    ddv_league1,
    ddv_player,
    ddv_positions
):

    # dropdown value
    ddv_league = League if ddv_league == None else ddv_league
    ddv_league1 = League1 if ddv_league1 == None else ddv_league1
    ddv_club = Club if ddv_club == None else ddv_club
    ddv_club1 = Club1 if ddv_club1 == None else ddv_club1

    # dropdowns
    ddClubs = df[df['league_name'] == ddv_league]["club_name"].unique()
    ddClubs1 = df[df['league_name'] == ddv_league1]["club_name"].unique()
    ddPlayers = df[(df['club_name'] == ddv_club) | (df['club_name'] == ddv_club1)]["short_name"].unique()
    
    # filter dataframes to suit graph rendering
    df_team = df[df['club_name'] == ddv_club]
    df_team1 = df[df['club_name'] == ddv_club1]
    df_notsel = df[(df['club_name'] != ddv_club) & (df['club_name'] != ddv_club1)]
    df_sel = df[(df['club_name'] == ddv_club) | (df['club_name'] == ddv_club1)]
    df_highPo = df_sel[df_sel['potential'] >= 90]
    df_player = df_sel[df_sel['short_name'] == ddv_player]
    print(df_player)

    positions = list(df_allpositions[df_allpositions['short_name'] == ddv_player]['positions']) # retrieve list of positions player plays in 
    df_positions = df_allpositions[df_allpositions['positions'].isin(positions)]
    df_positions = df_positions.drop_duplicates(subset=['short_name'], keep='first') # dataframe of all players from all clubs who play in the same position(s)

    # reusable axis and grpah template
    axis_template = dict(
                title = dict(standoff= 20),
                color='rgba(255, 255, 255, 1)',
                gridcolor= 'rgba(255, 255, 255, 0.3)', 
                gridwidth=1
            )

    chart_template = dict( 
        layout=go.Layout(
            autosize=True,
            margin=dict(l=40, r=20, t=30, b=40),
            plot_bgcolor='rgba(0, 0, 0, 0)',
            paper_bgcolor='rgba(0, 0, 0, 0)',
            font=dict(color='white', family='Lato'),
            xaxis= axis_template,
            yaxis= axis_template,
            legend=dict(
                orientation="h",
                yanchor="top",
                y=1
            )
        )
    )

    # scatter graph
    fig = go.Figure()

    # scatter points for players from not-selected clubs with/without selected position(s)
    if((ddv_player == None) & ((ddv_positions == []) | (ddv_positions == None))):
        DF = df_notsel
        name = 'Player from other club'
    elif ((ddv_player != None) & ((ddv_positions == []) | (ddv_positions == None))):
        DF= df_positions
        name = 'All players in same position(s) as selected player: ' + ', '.join(positions)
    elif ((ddv_player == None) & (ddv_positions != []) & (ddv_positions != None)):
        DF = df_allpositions[(df_allpositions['positions'].isin(ddv_positions)) & (df_allpositions['club_name'] != ddv_club) & (df_allpositions['club_name'] != ddv_club1)]
        name = 'All players with selected position(s): ' + ', '.join(ddv_positions)
    elif ((ddv_player != None) & (ddv_positions != []) & (ddv_positions != None)):
        DF= df_positions[(df_positions['club_name'] != ddv_club) & (df_positions['club_name'] != ddv_club1)]
        name = 'All players in same position(s) as selected player: ' + ', '.join(positions)

    fig.add_trace(
        go.Scattergl(
            x=DF["wage_eur"],
            y=DF["overall"],
            name=name,
            text=DF['short_name'],
            customdata=DF['age'],
            marker=dict(color='white', size=3, opacity=0.3),
            showlegend=True,
            hoverinfo='none'
        )
    )

    # scatter points only for players with high potential from both clubs
    fig.add_trace(
        go.Scatter(
            x=df_highPo["wage_eur"],
            y=df_highPo["overall"],
            name="potential >= 90",
            text=df_highPo['short_name'],
            customdata=df_highPo['age'],
            marker_size=[x/3 for x in df_highPo['age']],
            marker = dict(
                color='yellow',
                symbol='circle-open', 
                opacity=1
            ),
            showlegend=True,
            hoverinfo='none'
        )
    )

    # scatter points for all players from both clubs
    fig.add_trace(
        go.Scatter(
            x=df_sel["wage_eur"],
            y=df_sel["overall"],
            name="potential < 90", # will show as trace label in legend
            text=df_sel['short_name'], # will show in tooltip content, or as marker label if mode='circle+text'
            customdata=df_sel['age'], # declare extra data for tooltip content
            marker_size=[x/4 for x in df_sel['age']], # sized based on age
            marker = dict(
                color=np.where(df_sel['club_name'] == ddv_club, 'blue', 'lightseagreen'), # color code based on club
                line=dict(width=0), # no marker stroke
                symbol='circle', 
                opacity=0.8
            ),
            showlegend=False,
            hovertemplate=
            "<b>%{text}</b><br><br>" +
            "Weekly wage: %{x}<br>" +
            "Overall Score: %{y}<br>" +
            "Age: %{customdata}" +
            "<extra></extra>"
            )
    )

    # scatter points only for players from both clubs with selected position(s)
    if((ddv_positions != []) & (ddv_positions != None)):
        df_sel_allpositions = df_allpositions[(df_allpositions['club_name'] == ddv_club) | (df_allpositions['club_name'] == ddv_club1)]
        df_fpos = df_sel_allpositions[df_sel_allpositions['positions'].isin(ddv_positions)]
        df_fpos = df_fpos.drop_duplicates(subset=['short_name'], keep='first')
        fig.add_trace(
            go.Scatter(
                x=df_fpos["wage_eur"],
                y=df_fpos["overall"],
                name=', '.join(ddv_positions),
                text=df_fpos['short_name'],
                customdata=df_fpos['age'],
                marker_size=11,
                marker = dict(
                    color=np.where(df_fpos['club_name'] == ddv_club, 'blue', 'lightseagreen'), 
                    line=dict(width=1.5, color='white'),
                    symbol='diamond', 
                    opacity=1
                ),
                showlegend=True,
                hoverinfo='none'
            )
        )

    # single point for selected player
    if len(df_player) != 0:
        fig.add_trace(
            go.Scatter(
                x=df_player["wage_eur"],
                y=df_player["overall"],
                name=ddv_player,
                text=df_player['short_name'],
                customdata=df_player['age'],
                marker_size=10,
                marker = dict(
                    color='magenta', 
                    symbol='circle', 
                    line=dict(width=0),
                    opacity=1
                ),
                showlegend=False,
                hoverinfo='none'
            )
        )

    # common attributes for all traces
    fig.update_traces(
        mode='markers'
    ) 

    fig.update_layout(
        title="Wages vs Overall Score",
        xaxis_zeroline=False, 
        template=chart_template
    )
    fig.update_xaxes(title_text = "Weekly wage (in euros)")
    fig.update_yaxes(title_text = "Score", range=[50, 100])

    #violin plot
    fig1 = go.Figure()
    
    for i in range(0,len(categories)):
        # curve only for players from not-selected clubs with/without selected position(s)
        if((ddv_player == None) & ((ddv_positions == []) | (ddv_positions == None))):
            print('all')
            DF = df
            name = 'All players'
        elif ((ddv_player != None) & ((ddv_positions == []) | (ddv_positions == None))):
            print('player selected, no positions')
            DF= df_positions
            name = 'All players in same position(s) as selected player: ' + ', '.join(positions)
        elif ((ddv_player == None) & (ddv_positions != []) & (ddv_positions != None)):
            print('no player selected, positions selected')
            DF = df_allpositions[df_allpositions['positions'].isin(ddv_positions)]
            DF = DF.drop_duplicates(subset=['short_name'], keep='first')
            name = 'All players with selected position(s): ' + ', '.join(ddv_positions)
        elif ((ddv_player != None) & (ddv_positions != []) & (ddv_positions != None)):
            print('player selected, positions selected')
            DF= df_positions
            name = 'All players in same position(s) as selected player: ' + ', '.join(positions)

        fig1.add_trace(go.Violin(
            x=[categories[i]] * len(DF),
            y=DF[categories[i]],
            legendgroup=name, 
            scalegroup=name,  
            name=name, 
            fillcolor='rgba(255, 255, 255, 0.3)',
            line_width=0,
            points=False,
            showlegend=True if i==0 else False
        ))

        # curve+points for players from club 1
        fig1.add_trace(violin_trace(
            df_team, 
            categories[i],
            ddv_club, 
            dict(side='negative', pointpos=-1, fillcolor='rgba(0,0,255,0.5)'),
            dict(color='blue', size=4, opacity= 0.6),
            'all'
        ))
        # curve+points for players from club 2
        fig1.add_trace(violin_trace(
            df_team1, 
            categories[i],
            ddv_club1, 
            dict(side='positive', pointpos=1, fillcolor='rgba(32,178,170,0.5)'), 
            dict(color='lightseagreen', size=4, opacity= 0.6),
            'all'
        ))

        if((ddv_positions != []) & (ddv_positions != None)):
            df_sel_allpositions = df_allpositions[df_allpositions['club_name'] == ddv_club]
            df_fpos = df_sel_allpositions[df_sel_allpositions['positions'].isin(ddv_positions)]
            df_fpos = df_fpos.drop_duplicates(subset=['short_name'], keep='first')
            # points only for players from club 1 with selected position(s)
            fig1.add_trace(violin_trace(
                df_fpos, 
                categories[i],
                ddv_club + '-' + ', '.join(ddv_positions), 
                dict(side='negative', pointpos=-1, fillcolor='rgba(0,0,0,0)'), 
                dict(color='blue', size=9, opacity= 1, symbol='diamond', line=dict(width=1.5, color='white')),
                'none'
            ))

            df_sel_allpositions = df_allpositions[df_allpositions['club_name'] == ddv_club1]
            df_fpos1 = df_sel_allpositions[df_sel_allpositions['positions'].isin(ddv_positions)]
            df_fpos1 = df_fpos1.drop_duplicates(subset=['short_name'], keep='first')
            # points only for players from club 2 with selected position(s)
            fig1.add_trace(violin_trace(
                df_fpos1, 
                categories[i],
                ddv_club1 + '-' + ', '.join(ddv_positions), 
                dict(side='positive', pointpos=1, fillcolor='rgba(0,0,0,0)'), 
                dict(color='lightseagreen', size=9, opacity= 1, symbol='diamond', line=dict(width=1.5, color='white')),
                'none'
            ))

        if len(df_player) != 0:
            # points only for selected player
            fig1.add_trace(violin_trace(
                df_player, 
                categories[i],
                ddv_player, 
                dict(side='both', pointpos=-0.05, fillcolor='rgba(0,0,0,0)'), 
                dict(size=10, opacity= 1, color='magenta'),
                'none'
            ))

    fig1.update_traces(
        meanline_visible=True,
        spanmode = 'hard',
        hovertemplate=
            "<b>%{text}</b><br><br>" +
            "Category: %{x}<br>" +
            "Score: %{y}<br>" +
            "Positions: %{customdata}" +
            "<extra></extra>",
    ) 

    fig1.update_layout(
        title="Distribution of scores among traits",
        violingap=0, 
        violingroupgap=0.3, 
        template=chart_template,
    )
    fig1.update_yaxes(title_text = "Score", range=[10,100])

    # Error
    if len(df_team) == 1:
        errorMSG = "! Query contains only one record. Cannot Plot"
    else:
        errorMSG = ""

    # table
    tbl = createTable(df_team, 'blue')
    tbl1 = createTable(df_team1, 'lightseagreen')

    # average team scores for header 
    avg_team_score = "{:.1f}".format(sum(df_team['overall']) / len(df_team))
    avg_team1_score = "{:.1f}".format(sum(df_team1['overall']) / len(df_team1))

    # team names for header
    club_label = ddv_club.replace('_', ' ')
    club1_label = ddv_club1.replace('_', ' ')

    return (
        fig,
        fig1,
        tbl,
        tbl1,
        ddClubs,
        ddClubs1,
        ddPlayers,
        ddv_club,
        ddv_league,
        ddv_club1,
        ddv_league1,
        club_label,
        club1_label,
        avg_team_score,
        avg_team1_score,
        errorMSG
    )

def violin_trace(df, category, name, violin, marker, hover):
    return go.Violin(
        x=[category] * len(df),
        y=df[category],
        name=name, 
        side=violin['side'],
        pointpos=violin['pointpos'],
        text=df['short_name'],
        customdata=df['player_positions'],
        fillcolor=violin['fillcolor'],
        line_width=0,
        points='all',
        jitter=0.1,
        marker=marker,
        showlegend=False,
        hoveron= 'points' if hover == 'none' else "violins+points",
        hoverinfo=hover
    )

def createTable(df, color):  
    tbl = dash_table.DataTable(
        data=df[['short_name', 'nationality_name', 'age', 'player_positions', 'overall' ,'potential', 'club_joined', 'wage_eur']].to_dict('records'),
        columns=[{"name": 'name', "id": "short_name"}, {"name": 'nationality', "id": "nationality_name"}, {"name": 'age', "id": "age"}, {"name": 'positions', "id": "player_positions"}, {"name": 'overall', "id": "overall"}, {"name": 'potential', "id": "potential"}, {"name": 'joined since', "id": "club_joined"}, {"name": 'weekly wage (in euros)', "id": "wage_eur"}],
        page_action='none',
        sort_action="native",
        sort_mode="multi",
        fixed_rows = {'headers': True },
        style_table={ 'width': '45.7vw', 'height': '400px', 'overflowX': 'auto', 'overflowY': 'auto'},
        style_data={ 'border': '1px solid white'},
        style_cell={
            'backgroundColor': 'rgb(34, 34, 34)',
            'color': 'white',
            'padding': '5px',
            'font-family':'Lato',
            'minWidth': '110px'
        },
        style_header={
            'backgroundColor': color,
            'fontWeight': 'bold',
            'color': 'white',
            'font-family':'Lato',
            'minWidth': '110px'
        },
    )
    return tbl

server = app.server

if __name__ == "__main__":
    app.run_server(port=8080, debug=True)