import streamlit as st
from annotated_text import annotated_text, parameters
from streamlit_tags import st_tags, st_tags_sidebar
from st_files_connection import FilesConnection
from streamlit_echarts import JsCode
from streamlit_echarts import st_echarts
import datetime
import pandas
import pathlib
import sys


st.set_page_config(page_title="Sparky Words", page_icon="💬")
#st.write(sys.path)
# This adds the path of the …/src folder
# to the PYTHONPATH variable
sys.path.append(str(pathlib.Path().absolute()).split("/src")[0] + "/src")
sys.path.append('/mount/src/emotions_dashboard/src/')
#st.write(sys.path)
from my_module.sparky_NLP import get_ocurrences
#st.write(sys.path)

#ANOTATED TEXT PARAMETERS
parameters.SHOW_LABEL_SEPARATOR = True
parameters.BORDER_RADIUS = 0
parameters.PADDING = "0 0.25rem"

st.markdown("# Sparky Words")
#st.sidebar.header("Personaliza ")
st.write(
    """Sparky Words es un módulo de Sparky que permite registrar 
    ocurrencias de palabras clave encontradas en el texto que es tecleado en la computadora. 
    Algunos casos de uso son detección de acoso o cyberbullying, robo de información en beneficio de terceros.
    Actualmente esta información se actualiza una vez al día a la media noche. Es posible tener esta información 
    en tiempo real (con un retraso de algunos minutos). Para esto se debe contratar la opción adicional "tiempo real"
    """)

@st.cache_data
def get_data():
    conn = st.experimental_connection('s3', type=FilesConnection)
    data = conn.read("sparky-final-summaries/Demo/SPARKY_WORDS/summary.csv", input_format="csv", ttl=600)
    data = data.drop_duplicates()
    users_names = {"user_kl_13":"13","user_kl_24":"24","user_kl_test":"test","user_kl_test_win":"test_win"}

    data["user_name"] = [users_names[user_key] for user_key in data["user"]]
    data = data[data['user_name']!='UNKNOWN']
    
    return  data

data = get_data()


#def get_complete_corpus(my_dataframe):
#    corpus = {}
#    for index, row in my_dataframe.iterrows():
#        date = row["short_start_time"]
#        if date not in corpus.keys():
#            corpus[date] = ''
#        corpus[date] = corpus[date] + row["words"]+"\n"
#    return corpus

def get_formatted_corpus_as_txt(corpus):
    # receives a list of dicts, each one with the following keys:
    #| "user" | "date" "| short_date" | "week_info" | "original_message" | "cleaned_message"|
    #
    # returns a dict 
    #| "date": [string]
    formatted_corpus = {}
    for row in corpus:
        date = row["short_date"]
        if date not in formatted_corpus.keys():
            formatted_corpus[date] = ''
        formatted_corpus[date] = formatted_corpus[date] + row["cleaned_message"]+"\n"
    return formatted_corpus

def get_formatted_corpus_as_df(corpus):
    # receives a list of dicts, each one with the following keys:
    #| "user" | "date" "| short_date" | "week_info" | "original_message" | "cleaned_message"|
    #
    # returns a dict 
    # "data" dataframe 
    # each dataframe contains | "user" | "date" "| short_date" | "cleaned_message"|
    formatted_corpus_df = {}
    for row in corpus:
        date = row["short_date"]
        if date not in formatted_corpus_df.keys():
            formatted_corpus_df[date] = []
        formatted_corpus_df[date].append({"user_name":row["user_name"],"date":row["date"],"texto":row["cleaned_message"]})

    for date in formatted_corpus_df.keys():
        list_of_dicts = formatted_corpus_df[date]
        formatted_corpus_df[date] = pandas.DataFrame.from_records(list_of_dicts)
    return formatted_corpus_df

def get_dates_from_week_info(weeks):
    dates = []
    for week_start_date in weeks:
        week_start_date_obj = datetime.datetime.strptime(week_start_date,"%Y-%m-%d")
        for n in range(0,7):
            date_obj = week_start_date_obj + datetime.timedelta(days=n)
            date_str = date_obj.strftime('%Y-%m-%d')
            dates.append(date_str)
    return dates

# The side bar that contains radio buttons for selection of charts-----------------------------------------------------------
with st.sidebar:
    st.header('Persona')
    users = tuple(data['user_name'].unique())
    user_selected = st.radio("Selecciona un usuario",users)
    df = data[data['user_name']==user_selected]


    #st.header('Fecha')
    #dates = df['short_start_time'].unique()
    #selected_dates = st.multiselect('Selecciona una o varias fechas',dates, dates)
    #df = df[df['short_start_time'].isin(selected_dates)]

    st.header('Semana')
    weeks = df['week_info'].unique()
    selected_weeks = st.multiselect('Selecciona una o varias semanas',weeks, weeks)
    selected_dates = get_dates_from_week_info(selected_weeks)
    df = df[df['short_start_time'].isin(selected_dates)]


## This container will be displayed below the text above-----------------------------------------------------------
annotated_text(tuple(["Esta información se actualiza cada 24 horas a la media noche.","","#fea"]))
annotated_text(tuple(["Esto es, todos los días a la media noche se agrega a este panel la información generada por el usuario durante ese mismo día.","","#fea"]))

with st.container():
    #st.header("¿Qué están escribiendo?")
    #st.info("""Puedes visualizar si existe una ocurrencia de alguna palabra. Algunas plabras están precargadas, puedes quitar o agregar más.""")

    st.divider() 
    values = ["faby","fabi","siemens", "gamifi", "extern"]
    st.markdown("## 1. Puede buscar palabras exactas en el texto tecleado por el usuario")
    keywords = st_tags(
                label='### Seleccione las palabras exactas que desea buscar',
                text='Escribe una palabra y da Enter',
                value=values,
                suggestions=[],
                maxtags = -1,
                key='1')
    
    st.divider() 
    st.markdown('### Resultados')
    
    patterns_detected = []
    patterns_occurrences = {}
    corpus,patterns_detected,patterns_occurrences = get_ocurrences(data=df,patterns_to_find=keywords,size=10)
    
    st.markdown('#### Resumen de Resultados')
        
    for pattern in keywords:
        if pattern in patterns_occurrences.keys():
            text_to_show = [f"* Para la palabra",tuple([pattern,"","#fea"]),f"se encontraron **{patterns_occurrences[pattern]}** ocurrencias"]
        else:
            text_to_show = [f"* Para la palabra",tuple([pattern,"","#fea"]),f"**no** se encontraron ocurrencias"]
        annotated_text(text_to_show)

    st.markdown('#### Detalle de Resultados')
    
    for pattern in keywords:
        if len(patterns_detected)>0:
            if pattern in patterns_detected.keys():
                st.write(f'##### {pattern}')
                ocurrences = patterns_detected[pattern]

                for element in ocurrences:
                    fecha_de_ocurrencia = element["date"]    
                    text_to_display = element["message_formatted"]
                    
                    #Display ocurrence details
                    st.write(f'###### Encontrado el {fecha_de_ocurrencia}')
                    annotated_text(text_to_display)
                    with st.expander("Ver contexto"):
                        st.markdown('###### Antes escribió')
                        st.write(element["lines_before"])
                        
                        st.markdown('###### Después escribió')
                        st.write(element["lines_after"])

    st.divider()
    st.markdown('## 2. Panorama completo')
    st.markdown('#### Puede ver todo el texto tecleado por el usuario por fecha')
    #Format corpus as list of strings to display in text area below
    formatted_corpus = get_formatted_corpus_as_txt(corpus)
    
    #Format corpus as data frame to display it in a Table
    formatted_corpus_df = get_formatted_corpus_as_df(corpus)
    
    #st.markdown("## Texto completo generado por el usuario en el intervalo de fechas seleccionado")
    #for date in selected_dates:
    #    formatted_corpus_by_date = formatted_corpus[date]
    #    txt = st.text_area(label=f'Texto tecleado por el usuario durante el día {date}', 
    #                 value=formatted_corpus_by_date+'.',
    #                 placeholder = 'Introduzca un texto',
    #                 disabled=True)


    for date in selected_dates:
        if date in formatted_corpus.keys():
            formatted_corpus_by_date = formatted_corpus[date]
            txt = st.text_area(label=f'Texto tecleado por el usuario durante el día {date}', 
                         value=formatted_corpus_by_date+'.',
                         placeholder = 'Introduzca un texto',
                         disabled=True)
            with st.expander("Ver más detalle (hora específica)"):
                st.table(formatted_corpus_df[date])
        else:
            st.write(f"Sin datos para el usuario seleccionado, en la fecha del {date}")
