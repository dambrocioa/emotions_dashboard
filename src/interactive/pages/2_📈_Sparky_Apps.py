import streamlit as st
from st_files_connection import FilesConnection
from streamlit_echarts import JsCode
from streamlit_echarts import st_echarts
#from streamlit_raw_echarts import st_echarts,JsCode,CustomMap
import random
import numpy as np
import pandas
import json
import math
import datetime

st.set_page_config(page_title="Sparky Apps", page_icon="📈")

st.markdown("# Sparky Apps")
#st.sidebar.header("Personaliza ")
st.write(
    """Sparky Apps es un módulo de Sparky que permite registrar 
    qué aplicaciones se usan en el equipo PC. 
    Ejemplos de aplicaciones son Excel, Word, etc."""
)

@st.cache_data
def get_data_apps():
    conn = st.experimental_connection('s3', type=FilesConnection)
    data_apps = conn.read("sparky-final-summaries/Emotions/SPARKY_APPS/summary.csv", input_format="csv", ttl=600)
    data_apps = data_apps.drop_duplicates()
    return  data_apps

data_apps = get_data_apps()


# The side bar that contains radio buttons for selection of charts-----------------------------------------------------------
with st.sidebar:
    def update_selected_user():
        st.session_state["selected_user"] = st.session_state['selected_user_apps']
    st.header('Persona')
    users = data_apps['user'].unique()
    
    if 'selected_user' not in st.session_state:
        st.session_state["selected_user"] = users[0]
    else:
        if st.session_state["selected_user"] in users:
            st.session_state['selected_user_apps'] = st.session_state["selected_user"]
        else:
            st.write('no user found')
            st.session_state['selected_user_apps'] = users[0]

    selected_user_apps = st.radio('Selecciona una persona',(users),key="selected_user_apps",on_change=update_selected_user)

    df = data_apps[data_apps['user']==selected_user_apps]
    st.write(st.session_state['selected_user'])


    st.header('Fecha')
    #sort dates to display them in order
    dates = list(df['date'].unique())
    dates.sort(key=lambda date: datetime.datetime.strptime(date, "%Y-%m-%d"))
    
    selected_dates = st.multiselect('Selecciona una o varias fechas',dates, dates)
    df = df[df['date'].isin(selected_dates)]

    # Data is a list of dict {'value': your_value, 'name': your_name}
    edata = []
    res = {}

    for index, row in df.iterrows():
        app = row["app"]
        usage_time = row["total_usage_time"]
        if app not in res.keys():
            res[app] = 0
        res[app] = res[app] + usage_time
    for app in res.keys():
        edata.append({"value":int(res[app]/60.),"name":app.lower().replace(".exe","").title()})
    
    def randomly_distribute(number):
        l = []
        for i in range(0,7,1):
            random_n = random.randint(0, int(number)) 
            number = number - random_n
            l.append(random_n)
        return l

    data_stacked_chart = []
    days_stacked_chart = selected_dates
    
    def get_data_aps_usage_per_day():
        apps_universe = df["app"].unique()
        
        for app in apps_universe:
            list_of_values = []
            Total_usage_time = math.ceil(df[df["app"]==app]["total_usage_time"].sum()/60.)
            if Total_usage_time>=0:
                for date in selected_dates:
                    current_date_apps = df[df["date"]==date]["app"].unique()
                    if app in current_date_apps:
                        total_usage_time = math.ceil(df[(df["app"]==app) & (df["date"]==date)]["total_usage_time"].sum()/60.)
                    else:
                        total_usage_time = 0
                    list_of_values.append(total_usage_time)
                data_stacked_chart.append({"name":app,"type": 'bar',"stack": 'total',"label": {"show": "true"},"emphasis": {"focus": "series"},"data":list_of_values})
        return data_stacked_chart

    data_stacked_chart = get_data_aps_usage_per_day()

# This container will be displayed below the text above
with st.container():
    st.header("¿Qué aplicaciones están usando?")
    st.info("""Minutos destinados en cada aplicación, por el usuario seleccionado y dentro del rango de fechas seleccionadas.""")
    option = {
                "toolbox": {
                    "show": "true",
                    "feature": {
                        "mark": {"show": "true"},
                        "dataView": {"show": "true", "readOnly": "false"},
                        "restore": {"show": "true"},
                        
                    }
                },
                "series": [
                        {
                            "name": 'Tiempo de uso (min)',
                            "type": 'pie',
                            "radius": ['40%', '75%'],
                            "avoidLabelOverlap": "false",
                            "itemStyle": {
                                "borderRadius": "10",
                                "borderColor": '#fff',
                                "borderWidth": "2"
                            },
                            "label": {
                                "show": "true",
                                "position": "center"
                            },
                            "emphasis": {
                                "label": {
                                    "show": "false",
                                    "fontSize": '15',
                                    "fontWeight": 'bold'
                                }
                            },
                            "labelLine": {
                                "show": "false"
                            },
                            "data": edata
                        }
                    ],
                "tooltip": {
                            "show": "false"
                            },
            };
    st_echarts(options=option, key="2",height=400)
with st.container():
    st.header("¿Qué días usan qué aplicaciones?")
    st.info("""Minutos destinados a cada aplicación por día seleccionado. Esta gráfica muestra el detalle por día.""")
    option = {
              "tooltip": {
                "trigger": 'axis',
                "axisPointer": {
                  "type": 'shadow' 
                },
                "order":'valueDesc'
              },
              "grid": {
                "left": '3%',
                "right": '4%',
                "bottom": '3%',
                "containLabel": "false"
              },
              "xAxis": {
                "type": "value",
                "axisLabel": {
                        "formatter": '{value} min',
                        "align": 'center'
                        }
              },
              "yAxis": {
                "type": "category",
                "data": days_stacked_chart
              },
              "series": data_stacked_chart
            };
    st_echarts(options=option, key="1",height=400)

