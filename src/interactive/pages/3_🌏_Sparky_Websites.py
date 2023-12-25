import streamlit as st
from st_files_connection import FilesConnection
from streamlit_echarts import JsCode
from streamlit_echarts import st_echarts
#from streamlit_raw_echarts import st_echarts,JsCode,CustomMap
import random
import numpy as np
import pandas
import json
import datetime

st.set_page_config(page_title="Sparky Websites", page_icon="🌏")

st.markdown("# Sparky Websites")
#st.sidebar.header("Plotting Demo")
st.write(
    """Sparky websites permite visualizar el historial de navegación en la PC."""
)

@st.cache_data
def get_data_websites():
    conn = st.experimental_connection('s3', type=FilesConnection)
    data_websites = conn.read("sparky-final-summaries/Emotions/SPARKY_WEBSITES/summary.csv", input_format="csv", ttl=600)
    data_websites = data_websites.drop_duplicates() # not very comftable with this but it works.
    #data_websites["user"] = "user_kl_test" #--WARNING THIS LINE IS SPECIALLY FOR DEMO PURPOSES------
    data_websites['netloc'] = data_websites['netloc'].fillna("no_data")

    #rename some columns to display df
    data_websites.rename(columns = {'netloc':'sitio','path':'sub_sitio','short_date':'fecha','date':'fecha_y_hora'}, inplace = True)
    
    
    return  data_websites

data_websites = get_data_websites()


# The side bar that contains radio buttons for selection of charts-----------------------------------------------------------
with st.sidebar:
    
    def update_selected_user():
        st.session_state["selected_user"] = st.session_state['selected_user_websites']
    
    st.header('Persona')
    users = data_websites['user'].unique()
    
    if 'selected_user' not in st.session_state:
        st.session_state["selected_user"] = users[0]
    else:
        if st.session_state["selected_user"] in users:
            st.session_state['selected_user_websites'] = st.session_state["selected_user"]
        else:
            st.write('no user found')
            st.session_state['selected_user_websites'] = users[0]

    selected_user_websites = st.radio('Selecciona una persona',(users),key="selected_user_websites",on_change=update_selected_user)
    df_ws = data_websites[data_websites['user']==selected_user_websites]


    st.header('Fecha')
    #sort dates to display them in order
    dates = list(df_ws['fecha'].unique())
    dates.sort(key=lambda date: datetime.datetime.strptime(date, "%Y-%m-%d"))

    selected_date = st.radio('Selecciona una o varias fechas',(dates))
    df_ws = df_ws[df_ws['fecha'] == selected_date] 

    df_ws = df_ws[(df_ws['sitio']!= "") &(df_ws['sitio']!= "no_data")]
    df_ws['Count'] = [len(df_ws[df_ws['sitio']==sitio]) for sitio in df_ws['sitio']]
    df_ws = df_ws.sort_values(['Count'], ascending=False)

    # Data is a list of dict {'value': your_value, 'name': your_name}
    data_web_rose_chart = []
    for sitio in df_ws['sitio'].unique():
        count = int(df_ws[df_ws['sitio']==sitio]['sitio'].count())
        data_web_rose_chart.append({"value":count,"name":sitio})

with st.container():
    st.header("¿Qué sitios visitan y cuándo?")
    st.info("""Observa el historial de navegación del usuario seleccionado, en el intervalo de tiempo seleccinado.""")
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
                        "name": 'Websites visitados',
                        "type": 'pie',
                        "radius": ["30", "120"],
                        "center": ['50%', '60%'],
                        "roseType": 'area',
                        "itemStyle": {
                            "borderRadius": "8"
                        },
                        "data": data_web_rose_chart
                    }
                ],
                "tooltip": {
                                "show": "false"
                            },
                "label": {
                    "show":"false"
                },
            };
    st_echarts(options=option, height="400px")

with st.container():
    st.header("Header")
    st.info("""Description""")
    

    websites = df_ws[["user","sitio","sub_sitio","fecha","fecha_y_hora"]]
    st.dataframe(websites)
