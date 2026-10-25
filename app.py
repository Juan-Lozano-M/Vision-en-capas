"""Interfaz Streamlit del prototipo de analisis de imagenes."""

from pathlib import Path

import cv2
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

from src.image_processor import detect_objects, summarize_detections


st.set_page_config(
    page_title="Vision en capas",
    page_icon="◉",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');
:root { --ink:#f4f1fb; --muted:#9895a4; --panel:#1d1e23; --panel-2:#25262d; --line:#30313a; --purple:#8b5cf6; --cyan:#06b6d4; --coral:#f43f5e; --lavender:#c4b5fd; --cream:#f7f4fb; }
.stApp { background-color:#121316; background-image:radial-gradient(circle, rgba(196,181,253,.22) 1px, transparent 1px), radial-gradient(circle at 15% 0%, rgba(139,92,246,.18), transparent 30%), radial-gradient(circle at 90% 85%, rgba(6,182,212,.10), transparent 28%); background-size:22px 22px, 100% 100%, 100% 100%; color:var(--ink); }
html, body, [class*="css"] { font-family:'Space Grotesk', sans-serif; }
[data-testid="stHeader"] { background:transparent; }
[data-testid="stToolbar"] { visibility:hidden; }
h1, h2, h3 { letter-spacing:-.04em; }
.hero { padding:2.2rem 1rem 1.45rem; background:rgba(29,30,35,.88); border:1px solid var(--line); border-radius:20px; margin-bottom:1.15rem; box-shadow:0 18px 50px rgba(0,0,0,.18); }
.eyebrow { font:500 .72rem 'JetBrains Mono', monospace; color:var(--lavender); letter-spacing:.12em; text-transform:uppercase; }
.hero h1 { color:var(--cream); font-size:clamp(2.5rem,5vw,4.8rem); line-height:.94; max-width:760px; margin:.55rem 0 .95rem; }
.hero p { color:var(--muted); max-width:700px; font-size:1.02rem; line-height:1.55; margin:0; }
.hero-mark { float:right; color:var(--purple); font-size:5rem; line-height:.7; opacity:.95; text-shadow:0 0 35px rgba(139,92,246,.45); }
.credits { margin:.85rem 0 1.2rem; padding:.72rem 1rem; background:rgba(29,30,35,.72); border-left:3px solid var(--cyan); border-radius:0 12px 12px 0; color:var(--muted); font-size:.78rem; line-height:1.55; }
.credits strong { color:var(--lavender); font-family:'JetBrains Mono', monospace; font-size:.7rem; letter-spacing:.08em; text-transform:uppercase; }
.process-step { background:rgba(29,30,35,.9); border:1px solid var(--line); border-radius:16px; padding:13px 14px 14px; min-height:104px; margin-bottom:.4rem; transition:transform .18s ease, border-color .18s ease, box-shadow .18s ease; }
.process-step:hover { transform:translateY(-2px); border-color:var(--purple); box-shadow:0 12px 24px rgba(0,0,0,.18); }
.process-num { color:var(--purple); font:500 .75rem 'JetBrains Mono', monospace; }
.process-step b { display:block; color:var(--cream); font-size:.88rem; margin:.38rem 0 .28rem; }
.process-step small { color:var(--muted); font-size:.72rem; line-height:1.38; }
.section-kicker { color:var(--cyan); font:500 .7rem 'JetBrains Mono', monospace; letter-spacing:.12em; text-transform:uppercase; margin-top:.75rem; margin-bottom:.55rem; }
.section-title { color:var(--cream); font-size:1.62rem; font-weight:800; letter-spacing:-.045em; margin-bottom:.25rem; }
.section-copy { color:var(--muted); line-height:1.55; }
.metric-card { background:linear-gradient(135deg,#25262d,#1b1c21); border:1px solid var(--line); border-radius:16px; padding:15px 16px; min-height:82px; margin-bottom:.7rem; }
.metric-card strong { display:block; color:var(--lavender); font-size:1.9rem; line-height:1; }
.metric-card span { display:block; color:var(--muted); font-size:.74rem; margin-top:.42rem; }
.source-pill { display:inline-block; background:#252136; border:1px solid #6346b6; border-radius:999px; color:var(--lavender); padding:6px 12px; margin:1.15rem 0 .7rem; font:500 .7rem 'JetBrains Mono', monospace; }
.interpretation { border-left:3px solid var(--coral); background:rgba(29,30,35,.94); padding:1rem 1.2rem; border-radius:0 16px 16px 0; color:#dedbe6; line-height:1.55; }
.stage-caption { color:var(--muted); font-size:.78rem; margin-top:-.3rem; }
.result-gap { height:.65rem; }
[data-testid="stSidebar"] { background:#17181c; border-right:1px solid var(--line); }
[data-testid="stSidebar"] h3 { color:var(--cream); }
[data-testid="stFileUploader"] { margin-top:.35rem; }
[data-testid="stFileUploader"] section { background:#1d1e23; border:1px dashed #6b5aa8; border-top:0 !important; border-radius:0 0 16px 16px; padding:6px 14px 14px; min-height:54px; margin-top:-1px; }
[data-testid="stFileUploaderDropzone"] { background:transparent; border:0; min-height:80px; }
[data-testid="stFileUploaderDropzoneInstructions"] { display:none; }
[data-testid="stFileUploaderDropzoneInstructions"] small { color:var(--muted); }
[data-testid="stFileUploaderDropzone"] button { background:#25262d; border:1px solid #575a68; border-radius:10px; color:#fff; font-weight:700; padding:.58rem .9rem; }
[data-testid="stFileUploaderDropzone"] button p { font-size:0; }
[data-testid="stFileUploaderDropzone"] button p::after { content:'Seleccionar imagen'; font-size:.78rem; }
[data-testid="stFileUploaderDropzone"] button:hover { border-color:var(--lavender); background:#302b45; }
.upload-hero { text-align:center; background:#1d1e23; border:1px solid #30313a; border-bottom:0; border-radius:16px 16px 0 0; padding:16px 12px 8px; margin-top:.65rem; margin-bottom:0; }
.upload-icon { width:42px; height:42px; margin:0 auto 9px; display:grid; place-items:center; border-radius:12px; background:#252136; border:1px solid #6346b6; color:var(--lavender); font-size:1.35rem; }
.upload-title { color:var(--cream); font-weight:700; font-size:.95rem; }
.upload-subtitle { color:var(--muted); font-size:.76rem; margin-top:.2rem; }
.upload-meta { color:#aaa5b7; font:400 .68rem 'JetBrains Mono', monospace; text-align:center; margin:.45rem 0 .2rem; }
div.stButton > button, div.stDownloadButton > button { border-radius:10px; border:1px solid #6d4dd0; background:#8b5cf6; color:#fff; font-weight:700; }
div.stDownloadButton > button:hover, div.stButton > button:hover { border-color:var(--lavender); background:#a78bfa; color:#15121e; }
[data-testid="stDataFrame"] { border:1px solid var(--line); border-radius:12px; overflow:hidden; }
footer { visibility:hidden; }
@media (max-width: 800px) { .hero-mark { display:none; } .process-step { min-height:88px; } }
</style>
""",
    unsafe_allow_html=True,
)


def bgr_to_rgb(image: np.ndarray) -> np.ndarray:
    """Convierte una imagen OpenCV de BGR a RGB."""
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)


def make_download_png(image: np.ndarray) -> bytes:
    """Codifica una imagen BGR como PNG descargable."""
    ok, encoded = cv2.imencode(".png", image)
    return encoded.tobytes() if ok else b""


def build_demo_image() -> np.ndarray:
    """Crea una imagen de demostracion si no existe el archivo de ejemplo."""
    canvas = np.full((520, 900, 3), (235, 240, 236), dtype=np.uint8)
    cv2.circle(canvas, (150, 210), 90, (70, 70, 220), -1)
    cv2.rectangle(canvas, (300, 120), (475, 295), (50, 180, 70), -1)
    triangle = np.array([[650, 105], [545, 310], [755, 310]], np.int32)
    cv2.fillPoly(canvas, [triangle], (230, 130, 40))
    cv2.rectangle(canvas, (155, 370), (340, 465), (40, 140, 240), -1)
    cv2.circle(canvas, (540, 415), 58, (180, 80, 180), -1)
    return canvas


st.markdown(
    '<div class="hero"><span class="hero-mark">◉</span><div class="eyebrow">CIPAS / laboratorio de vision por computadora</div><h1>Vision en capas</h1><p>Lee una imagen como un sistema de evidencias: colores, contornos, formas y cantidades en una sola vista.</p></div>',
    unsafe_allow_html=True,
)
st.markdown('<div class="credits"><strong>Hecho por</strong><br>Juan Martin Lozano<br>Daniel Felipe Escamilla<br>Andres Felipe Arias</div>', unsafe_allow_html=True)

steps = [
    ("01", "Imagen original", "Carga y observa la fotografia"),
    ("02", "Preprocesamiento", "Limpia y prepara los datos"),
    ("03", "Extraccion", "Encuentra regiones y contornos"),
    ("04", "Resultado", "Etiqueta y cuenta objetos"),
    ("05", "Interpretacion", "Explica hallazgos y limites"),
]
process_cols = st.columns(5)
for col, (number, title, description) in zip(process_cols, steps):
    with col:
        st.markdown(
            f'<div class="process-step"><span class="process-num">{number}</span><b>{title}</b><small>{description}</small></div>',
            unsafe_allow_html=True,
        )

with st.sidebar:
    st.markdown("### Panel de analisis")
    st.caption("Configura la imagen y el umbral antes de leer el resultado.")
    st.markdown('<div class="upload-hero"><div class="upload-icon">▧</div><div class="upload-title">Arrastra y suelta tu imagen aqui</div><div class="upload-subtitle">o selecciona una imagen para analizarla</div></div>', unsafe_allow_html=True)
    uploaded = st.file_uploader("Carga una imagen", type=["png", "jpg", "jpeg", "webp"], label_visibility="collapsed")
    st.markdown('<div class="upload-meta">PNG / JPG / JPEG / WEBP &nbsp;•&nbsp; hasta 200 MB por archivo</div>', unsafe_allow_html=True)
    min_area = st.slider("Area minima de objeto", 100, 5000, 500, 100)
    show_details = st.checkbox("Mostrar detalles tecnicos", value=False)
    st.markdown("---")
    st.markdown("**Colores reconocidos**")
    st.caption("Rojo / naranja / amarillo / verde / azul / morado")
    st.markdown("---")
    st.caption("Consejo: usa objetos separados sobre un fondo contrastante.")

if uploaded is None:
    example_path = Path("assets/example_shapes.png")
    if example_path.exists():
        source_label = "EJEMPLO INCLUIDO"
        image_bytes = example_path.read_bytes()
        original = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
    else:
        source_label = "DEMO GENERADA"
        original = build_demo_image()
else:
    source_label = uploaded.name.upper()
    original = cv2.imdecode(np.frombuffer(uploaded.getvalue(), np.uint8), cv2.IMREAD_COLOR)

if original is None:
    st.error("No fue posible leer la imagen. Usa un archivo PNG o JPG valido.")
    st.stop()

processed, detections, stages = detect_objects(original, min_area=min_area)
summary = summarize_detections(detections)

st.markdown(f'<div class="source-pill">FUENTE / {source_label}</div>', unsafe_allow_html=True)

st.markdown('<div class="section-kicker">01 / evidencia de entrada</div><div class="section-title">Imagen original</div>', unsafe_allow_html=True)
left, right = st.columns([1.52, 1], gap="large")
with left:
    st.image(bgr_to_rgb(stages["resized"]), use_container_width=True)
with right:
    st.markdown("### Lectura inicial")
    st.markdown('<p class="section-copy">La fotografia se convierte en una matriz de pixeles. Esta vista conserva la referencia visual antes de separar colores y contornos.</p>', unsafe_allow_html=True)
    m1, m2 = st.columns(2)
    with m1:
        st.markdown(f'<div class="metric-card"><strong>{stages["resized"].shape[1]}</strong><span>ancho analizado</span></div>', unsafe_allow_html=True)
    with m2:
        st.markdown(f'<div class="metric-card"><strong>{stages["resized"].shape[0]}</strong><span>alto analizado</span></div>', unsafe_allow_html=True)

st.markdown('<div class="section-kicker">02 + 03 / transformacion y lectura</div><div class="section-title">Preprocesamiento y extraccion</div>', unsafe_allow_html=True)
prep_cols = st.columns(3, gap="medium")
with prep_cols[0]:
    st.image(bgr_to_rgb(stages["blurred"]), caption="Suavizado / reduce ruido", use_container_width=True)
with prep_cols[1]:
    st.image(stages["edges"], caption="Bordes / encuentra cambios", use_container_width=True)
with prep_cols[2]:
    st.image(bgr_to_rgb(stages["masks_preview"]), caption="Mascara / separa color", use_container_width=True)
st.markdown('<p class="stage-caption">HSV separa el tono del brillo; luego la mascara se limpia y los contornos se filtran por area minima.</p>', unsafe_allow_html=True)

st.markdown('<div class="section-kicker">04 / evidencia de salida</div><div class="section-title">Resultado</div>', unsafe_allow_html=True)
metric_cols = st.columns(4, gap="medium")
metric_values = [("Objetos", summary["total"]), ("Colores", len(summary["by_color"])), ("Formas", len(summary["by_shape"])), ("Area minima", f"{min_area}px")]
for col, (label, value) in zip(metric_cols, metric_values):
    with col:
        st.markdown(f'<div class="metric-card"><strong>{value}</strong><span>{label}</span></div>', unsafe_allow_html=True)

st.markdown('<div class="result-gap"></div>', unsafe_allow_html=True)
st.image(bgr_to_rgb(processed), caption="Imagen anotada por el algoritmo", use_container_width=True)
st.download_button("Descargar imagen procesada", data=make_download_png(processed), file_name="resultado_vision_en_capas.png", mime="image/png")

table_col, chart_col = st.columns([1, 1], gap="large")
with table_col:
    st.markdown("### Objetos identificados")
    if detections:
        st.dataframe([d.to_dict() for d in detections], use_container_width=True, hide_index=True)
    else:
        st.warning("No se encontraron objetos con el area minima seleccionada.")
with chart_col:
    st.markdown("### Conteo por categoria")
    counts = {**{f"color / {k}": v for k, v in summary["by_color"].items()}, **{f"forma / {k}": v for k, v in summary["by_shape"].items()}}
    if counts:
        fig, ax = plt.subplots(figsize=(6, 3.2))
        fig.patch.set_alpha(0)
        ax.set_facecolor("#1d1e23")
        ax.barh(list(counts.keys()), list(counts.values()), color="#8b5cf6")
        ax.tick_params(colors="#dedbe6", labelsize=8)
        for spine in ax.spines.values():
            spine.set_visible(False)
        ax.grid(axis="x", alpha=.15, color="#c4b5fd")
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)

st.markdown('<div class="section-kicker">05 / lectura humana</div><div class="section-title">Interpretacion</div>', unsafe_allow_html=True)
if detections:
    colors_text = ", ".join(f"{count} {color}" for color, count in summary["by_color"].items())
    shapes_text = ", ".join(f"{count} {shape}" for shape, count in summary["by_shape"].items())
    interpretation = f"El algoritmo encontro {summary['total']} objeto(s): {colors_text}. Las formas estimadas fueron: {shapes_text}. Para llegar a este resultado, separo colores en HSV, limpio las mascaras con operaciones morfologicas y clasifico cada contorno segun sus vertices y circularidad."
else:
    interpretation = "No se detectaron regiones que superaran el area minima. Prueba reducir el control de area o usar una imagen con objetos de colores definidos y buen contraste."
st.markdown(f'<div class="interpretation">{interpretation}<br><br><b>Limitaciones:</b> funciona mejor con iluminacion uniforme, objetos separados y colores solidos. Sombras, reflejos, objetos superpuestos o fondos parecidos pueden producir falsos positivos.</div>', unsafe_allow_html=True)

if show_details:
    with st.expander("Detalles tecnicos"):
        st.json({"imagen_original": list(original.shape), "imagen_analizada": list(stages["resized"].shape), "min_area": min_area, "detecciones": len(detections)})

