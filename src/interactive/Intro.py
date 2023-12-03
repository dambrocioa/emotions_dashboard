import streamlit as st
from annotated_text import annotated_text, parameters
from PIL import Image
import pathlib
import sys

st.set_page_config(page_title="Sparky Dashboard", page_icon="🐶")

# This adds the path of the …/src folder
# to the PYTHONPATH variable
sys.path.append(str(pathlib.Path().absolute()).split("/src")[0] + "/src")


st.write("# Bienvenido al Dashboard interactivo de Sparky! 👋 🐶 👋 ")

st.markdown(
        """
        Este Dashboard fue hecho para Emotions con ❤️.

        ## ¿Qué es Sparky?

        Sparky es un fiel guardián de tu organización. Es un software que permite monitorear el uso de un equipo de tipo PC.
        Sparky tiene los siguientes módulos de monitoreo:
        - **Sparky Apps** Aplicaciones que se usan en el equipo. Ejemplos de aplicaciones son Excel, Word, etc.
        - **Sparky Files** Archivos que se crean, modifican, se mueven de carpeta o se borran.
        - **Sparky Websites** Websites visitados en el equipo, en Chrome, Edge y Firefox.
        - **Sparky Hours** Es un reloj checador, permite al usuario de la PC registrar su hora de entrada y de salida.
        - **Sparky Words** Es un buscador de palabras clave, permite monitorear las palabras tecleadas en la PC. 
        
        Estos módulos se instalan en el equipo o PC y de manera discreta permiten el moniteo. 
        No es necesario activar los módulos, sino que corren cada vez que se desbloquea la PC y 
        envían información de manera regular. Ningún módulo hace lento al equipo en el que se usa. 

        Toda la información recibida está almacenada indefinidamente y de manera segura en servidores de Amazon Webservices (AWS). 

        Sparky dashboard, consume esa información y permite visualizar estos reportes de las PC's en este dashbord.

        ## Beneficios
        - **Visibilidad inmediata** El monitoreo es en tiempo real (con un retraso de algunos min).
        - **Seguridad y Discreción**. El acceso al dashboard (a excepción de este que es un Demo) se hace mediante un usuario y password. No hay necesidad de archivos que pueden caer en las manos incorrectas.
        - **Fácilidad de lectura**. La lectura de los charts es más sencilla que la de los reportes en PDF. Además, en un solo dashboard se puede ver la actividad de todos los usuarios así su actividad de cualquier fecha (a partir de la instalación del software). 

        
        ## Posibles módulos personalizados

        Se pueden desarrollar módulos personalizados a medida, como por ejemplo:
        - Alertas ante palabras clave encontradas en nombres de archivos
        - Dashboard de desempeño de un área o equipo de trabajo en el que un manager/gerente de área podría visualizar ciertos módulos de su equipo a cargo.
        - Dashboard de desempeño personal. Un usuario puede tener su propio dashboard para ver sus horas de check in / check out. Podría tener sus metas de semana y el avance logrado en la misma. 
        - Contraste de horas reportadas de check in / check out contra la actividad en la PC.
    

        ## Planes y precios
    """
    )



image = Image.open('src/interactive/images/planes.png')

st.image(image, caption='Planes')
