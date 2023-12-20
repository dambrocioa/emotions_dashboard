import streamlit as st
from st_files_connection import FilesConnection
from streamlit_echarts import JsCode
from streamlit_echarts import st_echarts
#from streamlit_raw_echarts import st_echarts,JsCode,CustomMap
import random
import numpy as np
import pandas
import json
import plotly.express as px

st.set_page_config(page_title="Sparky Hours", page_icon="⏰")

st.markdown("# Sparky Hours")
#st.sidebar.header("Personaliza ")
st.write(
    """Sparky Hours es un módulo de Sparky que permite registrar cuando un usuario hace check in o check out
        de unsa sesión de trabajo."""
)

@st.cache_data
def get_data_hours():
    conn = st.experimental_connection('s3', type=FilesConnection)
    data_hours = conn.read("sparky-final-summaries/Emotions/SPARKY_HOURS/summary.csv", input_format="csv", ttl=600)
    data_hours = data_hours.drop_duplicates()
    
    data_hours['date_obj'] = pandas.to_datetime(data_hours['date'],format='%Y-%m-%d %H:%M:%S')#.dt.time
    data_hours['time'] = data_hours['date_obj'].dt.time
    
    return data_hours

data_hours = get_data_hours()


# The side bar that contains radio buttons for selection of charts-----------------------------------------------------------
with st.sidebar:
    def update_selected_user():
        st.session_state["selected_user"] = st.session_state['selected_user_hours']
    st.header('Persona')
    users = tuple(list(data_hours["user"].unique()))
    
    if 'selected_user' not in st.session_state:
        st.session_state["selected_user"] = users[0]
    else:
        if st.session_state["selected_user"] in users:
            st.session_state['selected_user_hours'] = st.session_state["selected_user"]
        else:
            st.write('no user found')
            st.session_state['selected_user_hours'] = users[0]

    selected_user_hours = st.radio('Selecciona una persona',(users),key="selected_user_hours",on_change=update_selected_user)
    df = data_hours[data_hours['user']==selected_user_hours]


    st.header('Fecha')
    dates = df['short_date'].unique()
    selected_dates = st.multiselect('Selecciona una o varias fechas',dates, dates)
    df = df[df['short_date'].isin(selected_dates)]


    
# The main window--------------------------

#st.title("A Simple CO2 Emissions Dashboard")
#st.write("an example of a Streamlit layout using a sidebar")

df["time_str"] = df["date_obj"].dt.strftime('%H:%M:%S')
df["fake_date"] = ['2020-01-08 '+item for item in df["time_str"]]
df["fake_date_obj"] = pandas.to_datetime(df["fake_date"],format='%Y-%m-%d %H:%M:%S')
df["time_truncated"] = [time_str[0:5] for time_str in df["time_str"]]
n = df["short_date"].nunique()


with st.container():
    st.header("Horas de Check in / Check out")

    fig = px.scatter(df,
        x="fake_date_obj",
        y="short_date",
        range_x=['00:00','23:59'],
        color="action",
        color_discrete_map={
                            "check_in": "#16A085",
                            "check_out": "#FA8072",
                            "opt3": "#008aff"},
        text="time_truncated")
    
    fig.update_traces(marker_size=20,
                        textposition='top center',
                        hovertemplate = None,
                        hoverinfo = "skip")
    
    fig.update_layout(
        xaxis_title="Hora",
        yaxis_title="Día")
    
    fig.update_layout(
    yaxis_tickformat = '%Y-%m-%d',
    xaxis_tickformat = '%H:%M',
    showlegend=True)
    fig.update_yaxes(nticks=n) 

    st.plotly_chart(fig, theme=None, use_container_width=True) 

