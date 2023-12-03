import streamlit as st
from st_files_connection import FilesConnection
from streamlit_echarts import JsCode
from streamlit_echarts import st_echarts
#from streamlit_raw_echarts import st_echarts,JsCode,CustomMap
import random
import numpy as np
import pandas
import json
import pathlib
import sys
import plotly.express as px

st.set_page_config(page_title="Sparky Files", page_icon="🗂")

# This adds the path of the …/src folder
# to the PYTHONPATH variable
sys.path.append(str(pathlib.Path().absolute()).split("/src")[0] + "/src")

st.markdown("# Sparky Files")
#st.sidebar.header("Plotting Demo")
st.write(
    """Sparky Files registra las acciones que se realizan sobre archivos en la PC: creación, modificación, cambio de carpeta y borrado de archivos."""
)

@st.cache_data
def get_data_files():
    conn = st.experimental_connection('s3', type=FilesConnection)
    data_files = conn.read("sparky-final-summaries/Demo/SPARKY_FILES/summary.csv", input_format="csv", ttl=600)
    data_files = data_files.drop_duplicates()

    #create date time obje column
    data_files['date_obj'] = pandas.to_datetime(data_files['date'],format='%Y-%m-%d %H:%M:%S')#.dt.time
    
    #remove sparky files
    data_files = data_files[data_files["src_path"].str.contains(r'C:\\kls_checkin\\', na = False) == False]

    #rename some columns to display df
    data_files.rename(columns = {'src_path':'ruta','display_src_path':'archivo','date':'fecha'}, inplace = True)

    return  data_files

data_files = get_data_files()

#--------single axis scatter chart

with st.sidebar:
    def update_selected_user():
        st.session_state["selected_user"] = st.session_state['selected_user_files']
    st.header('Persona')
    users = tuple(list(data_files["user"].unique()))
    
    if 'selected_user' not in st.session_state:
        st.session_state["selected_user"] = users[0]
    else:
        if st.session_state["selected_user"] in users:
            st.session_state['selected_user_files'] = st.session_state["selected_user"]
        else:
            st.write('no user found')
            st.session_state['selected_user_files'] = users[0]

    selected_user_files = st.radio('Selecciona una persona',(users),key="selected_user_files",on_change=update_selected_user)
    df = data_files[data_files['user']==selected_user_files]

    st.header('Fecha')
    dates = tuple(list(df['short_date'].unique()))
    date_selected = st.radio("Selecciona una fecha",(dates))
    df = df[df['short_date'] ==date_selected]

    
# The main window--------------------------

#st.title("A Simple CO2 Emissions Dashboard")
#st.write("an example of a Streamlit layout using a sidebar")

# This container will be displayed below the text above
with st.container():
    st.header("¿Qué archivos se trabajan?")
    st.info("""Esta tabla muestra los archivos trabajados por el usuario en la fecha seleccionada""")
    
    files = df[["archivo","ruta","fecha"]]
    st.dataframe(files)
    

with st.container():
    #col1 = st.columns((100))
    #with col2:
    st.header("¿Cuándo estuvieron trabajando sobre los archivos?")
    st.info("Detalle del día en que se trabajaron los archivos.")
    
    #fig = px.line(df, x='fecha', y='lifeExp', color='country', markers=True)
    
    #st.plotly_chart(fig, theme=None, use_container_width=True) 

    df["time_str"] = df["date_obj"].dt.strftime('%H:%M:%S')
    df["fake_date"] = ['2020-01-08 '+item for item in df["time_str"]]
    df["fake_date_obj"] = pandas.to_datetime(df["fake_date"],format='%Y-%m-%d %H:%M:%S')
    df["time_truncated"] = [time_str[0:5] for time_str in df["time_str"]]
    n = df["short_date"].nunique()

    fig = px.scatter(df,
        x="fake_date_obj",
        y="short_date",
        range_x=['00:00','23:59'])
    
    fig.update_traces(mode="markers+lines",
                        marker_size=20,
                        textposition='top center',
                        hovertemplate ="{archivo}")
    
    fig.update_layout(
        xaxis_title="Hora",
        yaxis_title="Día")
    
    fig.update_layout(
    yaxis_tickformat = '%Y-%m-%d',
    xaxis_tickformat = '%H:%M',
    showlegend=True)
    fig.update_yaxes(nticks=n) 

    st.plotly_chart(fig, theme=None, use_container_width=True) 
    

  