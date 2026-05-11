import streamlit as st
import requests
import tweepy
import os
import random
from datetime import datetime

# ===================== CONFIGURACIÓN DE PÁGINA =====================
st.set_page_config(
    page_title="KDP Social Promoter PRO",
    page_icon="📚",
    layout="wide"
)

# Estilos CSS personalizados
st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f0f2f6;
        border-radius: 5px 5px 0px 0px;
        gap: 1px;
    }
    .stTabs [aria-selected="true"] { background-color: #FF9900 !important; color: white !important; }
    .main-header { font-size: 2.2rem; color: #FF9900; font-weight: bold; margin-bottom: 1rem; }
    .script-box { background-color: #fff4e6; padding: 20px; border-radius: 10px; border-left: 5px solid #ff9900; color: #333; }
    </style>
""", unsafe_allow_html=True)

# ===================== FUNCIONES DE REDES SOCIALES =====================

def post_to_linkedin(token, message):
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    try:
        user_info = requests.get('https://api.linkedin.com/v2/userinfo', headers=headers)
        if user_info.status_code != 200:
            return False, f"Error perfil: {user_info.text}"
        author_urn = f"urn:li:person:{user_info.json().get('sub')}"
        post_data = {
            "author": author_urn, "lifecycleState": "PUBLISHED",
            "specificContent": {"com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": message}, "shareMediaCategory": "NONE"
            }},
            "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
        }
        r = requests.post('https://api.linkedin.com/v2/ugcPosts', headers=headers, json=post_data)
        return r.ok, r.text
    except Exception as e:
        return False, str(e)

def post_to_tiktok(token, video_url, title):
    url = "https://open.tiktokapis.com/v2/post/publish/video/init/"
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json; charset=utf-8'}
    body = {
        "source_info": {"source": "PULL_FROM_URL", "video_url": video_url},
        "post_info": {"title": title, "privacy_level": "PUBLIC_TO_EVERYONE", "video_label": "COMMERCIAL_CONTENT"}
    }
    try:
        r = requests.post(url, headers=headers, json=body)
        return r.ok, r.text
    except Exception as e:
        return False, str(e)

def generar_ideas_video(titulo, genero):
    estilos = {
        "Romance": {"mood": "💖 Cálido", "musica": "Piano o Pop Acústico", "hook": "¿Y si el amor de tu vida fuera tu peor enemigo?"},
        "Misterio": {"mood": "🌑 Tenso", "musica": "Suspenso / Cinematic", "hook": "Hay secretos que nunca deberían salir a la luz..."},
        "Autoayuda": {"mood": "🌱 Inspirador", "musica": "Lo-fi relajante", "hook": "Este hábito cambió mi vida para siempre."},
        "Fantasía": {"mood": "🧙 Mágico", "musica": "Orquestal / Épico", "hook": "Bienvenidos a un mundo donde la magia es real."}
    }
    e = estilos.get(genero, {"mood": "🔥 Dinámico", "musica": "Trending Audio", "hook": "Tienes que leer esto ahora mismo."})
    return f"""
    🎵 **Audio sugerido:** {e['musica']}  
    ✨ **Mood:** {e['mood']}
    
    **Escena 1 (0-3s):** Muestra el libro (o Kindle) con texto: "{e['hook']}"
    **Escena 2 (3-10s):** Pasa las páginas rápido mostrando frases impactantes.
    **Escena 3 (10-15s):** Tu reacción final al libro con texto: "No puedo creer el final de '{titulo}' 🤯"
    """

# ===================== SIDEBAR - CREDENCIALES =====================
with st.sidebar:
    st.header("🔑 Configuración de APIs")
    st.caption("Consigue tus llaves en los portales de desarrolladores de cada red.")
    with st.expander("X / Twitter"):
        x_ck = st.text_input("Consumer Key", type="password")
        x_cs = st.text_input("Consumer Secret", type="password")
        x_at = st.text_input("Access Token", type="password")
        x_as = st.text_input("Access Secret", type="password")
    
    fb_token = st.text_input("Meta (FB/IG) Token", type="password")
    li_token = st.text_input("LinkedIn Token", type="password")
    tt_token = st.text_input("TikTok Token", type="password")

# ===================== FORMULARIO PRINCIPAL =====================
st.markdown('<p class="main-header">📚 KDP Social Promoter PRO</p>', unsafe_allow_html=True)

with st.form("book_form"):
    col1, col2 = st.columns(2)
    with col1:
        titulo = st.text_input("Título del libro *", placeholder="Ej: El Susurro del Bosque")
        autor = st.text_input("Autor", value="Tu Nombre")
        asin = st.text_input("ASIN de Amazon", placeholder="B012345678")
    with col2:
        precio = st.text_input("Precio", value="2.99 USD")
        genero = st.selectbox("Género", ["Romance", "Misterio", "Autoayuda", "Fantasía", "Ciencia Ficción", "Terror"])
        portada_url = st.text_input("URL de Portada (Direct Link)")
    
    descripcion = st.text_area("Descripción / Blurb *", height=100)
    submitted = st.form_submit_button("🚀 Generar Estrategia Completa", type="primary")

# ===================== PROCESAMIENTO Y TABS =====================
if submitted:
    if not titulo or not descripcion:
        st.error("❌ Los campos con * son obligatorios")
    else:
        enlace = f"https://www.amazon.com/dp/{asin}" if asin else "https://amazon.com"
        
        st.session_state.posts = {
            "x": f"📖 ¡Nueva lectura! '{titulo}' de {autor}.\\n\\n{descripcion[:150]}...\\n\\nConsíguelo aquí: {enlace}\\n\\n#KDP #{genero}",
            "fb": f"🌟 ¡NUEVO LANZAMIENTO! 🌟\\n\\nPresento mi libro: '{titulo}'.\\n\\n{descripcion}\\n\\n🛒 Disponible en Amazon por {precio}\\n👉 {enlace}",
            "li": f"Orgulloso de anunciar mi nueva publicación: '{titulo}'. Un trabajo enfocado en {genero.lower()}.\\n\\n#Escritores #KDP #Publishing\\n{enlace}",
            "tt_caption": f"¡Ya disponible! 📖 {titulo} #BookTok #KDP #LibrosRecomendados",
            "script": generar_ideas_video(titulo, genero)
        }

if "posts" in st.session_state:
    p = st.session_state.posts
    tabs = st.tabs(["🐦 X (Twitter)", "📘 Facebook", "🔗 LinkedIn", "🎵 TikTok / Reels"])

    with tabs[0]:
        new_x = st.text_area("Editar post X", p['x'], height=150)
        if st.button("Publicar en X"):
            try:
                client = tweepy.Client(consumer_key=x_ck, consumer_secret=x_cs, access_token=x_at, access_token_secret=x_as)
                client.create_tweet(text=new_x)
                st.success("✅ ¡Publicado en X!")
            except Exception as e: st.error(f"Error: {e}")

    with tabs[1]:
        new_fb = st.text_area("Editar post Facebook", p['fb'], height=150)
        if st.button("Publicar en Facebook"):
            try:
                r = requests.post("https://graph.facebook.com/v22.0/me/feed", data={"message": new_fb, "access_token": fb_token})
                if r.ok: st.success("✅ ¡Publicado en Facebook!")
                else: st.error(f"Error FB: {r.text}")
            except Exception as e: st.error(str(e))

    with tabs[2]:
        new_li = st.text_area("Editar post LinkedIn", p['li'], height=150)
        if st.button("Publicar en LinkedIn"):
            ok, msg = post_to_linkedin(li_token, new_li)
            if ok: st.success("✅ ¡Publicado en LinkedIn!")
            else: st.error(msg)

    with tabs[3]:
        st.markdown("### 💡 Guion sugerido para tu Video")
        st.markdown(f'<div class="script-box">{p["script"]}</div>', unsafe_allow_html=True)
        st.divider()
        st.subheader("🚀 Publicar mediante API")
        v_url = st.text_input("URL del video MP4 (Enlace directo)")
        tt_cap = st.text_area("Caption para TikTok", p['tt_caption'])
        if st.button("Enviar a TikTok"):
            ok, msg = post_to_tiktok(tt_token, v_url, tt_cap)
            if ok: st.success("✅ Enviado a revisión en TikTok")
            else: st.error(msg)

    st.divider()
    all_text = f"TÍTULO: {titulo}\\n\\nPOST X:\\n{p['x']}\\n\\nPOST FB:\\n{p['fb']}\\n\\nGUION VIDEO:\\n{p['script']}"
    st.download_button("📥 Descargar Plan en TXT", all_text, file_name=f"plan_{titulo}.txt")
