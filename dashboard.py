# -*- coding: utf-8 -*-
"""
Created on Wed May 16 10:56:08 2018

@author: Pranav
"""
import pandas as pd
import numpy as np
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import base64
import operator
import calendar
from win32api import GetSystemMetrics

#background color
bg_color='rgb(240,240,220)'

#col func
def coldec(i):
    if(DispRules.iloc[i]['Important']==1):
        return 'rgb(235,0,0)'
    else:
        return 'rgb(148,148,161)'
        
#initializing files

op={'<':operator.lt,'>':operator.gt,'==':operator.eq}

Rules=pd.read_csv('C:/Users/Pranav/Desktop/project/Ready_Files/CMMH/Rules.csv',sep='\t')

## resets index
Rules.reset_index(drop=True,inplace=True)
Rules.Value=pd.to_numeric(Rules.Value,errors='ignore')



OMH01=pd.read_csv('C:/Users/Pranav/Desktop/project/Ready_Files/CMMH/MH01.csv',sep='\t')
OMH02=pd.read_csv('C:/Users/Pranav/Desktop/project/Ready_Files/CMMH/MH02.csv',sep='\t')
OMH03=pd.read_csv('C:/Users/Pranav/Desktop/project/Ready_Files/CMMH/MH03.csv',sep='\t')

MH01=OMH01
MH02=OMH02
MH03=OMH03
## creating rule columns in MH dataset & datetime formatting
for i in range(len(Rules)):
    globals()[Rules.Machine[i]]['rule{}'.format(i)]=True
    globals()[Rules.Machine[i]]['TIME STAMP']= pd.to_datetime(globals()[Rules.Machine[i]]['TIME STAMP'], infer_datetime_format=True)




for i in range(len(Rules)):
    operator=op[Rules.Operator[i]]
    if(len(Rules.Value[i])<10):
        a=operator(globals()[Rules.Machine[i]][globals()[Rules.Machine[i]].columns[globals()[Rules.Machine[i]].columns==Rules.Attribute[i]].values],int(Rules.Value[i]))
    else:
        if(isinstance(eval(Rules.Value[i]),float)):
            expr=int(eval(Rules.Value[i]))
        else:
            expr=int(eval(Rules.Value[i])[(eval(Rules.Value[i]).index==True)])
        a=operator(globals()[Rules.Machine[i]][globals()[Rules.Machine[i]].columns[globals()[Rules.Machine[i]].columns==Rules.Attribute[i]].values],expr)
    a=np.array(a)    
    globals()[Rules.Machine[i]]['rule{}'.format(i)]=a
            
            


MH01_rules=list(MH01.columns[MH01.columns.str.contains('rule')].values)
MH02_rules=list(MH02.columns[MH02.columns.str.contains('rule')].values)
MH03_rules=list(MH03.columns[MH03.columns.str.contains('rule')].values)

#####detecting broken rules

def breakdetect():
    rule_broken=list()
    for i in range(len(MH01_rules)):
       if(any(MH01[MH01_rules[i]]==False)):
           rule_broken.append(MH01_rules[i])
    for i in range(len(MH02_rules)):
       if(any(MH02[MH02_rules[i]]==False)):
           rule_broken.append(MH02_rules[i])
    for i in range(len(MH03_rules)):
       if(any(MH03[MH03_rules[i]]==False)):
           rule_broken.append(MH03_rules[i])
    return rule_broken 

## calculating index
    
def prov_index(rule_broken):
    rule_broken_index=list()
    for i in range(len(rule_broken)):
        rule_broken_index.append(rule_broken[i].split('e')[1])
    return rule_broken_index
    

def Timegen():
    count=np.zeros(len(rule_broken_index))
    time=np.zeros(len(rule_broken_index),dtype='datetime64[ns]')
    maxval=np.zeros(len(rule_broken_index))
    j=0
    for i in Rules.loc[rule_broken_index].Machine.index:
        mach=Rules.Machine[i]
        xx=globals()[mach]['rule'+str(i)]
        maxval[j]=globals()[mach][Rules.Attribute[i]].max()   
        count[j]=len(xx[xx==False])
        zz=xx[xx==False]
        time[j]=globals()[mach]['TIME STAMP'][zz.index[-1]]
        j=j+1
    return count,time,maxval



rule_broken=breakdetect()
rule_broken_index=pd.to_numeric(prov_index(rule_broken)) 
count,time,maxval=Timegen()

### displaying broken rules 

DispRules=pd.DataFrame(Rules.iloc[rule_broken_index,:])
DispRules.drop(labels=['Value'],axis=1,inplace=True)
DispRules=DispRules.assign(Count=count,Last_Occurence=time,Max=maxval)

DispRules.sort_values(['Important','Count'],ascending=False,kind='mergesort',inplace=True)


def generate_table():
    global MH01_rules
    global MH02_rules
    global MH03_rules
    global rule_broken
    global rule_broken_index
    global count,time,maxval
    global groupm
    global machlist
    global groupl
    global DispRules
    MH01_rules=list(MH01.columns[MH01.columns.str.contains('rule')].values)
    MH02_rules=list(MH02.columns[MH02.columns.str.contains('rule')].values)
    MH03_rules=list(MH03.columns[MH03.columns.str.contains('rule')].values)
    rule_broken=breakdetect()
    rule_broken_index=pd.to_numeric(prov_index(rule_broken)) 
    count,time,maxval=Timegen()
    DispRules=pd.DataFrame(Rules.iloc[rule_broken_index,:])
    DispRules.drop(labels=['Value'],axis=1,inplace=True)
    DispRules=DispRules.assign(Count=count,Last_Occurence=time,Max=maxval)
    DispRules.sort_values(['Important','Count'],ascending=False,kind='mergesort',inplace=True)   
    groupm=list(DispRules.groupby('Machine'))
    machlist=list()
    groupl=list()
    for i in range(len(groupm)):
        machlist.append(groupm[i][0])
        groupl.append(len(groupm[i][1]))
    return html.Table(
        # Header
        [html.Tr([html.Th(col,style={'textAlign':'Center','fontFamily':'Arial','fontSize':'16','color':'rgb(88, 88, 101)'}) for col in DispRules.columns[~DispRules.columns.str.contains('Important')]])] +

        # Body
        [html.Tr([
            html.Td(DispRules.iloc[i][col],style={'textAlign':'Center','fontFamily':'Arial','fontSize':'12','color':coldec(i),'fontWeight':'800'}) for col in DispRules.columns[~DispRules.columns.str.contains('Important')]
        ]) for i in range(len(DispRules))]
    ,style={'marginLeft':'10','backgroundColor':'rgb(230,230,210)','paddingTop':'15','paddingRight':'10','paddingLeft':'3','border-radius':'15px','border':'solid','borderColor':'rgb(220,220,200)'})


    
img = 'zf.png' 
enc_img = base64.b64encode(open(img, 'rb').read())


app = dash.Dash()
app.config['suppress_callback_exceptions']=True
app.layout= html.Div(children=[
        
html.Div(html.Img(src='data:image/png;base64,{}'.format(enc_img.decode()),style={'width':'200','height':'70','marginLeft':'42.5%'})),

html.Div(
        children=[
                dcc.Tabs(
        tabs=[
            {'label': 'Anomaly Report', 'value': 'dv'},{'label':'Visualization tool','value':'gv'}
        ],
        value='dv',
        id='tabs'
    ),html.Br(),html.Div(children=['Showing data during:',html.Br(),
    dcc.DatePickerRange(
        id='dpr',
        min_date_allowed= MH01['TIME STAMP'].dt.date.min(),
        max_date_allowed=MH01['TIME STAMP'].dt.date.max(),
        start_date=MH01['TIME STAMP'].dt.date.min(),
        end_date=MH01['TIME STAMP'].dt.date.max()
    ),
],style={'textAlign':'center','backgroundColor':bg_color,'fontWeight':'550','fontFamily':'Arial','color':'rgb(118, 118, 131)'})


],style={'fontFamily':'Arial','backgroundColor':bg_color,'fontWeight':'550'}),   

html.Br(),

html.Div(id='main'

)    
],style={'margin':'-7px -7px -7px -7px','padding':'0','minHeight':GetSystemMetrics(1),'backgroundColor':bg_color})



@app.callback(
    dash.dependencies.Output('main', 'children'),
    [dash.dependencies.Input('tabs', 'value'),
     dash.dependencies.Input('dpr','start_date'),
     dash.dependencies.Input('dpr','end_date')])
def set_display_children(sel_view,start,end):
    global MH01
    global MH02
    global MH03
    MH01=OMH01  
    MH02=OMH02
    MH03=OMH03
    MH01=MH01[(MH01['TIME STAMP']>=pd.to_datetime(start)) & (MH01['TIME STAMP']<=pd.to_datetime(end))]
    MH02=MH02[(MH02['TIME STAMP']>=pd.to_datetime(start)) & (MH02['TIME STAMP']<=pd.to_datetime(end))]
    MH03=MH03[(MH03['TIME STAMP']>=pd.to_datetime(start)) & (MH03['TIME STAMP']<=pd.to_datetime(end))]
    if(sel_view=='gv'):
        a=[html.Div(children=['HECKERT'], style={'fontFamily':'Arial','size':'40','fontSize':'40','marginLeft':'20','backgroundColor':bg_color,'color':'rgb(118, 118, 131)','fontWeight':'600'}),
        html.Div(children=[html.Div('X-Axis',style={'textAlign':'Center','fontFamily':'Arial','fontSize':'15','color':'rgb(118, 118, 131)'}),
                dcc.Dropdown(
                             id='x',options=[{'label':col,'value':col}for col in MH01.columns[~MH01.columns.str.contains('rule')]]           
                                      ,value='TIME STAMP'),
    html.Div('Y-Axis',style={'textAlign':'Center','fontFamily':'Arial','fontSize':'15','color':'rgb(118, 118, 131)'}),
                          dcc.Dropdown(
                             id='y',options=[{'label':col,'value':col}for col in MH01.columns[~MH01.columns.str.contains('rule')]]           
                                       ,value='X-TEMP')
                          ]
                ,style={'width':'30%'}),
        
        dcc.Graph(id='grh', figure={
            'data': [
                go.Scatter(
                    x=globals()['MH0'+str(i+1)]['TIME STAMP'],
                    y=globals()['MH0'+str(i+1)]['X-TEMP'] ,
                    
                    mode='lines',
                    opacity=1.8,
                    line= {'width': 1},
                    name='MH0'+str(i+1)
                    ) for i in range(3) 
            ],
            'layout':go.Layout(
                         xaxis={'title': 'TIME STAMP'},
                         yaxis={'title': 'X-TEMP'},
                         hovermode='x',
                         plot_bgcolor=bg_color,
                         paper_bgcolor=bg_color,
                         height=650
                            )
        ,})
       ]
        
            
    elif(sel_view=='dv'):    
        a=[html.Div(style={'textAlign':'Center','fontFamily':'Arial'},children=[  html.Div(children=['ANOMALIES',html.Br(),html.Br(),
    html.Div(generate_table(),style={'width':'55%','float':'left','marginTop':'-15'}),
    html.Div(

             dcc.Graph(id='pch',figure={
                        'data':[go.Pie(
                                labels=machlist,
                                values=groupl,
                                hoverinfo='label+percent',textinfo='value',textfont=dict(size=20,color='rgb(0,0,0)'),marker=dict(
                           line=dict(color='#000000', width=1.5)))],
                         'layout':go.Layout(title='<b>DISTRIBUTION OF ANOMALIES</b>',paper_bgcolor=bg_color,font=dict(family='Arial', size=12, color='rgb(118, 118, 131)'))            
                       }
                       )
 
            ,style={'marginLeft':'60%','marginTop':'-30',})
   ],style={'textAlign':'Center','fontFamily':'Arial','fontSize':'25','color':'rgb(118, 118, 131)','width':'100%','fontWeight':'600'} )  
]
    )]

    return a

@app.callback(
        dash.dependencies.Output('grh', 'figure'),
        [dash.dependencies.Input('x', 'value'),
        dash.dependencies.Input('y', 'value')])
def axsel(xx,yy):
    figure={
    'data': [
        go.Scatter(
            x=globals()['MH0'+str(i+1)][xx],
            y=globals()['MH0'+str(i+1)][yy] ,
            
            mode='lines',
            opacity=1.8,
            line= {'width': 1},
            name='MH0'+str(i+1)
            ) for i in range(3) 
    ],
    'layout':go.Layout(
                 xaxis={'title': xx},
                 yaxis={'title': yy},
                 hovermode='x',
                 plot_bgcolor=bg_color,
                 paper_bgcolor=bg_color,
                 height=650
                    )
   ,}
    return figure    


app.scripts.config.serve_locally = True
app.css.config.serve_locally = True
if __name__ == '__main__':
    app.run_server(debug=False,port=8080,host='0.0.0.0')



    
    