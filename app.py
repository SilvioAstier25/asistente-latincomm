import streamlit as st
import openai
import os
import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configurar la clave de API de OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

import streamlit as st
import os

# Definir las rutas de los logotipos
logo_color = "Logo_LatinComm_color.png"
logo_blanco = "Logo_LatinComm_blanco.png"

# Inyectar CSS y JavaScript para detectar el modo oscuro
st.markdown(
    f"""
    <style>
        /* Establecer ID para la imagen del logo */
        .logo-container {{
            text-align: center;
        }}

        #logo-img {{
            width: 200px;
        }}

        /* Modo oscuro */
        @media (prefers-color-scheme: dark) {{
            #logo-img {{
                content: url('{logo_blanco}');
            }}
        }}

        /* Modo claro */
        @media (prefers-color-scheme: light) {{
            #logo-img {{
                content: url('{logo_color}');
            }}
        }}
    </style>
    <div class="logo-container">
        <img id="logo-img" src="{logo_color}" alt="Logo_LatinComm">
    </div>
    """,
    unsafe_allow_html=True
)

# 📌 Definir los servicios antes de que el asistente IA los use
servicios = {
    "eComm": {
        "Contenidos para webs médicas": "https://latincomm.com/medicos.html",
        "Contenidos para webs pacientes": "https://latincomm.com/web-pacientes.html",
        "Programación web": "https://latincomm.com/programacion-web.html",
        "Programación CLM": "https://latincomm.com/clm.html",
        "Programación Apps": "https://latincomm.com/programacion-apps.html",
        "Gamming": "https://latincomm.com/gamming.html",
        "eMail Mkt": "https://latincomm.com/mkt.html",
        "Community management": "https://latincomm.com/comman.html"
    },
    "Comunicación editorial": {
        "Latest Review": "https://latincomm.com/latest-review.html",
        "LR Play": "https://latincomm.com/lrplay.html",
        "Congress Report": "https://latincomm.com/congress-report.html",
        "Highlights/Reportes": "https://latincomm.com/highlights.html",
        "Principio Activo": "https://latincomm.com/principio-activo.html",
        "Following Outcomes": "https://latincomm.com/following.html",
        "Guías terapéuticas": "https://latincomm.com/guias.html",
        "Slidekits": "https://latincomm.com/slidekits.html",
        "Monografías": "https://latincomm.com/monografias.html",
        "Compendios": "https://latincomm.com/compendios.html"
    },
    "Comunicación publicitaria": {
        "Estrategia multicanal": "https://latincomm.com/multicanal.html",
        "Detailing": "https://latincomm.com/detailing.html",
        "Producción audiovisual": "https://latincomm.com/audiovisual.html",
        "Campañas publicitarias": "https://latincomm.com/publicitaria.html",
        "Comunicación para pacientes": "https://latincomm.com/pacientes.html",
        "Comunicación institucional": "https://latincomm.com/institucional.html",
        "Brand design": "https://latincomm.com/brand.html",
        "Stands y POP": "https://latincomm.com/standspop.html"
    }
}

# 📌 Preguntas Frecuentes (1° Bloque)
st.markdown("## Preguntas Frecuentes")
preguntas = {
    "¿Qué es Latincomm?": "Latincomm es una agencia especializada en comunicación editorial y publicitaria para la industria de la salud.",
    "¿Qué servicios ofrece Latincomm?": "Ofrecemos comunicación editorial, producción publicitaria y soluciones digitales para la industria de la salud.",
    "¿Cómo contactar con Latincomm?": "Puedes escribirnos a lrivet@latincomm.com o completar el formulario de contacto al final de esta página.",
    "¿Latincomm trabaja con clientes internacionales?": "Sí, brindamos servicios a clientes en distintos países, adaptando nuestros contenidos a cada mercado."
}

pregunta_seleccionada = st.selectbox("Selecciona una pregunta:", ["Selecciona una pregunta..."] + list(preguntas.keys()))

if pregunta_seleccionada != "Selecciona una pregunta...":
    st.write(f"**Respuesta:** {preguntas[pregunta_seleccionada]}")

# 📌 Asistente con IA (2° Bloque)
st.markdown("## Asistente con IA")
pregunta_usuario = st.text_input("Escribe tu pregunta aquí")

# Función para extraer el texto de una URL
def extraer_contenido_web(url):
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        texto = " ".join([p.text for p in soup.find_all("p")])
        return texto[:2000]  # Limitar a 2000 caracteres para evitar respuestas muy largas
    except Exception:
        return "No se pudo obtener información actualizada de esta página."

if st.button("Enviar"):
    if pregunta_usuario:
        url_relevante = None
        for categoria, items in servicios.items():
            for servicio, link in items.items():
                if servicio.lower() in pregunta_usuario.lower():
                    url_relevante = link
                    break
        
        contenido_extra = ""
        if url_relevante:
            contenido_extra = extraer_contenido_web(url_relevante)

        try:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": f"""Eres el asistente virtual de Latincomm, una agencia de comunicación editorial y publicitaria para la industria farmacéutica. 
Tu tarea es responder exclusivamente sobre los servicios, soluciones y capacidades de Latincomm. 
Tus respuestas deben basarse en la información disponible en el sitio web de Latincomm y nunca inventar información.
Si te hacen preguntas sobre empleados, datos internos, precios específicos o información confidencial, responde con:
'Lo siento, pero no puedo proporcionar esa información. Para consultas comerciales, puedes escribir a lrivet@latincomm.com'
 
                    LatinComm ofrece los siguientes servicios:
                    - Comunicación editorial (Congress Reports, monografías, guías terapéuticas, etc.).
                    - Producción publicitaria (campañas, videos, estrategias multicanal).
                    - Desarrollo de soluciones digitales (e-detailing, CLM, apps, web médica).

                    Si el usuario pregunta por un servicio específico, usa la siguiente información extraída en tiempo real: {contenido_extra}
                    """},
                    {"role": "user", "content": pregunta_usuario}
                ]
            )

            st.write("**Respuesta:**", response.choices[0].message.content)
        except Exception:
            st.error("Error al obtener respuesta. Intenta nuevamente.")
    else:
        st.warning("Por favor, ingresa una pregunta.")

# 📌 Explorar servicios (3° Bloque)
st.markdown("## Explorar Servicios")
for categoria, items in servicios.items():
    with st.expander(categoria):
        for servicio, link in items.items():
            st.markdown(f"- [{servicio}]({link})")

# 📩 Formulario de Contacto (4° Bloque)
st.markdown("## Formulario de Contacto")
st.write("Si tienes consultas, puedes escribirnos directamente.")

nombre = st.text_input("Nombre")
email = st.text_input("Correo electrónico")
mensaje = st.text_area("Mensaje")

def enviar_correo(nombre, email, mensaje):
    try:
        # Configurar datos del email desde los secretos de Streamlit
        smtp_host = os.getenv("EMAIL_HOST")
        smtp_port = int(os.getenv("EMAIL_PORT"))
        smtp_user = os.getenv("EMAIL_USER")
        smtp_password = os.getenv("EMAIL_PASSWORD")
        email_receiver = [email.strip() for email in os.getenv("EMAIL_RECEIVER").split(",")]

        # Crear el mensaje
        msg = MIMEMultipart()
        msg["From"] = smtp_user
        msg["To"] = ", ".join(email_receiver)
        msg["Subject"] = "Nuevo mensaje desde el asistente de Latincomm"
        
        body = f"Nombre: {nombre}\nCorreo: {email}\n\nMensaje:\n{mensaje}"
        msg.attach(MIMEText(body, "plain"))

        # Conectar con el servidor SMTP
        server = smtplib.SMTP(smtp_host, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.sendmail(smtp_user, email_receiver, msg.as_string())
        server.quit()

        return True
    except Exception as e:
        print("Error al enviar correo:", e)
        return False

if st.button("Enviar mensaje"):
    if nombre and email and mensaje:
        if enviar_correo(nombre, email, mensaje):
            st.success("✅ Tu mensaje ha sido enviado correctamente.")
        else:
            st.error("❌ Error al enviar el mensaje. Inténtalo de nuevo.")
    else:
        st.warning("⚠️ Por favor, completa todos los campos.")
