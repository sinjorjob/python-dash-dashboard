import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd

terr2 = pd.read_csv('modified_globalterrorismdb_0718dist.csv')
# Create dictionary of list
terr2_list = terr2[['country_txt', 'latitude', 'longitude']]
dict_of_locations = terr2_list.set_index('country_txt')[['latitude', 'longitude']].T.to_dict('dict')


app = dash.Dash(__name__, meta_tags=[
                {"name": "viewport", "content": "width=device-width"}], 
                external_stylesheets=['https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700&display=swap'])


app.layout = html.Div([
    html.Div([
        html.Div([
            html.Div([
                html.H3('国際テロリズムデータベース', style={
                        'margin-bottom': '0px', 'color': 'white'}),
                html.H5('(1970～2017年)',
                      style={'margin-top': '0px', 'color': 'white'}),
            ])

        ], className='six column', id='title')
    ], id='header', className='row flex-display', style={'margin-botttom': '25px'}),
    
    html.Div([
        html.Div([
            dcc.Graph(id='map_chart', config={'displayModeBar': 'hover'})

        ], className='create_container twelve columns'),

    ], className='row flex-display'),
    
    html.Div([
        html.Div([
            html.P('地域の選択', className='fix_label', style={'color': 'white'}),
            dcc.Dropdown(id='w_countries',
                         multi=False,
                         searchable=True,
                         value='South Asia',
                         placeholder='Select Region',
                         options=[{'label': c, 'value': c} for c in (terr2['region_txt'].unique())], className='dcc_compon'),  # 地域のリストを取得


            html.P('国名の選択', className='fix_label', style={'color': 'white'}),
            dcc.Dropdown(id='w_countries1',
                         multi=False,
                         searchable=True,
                         placeholder='Select Country',
                         options=[], className='dcc_compon'),

            html.P('年度を選択', className='fix_label', style={'color': 'white'}),
            dcc.RangeSlider(id='select_years',
                            min=1970,
                            max=2017,
                            dots=False,
                            value=[2010, 2017],
                            marks={str(year): str(year)
                                   for year in range(1970, 2018, 10)},
                            )

        ], className='create_container three columns'),

        html.Div([
            dcc.Graph(id='bar_chart', config={'displayModeBar': 'hover'})

        ], className='create_container six columns'),
        
        html.Div([
            dcc.Graph(id='pie_chart', config={'displayModeBar': 'hover'})

        ], className='create_container three columns'),
    
    ], className='row flex-display')

], id='mainContainer', style={'display': 'flex', 'flex-direction': 'column'})

#マップの表示
@app.callback(Output('map_chart', 'figure'),
              [Input('w_countries','value')],
              [Input('w_countries1','value')],
              [Input('select_years','value')])
def update_graph(w_countries, w_countries1, select_years):
    # データをグループ化し、特定の条件を満たすデータを選択
    terr8 = terr2.groupby(['region_txt', 'country_txt', 'provstate', 'city', 'iyear', 'latitude', 'longitude'])[['nkill', 'nwound', 'attacktype1']].sum().reset_index()
    terr9 = terr8[(terr8['region_txt'] == w_countries) &
                 (terr8['country_txt'] == w_countries1) &
                 (terr8['iyear'] >= select_years[0]) & (terr8['iyear'] <= select_years[1])]
    # 地図を特定の位置にズーム
    if w_countries1:
        zoom=3   # ズームの設定
        zoom_lat = dict_of_locations[w_countries1]['latitude']  # ズームする緯度
        zoom_long = dict_of_locations[w_countries1]['longitude']  # ズームする経度


    return {
        'data': [go.Scattermapbox(
            lon=terr9['longitude'],
            lat=terr9['latitude'],
            mode='markers',
            marker=go.scattermapbox.Marker(size=terr9['nwound'], #負傷者数に応じてサイズを調整
                                           color=terr9['nwound'],#負傷者数に応じて色を調整
                                           colorscale='HSV',
                                           showscale=False,
                                           sizemode='area',
                                           opacity=0.3),
            hoverinfo='text',
            hovertext=
            '<b>Region</b>: ' + terr9['region_txt'].astype(str) + '<br>' +
            '<b>Country</b>: ' + terr9['country_txt'].astype(str) + '<br>' +
            '<b>Province/State</b>: ' + terr9['provstate'].astype(str) + '<br>' +
            '<b>City</b>: ' + terr9['city'].astype(str) + '<br>' +
            '<b>Year</b>: ' + terr9['iyear'].astype(str) + '<br>' +
            '<b>Death</b>: ' + [f'{x:,.0f}' for x in terr9['nkill']] + '<br>' +
            '<b>Injured</b>: ' + [f'{x:,.0f}' for x in terr9['nwound']] + '<br>' +
            '<b>Attack</b>: ' + [f'{x:,.0f}' for x in terr9['attacktype1']] + '<br>'


        )],

        'layout': go.Layout(
            hovermode='x',
            paper_bgcolor='#010915',
            plot_bgcolor='#010915',
            margin=dict(r=0, l =0, b = 0, t = 0),
            mapbox=dict(
                accesstoken='pk.eyJ1IjoicXM2MjcyNTI3IiwiYSI6ImNraGRuYTF1azAxZmIycWs0cDB1NmY1ZjYifQ.I1VJ3KjeM-S613FLv3mtkw',
                center = go.layout.mapbox.Center(lat=zoom_lat, lon=zoom_long),
                style='satellite-streets',
                # style='open-street-map',
                zoom=zoom,
            ),
            autosize=True



        )
    }
    
    
@app.callback(Output('w_countries1', 'options'),
              [Input('w_countries', 'value')])
def update_country(w_countries):
    terr3 = terr2[terr2['region_txt'] == w_countries]
    return [{'label': i, 'value': i} for i in terr3['country_txt'].unique()]


# Countryリストのデフォルト値を返す
@app.callback(Output('w_countries1', 'value'),
              [Input('w_countries1', 'options')])
def update_country(w_countries1):
    return [k['value'] for k in w_countries1][0]


@app.callback(Output('bar_chart', 'figure'),
              [Input('w_countries', 'value')],
              [Input('w_countries1', 'value')],
              [Input('select_years', 'value')])
def update_graph(w_countries, w_countries1, select_years):
    terr5 = terr2.groupby(['region_txt', 'country_txt', 'iyear'])[
        ['nkill', 'nwound', 'attacktype1']].sum().reset_index()
    terr6 = terr5[(terr5['region_txt'] == w_countries) &
                  (terr5['country_txt'] == w_countries1) &
                  (terr5['iyear'] >= select_years[0]) & (terr5['iyear'] <= select_years[1])]

    return {
        'data': [go.Scatter(
            x=terr6['iyear'],
            y=terr6['nkill'],
            mode='markers+lines',
            name='死亡',
            line=dict(shape='spline', smoothing=1.3, width=3, color='#16FEC7'),
            marker=dict(color='white', size=10, symbol='circle',
                        line=dict(color='#16FEC7', width=2)),
            hoverinfo='text',
            hovertext='<b>地域名</b>: ' + terr6['region_txt'].astype(str) + '<br>' +
            '<b>国名</b>: ' + terr6['country_txt'].astype(str) + '<br>' +
            '<b>年度</b>: ' + terr6['iyear'].astype(str) + '<br>' +
            '<b>死亡者数</b>: ' +
            [f'{x:,.0f}' for x in terr6['nkill']] + '<br>'
        ),
            go.Bar(
            x=terr6['iyear'],
            y=terr6['attacktype1'],
            text=terr6['attacktype1'],
            texttemplate='%{text:,0f}',
            textposition='auto',
            name='攻撃',
            marker=dict(color='orange'),
            hoverinfo='text',
            hovertext='<b>地域名</b>: ' + terr6['region_txt'].astype(str) + '<br>' +
            '<b>国名</b>: ' + terr6['country_txt'].astype(str) + '<br>' +
            '<b>年度</b>: ' + terr6['iyear'].astype(str) + '<br>' +
            '<b>攻撃</b>: ' +
            [f'{x:,.0f}' for x in terr6['attacktype1']] + '<br>'
        ),
            go.Bar(
            x=terr6['iyear'],
            y=terr6['nwound'],
            text=terr6['nwound'],
            texttemplate='%{text:,.0f}',
            textposition='auto',
            name='負傷者',
            marker=dict(color='#9C0C38'),
            hoverinfo='text',
            hovertext='<b>地域名</b>: ' + terr6['region_txt'].astype(str) + '<br>' +
                '<b>国名</b>: ' + terr6['country_txt'].astype(str) + '<br>' +
                '<b>年度</b>: ' + terr6['iyear'].astype(str) + '<br>' +
                '<b>負傷者</b>: ' +
            [f'{x:,.0f}' for x in terr6['nwound']] + '<br>'

        ),



        ],

        'layout': go.Layout(
            barmode = 'stack',  #棒グラフのフォーマット指定（積み上げグラフ）
            title={'text': '死亡、負傷者、攻撃: ' + (w_countries1) + ' ' + '<br>（'
                   + ' ~ ' .join([str(y) for y in select_years]) + '年）</br>',
                   'y': 0.93,
                   'x': 0.5,
                   'xanchor': 'center',
                   'yanchor': 'top'},
            titlefont={'color': 'white',
                       'size': 20},
            font=dict(family='sans-serif',
                      color='white',
                      size=12),
            hovermode='closest',
            paper_bgcolor='#1f2c56',  # グラフの背景色
            plot_bgcolor='#1f2c56',  # グラフの背景色
            legend={'orientation': 'h',
                    'bgcolor': '#1f2c56',
                    'xanchor': 'center', 'x': 0.5, 'y': -0.7},
            margin=dict(r=0),
            xaxis=dict(title='<b>年度</b>',
                       tick0 = 0,
                       dtick = 1,
                       color='white',
                       showline=True,
                       showgrid=True,
                       showticklabels=True,
                       linecolor='white',
                       linewidth=1,
                       ticks='outside',
                       tickfont=dict(
                           family='Aerial',
                           color='white',
                           size=12
                       )),
            yaxis=dict(title='<b>死亡、負傷者、攻撃</b>',
                       color='white',
                       showline=True,
                       showgrid=True,
                       showticklabels=True,
                       linecolor='white',
                       linewidth=1,
                       ticks='outside',
                       tickfont=dict(
                           family='Aerial',
                           color='white',
                           size=12
                       )
                       )


        )
    }


@app.callback(Output('pie_chart', 'figure'),
              [Input('w_countries','value')],
              [Input('w_countries1','value')],
              [Input('select_years','value')])
def update_graph(w_countries, w_countries1, select_years):
    terr7 = terr2.groupby(['region_txt', 'country_txt', 'iyear'])[['nkill', 'nwound', 'attacktype1']].sum().reset_index()
    death = terr7[(terr7['region_txt'] == w_countries) &
                  (terr7['country_txt'] == w_countries1) &
                  (terr7['iyear'] >= select_years[0]) & (terr7['iyear'] <= select_years[1])]['nkill'].sum()
    injured = terr7[(terr7['region_txt'] == w_countries) &
                  (terr7['country_txt'] == w_countries1) &
                  (terr7['iyear'] >= select_years[0]) & (terr7['iyear'] <= select_years[1])]['nwound'].sum()
    attack = terr7[(terr7['region_txt'] == w_countries) &
                    (terr7['country_txt'] == w_countries1) &
                    (terr7['iyear'] >= select_years[0]) & (terr7['iyear'] <= select_years[1])]['attacktype1'].sum()
    colors = ['#FF00FF', '#9C0C38', 'orange']

    return {
        'data': [go.Pie(
            labels=['死者数の合計', '負傷者数の合計', '攻撃者の合計'],
            values=[death, injured, attack],
            marker=dict(colors=colors),
            hoverinfo='label+value+percent',
            textinfo='label+value',
            # hole=.7,
            rotation=45,
            # insidetextorientation= 'radial'

        )],

        'layout': go.Layout(
            title={'text': '死亡、負傷、攻撃: ' + '<br>' + (w_countries1) + '</br>(' + ' ' +
                   ' ～ ' .join([str(y) for y in select_years]) + '年)',
                   'y': 0.93,
                   'x': 0.5,
                   'xanchor': 'center',
                   'yanchor': 'top'},
            titlefont={'color': 'white',
                       'size': 15},
            font=dict(family='sans-serif',
                      color='white',
                      size=12),
            hovermode='closest',
            paper_bgcolor='#010915',
            plot_bgcolor='#010915',
            legend={'orientation': 'h',
                    'bgcolor': '#010915',
                    'xanchor': 'center', 'x': 0.5, 'y': -0.7}


        )
    }
    
if __name__ == '__main__':
    app.run_server(debug=True)
