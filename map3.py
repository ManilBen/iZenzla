import dash
from dash.dependencies import Input, Output, State, Event
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import plotly
import plotly.offline as py
from plotly import graph_objs as go
from plotly.graph_objs import *
from flask import Flask
import pandas as pd
import numpy as np
import json
import os
import copy
#import plotly.plotly as py
from sklearn.cluster import KMeans
import plotly.figure_factory as ff
from reglesgen import *


app = dash.Dash(__name__)
server = app.server
app.config['suppress_callback_exceptions']=True
# API keys and datasets
mapbox_access_token = 'pk.eyJ1IjoibWFuaWxvMjMiLCJhIjoiY2pnaDVpOHY0MDZtaTJ3bnptOTRuOW9jaSJ9.c9uSa5jLArbfDBPxdfoxzQ'
radius_multiplier = {'inner': 1.5, 'outer': 3}

colorscale_magnitude = [
    [0, '#ffffb2'],
    [0.25, '#fecc5c'],
    [0.5, '#fd8d3c'],
    [0.75, '#f03b20'],
    [1, '#bd0026'],
]

# http://colorbrewer2.org/#type=sequential&scheme=Greys&n=3
colorscale_depth = [
    [0, '#f0f0f0'],
    [0.5, '#bdbdbd'],
    [0.1, '#636363'],
]


regions = {
    'world': {'lat': 0, 'lon': 0, 'zoom': 1},
    'europe': {'lat': 50, 'lon': 0, 'zoom': 3},
    'north_america': {'lat': 40, 'lon': -100, 'zoom': 2},
    'south_america': {'lat': -15, 'lon': -60, 'zoom': 2},
    'africa': {'lat': 0, 'lon': 20, 'zoom': 2},
    'asia': {'lat': 30, 'lon': 100, 'zoom': 2},
    'oceania': {'lat': -10, 'lon': 130, 'zoom': 2},
}
catalogues = {
    'usgs': {'cdate': 0, 'clat': 1,'clong': 2,'cdepth':3,'cmag':4,'clink':'C:\Users\ASUS X541U\Downloads\query.csv','k':3,'cid':11},
    'isc': {'cdate': 0, 'clat': 1, 'clong': 2,'cdepth':7,'cmag':10,'clink':'C:\Users\ASUS X541U\Desktop\Catalogues\isc-gem-cat.csv','k':5,'cid':12},
}
catalogue='usgs'
region='world'


@app.callback(
    output=Output('graph-geo', 'figure'),
    inputs=[Input('dropdown-region', 'value'),
            Input('dropdown-catalogue', 'value')
            ])

def _update_graph(region,catalogue):
    radius_multiplier = {'inner': 1.5, 'outer': 3}
    df = pd.read_csv(catalogues[catalogue]['clink'])
    colum = [catalogues[catalogue]['cdate'],catalogues[catalogue]['clat'],catalogues[catalogue]['clong'],catalogues[catalogue]['cdepth'],catalogues[catalogue]['cmag'],catalogues[catalogue]['cid']]
    df1=df.iloc[:,colum]
    df1=df1.dropna(axis=0, how='any')
    df1.columns=['Date','lat','long','depth','mag','id']
    df1['text'] = df1['Date'] + '<br>Magnitude ' + df1['mag'].astype(str)+'<br>Depth' + df1['depth'].astype(str)
    dff=df1
    layout = go.Layout(
        title=regions[region],
        autosize=True,
        hovermode='closest',
        height=750,
        margin=go.Margin(l=0, r=0, t=45, b=10),
        mapbox=dict(
            accesstoken=mapbox_access_token,
            bearing=0,
            center=dict(
                lat=regions[region]['lat'],
                lon=regions[region]['lon'],
            ),
            pitch=0,
            zoom=regions[region]['zoom'],
        ),
    )

    data = go.Data([
        # outer circles represent magnitude
        go.Scattermapbox(
            lat=dff['lat'],
            lon=dff['long'],
            mode='markers',
            marker=go.Marker(
                size=dff['mag'] * radius_multiplier['outer'],
                color=dff['mag'],
                colorscale=colorscale_magnitude,
                opacity=0.7,
            ),
            hoverinfo=dff['id'],
            text=dff['text'],
            # hoverinfo='text',
            showlegend=False,
        ),
    ])

    figure = go.Figure(data=data, layout=layout)
    return figure

#==============================================================================
#
#                             CARTE CLUSTERED
#==============================================================================
"""
@app.callback(
    output=Output('graph-clust', 'figure'),
    inputs=[Input('dropdown-region', 'value'),
            Input('dropdown-catalogue', 'value')
            ])
def _update_grapgcl(region,catalogue):
    radius_multiplier = {'inner': 1.5, 'outer': 3}
    df = pd.read_csv(catalogues[catalogue]['clink'])
    colum = [catalogues[catalogue]['cdate'],catalogues[catalogue]['clat'],catalogues[catalogue]['clong'],catalogues[catalogue]['cdepth'],catalogues[catalogue]['cmag']]
    df1=df.iloc[:,colum]
    df1=df1.dropna(axis=0, how='any')
    df1.columns=['Date','lat','long','depth','mag']
    dff=df1
    df1=df1.iloc[:,[1,2,3,4]]
    dd=df1.values.tolist()
    colonnes=['lat','long','depth','mag']
    datax=np.array(dd)
    k=catalogues[catalogue]['k']
    kmeans = KMeans(n_clusters=k,init='k-means++', max_iter=1000).fit(datax)
    col = ['#990000','#E7C843','#6B8E23','blue','olive','orange','cyan','purple']
    df3=pd.DataFrame(datax,columns=colonnes)
    data_clst=[]
    layout = go.Layout(
            title=regions[region],
            autosize=True,
            hovermode='closest',
            height=750,
            margin=go.Margin(l=0, r=0, t=45, b=10),
            mapbox=dict(
                accesstoken=mapbox_access_token,
                bearing=0,
                center=dict(
                    lat=regions[region]['lat'],
                    lon=regions[region]['lon'],
                ),
                pitch=0,
                zoom=regions[region]['zoom'],
            ),
        )
    for ind in range(0,k):
            #datac=[]
            c=datax[ClusterIndicesNumpy(ind,kmeans.labels_)]
            x=c[:,0]
            y=c[:,1]
            df3=pd.DataFrame(c,columns=colonnes)
            # outer circles represent magnitude
            datac=go.Scattermapbox(
                    lat=df3['lat'],
                    lon=df3['long'],
                    mode='markers',
                    marker=go.Marker(
                        size=df3['mag'] * radius_multiplier['outer'],
                        color=col[ind],
                        opacity=0.8,
                    ),
                    # hoverinfo='text',
                    showlegend=False,
                )
            data_clst.append(datac)

    #data_cluster=go.Data([data_clst])

    figure = go.Figure(data=data_clst, layout=layout)
    return figure
"""


@app.callback(
    Output('hidden-div', 'children'),
    [Input('graph-geo', 'clickData'),
     Input('typeinit', 'value')
    ],
    [State('hidden-div', 'children')]
    )

def get_selected_data(clickData, initialisation, previous):
    if initialisation == 'custom' :
        if clickData is not None:
            result = clickData['points']
            if previous:
                previous_list = json.loads(previous)
                if previous_list is not None:
                    result = previous_list + result
            return json.dumps(result)
    else :
        return None

@app.callback(
    Output('graph-clust', 'figure'),
    [Input('my-button','n_clicks'),
     Input('dropdown-catalogue', 'value')
    ],
    [
     State('dropdown_nbreclst', 'value'),
     State('hidden-div', 'children'),
     State('typeinit', 'value')
    ]
    )

def _update_grapgcl(n_clicks, catalogue, nbre_clst, points, initialisation):
    radius_multiplier = {'inner': 1.5, 'outer': 3}
    df = pd.read_csv(catalogues[catalogue]['clink'])
    colum = [catalogues[catalogue]['cdate'],catalogues[catalogue]['clat'],catalogues[catalogue]['clong'],catalogues[catalogue]['cdepth'],catalogues[catalogue]['cmag'],catalogues[catalogue]['cid']]
    df1=df.iloc[:,colum]
    df1=df1.dropna(axis=0, how='any')
    df1.columns=['Date','lat','lon','depth','mag','id']
    if initialisation == 'k++':
        colonnes=['lat','long','depth','mag']
        df1.columns=['Date','lat','lon','depth','mag','id']
        dff=df1
        df1=df1.iloc[:,[1,2,3,4]]
        dd=df1.values.tolist()
        datax=np.array(dd)
        k=catalogues[catalogue]['k']
        k=3
        kmeans = KMeans(n_clusters=k,init='k-means++', max_iter=1000).fit(datax)
        regles=genererregles(kmeans,k,datax)
        for l in range(0,k):
         print "Cluster "+str(l+1)
         print regles[l]
        col = ['blue','orange','green','purple','red','white','yellow','cyan','gray','rosybrown','peru','darkorchid','plum','gainsboro']
        data_clst=[]
        layout = go.Layout(
                    title=regions[region],
                    autosize=True,
                    hovermode='closest',
                    height=750,
                    margin=go.Margin(l=0, r=0, t=45, b=10),
                    mapbox=dict(
                        accesstoken=mapbox_access_token,
                        bearing=0,
                        center=dict(
                            lat=regions[region]['lat'],
                            lon=regions[region]['lon'],
                        ),
                        pitch=0,
                        zoom=regions[region]['zoom'],
                    ),
                )
        for ind in range(0,k):
                    #datac=[]
                    c=datax[ClusterIndicesNumpy(ind,kmeans.labels_)]
                    x=c[:,0]
                    y=c[:,1]
                    df3=pd.DataFrame(c,columns=colonnes)
                    # outer circles represent magnitude
                    datac=go.Scattermapbox(
                            lat=df3['lat'],
                            lon=df3['long'],
                            mode='markers',
                            marker=go.Marker(
                                size=df3['mag'] * radius_multiplier['outer'],
                                color=col[ind],
                                opacity=0.8,
                            ),
                            # hoverinfo='text',
                            showlegend=False,
                        )
                    data_clst.append(datac)
        figure = go.Figure(data=data_clst, layout=layout)
        return figure
    if initialisation == 'custom':
        if points :
            if n_clicks > 0:
                result = json.loads(points)
                if result is not None:
                    datafr=pd.DataFrame(result)
                    col=['curveNumber','marker.size','pointNumber','pointIndex','text','marker.color']
                    datafr=datafr.drop(col, axis=1)
                    datafr=datafr.rename(index=str, columns={"hoverinfo": "id"})
                    centroid=pd.merge(datafr, df1, on=['lat','lon','id'], how='inner')
                    centroid=centroid.iloc[:,[1,2,4,5]]
                    centroid=centroid[['lat','lon','depth','mag']]
                    centroid=centroid.values
                    print centroid
                    if  nbre_clst == len(centroid)  :
                        radius_multiplier = {'inner': 1.5, 'outer': 3}
                        dff=df1
                        df1=df1.iloc[:,[1,2,3,4]]
                        dd=df1.values.tolist()
                        colonnes=['lat','long','depth','mag']
                        datax=np.array(dd)
                        k=nbre_clst
                        kmeans = KMeans(n_clusters=nbre_clst,n_init=1,init=centroid, max_iter=1000).fit(datax)
                        print "kkk"
                        col = ['#990000','#E7C843','#6B8E23','blue','olive','orange','cyan','purple']
                        data_clst=[]
                        layout = go.Layout(
                                    title=regions[region],
                                    autosize=True,
                                    hovermode='closest',
                                    height=750,
                                    margin=go.Margin(l=0, r=0, t=45, b=10),
                                    mapbox=dict(
                                        accesstoken=mapbox_access_token,
                                        bearing=0,
                                        center=dict(
                                            lat=regions[region]['lat'],
                                            lon=regions[region]['lon'],
                                        ),
                                        pitch=0,
                                        zoom=regions[region]['zoom'],
                                    ),
                                )
                        for ind in range(0,k):
                                    #datac=[]
                                    c=datax[ClusterIndicesNumpy(ind,kmeans.labels_)]
                                    x=c[:,0]
                                    y=c[:,1]
                                    df3=pd.DataFrame(c,columns=colonnes)
                                    # outer circles represent magnitude
                                    datac=go.Scattermapbox(
                                            lat=df3['lat'],
                                            lon=df3['long'],
                                            mode='markers',
                                            marker=go.Marker(
                                                size=df3['mag'] * radius_multiplier['outer'],
                                                color=col[ind],
                                                opacity=0.8,
                                            ),
                                            # hoverinfo='text',
                                            showlegend=False,
                                        )
                                    data_clst.append(datac)
                        figure = go.Figure(data=data_clst, layout=layout)
                        centroid=[]
                        return figure
        else :
            colonnes=['lat','long','depth','mag']
            df1.columns=['Date','lat','lon','depth','mag','id']
            dff=df1
            df1=df1.iloc[:,[1,2,3,4]]
            dd=df1.values.tolist()
            datax=np.array(dd)
            k=catalogues[catalogue]['k']
            kmeans = KMeans(n_clusters=k,init='k-means++', max_iter=1000).fit(datax)
            col = ['#990000','#E7C843','#6B8E23','blue','olive','orange','cyan','purple']
            data_clst=[]
            layout = go.Layout(
                        title=regions[region],
                        autosize=True,
                        hovermode='closest',
                        height=750,
                        margin=go.Margin(l=0, r=0, t=45, b=10),
                        mapbox=dict(
                            accesstoken=mapbox_access_token,
                            bearing=0,
                            center=dict(
                                lat=regions[region]['lat'],
                                lon=regions[region]['lon'],
                            ),
                            pitch=0,
                            zoom=regions[region]['zoom'],
                        ),
                    )
            for ind in range(0,k):
                        #datac=[]
                        c=datax[ClusterIndicesNumpy(ind,kmeans.labels_)]
                        x=c[:,0]
                        y=c[:,1]
                        df3=pd.DataFrame(c,columns=colonnes)
                        # outer circles represent magnitude
                        datac=go.Scattermapbox(
                                lat=df3['lat'],
                                lon=df3['long'],
                                mode='markers',
                                marker=go.Marker(
                                    size=df3['mag'] * radius_multiplier['outer'],
                                    color=col[ind],
                                    opacity=0.8,
                                ),
                                # hoverinfo='text',
                                showlegend=False,
                            )
                        data_clst.append(datac)
            figure = go.Figure(data=data_clst, layout=layout)
            return figure





    #data_cluster=go.Data([data_clst])





def create_content():
    # create empty figure. It will be updated when _update_graph is triggered
    graph = dcc.Graph(id='graph-geo')
    content = html.Div(graph, id='content')
    return content

def create_dropdowns():
    drop1 = dcc.Dropdown(
        options=[
            {'label': 'USGS', 'value': 'usgs'},
            {'label': 'ISC', 'value': 'isc'},
        ],
        value='isc',
        id='dropdown-catalogue',
        className='three columns offset-by-four'
    )
    drop2 = dcc.Dropdown(
        options=[
            {'label': 'World', 'value': 'world'},
            {'label': 'Europe', 'value': 'europe'},
            {'label': 'North America', 'value': 'north_america'},
            {'label': 'South America', 'value': 'south_america'},
            {'label': 'Africa', 'value': 'africa'},
            {'label': 'Asia', 'value': 'asia'},
            {'label': 'Oceania', 'value': 'oceania'},
        ],
        value='world',
        id='dropdown-region',
        className='three columns offset-by-four'
    )
    return [drop1,drop2]

def create_mapclust():
    graphcl = dcc.Graph(id='graph-clust')
    content = html.Div(graphcl, id='clust')
    return content
#==============================================================================
#
#                                   Pie Chart
#==============================================================================
critere=['Magnitude','Profondeur']
labels = ['Low','Med','High']
def create_drop_stat():
    drop=dcc.Dropdown(id='dropdown_pie',
                options=[{'label': i, 'value': i} for i in critere ],
                value='Magnitude')
    return drop
def create_pie():
    pie = dcc.Graph(id='vp_port')
    pie_cont=html.Div(pie, id='pie_cont')
    return pie_cont

@app.callback(Output('vp_port','figure'),
 [Input('dropdown_pie', 'value'),
  Input('dropdown-catalogue', 'value')]
  )
def updatepie(value,catalogue):
    df = pd.read_csv(catalogues[catalogue]['clink'])
    colum = [catalogues[catalogue]['cdate'],catalogues[catalogue]['clat'],catalogues[catalogue]['clong'],catalogues[catalogue]['cdepth'],catalogues[catalogue]['cmag']]
    df1=df.iloc[:,colum]
    df1=df1.dropna(axis=0, how='any')
    df1.columns=['Date','lat','long','depth','mag']
    values=[]
    if value=='Magnitude':
        values = numbermag(df1,5.5,6.5,7.5)
        title_text='Selon la magnitude'
    else :
       values = numberdepth(df1,0,100,300)
       title_text='Selon la Profondeur'
    return { 'data' : [go.Pie(labels=labels,values=values,
        hoverinfo='label+value+percent',
        textinfo='percent' )], 'layout' : {'title' : title_text}
        }

def create_scat():
    scat = dcc.Graph(id='scatter')
    scat_cont=html.Div(scat, id='scat_cont')
    return scat_cont

@app.callback(Output('scatter','figure'),
 [Input('dropdown-catalogue', 'value')]
  )
def updatescat(catalogue):
    df = pd.read_csv(catalogues[catalogue]['clink'])
    colum = [catalogues[catalogue]['cdate'],catalogues[catalogue]['clat'],catalogues[catalogue]['clong'],catalogues[catalogue]['cdepth'],catalogues[catalogue]['cmag']]
    df1=df.iloc[:,colum]
    df1=df1.dropna(axis=0, how='any')
    df1.columns=['Date','lat','long','depth','mag']
    #print df1
    data=[go.Scatter(
            x=df1['depth'],
            y=df1['mag'],
            mode='markers',
            opacity=0.9,
            marker={
                'size': 15,
                'line': {'width': 0.5, 'color': 'white'}
            },
            name=i
        )]
    return {
        'data': data,
        'layout': go.Layout(
            xaxis={'title': 'Profondeur'},
            yaxis={'title': 'Magnitude'},
            margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
            legend={'x': 0, 'y': 1},
            hovermode='closest'
        )
    }

#==============================================================================
#
#                           CREATION TABLE
#
#==============================================================================

@app.callback(Output('cat-table','rows'),
 [Input('dropdown-catalogue', 'value')]
  )
def update_table(catalogue):
    df = pd.read_csv(catalogues[catalogue]['clink'])
    colum = [catalogues[catalogue]['cdate'],catalogues[catalogue]['clat'],catalogues[catalogue]['clong'],catalogues[catalogue]['cdepth'],catalogues[catalogue]['cmag']]
    df1=df.iloc[:,colum]
    df1.columns=['Date','lat','long','depth','mag']
    if catalogue == 'usgs' :
        df1['Date'],df1['Time']=df1['Date'].str.split('T',1).str
    df1=df1.dropna(axis=0, how='any')
    return df1.to_dict('records')


#==============================================================================
#
#                             YEAR/Number_Earthquakes
#==============================================================================
def create_year():
    year=dcc.Graph(id='year_nbr')
    year_cont=html.Div(year, id='year_cont')
    return year_cont
@app.callback(Output('year_nbr','figure'),
 [Input('dropdown-catalogue', 'value')]
  )
def update_year(catalogue):
    df = pd.read_csv(catalogues[catalogue]['clink'])
    colum = [catalogues[catalogue]['cdate'],catalogues[catalogue]['clat'],catalogues[catalogue]['clong'],catalogues[catalogue]['cdepth'],catalogues[catalogue]['cmag']]
    df1=df.iloc[:,colum]
    df1=df1.dropna(axis=0, how='any')
    df1.columns=['Date','lat','long','depth','mag']
    year_nbr=nbreyear(df1)
    data = [go.Scatter(
    x = year_nbr['Date'],
    y = year_nbr['Number_Earthquakes'],
    mode = 'lines+markers',
    name = 'lines+markers'
    )]
    layout=go.Layout(
        xaxis={'title': 'Annee'},
        yaxis={'title': 'Nbre d evenement' },
        margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
        legend={'x': 0, 'y': 1},
        hovermode='closest'
    )
    fig=go.Figure(data=data, layout=layout)
    return fig

#==============================================================================
#
#                                   Histogramme
#==============================================================================
def create_dist() :
    dist=dcc.Graph(id='histogram')
    dist_cont=html.Div(dist, id='dist_cont')
    return dist_cont
@app.callback(Output('histogram','figure'),
 [Input('dropdown_pie', 'value'),
  Input('dropdown-catalogue', 'value')]
  )
def update_dist(value,catalogue):
    df = pd.read_csv(catalogues[catalogue]['clink'])
    colum = [catalogues[catalogue]['cdate'],catalogues[catalogue]['clat'],catalogues[catalogue]['clong'],catalogues[catalogue]['cdepth'],catalogues[catalogue]['cmag']]
    df1=df.iloc[:,colum]
    df1=df1.dropna(axis=0, how='any')
    df1.columns=['Date','lat','long','depth','mag']
    if value=='Magnitude':
        group=['Mag']
        hist_data=[histo(df1,'mag')]
    else :
        group=['depth']
        hist_data=[histo(df1,'depth')]
    return ff.create_distplot(hist_data, group, bin_size=.5)

#==============================================================================
#
#                           REGLES TABLE
#==============================================================================

@app.callback(Output('clst-dropdown','options'),
 [Input('dropdown-catalogue', 'value')]
  )
def set_dropclust(catalogue):
    listclst=[]
    k=catalogues[catalogue]['k']
    [listclst.append("Cluster "+str(i)) for i in range(1,k+1)]
    regles=[]
    return [{'label': i, 'value': i} for i in listclst]

@app.callback(
    dash.dependencies.Output('clst-dropdown', 'value'),
    [dash.dependencies.Input('clst-dropdown', 'options')])
def set_cities_value(available_options):
    return available_options[0]['value']

@app.callback(Output('regles-table','rows'),
 [Input('dropdown-catalogue', 'value'),
  Input('clst-dropdown', 'value')]
  )

def update_regle(catalogue,clust):
    df = pd.read_csv(catalogues[catalogue]['clink'])
    colum = [catalogues[catalogue]['cdate'],catalogues[catalogue]['clat'],catalogues[catalogue]['clong'],catalogues[catalogue]['cdepth'],catalogues[catalogue]['cmag']]
    df1=df.iloc[:,colum]
    df1=df1.dropna(axis=0, how='any')
    df1.columns=['Date','lat','long','depth','mag']
    dff=df1
    df1=df1.iloc[:,[1,2,3,4]]
    dd=df1.values.tolist()
    colonnes=['lat','long','depth','mag']
    datax=np.array(dd)
    k=catalogues[catalogue]['k']
    kmeans = KMeans(n_clusters=k,init='k-means++', max_iter=1000).fit(datax)
    regles=genererregles(kmeans,k,datax)
    r=int(clust[-1])
    r=r-1
    print r
    return regles[r].to_dict('records')
#==============================================================================
#
#                           UPLOAD DATATABLE
#
#==============================================================================


def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    return html.Div([
        html.H5(filename),
        # Use the DataTable prototype component:
        # github.com/plotly/dash-table-experiments

        dt.DataTable(rows=df.to_dict('records')),

        html.Hr(),  # horizontal line

        # For debugging, display the raw contents provided by the web browser
        html.Div('Raw Content'),
        html.Pre(contents[0:200] + '...', style={
            'whiteSpace': 'pre-wrap',
            'wordBreak': 'break-all'
        })
    ])


@app.callback(Output('output-data-upload', 'children'),
              [Input('upload-data', 'contents'),
               Input('upload-data', 'filename'),
               Input('upload-data', 'last_modified')])
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children
#==============================================================================
#
#                       FILTER COLONNES
#
#==============================================================================
def filter_colonnes(cat):
    df = pd.read_csv(catalogues[cat]['clink'])
    colum = [catalogues[cat]['cdate'],catalogues[cat]['clat'],catalogues[cat]['clong'],catalogues[cat]['cdepth'],catalogues[cat]['cmag']]
    df1=df.iloc[:,colum]
    df1=df1.dropna(axis=0, how='any')
    return df1
#==============================================================================
#
#
#==============================================================================

#==============================================================================
#
#
#==============================================================================
nbr_clusters=[i for i in range(1,10)]
app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})
app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.Div(create_dropdowns(),style={'width':'60%'}),
                html.Div(create_content(),style={'width':'60%','height':'40%'}),
                html.Div(
                [
                    dcc.Upload(
                        id='upload-data',
                        children=html.Div([
                            'Drag and Drop or ',
                            html.A('Select Files')
                        ]),
                        style={
                            'width': '100%',
                            'height': '60px',
                            'lineHeight': '60px',
                            'borderWidth': '1px',
                            'borderStyle': 'dashed',
                            'borderRadius': '5px',
                            'textAlign': 'center',
                            'margin': '10px'
                        },
                        # Allow multiple files to be uploaded
                        multiple=True
                    ),
                    dt.DataTable(
                        rows=[{}], # initialise the rows
                        row_selectable=True,
                        filterable=True,
                        sortable=True,
                        selected_row_indices=[],
                        id='cat-table'
                )])
                ]),
                html.Div([dcc.Dropdown(id='clust_feat',
                    options=[
                        {'label': 'Lattitude', 'value': 'lat'},
                        {'label': 'Longitude', 'value': 'long'},
                        {'label': 'Magnitude', 'value': 'mag'},
                        {'label': 'Profondeur', 'value': 'depth'}
                    ],
                    value=['lat','long'],
                    multi=True
                )]),
               
                    html.Div([dcc.Dropdown(id='dropdown_nbreclst',
                                options=[{'label': i, 'value': i} for i in nbr_clusters ],
                                value='3')
                    ],
                    ),
                    html.Button('Run', id='my-button',n_clicks=0)
                    ,
                    html.Div([dcc.RadioItems(id='typeinit',
                                options=[
                                    {'label': 'Custom', 'value': 'custom'},
                                    {'label': 'K-means++', 'value': 'k++'},
                                ],
                                value='k++',
                                labelStyle={'display': 'inline-block'}
                            )
                    ]),
                html.Div(create_mapclust(),style={'width':'60%','height':'40%'}),
                html.Div(
                             [
                              dcc.Dropdown(id='clst-dropdown'),
                              dt.DataTable(
                            rows=[{}], # initialise the rows
                            row_selectable=True,
                            filterable=True,
                            sortable=True,
                            selected_row_indices=[],
                            id='regles-table'
                            )],
                ),
                html.Div(
            children=[
                html.Div(create_drop_stat()),
                html.Div(create_pie(),style={'width':'39%','float':'left'}),
                html.Div(create_dist(),style={'width':'59%','float':'right'}),
                html.Div(create_year(),style={'width':'59%','float':'right'}),
                html.Div(create_scat(),style={'width':'59%','float':'right'})
            ]
        ),
        html.Div(id = 'selected-data'),
        html.Div(id = 'hidden-div', style = {'display': 'none'})
        # html.Hr(),
    ],
    className='container'
)



if __name__ == '__main__':
    app.run_server(debug=True)
