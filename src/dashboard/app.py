import streamlit as st
import pandas as pd
import plotly.express as px
import sys
from pathlib import Path

# ─── Paths ────────────────────────────────────────────────────────────────────
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

from src.pipeline import queries
from src.pipeline.loaders.clickhouse import get_clickhouse_client

# ─── Brand tokens ─────────────────────────────────────────────────────────────
PRIMARY       = "#4328B1"   # violeta
PRIMARY_LIGHT = "#6c51d4"
PRIMARY_BG    = "#ede9fb"
ACCENT        = "#f59e0b"   # ámbar
SUCCESS       = "#166534"
SUCCESS_BG    = "#dcfce7"
DANGER        = "#991b1b"
DANGER_BG     = "#fee2e2"
BG            = "#ffffff"
SURFACE       = "#f4f4f6"
TEXT          = "#1a1a2e"
TEXT_MUTED    = "#373752"   # Más oscuro para máxima legibilidad y contraste
BORDER        = "#d8d8e8"
SHADOW_SM     = "0 1px 4px rgba(67,40,177,0.08)"
SHADOW_MD     = "0 2px 12px rgba(67,40,177,0.13)"

# Paleta de colores para gráficos basada estrictamente en la identidad de marca
CHART_COLS = [PRIMARY, ACCENT, PRIMARY_LIGHT, "#2563eb", "#059669"]

MONTHS_ES = {
    1: "Ene", 2: "Feb", 3: "Mar", 4: "Abr", 5: "May", 6: "Jun",
    7: "Jul", 8: "Ago", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dic"
}

# ─── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Jobby Analytics",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── Global CSS (Tighter paddings, balanced typography weights) ───────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Outfit:wght@300;700;800&display=swap');

*, html, body, [class*="css"] {{
    font-family: 'Inter', system-ui, sans-serif !important;
    box-sizing: border-box;
}}

/* ── Ocultar barra de streamlit ── */
header[data-testid="stHeader"],
[data-testid="stSidebar"],
footer, #MainMenu {{
    display: none !important;
    height: 0px !important;
    min-height: 0px !important;
}}

/* ── Fondo de la app ── */
.stApp {{
    background: {SURFACE};
}}

/* ── Eliminación agresiva de espacios vacíos en el tope (eje Y) ── */
.stApp,
.stApp > div,
.stApp [data-testid="stAppViewContainer"],
.stApp [data-testid="stMain"],
.stApp [data-testid="stMainTemplateContainer"],
.stApp [data-testid="stAppViewBlockContainer"],
.stApp .main,
.stApp .block-container,
.stApp [data-testid="stVerticalBlock"],
.stApp [data-testid="stVerticalBlock"] > div:first-child,
.stApp [data-testid="stMarkdownContainer"],
div[class*="block-container"],
div[class*="stAppViewBlockContainer"],
section[class*="main"] {{
    padding-top: 0px !important;
    margin-top: 0px !important;
    top: 0 !important;
}}

/* ── Block container: Padding optimizado y más denso ── */
.block-container {{
    padding-bottom: 15px !important;
    padding-left: 24px !important; /* Margen en los costados (eje X) */
    padding-right: 24px !important;
    max-width: 100% !important;
}}

/* ── Espaciado vertical compacto ── */
.element-container {{ margin-bottom: 0 !important; }}
div[data-testid="stVerticalBlock"] > div {{ gap: 0 !important; }}

/* ── Topbar: Cabecera plana y minimalista sin naranja ni gradientes ── */
.topbar {{
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    width: 100%;
    z-index: 999999;
    background: {PRIMARY};
    margin: 0 !important;
    padding: 10px 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 2px 10px rgba(67, 40, 177, 0.12);
    border-radius: 0px; /* Flat snap-fit docking */
}}
.topbar-brand {{
    font-family: 'Outfit', sans-serif;
    letter-spacing: 0.02em;
    display: flex;
    align-items: center;
    gap: 6px;
}}
.topbar-meta {{
    font-size: 0.72rem;
    color: rgba(255,255,255,0.92);
    font-weight: 700;
    letter-spacing: 0.04em;
}}
.topbar-pill {{
    display: inline-flex;
    align-items: center;
    gap: 7px;
    background: rgba(255,255,255,0.15);
    border: 1px solid rgba(255,255,255,0.3);
    color: #ffffff;
    font-size: 0.7rem;
    font-weight: 800;
    padding: 4px 10px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}}
.topbar-dot {{
    width: 6px; height: 6px;
    border-radius: 50%;
    background: #ffffff;
    animation: blink 1.8s infinite;
}}
@keyframes blink {{ 0%,100%{{opacity:1}} 50%{{opacity:0.15}} }}

/* ── Etiquetas de sección (Títulos en negrita destacada) ── */
.sec-label {{
    font-size: 0.76rem;
    font-weight: 800;
    color: {PRIMARY};
    text-transform: uppercase;
    letter-spacing: 0.12em;
    padding-bottom: 5px;
    border-bottom: 2px solid {PRIMARY};
    margin: 10px 0 6px 0;
    display: block;
}}

/* ── Forzar tema claro en los filtros (Selectbox) para evitar choques con el OS ── */
div[data-testid="stSelectbox"] label p {{
    color: #1a1a2e !important;
    font-weight: 700 !important;
    font-family: 'Inter', sans-serif !important;
}}
div[data-baseweb="select"] > div {{
    background-color: #ffffff !important;
    color: #1a1a2e !important;
    border: 1px solid #d8d8e8 !important;
    border-radius: 4px !important;
}}
div[data-baseweb="popover"] ul {{
    background-color: #ffffff !important;
}}
div[data-baseweb="popover"] li {{
    color: #1a1a2e !important;
}}
div[data-baseweb="select"] span {{
    color: #1a1a2e !important;
}}

/* ── Tarjetas KPI (Título en negrita y valores limpios en peso regular/médium) ── */
.kpi-card {{
    background: {BG};
    border-top: 3px solid {PRIMARY};
    padding: 8px 12px;
    box-shadow: {SHADOW_SM};
    min-height: 94px !important;
    height: 100% !important; /* Estiramiento al 100% de la columna */
    display: flex !important;
    flex-direction: column !important;
    justify-content: space-between !important;
    transition: box-shadow 0.18s ease;
    flex: 1 1 100% !important;
}}
.kpi-card:hover {{ box-shadow: {SHADOW_MD}; }}
.kpi-card.ac {{ border-top-color: {ACCENT}; }}

/* ── Estiramiento flex y altura idéntica para columnas de KPI ── */
div[data-testid="column"]:has(.kpi-card) > div,
div[data-testid="column"]:has(.kpi-card) div[data-testid="stVerticalBlock"],
div[data-testid="column"]:has(.kpi-card) div[data-testid="stVerticalBlock"] > div {{
    height: 100% !important;
    display: flex !important;
    flex-direction: column !important;
    flex: 1 1 100% !important;
}}

.kpi-lbl {{
    font-size: 0.72rem;
    font-weight: 800; /* Solamente el título de la tarjeta va en negrita */
    color: {TEXT_MUTED};
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 2px;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    display: block !important;
    width: 100% !important;
}}
.kpi-num {{
    font-family: 'Outfit', sans-serif;
    font-size: 1.7rem;
    font-weight: 500; /* Los números van en peso limpio/médium para balance visual */
    color: {TEXT};
    letter-spacing: -0.02em;
    line-height: 1.0;
    margin-bottom: 2px;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    display: block !important;
    width: 100% !important;
}}
.kpi-num.sm {{
    font-size: 1.05rem;
    font-weight: 500;
    font-family: 'Inter', sans-serif;
    line-height: 1.25;
    letter-spacing: -0.01em;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    display: block !important;
    width: 100% !important;
}}
.kpi-tag {{
    display: inline-block;
    font-size: 0.64rem;
    font-weight: 500; /* Chip en peso limpio */
    padding: 2px 6px;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    margin-top: 2px;
}}
.kpi-tag.pos {{ background:{SUCCESS_BG}; color:{SUCCESS}; }}
.kpi-tag.neg {{ background:{DANGER_BG}; color:{DANGER}; }}
.kpi-tag.neu {{ background:{PRIMARY_BG}; color:{PRIMARY}; }}

/* ── Títulos de gráficas ── */
.chart-title {{
    font-family: 'Outfit', sans-serif;
    font-size: 0.84rem;
    font-weight: 800;
    color: {TEXT};
    text-transform: uppercase;
    letter-spacing: 0.08em;
    padding-bottom: 4px;
    border-bottom: 1px solid {BORDER};
    margin-bottom: 6px;
}}
.chart-title.ac {{
    border-left: 3px solid {ACCENT};
    padding-left: 8px;
}}
.chart-title.pr {{
    border-left: 3px solid {PRIMARY};
    padding-left: 8px;
}}

/* ── Tabla de Empleados Destacados (Solamente cabeceras en negrita, datos normales) ── */
.emp-table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 0.8rem;
    background-color: #ffffff !important;
    margin-top: 4px;
}}
.emp-table th {{
    background-color: {PRIMARY} !important;
    color: #ffffff !important;
    font-family: 'Outfit', sans-serif;
    text-transform: uppercase;
    font-weight: 800; /* Headers en negrita destacada */
    letter-spacing: 0.06em;
    padding: 6px 10px;
    text-align: left;
    border: none !important;
}}
.emp-table td {{
    padding: 6px 10px;
    border-bottom: 1px solid #d8d8e8 !important;
    color: #1a1a2e !important;
    background-color: #ffffff !important;
    font-weight: 400; /* Datos normales de la tabla, libre de negrita */
}}
.emp-table tr:hover td {{
    background-color: #f6f5fc !important;
}}

/* ── Contenedor de tabla responsive ── */
.table-container {{
    width: 100%;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
    border-radius: 4px;
    border: 1px solid rgba(67, 40, 177, 0.08);
    margin-top: 4px;
}}

/* ── CONSULTAS DE MEDIOS RESPONSIVAS (Soporte Multi-dispositivo) ── */
@media (max-width: 1024px) {{
    /* En tabletas, envolver KPIs en 3 columnas */
    div[data-testid="stHorizontalBlock"]:has(.kpi-card) {{
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: wrap !important;
        align-items: stretch !important; /* Fuerza a que todas las columnas en la misma fila tengan la misma altura */
    }}
    .stApp div[data-testid="column"]:has(.kpi-card) {{
        width: calc(33.33% - 8px) !important;
        min-width: calc(33.33% - 8px) !important;
        flex: 1 1 calc(33.33% - 8px) !important;
        margin-bottom: 8px !important;
    }}
    .stApp .kpi-lbl {{
        font-size: 0.65rem !important; /* Texto ligeramente más pequeño para evitar elipsis */
    }}
    .stApp .kpi-num {{
        font-size: 1.45rem !important;
    }}
}}
@media (max-width: 768px) {{
    /* Envolver todas las columnas generales a ancho completo */
    div[data-testid="stHorizontalBlock"] {{
        flex-wrap: wrap !important;
    }}
    .stApp div[data-testid="column"]:not(:has(.kpi-card)) {{
        width: 100% !important;
        min-width: 100% !important;
        flex: 1 1 100% !important;
        margin-bottom: 12px !important;
    }}
    /* Envolver KPIs a 2 columnas en teléfonos (con especificidad definitiva para vencer a Streamlit a <700px) */
    div[data-testid="stHorizontalBlock"]:has(.kpi-card) {{
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: wrap !important;
        align-items: stretch !important;
    }}
    .stApp div[data-testid="column"]:has(.kpi-card) {{
        width: calc(50% - 6px) !important;
        min-width: calc(50% - 6px) !important;
        flex: 1 1 calc(50% - 6px) !important;
        margin-bottom: 8px !important;
    }}
    .stApp .kpi-lbl {{
        font-size: 0.62rem !important; /* Ajuste preciso para prevenir wrap en rejilla de 2 */
    }}
    .stApp .kpi-num {{
        font-size: 1.35rem !important;
    }}
}}
@media (max-width: 480px) {{
    /* En teléfonos muy pequeños, KPIs ocupan 100% */
    .stApp div[data-testid="column"]:has(.kpi-card) {{
        width: 100% !important;
        min-width: 100% !important;
        flex: 1 1 100% !important;
        margin-bottom: 8px !important;
    }}
    .stApp .kpi-lbl {{
        font-size: 0.72rem !important; /* Tamaño normal al ser columna completa */
    }}
    .stApp .kpi-num {{
        font-size: 1.7rem !important;
    }}
}}

/* ── Footer Bonito (Negro y Premium - Full Width) ── */
.dashboard-footer {{
    background: #222;
    color: #a0a0c0;
    padding: 30px 24px;
    border-radius: 0px !important;
    border: none !important;
    box-shadow: 0 -4px 30px rgba(0,0,0,0.3);
    margin-top: 40px;
    margin-left: -24px !important;
    margin-right: -24px !important;
    margin-bottom: -15px !important;
    width: calc(100% + 48px) !important;
    font-family: 'Inter', sans-serif;
}}
.footer-grid {{
    display: flex;
    flex-wrap: wrap;
    gap: 20px;
    justify-content: space-between;
    padding-bottom: 20px;
    border-bottom: 1px solid rgba(255,255,255,0.06);
}}
.footer-col {{
    flex: 1 1 200px;
    display: flex;
    flex-direction: column;
    gap: 6px;
}}
.footer-title {{
    font-family: 'Outfit', sans-serif;
    font-size: 0.85rem;
    font-weight: 700;
    color: #ffffff;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 2px;
}}
.footer-text {{
    font-size: 0.74rem;
    line-height: 1.4;
    color: #8c8ca8;
    display: flex;
    align-items: center;
    gap: 6px;
}}
.footer-dot {{
    width: 6px;
    height: 6px;
    border-radius: 50%;
    display: inline-block;
}}
.footer-dot.active {{
    background: #49b882;
    box-shadow: none !important;
}}
.footer-bottom {{
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    align-items: center;
    font-size: 0.68rem;
    color: #5c5c78;
    margin-top: 16px;
}}
</style>
""", unsafe_allow_html=True)


# ─── Metadata Helpers for Interactive Filters ─────────────────────────────────
@st.cache_data(ttl=60)
def fetch_tenants():
    client = get_clickhouse_client()
    if not client:
        return []
    try:
        res = client.execute("SELECT DISTINCT tenant_id FROM fact_sales_line")
        if isinstance(res, pd.DataFrame) and not res.empty:
            return sorted([str(t) for t in res.iloc[:, 0].tolist()])
        return []
    except Exception:
        return []


@st.cache_data(ttl=60)
def fetch_sucursales(tenant_id=None):
    client = get_clickhouse_client()
    if not client:
        return []
    try:
        query = "SELECT DISTINCT name FROM dim_sectional"
        if tenant_id and tenant_id != "Todos":
            query += f" WHERE tenant_id = {tenant_id}"
        res = client.execute(query)
        if isinstance(res, pd.DataFrame) and not res.empty:
            return sorted(res.iloc[:, 0].tolist())
        return []
    except Exception:
        return []


@st.cache_data(ttl=60)
def fetch_productos(tenant_id=None):
    client = get_clickhouse_client()
    if not client:
        return []
    try:
        query = "SELECT DISTINCT name FROM dim_product"
        if tenant_id and tenant_id != "Todos":
            query += f" WHERE tenant_id = {tenant_id}"
        res = client.execute(query)
        if isinstance(res, pd.DataFrame) and not res.empty:
            return sorted(res.iloc[:, 0].tolist())
        return []
    except Exception:
        return []


@st.cache_data(ttl=60)
def fetch_years():
    client = get_clickhouse_client()
    if not client:
        return []
    try:
        res = client.execute("SELECT DISTINCT year FROM dim_date")
        if isinstance(res, pd.DataFrame) and not res.empty:
            return sorted([int(y) for y in res.iloc[:, 0].tolist()])
        return []
    except Exception:
        return []


# ─── Data fetching (Dynamic Filter Injection) ──────────────────────────────────
@st.cache_data(ttl=60)
def fetch_data(query_string, tenant_id="Todos", sucursal="Todas", ano="Todos", producto="Todos", query_name="QUERY"):
    client = get_clickhouse_client()
    if not client:
        return pd.DataFrame()
    
    # Construct conditions for fact_sales_line subquery injection
    conditions = []
    
    # 1. Tenant Filter
    if tenant_id and tenant_id != "Todos":
        conditions.append(f"tenant_id = {tenant_id}")
        
    # 2. Branch Filter (Keep all branches visible in the comparison pie chart)
    if sucursal and sucursal != "Todas" and "Participación por Sucursal" not in query_name:
        conditions.append(f"sectional_id IN (SELECT sectional_id FROM dim_sectional WHERE name = '{sucursal}')")
        
    # 3. Year Filter (Keep all years visible in the YoY annual growth query)
    if ano and ano != "Todos" and "Crecimiento YoY" not in query_name:
        conditions.append(f"intDiv(date_id, 10000) = {ano}")
        
    # 4. Product Filter
    if producto and producto != "Todos":
        conditions.append(f"product_id IN (SELECT product_id FROM dim_product WHERE name = '{producto}')")
        
    # Inject conditions as a subquery for fact_sales_line
    if conditions:
        where_clause = " AND ".join(conditions)
        query_string = query_string.replace(
            "FROM fact_sales_line f",
            f"FROM (SELECT * FROM fact_sales_line WHERE {where_clause}) f"
        )
        
    df = client.execute(query_string)
    
    # Imprimir la consulta y el resultado en la consola del sistema para depuración
    print("\n" + "="*80)
    print(f"🔮 CLICKHOUSE QUERY EXECUTED: {query_name}")
    print("="*80)
    print(query_string.strip())
    print("-"*80)
    if isinstance(df, pd.DataFrame):
        print(f"📊 RESULTADO PANDAS ({len(df)} filas devueltas):")
        if not df.empty:
            print(df.head(5).to_string(index=False))
        else:
            print("[Resultado Vacío / DataFrame sin datos]")
    else:
        print(f"⚠️ Retorno no-DataFrame detectado: {type(df)}")
    print("="*80 + "\n")
    
    return df


# ─── Plotly layout helper (Anti-overlap axis margins & Bold Spanish labels) ────
def cl(fig, h=175, legend=False, xtitle="", ytitle=""):
    bottom_margin = 72 if legend else 25
    fig.update_layout(
        height=h,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", color=TEXT_MUTED, size=9.5),
        # Márgenes optimizados y compactados
        margin=dict(l=45, r=10, t=10, b=bottom_margin),
        xaxis=dict(
            # Títulos de ejes en negrita de alta legibilidad
            title=dict(text=f"<b>{xtitle}</b>" if xtitle else "", font=dict(size=9.5, color=TEXT_MUTED)),
            showgrid=False, 
            zeroline=False,
            tickfont=dict(size=9, color=TEXT_MUTED),
            tickcolor=BORDER, 
            linecolor=BORDER
        ),
        yaxis=dict(
            title=dict(text=f"<b>{ytitle}</b>" if ytitle else "", font=dict(size=9.5, color=TEXT_MUTED)),
            showgrid=True, 
            gridcolor=BORDER, 
            gridwidth=1,
            zeroline=False, 
            tickfont=dict(size=9, color=TEXT_MUTED)
        ),
        showlegend=legend,
        legend=dict(
            orientation="h", 
            yanchor="top", 
            y=-0.54 if legend else -0.2,
            xanchor="center", 
            x=0.5, 
            font=dict(size=8.5, color=TEXT_MUTED),
            bgcolor="rgba(0,0,0,0)",
            title=dict(text="")
        ),
        hoverlabel=dict(
            bgcolor=BG, 
            font_size=10, 
            font_family="Inter",
            bordercolor=BORDER, 
            font_color=TEXT
        ),
    )
    return fig


# ─── KPI card helper (Newline-safe HTML) ──────────────────────────────────────
def kpi(col, label, value, tag_text="", tag_cls="neu", accent=False, small_val=False):
    card_cls = "kpi-card ac" if accent else "kpi-card"
    val_cls  = "kpi-num sm" if small_val else "kpi-num"
    tag_html = f'<div class="kpi-tag {tag_cls}">{tag_text}</div>' if tag_text else ""
    
    # Strip all newlines to prevent Streamlit from leaking HTML code into the UI
    html_content = (
        f'<div class="{card_cls}">'
        f'<div class="kpi-lbl">{label}</div>'
        f'<div class="{val_cls}">{value}</div>'
        f'{tag_html}'
        f'</div>'
    ).replace("\n", " ")
    
    col.markdown(html_content, unsafe_allow_html=True)


# ─── Chart title helper ────────────────────────────────────────────────────────
def ctitle(text, accent=False):
    cls = "chart-title ac" if accent else "chart-title pr"
    st.markdown(f'<div class="{cls}">{text}</div>', unsafe_allow_html=True)


# ─── Empty placeholder helper (Glassmorphic and modern dashed border) ────────────
def render_empty_placeholder(height=230, message="No se encontraron datos para los filtros seleccionados"):
    html_content = (
        f'<div style="'
        f'height: {height}px; '
        f'display: flex; '
        f'flex-direction: column; '
        f'align-items: center; '
        f'justify-content: center; '
        f'border: 1px dashed {BORDER}; '
        f'border-radius: 4px; '
        f'background-color: {BG}; '
        f'box-shadow: {SHADOW_SM}; '
        f'padding: 20px; '
        f'text-align: center; '
        f'"> '
        f'<div style="font-size: 24px; margin-bottom: 8px; color: {TEXT_MUTED}; opacity: 0.6;">🔍</div>'
        f'<div style="font-family: \'Inter\', sans-serif; font-size: 0.8rem; font-weight: 500; color: {TEXT_MUTED}; opacity: 0.85;">'
        f'{message}'
        f'</div>'
        f'</div>'
    ).replace("\n", " ")
    st.markdown(html_content, unsafe_allow_html=True)


# ─── Custom HTML Table (Newline-safe for perfect rendering) ─────────────────────
def render_employee_table(df):
    if df.empty:
        return "<p style='color:#4a4a6a; font-size:0.8rem; padding:12px;'>No hay datos de colaboradores destacados.</p>"
    
    html = """
    <div class="table-container">
    <table class="emp-table">
        <thead>
            <tr>
                <th>ID Colaborador</th>
                <th>Puesto</th>
                <th>Facturas Emitidas</th>
                <th>Ventas Totales</th>
                <th>Ticket Promedio</th>
            </tr>
        </thead>
        <tbody>
    """
    for _, row in df.iterrows():
        emp_id = row.iloc[0]
        pos    = row.iloc[1]
        invs   = row.iloc[2]
        sales  = float(row.iloc[3])
        avg_t  = float(row.iloc[4])
        
        html += f"""
            <tr>
                <td style="color:#4328B1; background-color:#ffffff; font-weight:700;">{emp_id}</td>
                <td style="color:#1a1a2e; background-color:#ffffff;">{pos}</td>
                <td style="color:#1a1a2e; background-color:#ffffff; font-weight:600;">{int(invs)}</td>
                <td style="color:#166534; background-color:#ffffff; font-weight:700;">${sales:,.2f}</td>
                <td style="color:#4328B1; background-color:#ffffff; font-weight:700;">${avg_t:,.2f}</td>
            </tr>
        """
    html += """
        </tbody>
    </table>
    </div>
    """
    # CRITICAL: Streamlit interprets HTML strings with newlines as markdown blocks.
    # Replacing all newlines with spaces guarantees flawless HTML table rendering.
    return html.replace("\n", " ")


# ─── Main ─────────────────────────────────────────────────────────────────────
def main():

    # ── Topbar (Diseño ultra-minimalista: Solo marca "JOBBY ANALYTICS" y tiempo de refresco)
    st.markdown(
        f'<div class="topbar">'
        f'<div class="topbar-brand">'
        f'<span style="font-family:\'Outfit\', sans-serif; font-weight:800; font-size:1.25rem; letter-spacing:0.04em; color:#ffffff;">JOBBY ANALYTICS</span>'
        f'</div>'
        f'<div style="display:flex;align-items:center;">'
        f'<span class="topbar-pill"><span class="topbar-dot"></span>60s</span>'
        f'</div></div>'
        f'<div style="height:44px; margin-bottom:12px;"></div>',
        unsafe_allow_html=True,
    )

    # ── Filtros Interactivos (Español, cargados de forma reactiva) ───────────
    st.markdown('<span class="sec-label">Filtros de Búsqueda</span>', unsafe_allow_html=True)
    tenants_opt = ["Todos"] + fetch_tenants()

    # Filtros sin marcos ni contenedores molestos - minimalistas y limpios directamente en el fondo
    col_fil1, col_fil2, col_fil3, col_fil4 = st.columns(4, gap="small")
    
    with col_fil1:
        selected_tenant = st.selectbox("Filtrar por Tenant (ID)", tenants_opt, index=0)
        
    # Obtener dinámicamente las sucursales del tenant seleccionado
    sucursales_opt = ["Todas"] + fetch_sucursales(selected_tenant)
    with col_fil2:
        selected_sucursal = st.selectbox("Filtrar por Sucursal", sucursales_opt, index=0)
        
    # Obtener los años de la bodega
    anos_opt = ["Todos"] + [str(y) for y in fetch_years()]
    with col_fil3:
        selected_ano = st.selectbox("Filtrar por Año de Gestión", anos_opt, index=0)

    # Obtener los productos del tenant seleccionado
    products_opt = ["Todos"] + fetch_productos(selected_tenant)
    with col_fil4:
        selected_product = st.selectbox("Filtrar por Producto", products_opt, index=0)

    # ── Data Fetch (Ejecuta consultas dinámicamente filtradas por Tenant, Sucursal, Año, Producto) ──
    with st.spinner("Conectando con ClickHouse..."):
        df_annual     = fetch_data(queries.GET_ANNUAL_GROWTH_QUERY, selected_tenant, selected_sucursal, selected_ano, selected_product, "KPI: Crecimiento YoY")
        df_sectional  = fetch_data(queries.GET_CONTRIBUTION_PER_SECTIONAL_QUERY, selected_tenant, selected_sucursal, selected_ano, selected_product, "KPI: Sucursal Principal / Gráfica: Participación por Sucursal")
        df_employee   = fetch_data(queries.GET_PRODUCTIVITY_PER_EMPLOYEE_QUERY, selected_tenant, selected_sucursal, selected_ano, selected_product, "KPI: Ticket Promedio / Tabla: Colaboradores Destacados")
        df_monthly    = fetch_data(queries.GET_MONTHLY_EVOLUTION_QUERY, selected_tenant, selected_sucursal, selected_ano, selected_product, "KPI: Ingresos Totales / Gráfica: Evolución de Ingresos Mensuales")
        df_products   = fetch_data(queries.GET_TOP_PRODUCTS_QUERY, selected_tenant, selected_sucursal, selected_ano, selected_product, "KPI: Producto Principal / Gráfica: Top 10 Productos Más Vendidos")
        df_payment    = fetch_data(queries.GET_POPULAR_PAYMENT_METHODS_QUERY, selected_tenant, selected_sucursal, selected_ano, selected_product, "KPI: Transacciones / Gráfica: Métodos de Pago")
        df_avg_ticket = fetch_data(queries.GET_AVERAGE_TICKET_PER_SECTIONAL_AND_MONTH_QUERY, selected_tenant, selected_sucursal, selected_ano, selected_product, "Gráfica: Ticket Promedio por Sucursal")

    # ── Aplicar filtros adicionales en Pandas para interactividad instantánea ──
    df_sectional_filtered = df_sectional.copy()
    df_avg_ticket_filtered = df_avg_ticket.copy()
    df_monthly_filtered = df_monthly.copy()
    df_annual_filtered = df_annual.copy()
    
    # NOTA: Los filtros de Sucursal, Año y Producto ya se aplican directamente a nivel de consulta en ClickHouse!
    # El único filtro que se procesa aquí en Pandas es el Año de Gestión para la métrica YoY (Crecimiento YoY),
    # puesto que la consulta YoY requiere acceder a múltiples años para calcular correctamente la tasa de crecimiento.
    if selected_ano != "Todos":
        sel_year_int = int(selected_ano)
        if not df_annual_filtered.empty:
            df_annual_filtered = df_annual_filtered[df_annual_filtered["year"] == sel_year_int]

    # ── KPI derivation dinámico basado en filtros ───────────────────────────
    if selected_ano != "Todos":
        total_revenue = float(df_monthly_filtered["monthly_sales"].sum() or 0)
    else:
        total_revenue = float(df_sectional_filtered["total_sales"].sum() or 0)

    total_transactions = int(df_payment["transaction_count"].sum() or 0)        if not df_payment.empty   else 0
    avg_ticket_val     = float(df_employee["avg_ticket_per_sale"].mean() or 0)  if not df_employee.empty  else 0.0
    
    if selected_sucursal != "Todas":
        top_sectional = selected_sucursal
    else:
        top_sectional = str(df_sectional_filtered.iloc[0]["sectional_name"]) if not df_sectional_filtered.empty else "N/A"
        
    top_product = str(df_products.iloc[0]["product_name"]) if not df_products.empty else "N/A"
    
    _raw_growth        = (df_annual_filtered.iloc[-1]["growth_percent"]
                          if not df_annual_filtered.empty and "growth_percent" in df_annual_filtered.columns else None)
    growth             = float(_raw_growth) if _raw_growth is not None else 0.0

    growth_sign = "+" if growth >= 0 else ""
    g_tag_cls   = "pos" if growth >= 0 else "neg"
    g_tag_text  = "Crecimiento" if growth >= 0 else "Caída"

    # ── Sección: KPIs ───────────────────────────────────────────────────────
    st.markdown('<span class="sec-label">Métricas Clave</span>', unsafe_allow_html=True)

    k1, k2, k3, k4, k5, k6 = st.columns(6, gap="small")
    kpi(k1, "Ingresos Totales", f"${total_revenue/1000:,.1f}k", "Acumulado", "neu")
    kpi(k2, "Transacciones",   f"{total_transactions:,}",         "Registradas", "neu")
    kpi(k3, "Ticket Promedio", f"${avg_ticket_val:,.1f}",         "Por venta",   "neu",  accent=True)
    kpi(k4, "Crecimiento YoY", f"{growth_sign}{growth:,.1f}%",    g_tag_text,    g_tag_cls, accent=True)
    kpi(k5, "Sucursal Principal", top_sectional,                  "",            "neu",  small_val=True)
    kpi(k6, "Producto Principal", top_product,                    "",            "neu",  small_val=True)

    # ── Sección 1: Ingresos y Composición ───────────────────────────────────
    st.markdown('<span class="sec-label">Ingresos y Composición</span>', unsafe_allow_html=True)

    r1c1, r1c2, r1c3 = st.columns([2.2, 1.3, 1.5], gap="small")

    # Altura estándar unificada para todas las gráficas (230px)
    h_std = 230

    with r1c1:
        ctitle("Evolución de Ingresos Mensuales")
        if not df_monthly_filtered.empty:
            df_monthly_filtered = df_monthly_filtered.sort_values(["year", "month"])
            df_monthly_filtered["date"] = pd.to_datetime(
                df_monthly_filtered["year"].astype(str) + "-" +
                df_monthly_filtered["month"].astype(str).str.zfill(2) + "-01"
            )
            unique_dates = df_monthly_filtered["date"].unique()
            unique_labels = [f"{MONTHS_ES.get(d.month, '')} {d.year}" for d in pd.to_datetime(unique_dates)]
            
            fig = px.area(df_monthly_filtered, x="date", y="monthly_sales",
                          color_discrete_sequence=[PRIMARY],
                          markers=True,
                          labels={"date": "Fecha", "monthly_sales": "Ingresos ($)"})
            fig.update_traces(fillcolor="rgba(67,40,177,0.14)", line=dict(width=2))
            f = cl(fig, h=h_std, xtitle="Fecha", ytitle="Ingresos ($)")
            f.update_xaxes(
                tickmode="array",
                tickvals=unique_dates,
                ticktext=unique_labels
            )
            st.plotly_chart(f, use_container_width=True)
        else:
            render_empty_placeholder(h_std, "No hay datos de ingresos para esta selección")

    with r1c2:
        ctitle("Participación por Sucursal", accent=True)
        if not df_sectional_filtered.empty:
            fig = px.pie(df_sectional_filtered, names="sectional_name", values="total_sales",
                         hole=0.55, color_discrete_sequence=CHART_COLS,
                         labels={"sectional_name": "Sucursal", "total_sales": "Ventas ($)"})
            fig.update_traces(textposition="none",
                              hovertemplate="%{label}<br>%{value:,.0f}")
            f = cl(fig, h=h_std, legend=True)
            # Pie charts require optimized margins for maximum layout usage
            f.update_layout(margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(f, use_container_width=True)
        else:
            render_empty_placeholder(h_std, "No hay datos de sucursales para esta selección")

    with r1c3:
        ctitle("Métodos de Pago")
        if not df_payment.empty:
            fig = px.bar(df_payment, x="payment_method", y="total_amount",
                         color="type",
                         color_discrete_sequence=[PRIMARY, ACCENT],
                         barmode="group",
                         labels={"payment_method": "Método de Pago", "total_amount": "Total ($)", "type": "Tipo"})
            f = cl(fig, h=h_std, legend=True, xtitle="Método de Pago", ytitle="Total ($)")
            st.plotly_chart(f, use_container_width=True)
        else:
            render_empty_placeholder(h_std, "No hay datos de métodos de pago para esta selección")

    # ── Sección 2: Productos y Rendimiento ───────────────────────────────────
    st.markdown('<span class="sec-label">Productos y Rendimiento</span>', unsafe_allow_html=True)

    r2c1, r2c2 = st.columns([1, 1], gap="small")

    with r2c1:
        ctitle("Top 10 Productos Más Vendidos", accent=True)
        if not df_products.empty:
            top10 = df_products.head(10).sort_values("revenue", ascending=True)
            fig = px.bar(top10, x="revenue", y="product_name", orientation="h",
                         color_discrete_sequence=[PRIMARY],
                         labels={"revenue": "Ingresos ($)", "product_name": "Producto"})
            f = cl(fig, h=h_std, xtitle="Ingresos ($)", ytitle="") # Product names self-evident on Y-axis
            f.update_layout(yaxis=dict(showgrid=False, tickfont=dict(size=9, color=TEXT_MUTED)))
            st.plotly_chart(f, use_container_width=True)
        else:
            render_empty_placeholder(h_std, "No hay datos de productos para esta selección")

    with r2c2:
        ctitle("Ticket Promedio por Sucursal")
        if not df_avg_ticket_filtered.empty:
            df_avg_ticket_filtered = df_avg_ticket_filtered.sort_values(["year", "month"])
            df_avg_ticket_filtered["date"] = pd.to_datetime(
                df_avg_ticket_filtered["year"].astype(str) + "-" +
                df_avg_ticket_filtered["month"].astype(str).str.zfill(2) + "-01"
            )
            unique_dates = df_avg_ticket_filtered["date"].unique()
            unique_labels = [f"{MONTHS_ES.get(d.month, '')} {d.year}" for d in pd.to_datetime(unique_dates)]
            
            fig = px.line(df_avg_ticket_filtered, x="date", y="avg_ticket",
                          color="sectional",
                          color_discrete_sequence=CHART_COLS,
                          line_shape="spline",
                          markers=True,
                          labels={"date": "Fecha", "avg_ticket": "Ticket ($)", "sectional": "Sucursal"})
            fig.update_traces(line_width=2)
            f = cl(fig, h=h_std, legend=True, xtitle="Fecha", ytitle="Ticket ($)")
            f.update_xaxes(
                tickmode="array",
                tickvals=unique_dates,
                ticktext=unique_labels
            )
            st.plotly_chart(f, use_container_width=True)
        else:
            render_empty_placeholder(h_std, "No hay datos de ticket promedio para esta selección")

    # ── Sección 3: Desempeño de Colaboradores ────────────────────────────────
    st.markdown('<span class="sec-label">Desempeño de Colaboradores</span>', unsafe_allow_html=True)
    
    ctitle("Colaboradores Destacados", accent=True)
    if not df_employee.empty:
        st.markdown(render_employee_table(df_employee), unsafe_allow_html=True)
    else:
        render_empty_placeholder(120, "No hay datos de colaboradores para esta selección")

    # ── Sección 4: Footer Bonito ─────────────────────────────────────────────
    st.markdown("""
    <div class="dashboard-footer">
        <div class="footer-grid">
            <div class="footer-col">
                <span class="footer-title">Jobby Analytics v2.4</span>
                <span class="footer-text">Plataforma integrada de análisis multi-tenant de ventas, almacén y rendimiento comercial.</span>
            </div>
            <div class="footer-col">
                <span class="footer-title">Estado de la Integración</span>
                <span class="footer-text"><span class="footer-dot active"></span> ClickHouse Conectado</span>
                <span class="footer-text"><span class="footer-dot active"></span> Pipeline de Datos Activo</span>
            </div>
            <div class="footer-col">
                <span class="footer-title">Tecnologías Soportadas</span>
                <span class="footer-text">ClickHouse • Streamlit • Python • Debezium • Kafka • MongoDB</span>
            </div>
        </div>
        <div class="footer-bottom">
            <span>© 2026 Jobby ERP Corporation. Todos los derechos reservados.</span>
            <span>Sincronización en tiempo real • Latencia < 50ms</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
