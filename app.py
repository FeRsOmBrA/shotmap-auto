import os
import streamlit as st
import fitz  # PyMuPDF
import datetime
import google.generativeai as genai

# Configurar la clave de la API de Gemini
GOOGLE_API_KEY = st.secrets['google_api_key']
genai.configure(api_key=GOOGLE_API_KEY)

# Título de la aplicación
st.title("Generador de Plantillas de Correo de Voladuras")

# Selección de opción: Automático o Manual
option = st.selectbox(
    'Seleccione la opción de generación de plantillas:',
    ('Automático (usando el PDF del Daily Priority Report)', 'Manual')
)

# Función para extraer texto del PDF


def extract_text_from_pdf(pdf_file):
    pdf_document = fitz.open(stream=pdf_file.read(), filetype='pdf')
    text = ''
    for page in pdf_document:
        text += page.get_text()
    return text


# Obtener la fecha actual en formato MM/DD/YYYY
today = datetime.date.today()
date_str = today.strftime('%m/%d/%Y')

# Números de los coordinadores por PIT

coordinators = {
    'PIT 2': {
        'coordinator_phone': '3157514144',
        'meeting_point': 'Mirador 1 DE MAYO PIT 2'
    },
    'PIT 5': {
        'coordinator_phone': '3185166975',
        'meeting_point': 'Mirador Rampa 2 Pit 5'
    }
}

if option == 'Automático (usando el PDF del Daily Priority Report)':
    # Cargar el PDF
    uploaded_file = st.file_uploader(
        "Cargue el PDF del Daily Priority Report", type=['pdf'])
    if uploaded_file is not None:
        # Extraer texto del PDF
        pdf_text = extract_text_from_pdf(uploaded_file)

        # Seleccionar PIT y tipo de plantilla
        pit = st.selectbox('Seleccione el PIT:', ['PIT 2', 'PIT 5'])
        template_type = st.selectbox('Seleccione el tipo de plantilla:', [
            'Voladuras programadas',
            'Voladuras reprogramadas',
            'Voladuras canceladas',
            'No hay voladuras'
        ])

        if st.button('Generar plantilla'):
            # Preparar las instrucciones del sistema para la IA, incluyendo los ejemplos
            system_instructions = """
Eres un asistente que ayuda a generar plantillas de correo para programaciones de voladuras en una mina.

Sigue exactamente los formatos de correo como en los siguientes ejemplos proporcionados.

Todos los correos deben estar en fuente Calibri 12, y los textos que estén entre ** ** deben ir en negrilla.

Ejemplos, estos ejemplos pueden variar sus datos, debes tener en cuenta lo que te dice el usuario, ademas, debes respetar y colocar de manera espaciada los parrafos del correo para evitar que se monten en la misma linea, esto lo consigues colocandolos de manera separada por espacios.

1. Correo de voladuras programadas para el pit 5.

Subject : EDN PIT5_ 11/26/24 Voladuras programadas para hoy / Shots Scheduled Today

Archivo adjunto: Voladuras_El Descanso_November_26_2024_Pit5.pdf

Cuerpo:
Buenos Días,

Las siguientes son las voladuras programadas para el día de hoy **11/26/2024**, en la Mina El Descanso. Por favor revisar el mapa adjunto.
Reunión con el Coordinador de Voladuras en el **PUNTO DE REUNION***, a las 8:00 am.
Coordinador de voladuras: Celular 3185166975
**Las voladuras son a la 12:30 PM**

Good Morning,
Following are the shots scheduled for today **11/26/2024** at El Descanso Mine. Please see the map attached.
Blasting coordinator meeting at  **PUNTO DE REUNION*** at 8:00 am.
Blasting Coordinator: Cell Phone 3185166975
**The shots are at 12:30 PM**

[tabla con las voladuras, coordenadas]

Regards,

[firma]

2. Correo de voladuras programadas para el pit 2.

Subject: EDN PIT2_ 11/26/24 Voladuras programadas para hoy / Shots Scheduled Today

Archivo adjunto: Voladuras_El Descanso_November_26_2024_Pit2.pdf

Cuerpo:
Buenos Días,

Las siguientes son las voladuras programadas para el día de hoy **11/26/2024**, en la Mina El Descanso. Por favor revisar el mapa adjunto.
Reunión con el Coordinador de Voladuras en el **PUNTO DE REUNION***, a las 8:00 am.
Coordinador de voladuras: Celular 3157514144
**Las voladuras son a la 12:30 PM**

Good Morning,
Following are the shots scheduled for today **11/26/2024** at El Descanso Mine. Please see the map attached.
Blasting coordinator meeting at lookout **PUNTO DE REUNION** at 8:00 am.
Blasting Coordinator: Cell Phone 3157514144
**The shots are at 12:30 PM**

[tabla con las voladuras, coordenadas]

Regards,

[firma]

3. Correo de voladuras reprogramadas para el pit 5.

Subject: EDN PIT5_ 11/22/24 MODIFICACION PROGRAMACION DE VOLADURAS para hoy / Shots Scheduled Today

Archivo adjunto: Ninguno

Cuerpo:

Buenos Días,

Las voladuras para el día de hoy 11/22/2024 **fueron reprogramada a las 1:30 PM**, Pit 5 en la Mina Descanso.

Good Morning,

The shot schedule for today 11/22/2024 **was rescheduled at 1:30 PM**, Pit 5 at Descanso Mine.

Regards,

[firma]

4. Correo de voladuras canceladas para el pit 2

Subject: EDN PIT2_ 11/22/24 MODIFICACION PROGRAMACION DE VOLADURAS para hoy /

Archivo adjunto: Ninguno

Cuerpo:

Buenos Días,
Las voladuras programadas para el día de hoy 11/22/2024 en el Bloque G fueron **CANCELADAS**

Good Morning,
The shot schedule for today 11/22/2024 in the Block G, was **CANCELLED**

Regards,

[firma]

5. Correo de no hay voladuras para el pit 5.

Subject: EDN PIT5_ 12/1/2024 NO hay Voladuras programadas para hoy/ NO Shots Scheduled Today

Archivo adjunto: Ninguno

Cuerpo:
Buenos Días,

No hay voladuras programadas para el día de hoy 12/1/2024, en el Pit 5

Saludos,

Good Morning,

No shots schedule for today 12/1/2024 at PIT 5

Regards,

[firma]

6. Correo de no hay voladuras programadas para el pit 2.

Subject: EDN PIT2_ 11/29/24 NO hay Voladuras programadas para hoy/ NO Shots Scheduled Today

Archivo adjunto: Ninguno

Cuerpo:

Buenos Días,

No hay voladuras programadas para el día de hoy 11/29/2024, en el Pit 2

Saludos,

Good Morning,

No shots schedule for today 11/29/2024 at PIT 2.

Regards,

[firma]

Recuerda que el correo debe tener el mismo formato, con el Asunto y luego el Cuerpo.

No incluyas ningún texto extra.

"""

            # Crear el modelo con las instrucciones del sistema
            model = genai.GenerativeModel(
                model_name='gemini-1.5-pro-latest', system_instruction=system_instructions)

            # Preparar el prompt específico
            prompt = f"""
Genera la plantilla de correo basada en los siguientes datos:
- Pit: {pit}
- Tipo de plantilla: {template_type}
- Fecha: {date_str}
- Texto del PDF: {pdf_text}
- Número de coordinador: {coordinators[pit]['coordinator_phone']}

Reemplaza las variables según corresponda.

No incluyas ningún texto extra a excepción de lo que se te pide y respeta el formato del correo, sigue mis instrucciones de manera obligatoria.
"""

            # Generar el correo usando la API de Gemini
            response = model.generate_content(prompt)
            email_text = response.text

            # Mostrar el correo
            st.markdown(email_text)

else:
    # Entrada manual de datos
    pit = st.selectbox('Seleccione el PIT:', ['PIT 2', 'PIT 5'])
    template_type = st.selectbox('Seleccione el tipo de plantilla:', [
        'Voladuras programadas',
        'Voladuras reprogramadas',
        'Voladuras canceladas',
        'No hay voladuras'
    ])
    date_input = st.date_input('Fecha', today)
    date_str = date_input.strftime('%m/%d/%Y')

    if template_type == 'Voladuras programadas':
        punto_reunion = st.text_input(
            'Punto de reunión', coordinators[pit]['meeting_point'])
        hora_reunion = st.text_input('Hora de reunión', '8:00 am')
        hora_voladura = st.text_input('Hora de las voladuras', '12:30 PM')
        table_image = st.file_uploader(
            "Cargue la imagen de la tabla con las voladuras", type=['png', 'jpg', 'jpeg'])
    elif template_type == 'Voladuras reprogramadas':
        hora_voladura_reprogramada = st.text_input(
            'Nueva hora de las voladuras', '1:30 PM')
        bloque = st.text_input('Bloque', 'Pit 5' if pit ==
                               'PIT 5' else 'Bloque G')
    elif template_type == 'Voladuras canceladas':
        bloque = st.text_input('Bloque', 'Bloque G')
    else:
        pass  # No se necesitan más datos

    if st.button('Generar plantilla'):
        # Preparar el cuerpo del correo según el tipo de plantilla
        if template_type == 'Voladuras programadas':
            subject = f"EDN {pit}_ {
                date_str} Voladuras programadas para hoy / Shots Scheduled Today"
            attachment = f"Voladuras_El Descanso_{today.strftime('%B')}_{today.day}_{
                today.year}_{pit.replace(' ', '')}.pdf"
            body = f"""
**Subject:** {subject}

**Archivo adjunto:** {attachment}

Buenos Días,

Las siguientes son las voladuras programadas para el día de hoy **{date_str}**, en la Mina El Descanso. Por favor revisar el mapa adjunto.

Reunión con el Coordinador de Voladuras en el **{punto_reunion}**, a las {hora_reunion}.

Coordinador de voladuras: Celular {coordinators[pit]['coordinator_phone']}

**Las voladuras son a la {hora_voladura}**

Good Morning,

Following are the shots scheduled for today **{date_str}** at El Descanso Mine. Please see the map attached.

Blasting coordinator meeting at  **{punto_reunion}** at {hora_reunion}.

Blasting Coordinator: Cell Phone {coordinators[pit]['coordinator_phone']}

**The shots are at {hora_voladura}**

[tabla con las voladuras, coordenadas]

Regards,

[firma]
"""
        elif template_type == 'Voladuras reprogramadas':
            subject = f"EDN {pit}_ {
                date_str} MODIFICACION PROGRAMACION DE VOLADURAS para hoy / Shots Scheduled Today"
            attachment = "Ninguno"
            body = f"""
**Subject:** {subject}

**Archivo adjunto:** {attachment}

Buenos Días,

Las voladuras para el día de hoy {date_str} **fueron reprogramada a las {hora_voladura_reprogramada}**, {bloque} en la Mina Descanso.

Good Morning,

The shot schedule for today {date_str} **was rescheduled at {hora_voladura_reprogramada}**, {bloque} at Descanso Mine.

Regards,

[firma]
"""
        elif template_type == 'Voladuras canceladas':
            subject = f"EDN {pit}_ {
                date_str} MODIFICACION PROGRAMACION DE VOLADURAS para hoy /"
            attachment = "Ninguno"
            body = f"""
**Subject:** {subject}

**Archivo adjunto:** {attachment}

Buenos Días,
Las voladuras programadas para el día de hoy {date_str} en el {bloque} fueron **CANCELADAS**

Good Morning,
The shot schedule for today {date_str} in the {bloque}, was **CANCELLED**

Regards,

[firma]
"""
        else:  # No hay voladuras
            subject = f"EDN {pit}_ {
                date_str}  NO hay Voladuras programadas para hoy/ NO Shots Scheduled Today"
            attachment = "Ninguno"
            body = f"""
**Subject:** {subject}

**Archivo adjunto:** {attachment}

Buenos Días,

No hay voladuras programadas para el día de hoy {date_str}, en el {pit}

Saludos,

Good Morning,

No shots schedule for today {date_str} at {pit}

Regards,

[firma]
"""

        # Mostrar el correo
        st.markdown(body)
