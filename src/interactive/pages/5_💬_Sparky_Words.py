import streamlit as st
from annotated_text import annotated_text, parameters
from streamlit_tags import st_tags, st_tags_sidebar
from st_files_connection import FilesConnection
from streamlit_echarts import JsCode
from streamlit_echarts import st_echarts
import pandas
import pathlib
import sys


st.set_page_config(page_title="Sparky Words", page_icon="💬")

# This adds the path of the …/src folder
# to the PYTHONPATH variable
sys.path.append(str(pathlib.Path().absolute()).split("/src")[0] + "/src")

from mymodule.sparky_NLP import get_ocurrences
st.write(sys.path)

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
    En este demo, esta información se actualiza cada semana. Es posible tener esta información 
    en tiempo real (con un retraso de algunos minutos).
    Para este demo usamos las palabras clave siguientes: """)

@st.cache_data
def get_data():
    conn = st.experimental_connection('s3', type=FilesConnection)
    data = conn.read("sparky-final-summaries/Demo/SPARKY_WORDS/summary.csv", input_format="csv", ttl=600)
    data = data.drop_duplicates()
    return  data

data = get_data()


# The side bar that contains radio buttons for selection of charts-----------------------------------------------------------
with st.sidebar:
    st.header('Persona')
    users = tuple(data['user'].unique())
    user_selected = st.radio("Selecciona un usuario",users)
    df = data[data['user']==user_selected]


    st.header('Fecha')
    dates = df['short_start_time'].unique()
    selected_dates = st.multiselect('Selecciona una o varias fechas',dates, dates)
    df = df[df['short_start_time'].isin(selected_dates)]


## This container will be displayed below the text above-----------------------------------------------------------
with st.container():
    ##st.header("¿Qué están escribiendo?")
    ##st.info("""Puedes visualizar si existe una ocurrencia de alguna palabra""")

    texto = """ Instrucciones para volar
        El volar es un arte o, mejor dicho, un don.
        El don consiste en aprender a tirarse al suelo y fallar.
        La primer parte es fácil. Lo único que se necesita es simplemente la habilidad de tirarse hacia adelante con todo el peso del cuerpo, y buena voluntad para que a uno no le importe que duela. Es decir, dolerá si no se logra evitar el suelo. La mayoría de la gente no consigue evitar el suelo, y si de verdad lo intenta como es debido, lo más probable es que no logre evitarlo de ninguna manera.
        Está claro que la segunda parte, la de evitar el suelo, es la que presenta dificultades.
        El primer problema es que hay que evitar el suelo por accidente. No es bueno tratar de evitarlo deliberadamente, porque no se conseguirá. Hay que distraer de golpe la atención con otra cosa cuando se está a medio camino, de manera que ya no se piense en caer, o en el suelo, o en cuánto le va a doler a uno si no logra evitarlo.
        Es sumamente difícil distraer la atención de esas tres cosas durante la décima de segundo que uno tiene a su disposición. De ahí que fracasen la mayoría de las personas y que finalmente se sientan decepcionadas de este deporte estimulante y espectacular. Sin embargo, si se es lo suficientemente afortunado para quedar distraído justo en el momento crucial por, digamos, unas piernas espléndidas, por una bomba que estalle cerca o por la repentina visión de una especie sumamente rara de escarabajo que se arrastre junto a un hierbajo próximo, entonces, para sopresa propia, se evitará el suelo por completo y uno quedará flotando a pocos centímetros de él en una postura que podría parecer un tanto estúpida.
        Es éste un momento de soberbia y delicada concentración.
        Oscilar y flotar, flotar y oscilar.
        Ignore toda consideración sobre su propio peso y déjese flotar más alto.
        No escuche lo que alguien le diga en ese momento, porque es improbable que sea algo de provecho.
        – ¡Santo Dios, no es posible que estés volando! – es el tipo de comentario que suele hacerse.
        Es de importancia vital no creerlo, o ese alguien tendrá razón de pronto.
        Flote cada vez más alto.
        Intente unos descensos en picado, suaves al principio, luego flote a la deriva sobre las copas de los árboles respirando con normalidad.
        NO SALUDE A NADIE.
        Cuando haya hecho esto unas cuantas veces, descubrirá que el momento de distracción se logra cada vez con mayor facilidad.
        Entonces aprenderá todo tipo de cosas sobre cómo dominar el vuelo, la velocidad, la capacidad de maniobra, y el truco consiste normalmente en no pensar demasiado en lo que uno quiere hacer, sino limitarse a dejar que ocurra como si fuese a suceder de todos modos.
        También aprenderá a aterrizar como es debido, algo en que casi con seguridad fracasará, y de mala manera, al primer intento. 
        Del libro: “La vida, el universo y todo lo demás” de Douglas Adams
        """

    def get_corpus(txt):
        list_of_strings_to_analyse = texto.split(".")
        list_of_strings_to_analyse = [string_item +'.' for string_item in list_of_strings_to_analyse]
        return list_of_strings_to_analyse

    def format_pattern(pattern):
        return tuple([pattern, "found","#fea"])

    #default corpus
    list_of_strings_to_analyse = get_corpus(texto)

    st.divider() 
    st.markdown("## Paso 1: Introduzca un texto")
    txt = st.text_area(label='Texto para hallar ocurrencias', 
                     value=texto+'.',
                     placeholder = 'Introduzca un texto',
                     disabled=True)

    st.divider() 
    keywords = st_tags(
                label='## Paso 2: Introduzca las palabras que quiere buscar:',
                text='Escribe una palabra y da Enter',
                value=['demas','volar','alas'],
                suggestions=[],
                maxtags = -1,
                key='1')
    
    list_of_strings_to_analyse = get_corpus(txt)

    
    st.divider() 
    st.markdown('## Paso 3: Observe los resultados')
    
    patterns_detected = []
    patterns_occurrences = {}
    patterns_detected,patterns_occurrences = get_ocurrences(list_of_strings_to_analyse=list_of_strings_to_analyse,patterns_to_find=keywords,size=2)
    
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
                    text_to_display = element["message_formatted"]
                    
                    #Display ocurrence details
                    annotated_text(text_to_display)
                    with st.expander("Ver contexto"):
                        st.markdown('###### Antes escribió')
                        st.write(element["lines_before"])
                        
                        st.markdown('###### Después escribió')
                        st.write(element["lines_after"])

        

