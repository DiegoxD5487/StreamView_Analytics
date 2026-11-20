"""StreamView Analytics EV3 — Dashboard interactivo para exposición ejecutiva.

Ejecutar desde esta carpeta: python -m streamlit run app.py
"""
from __future__ import annotations

from pathlib import Path
import base64
import html
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import pycountry
import streamlit as st

from core import load_data, filter_data, portfolio_metrics, genre_aggregates, country_aggregates
from analytics import (
    most_common_genre, most_common_country, opportunities,
    comparable_movies, languages_for_chart, genre_evidence,
    genre_decision_matrix, financial_comparison_metrics,
)

BASE = Path(__file__).resolve().parent
DATA = BASE / 'datos' / 'STREAMVIEW_POWERBI.csv'
LOGO = BASE / "recursos" / "logo_streamview.png"
FONDO = BASE / 'recursos' / 'fondo_streamview.png'
NAVY = '#111827'
NIGHT = '#0E1A77'
PURPLE = '#7C208A'
VIOLET = '#7C3AED'
LAVENDER = '#9071CE'
BLUE = '#3B82F6'
CYAN = '#38BDF8'
GOLD = '#A38600'
INK = '#172033'
MUTED = '#546179'

st.set_page_config(page_title='StreamView | Analytics', page_icon='📊', layout='wide',
                   initial_sidebar_state='collapsed')

# El diseño anterior usaba imágenes con botones y cajas dibujadas. Esto causaba
# superposiciones. Ahora todos los paneles son HTML/CSS o widgets reales.
st.markdown('''
<style>
:root { color-scheme: dark; }
.stApp {
  background:
    radial-gradient(ellipse 58% 44% at 98% 0%, rgba(146,52,220,.22), transparent 74%),
    radial-gradient(ellipse 47% 54% at 0% 100%, rgba(35,86,211,.18), transparent 76%),
    linear-gradient(150deg,#10122c 0%,#181246 48%,#321056 100%);
}
header[data-testid="stHeader"] { background:transparent; }
[data-testid="stMainBlockContainer"] {max-width:1510px; padding:1.1rem 1.7rem 2.5rem;}
[data-testid="stSidebar"] {display:none;}
#MainMenu, footer {visibility:hidden;}
[data-testid="stToolbar"] {visibility:hidden;}

.st-key-brand_bar {
 background:linear-gradient(112deg,rgba(18,32,88,.97),rgba(81,33,155,.97) 70%,rgba(123,28,158,.95));
 border:1px solid rgba(210,180,255,.30);border-radius:20px;
 padding:13px 25px 8px;box-shadow:0 12px 35px rgba(4,7,30,.23);
}
.st-key-brand_bar img {max-width:100%; width:100%; height:auto; object-fit:contain; display:block; border-radius:9px;}
.sv-brand-title {color:white;font-size:1.34rem;font-weight:800;line-height:1.2;letter-spacing:.2px;text-align:right}
.sv-brand-sub {color:#E9D5FF;font-size:.82rem;text-align:right;margin-top:5px}

.st-key-nav_shell {display:flex;justify-content:center;margin:.78rem auto 1.08rem;}
.st-key-nav_shell [data-testid="stRadio"] {margin:auto;max-width:100%;}
.st-key-nav_shell [role="radiogroup"] {
 display:flex;justify-content:center;flex-wrap:wrap;gap:.35rem;
 width:fit-content;margin:auto;border:1px solid rgba(192,173,255,.28);
 border-radius:13px;background:rgba(8,18,83,.96);padding:6px 12px;
 box-shadow:0 8px 20px rgba(3,7,23,.17);
}
.st-key-nav_shell [role="radiogroup"] label {padding:4px 8px;border-radius:9px;}
.st-key-nav_shell [role="radiogroup"] label:hover {background:rgba(255,255,255,.07)}
.st-key-nav_shell [role="radiogroup"] p {font-size:.92rem;font-weight:750;color:white!important;}

.sv-section-kicker {color:#C8A7FF; font-size:.72rem;letter-spacing:.11em;font-weight:850;text-transform:uppercase}
.sv-section-title {color:#FFF;font-size:1.55rem;font-weight:800;line-height:1.2;margin:.15rem 0 .2rem;}
.sv-section-desc {color:#D2CFEB;font-size:.90rem;margin:0 0 1rem;max-width:920px;}

.st-key-filters_band {
 background:rgba(14,20,50,.96);border:1px solid rgba(184,156,254,.28);
 border-radius:16px;padding:10px 17px 0px;margin-bottom:1.06rem;
 box-shadow:0 10px 28px rgba(4,7,24,.18);
}
.st-key-filters_band [data-testid="stWidgetLabel"] *,
.st-key-filters_band label {color:#F3EEFF!important;font-weight:650!important;}
.st-key-filters_band [data-baseweb="select"] {background:#fff;border-radius:8px;}
.st-key-filters_band [data-baseweb="select"] * {color:#172033!important;}
.st-key-filters_band [data-testid="stSlider"] * {color:#fff;}
.st-key-filters_band [data-testid="stButton"] button {
 background:#A38600!important;color:white!important;border:0!important;
 border-radius:11px;font-weight:800;min-height:41px;margin-top:11px;
}
.st-key-filters_band [data-testid="stButton"] button:hover {background:#C3A21A!important}
.st-key-filters_band [data-testid="stSliderTickBarMin"],
.st-key-filters_band [data-testid="stSliderTickBarMax"] {color:#fff!important;}

.sv-kpi {min-height:122px; padding:13px 12px 12px;border-radius:12px;
 background:#111B35;border:1px solid #45538E;border-top:3px solid #8B5CF6;
 box-shadow:0 8px 20px rgba(6,5,28,.13);}
.sv-kpi.blue {background:#18375D;border-top-color:#38BDF8;}
.sv-kpi.finance {background:#2B2678;border-top-color:#A78BFA;}
.sv-kpi .label {font-size:.73rem;color:#DBEAFE;min-height:29px;line-height:1.15;}
.sv-kpi .value {font-size:1.35rem;color:#fff;font-weight:820;line-height:1.3;overflow-wrap:anywhere;}
.sv-kpi .suffix {font-size:.71rem;line-height:1.32;color:#CFD4F5;margin-top:6px;min-height:26px;}

[data-testid="stVerticalBlockBorderWrapper"]:has([class*="st-key-chart_"]) {background:#fff;}
.st-key-chart_donut, .st-key-chart_genres, .st-key-chart_countries,
.st-key-chart_popularity, .st-key-chart_map, .st-key-chart_rating,
.st-key-chart_languages, .st-key-chart_scatter, .st-key-chart_priority,
.st-key-chart_financial, .st-key-chart_table {
  background:#FFFFFF!important;border-radius:13px!important;
  border:1px solid rgba(74,85,120,.20)!important;
  padding:7px 9px 4px!important;box-shadow:0 11px 25px rgba(4,7,24,.18);
}
/* Textos de Plotly se fijan explícitamente en los gráficos, evitando ejes blancos. */
.sv-insight {background:#17203B;border:1px solid #3F446A;border-left:4px solid #A38600;
 border-radius:12px;padding:16px 18px;color:#F5F5FC;min-height:115px;line-height:1.55;font-size:.90rem;}
.sv-insight strong {color:#D8B4FE;}
.sv-insight .eyebrow {font-size:.72rem;font-weight:850;letter-spacing:.06em;color:#E9D5FF;margin-bottom:7px;}
.sv-mini {font-size:.83rem;color:#D0CCEC;margin:10px 0;}
.sv-tag {display:inline-flex;color:#F3E8FF;background:#432375;border:1px solid #8058C3;
 border-radius:99px;padding:.28rem .72rem;font-weight:700;font-size:.83rem;}
.sv-table-title {font-size:1.06rem;color:white;font-weight:780;margin:.7rem 0 .4rem;}
.st-key-country_reset [data-testid="stButton"] button {
 color:#F3E8FF;background:#552783;border:1px solid #8A61CC;border-radius:20px;
 padding:.2rem .9rem;min-height:34px;
}
.st-key-country_reset [data-testid="stButton"] button:hover {background:#6B36A6;color:white;}
[data-testid="stExpander"] {background:rgba(20,27,58,.94);border:1px solid #4C477B;border-radius:12px;}
[data-testid="stExpander"] * {color:white!important;}
[data-testid="stDataFrame"] {border-radius:12px;overflow:hidden;}
@media(max-width:960px){
 [data-testid="stMainBlockContainer"] {padding:.55rem .75rem 1.5rem;}
 .sv-brand-title,.sv-brand-sub{text-align:left;}
 .sv-kpi{min-height:78px}.sv-kpi .value{font-size:1.12rem;}
 .sv-section-title{font-size:1.3rem;}
}
</style>
''', unsafe_allow_html=True)


# Fondo decorativo de StreamView
# Se aplica sobre la página, manteniendo intactos los paneles y gráficos.

if FONDO.is_file():
    fondo_b64 = base64.b64encode(FONDO.read_bytes()).decode("ascii")

    st.markdown(
        f"""
        <style>
        .stApp {{
            background:
                linear-gradient(
                    135deg,
                    rgba(10, 10, 37, 0.28),
                    rgba(30, 9, 57, 0.07)
                ),
                url("data:image/png;base64,{fondo_b64}")
                center bottom / cover fixed no-repeat !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

# Estilo exclusivo de la guía de indicadores
st.markdown(
    """
    <style>
    .st-key-kpi_help {
        width: 100%;
        margin-top: 7px;
        margin-bottom: 11px;
    }

    .st-key-kpi_help [data-testid="stExpander"] {
        background: rgba(20, 27, 58, 0.96);
        border: 1px solid #59528A;
        border-radius: 11px;
    }

    .st-key-kpi_help [data-testid="stExpander"] summary {
        padding: 8px 14px !important;
    }

    .st-key-kpi_help [data-testid="stExpander"] summary p {
        font-size: 0.88rem !important;
        font-weight: 700 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

def number(value: int | float) -> str:
    return f'{int(value):,}'.replace(',', '.')


def decimal(value: float | None, digits: int = 2) -> str:
    if value is None or pd.isna(value):
        return '—'
    return f'{value:,.{digits}f}'.replace(',', '|').replace('.', ',').replace('|','.')


def short_amount(value: float | None) -> str:
    if value is None or pd.isna(value):
        return '—'
    if abs(value) >= 1_000_000_000:
        return f'{decimal(value/1_000_000_000, 1)} mil M'
    if abs(value) >= 1_000_000:
        return f'{decimal(value/1_000_000, 1)} M'
    return number(value)


def metric(label: str, val: str, variant: str = '', suffix: str = '') -> None:
    st.markdown(f'<div class="sv-kpi {variant}"><div class="label">{html.escape(label)}</div>'
                f'<div class="value">{html.escape(val)}</div>'
                f'<div class="suffix">{html.escape(suffix)}</div></div>',
                unsafe_allow_html=True)


def section(kicker: str, title: str, description: str) -> None:
    st.markdown(f'<div class="sv-section-kicker">{html.escape(kicker)}</div>'
                f'<div class="sv-section-title">{html.escape(title)}</div>'
                f'<p class="sv-section-desc">{html.escape(description)}</p>',
                unsafe_allow_html=True)


def insight(title: str, text: str) -> None:
    st.markdown(f'<div class="sv-insight"><div class="eyebrow">{html.escape(title)}</div>'
                f'{html.escape(text)}</div>', unsafe_allow_html=True)


def configure(fig: go.Figure, title: str, height: int = 365, l: int = 58,
              r: int = 28, b: int = 50) -> go.Figure:
    fig.update_layout(
        title=dict(text=title, x=.5, y=.97, xanchor='center', yanchor='top',
                   font=dict(color=INK, size=15, family='Arial')),
        margin=dict(l=l, r=r, t=57, b=b),height=height,
        autosize=True, paper_bgcolor='#FFFFFF', plot_bgcolor='#FFFFFF',
        font=dict(color=INK, size=11, family='Arial'),
        hoverlabel=dict(bgcolor=NAVY, font=dict(color='#FFFFFF',size=12)),
        showlegend=False,
    )
    fig.update_xaxes(tickfont=dict(color=MUTED, size=10),title_font=dict(color=MUTED, size=11),
                     gridcolor='#E9EDF4',zeroline=False,automargin=True)
    fig.update_yaxes(tickfont=dict(color=MUTED,size=10),title_font=dict(color=MUTED,size=11),
                     gridcolor='#EDF0F5',zeroline=False,automargin=True)
    return fig


def no_data(title: str, height: int = 365) -> go.Figure:
    fig = go.Figure()
    fig.add_annotation(text='No hay datos para esta selección',x=.5,y=.5,
                       xref='paper',yref='paper',showarrow=False,font=dict(color=MUTED,size=13))
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return configure(fig,title,height)


def bars(data: pd.DataFrame, category: str, value: str, title: str,
         horizontal: bool = True, height: int = 365, n: int = 10,
         precision: int = 0, active: str | None = None) -> go.Figure:
    if data.empty:
        return no_data(title,height)
    top = data.sort_values(value,ascending=False).head(n).copy()
    colors = [('#A044E8' if active is not None and str(label)==active else
               VIOLET if active is None and i==0 else BLUE if i<5 else '#76B5F8')
              for i,label in enumerate(top[category])]
    if horizontal:
        top = top.iloc[::-1]
        colors = colors[::-1]
        labels = [decimal(x,precision) if precision else number(x) for x in top[value]]
        fig=go.Figure(go.Bar(x=top[value],y=top[category],orientation='h',
                             marker_color=colors,text=labels,textposition='outside',
                             cliponaxis=False,
                             hovertemplate='<b>%{y}</b><br>Valor: %{x:,.2f}<extra></extra>'))
        fig.update_xaxes(rangemode='tozero',title=None)
        fig.update_yaxes(showgrid=False,type='category')
        return configure(fig,title,height,l=155,r=78,b=40)
    labels=[decimal(x,precision) if precision else number(x) for x in top[value]]
    fig=go.Figure(go.Bar(x=top[category],y=top[value],marker_color=colors,
                         text=labels,textposition='outside',cliponaxis=False,
                         hovertemplate='<b>%{x}</b><br>Valor: %{y:,.2f}<extra></extra>'))
    fig.update_yaxes(rangemode='tozero')
    fig.update_xaxes(tickangle=-28,type='category')
    return configure(fig,title,height,l=50,r=30,b=85)


def donut(df: pd.DataFrame) -> go.Figure:
    groups=df.type.value_counts()
    labels=[x for x in ('Movie','TV Show') if groups.get(x,0)>0]
    if not labels:
        return no_data('Composición del catálogo')
    fig=go.Figure(go.Pie(labels=labels,values=[int(groups[x]) for x in labels],
                         hole=.67,sort=False,marker=dict(colors=[BLUE if x=='Movie' else VIOLET for x in labels]),
                         textinfo='label+percent',textposition='outside',automargin=True,
                         hovertemplate='%{label}<br>%{value:,} títulos<br>%{percent}<extra></extra>'))
    fig.update_layout(annotations=[dict(x=.5,y=.5,text=number(df.content_id.nunique()),showarrow=False,
                                      font=dict(size=19,color=INK))])
    fig=configure(fig,'Composición del catálogo',height=385,l=26,r=26,b=25)
    fig.update_layout(showlegend=True,legend=dict(orientation='h',y=-.07,x=.5,xanchor='center',
                                                   font=dict(color=MUTED,size=10)))
    return fig


def country_chart(base_df: pd.DataFrame, active: str | None) -> go.Figure:
    # Una selección en estas barras filtra los demás gráficos; este gráfico
    # conserva el conjunto sin país para poder seleccionar otro país.
    countries = country_aggregates(base_df)
    fig=bars(countries,'country_principal','contenidos','Países con mayor presencia',
             height=385,n=10,active=active)
    fig.update_layout(clickmode='event+select',dragmode='select')
    return fig


def country_iso3(name: str) -> str | None:
    aliases={'United States of America':'USA','South Korea':'KOR','Russia':'RUS',
             'Turkey':'TUR','Palestinian Territory':'PSE','Macedonia':'MKD','Cote D\'Ivoire':'CIV'}
    if name in aliases:
        return aliases[name]
    try:
        return pycountry.countries.lookup(name).alpha_3
    except LookupError:
        return None


def map_chart(base_df: pd.DataFrame, active: str | None) -> go.Figure:
    countries=country_aggregates(base_df).copy()
    countries['iso']=countries.country_principal.map(country_iso3)
    countries=countries.dropna(subset=['iso'])
    if countries.empty:
        return no_data('Mapa de países de origen')
    fig=px.scatter_geo(countries,locations='iso',locationmode='ISO-3',size='contenidos',
                       hover_name='country_principal',custom_data=['country_principal'],
                       projection='natural earth',size_max=30,
                       color_discrete_sequence=[BLUE])
    marker_colors=[VIOLET if active and name==active else BLUE for name in countries.country_principal]
    fig.update_traces(marker=dict(color=marker_colors,opacity=.82,line=dict(color=NIGHT,width=.9)),
                      hovertemplate='<b>%{customdata[0]}</b><br>Selecciona el país<extra></extra>')
    fig.update_geos(showcoastlines=True,coastlinecolor='#BDD0E8',showcountries=True,
                    countrycolor='#B6CAE1',showland=True,landcolor='#D1E8DD',
                    showocean=True,oceancolor='#A8D3F5',showlakes=False,
                    bgcolor='#FFFFFF',showframe=False)
    fig=configure(fig,'Mapa de países de origen',height=385,l=8,r=8,b=8)
    fig.update_layout(clickmode='event+select')
    return fig


def quadrant(df: pd.DataFrame, minimum: int, min_median_votes: int=0) -> go.Figure:
    g=genre_evidence(df,min_titles=minimum)
    g=g.loc[g['votos_medianos'].ge(min_median_votes)]
    if g.empty:
        return no_data('Presencia y popularidad por género',height=365)
    xlim=float(g.contenidos.mean())
    ylim=float(g.popularidad.mean())
    fig=go.Figure(go.Scatter(x=g.contenidos,y=g.popularidad,mode='markers',
                             text=g.genre_principal,
                             marker=dict(size=12,color=BLUE,line=dict(color='#FFFFFF',width=1)),
                             customdata=g[['valoracion','votos_medianos']].to_numpy(),
                             hovertemplate='<b>%{text}</b><br>Contenidos: %{x:,}'
                                           '<br>Popularidad media: %{y:.2f}'
                                           '<br>Valoración: %{customdata[0]:.2f}'
                                           '<br>Mediana de votos: %{customdata[1]:,.0f}<extra></extra>'))
    fig.add_hline(y=ylim,line_dash='dot',line_color='#9B84B5',line_width=1.5)
    fig.add_vline(x=xlim,line_dash='dot',line_color='#9B84B5',line_width=1.5)
    fig.update_xaxes(title='Cantidad de títulos',rangemode='tozero')
    fig.update_yaxes(title='Popularidad promedio',rangemode='tozero')
    return configure(fig,'Presencia y popularidad por género',height=365,l=60,r=25,b=60)


def priority_chart(o: pd.DataFrame) -> go.Figure:
    """Compara una variable observada, no un índice comercial inventado."""
    if o.empty:
        return no_data('Géneros sujetos a evaluación editorial')
    top=o.head(8).iloc[::-1]
    categories={
        'Evaluar expansión':VIOLET,
        'Consolidar':BLUE,
        'Revisar recepción':'#C68B15',
        'Revisar oferta':'#64748B',
        'Monitorear':'#76B5F8',
    }
    tooltip=top[['Títulos','Valoración media','Votos medianos','Foco de revisión']].to_numpy()
    fig=go.Figure(go.Bar(
        y=top['Género'], x=top['Popularidad media'],orientation='h',
        marker_color=[categories.get(c,BLUE) for c in top['Foco de revisión']],
        text=top['Foco de revisión'],textposition='outside',cliponaxis=False,
        customdata=tooltip,
        hovertemplate='<b>%{y}</b><br>Popularidad media: %{x:.2f}'
                      '<br>Títulos: %{customdata[0]:,}'
                      '<br>Valoración media: %{customdata[1]:.2f}'
                      '<br>Votos medianos por título: %{customdata[2]:,.0f}'
                      '<br>Foco: %{customdata[3]}<extra></extra>'
    ))
    fig.update_xaxes(title='Popularidad media (métrica del dataset)',rangemode='tozero')
    fig.update_yaxes(showgrid=False)
    return configure(fig,'Géneros sujetos a evaluación editorial',height=385,l=150,r=143,b=60)


def financial_chart(fin: pd.DataFrame) -> go.Figure:
    if fin.empty:
        return no_data('Películas con mayor múltiplo de recaudación')
    top=fin.sort_values('multiplo',ascending=False).head(8).iloc[::-1]
    fig=go.Figure(go.Bar(y=top.title,x=top.multiplo,orientation='h',
                         marker_color=BLUE,text=[decimal(v,1)+'×' for v in top.multiplo],
                         textposition='outside',cliponaxis=False,
                         hovertemplate='<b>%{y}</b><br>Recaudación / presupuesto: %{x:.2f}×<extra></extra>'))
    fig.update_yaxes(showgrid=False)
    fig.update_xaxes(title='Recaudación / presupuesto de producción (veces)',rangemode='tozero')
    return configure(fig,'Películas con mayor múltiplo de recaudación',height=385,l=170,r=52,b=58)


def process_country_click(event, field: str) -> None:
    """Aplica la selección Plotly a un filtro común, sin tocar el selectbox ya creado."""
    if event is None:
        return
    try:
        points=event['selection']['points']
        if not points:
            return
        point=points[-1]
        if field=='y':
            value=str(point['y'])
        else:
            raw=point.get('customdata',[])
            value=str(raw[0] if isinstance(raw,(list,tuple)) and raw else raw)
        if not value or value=='None':
            return
        if st.session_state.clicked_country != value:
            st.session_state.clicked_country=value
            st.rerun()
    except (KeyError,IndexError,TypeError,ValueError):
        pass


@st.cache_data(show_spinner='Cargando catálogo…')
def load_default() -> pd.DataFrame:
    return load_data(DATA)

if not DATA.exists():
    st.error('No se encontró data/STREAMVIEW_POWERBI.csv. Extrae todo el ZIP y abre la carpeta correcta.')
    st.stop()
try:
    all_data=load_default()
except (OSError,ValueError,pd.errors.ParserError) as exc:
    st.error(f'Error al abrir el catálogo: {exc}')
    st.stop()

min_year=int(all_data.release_year.dropna().min())
max_year=int(all_data.release_year.dropna().max())
TYPES=['Movie','TV Show']

for key,val in {
    'filters_types':TYPES[:], 'filters_genre':'Todos','filters_country':'Todos',
    'filters_years':(min_year,max_year), 'clicked_country':None,
    'country_chart_nonce':0, 'view':'Resumen Ejecutivo',
}.items():
    if key not in st.session_state:
        st.session_state[key]=val


def clear_clicked():
    st.session_state.clicked_country=None
    st.session_state.country_chart_nonce+=1


def reset_filters():
    st.session_state.filters_types=TYPES[:]
    st.session_state.filters_genre='Todos'
    st.session_state.filters_country='Todos'
    st.session_state.filters_years=(min_year,max_year)
    clear_clicked()

def clear_country_button():
    st.session_state.filters_country='Todos'
    clear_clicked()

with st.container(key='brand_bar'):
    logo_col,hero_col=st.columns([.39,.61],gap='medium',vertical_alignment='center')
    with logo_col:
        st.image(str(LOGO),width=360)
    with hero_col:
        st.markdown('<div class="sv-brand-title">STREAMVIEW · INTELIGENCIA DE CONTENIDOS</div>'
                    '<div class="sv-brand-sub">Una mirada ejecutiva para tomar mejores decisiones audiovisuales</div>',
                    unsafe_allow_html=True)

with st.container(key='nav_shell'):
    view=st.radio('Navegación',
                  ['Resumen Ejecutivo','Potencial de contenido','Decisiones estratégicas'],
                  key='view',horizontal=True,label_visibility='collapsed')

PAGE_DESC={
    'Resumen Ejecutivo':('VISIÓN GENERAL','Resumen ejecutivo',
        'Distribución del catálogo, indicadores globales y concentración por género y origen.'),
    'Potencial de contenido':('ANÁLISIS DE CONTENIDOS','Potencial de contenido',
        'Popularidad, valoración, idiomas y oportunidades de exploración editorial.'),
    'Decisiones estratégicas':('GESTIÓN Y RECOMENDACIONES','Decisiones estratégicas',
        'Prioridades, evidencia, limitaciones e impacto esperado para el negocio.'),
}
section(*PAGE_DESC[view])

country_opts=['Todos']+sorted(country_aggregates(all_data).country_principal.astype(str).unique())
genre_opts=['Todos']+sorted(genre_aggregates(all_data).genre_principal.astype(str).unique())

with st.container(key='filters_band'):
    f1,f2,f3,f4,f5=st.columns([1.35,1.35,1.35,1.75,1.5],gap='medium',vertical_alignment='bottom')
    with f1:
        st.multiselect('Tipo de contenido',TYPES,key='filters_types')
    with f2:
        st.selectbox('Género principal',genre_opts,key='filters_genre')
    with f3:
        st.selectbox('País principal',country_opts,key='filters_country',on_change=clear_clicked)
    with f4:
        st.slider('Periodo de estreno',min_year,max_year,key='filters_years')
    with f5:
        st.button('↺ Reiniciar filtros',on_click=reset_filters,use_container_width=True)

base_df=filter_data(all_data,types=st.session_state.filters_types,
                    years=st.session_state.filters_years,
                    genre=st.session_state.filters_genre)
active_country=st.session_state.clicked_country or st.session_state.filters_country
filtered=filter_data(base_df,country=active_country)
metrics=portfolio_metrics(filtered)

if active_country != 'Todos':
    with st.container(key='country_reset'):
        bleft,bright=st.columns([.85,.15],vertical_alignment='center')
        with bleft:
            st.markdown('<span class="sv-tag">📍 País activo: '+html.escape(active_country)+'</span>',
                        unsafe_allow_html=True)
        with bright:
            st.button('✕ Quitar país',use_container_width=True,
                      on_click=clear_country_button)

if filtered.empty:
    st.warning('No hay títulos con los filtros actuales. Prueba reiniciar filtros o ampliar el periodo.')

if view=='Resumen Ejecutivo':
    kcols=st.columns(7,gap='small')
    entries=[
        ('Total contenidos',number(metrics['total']),''),
        ('Total películas',number(metrics['movies']),''),
        ('Total series',number(metrics['series']),''),
        ('Valoración promedio',decimal(metrics['rating']),'blue'),
        ('Popularidad promedio',decimal(metrics['popularity']),'blue'),
        ('Recaudación / presupuesto',decimal(metrics['revenue_budget_ratio'])+'×' if metrics['revenue_budget_ratio'] else '—','finance'),
        ('Ingresos − presupuesto',short_amount(metrics['revenue_budget_delta']),'finance'),
    ]
    for c,(label,value,kind) in zip(kcols,entries):
        with c: metric(label,value,kind)

  
    with st.container(key="kpi_help"):
        with st.expander("Guía de lectura de indicadores", expanded=False):
            st.markdown("""
**Composición del catálogo:** los indicadores de contenidos, películas y series representan la cantidad de títulos únicos que cumplen los filtros seleccionados.

**Valoración promedio:** promedio de las calificaciones registradas para los contenidos seleccionados.

**Popularidad promedio:** índice relativo de popularidad registrado en la base de datos. No equivale a visualizaciones ni suscripciones.

**Recaudación / presupuesto:** relación entre la recaudación acumulada y el presupuesto acumulado de películas con datos financieros válidos. Se expresa como múltiplo.

**Ingresos − presupuesto:** diferencia acumulada entre ambas variables. No representa las ganancias netas de StreamView.
""")

    st.write('')
    a,b,c=st.columns([1,1.15,1],gap='medium')
    with a:
        with st.container(key='chart_donut'):
            st.plotly_chart(donut(filtered),use_container_width=True,config={'displayModeBar':False})
    with b:
        with st.container(key='chart_genres'):
            gg=genre_aggregates(filtered)
            st.plotly_chart(bars(gg,'genre_principal','contenidos','Géneros con mayor presencia',
                                 height=385),use_container_width=True,config={'displayModeBar':False})
    with c:
        with st.container(key='chart_countries'):
            # Este gráfico no usa el filtro país para permitir cambiar a otro de un solo clic.
            event=st.plotly_chart(country_chart(base_df,active_country if active_country!='Todos' else None),
                                  use_container_width=True,config={'displayModeBar':False},
                                  key=f'country_bar_{st.session_state.country_chart_nonce}',
                                  on_select='rerun',selection_mode='points')
            process_country_click(event,'y')
    st.markdown('<div class="sv-mini">💡 Haz clic en una barra del gráfico de países: el resto del dashboard se actualizará. También puedes elegir un país en los filtros superiores.</div>',unsafe_allow_html=True)

    genre_name,genre_count=most_common_genre(filtered)
    country_name,country_count=most_common_country(filtered)
    e1,e2=st.columns(2,gap='medium')
    with e1:
        share=genre_count/len(filtered)*100 if len(filtered) else 0
        insight('ESTRUCTURA DE LA OFERTA',
                f'{genre_name} representa {decimal(share,1)} % de la selección '
                f'({number(genre_count)} de {number(len(filtered))} títulos). '
                'Este nivel de concentración justifica comparar presencia con valoración y popularidad '
                'antes de renovar o incorporar contenidos.')
    with e2:
        share=country_count/len(filtered)*100 if len(filtered) else 0
        insight('CONCENTRACIÓN POR ORIGEN',
                f'{country_name} es el origen principal de {number(country_count)} títulos '
                f'({decimal(share,1)} % del total seleccionado). '
                'La gerencia puede usarlo para identificar dependencias del catálogo por país y '
                'evaluar la diversificación geográfica, sin asumir preferencias de suscriptores.')

    with st.expander('Ver detalle de los títulos seleccionados',expanded=False):
        tbl=filtered[['title','type','release_year','genre_principal','country_principal',
                      'popularity','vote_average','vote_count']].copy()
        tbl=tbl.sort_values('popularity',ascending=False).head(50)
        tbl.columns=['Título','Tipo','Estreno','Género','País principal','Popularidad','Valoración','Votos']
        st.dataframe(tbl,use_container_width=True,hide_index=True)

elif view=='Potencial de contenido':
    controls=st.columns([1,1,1],gap='medium')
    with controls[0]:
        min_genre=st.select_slider('Títulos mínimos por género',
                                   options=[1,25,50,100,200,400],value=100,
                                   help='Se incluyen solamente géneros principales con al menos esta cantidad de títulos.')
    with controls[1]:
        min_median_votes=st.select_slider('Mediana mínima de votos por género',
                                         options=[0,5,10,20,50,100],value=10,
                                         help='Exige que la mediana de votos por título del género alcance este valor.')
    with controls[2]:
        min_language=st.select_slider('Títulos mínimos por idioma',
                                      options=[1,10,20,30,50,100],value=30)

    genre_all=genre_evidence(filtered,min_titles=min_genre)
    g=genre_all.loc[genre_all['votos_medianos'].ge(min_median_votes)]
    excluded=len(genre_all)-len(g)
    st.markdown('<div class="sv-mini"><strong>Criterio de lectura:</strong> se comparan géneros con suficiente presencia y respaldo de votos; '
                'la popularidad no equivale a reproducciones de StreamView. '
                f'Géneros incluidos: <strong>{number(len(g))}</strong>; excluidos por votos: <strong>{number(excluded)}</strong>.</div>',
                unsafe_allow_html=True)
    one,two,three=st.columns(3,gap='medium')
    with one:
        with st.container(key='chart_popularity'):
            st.plotly_chart(bars(g,'genre_principal','popularidad','Géneros con mayor popularidad media',
                                 horizontal=False,precision=1,height=385),
                            use_container_width=True,config={'displayModeBar':False})
    with two:
        with st.container(key='chart_map'):
            map_event=st.plotly_chart(map_chart(base_df,active_country if active_country!='Todos' else None),
                                      use_container_width=True,config={'displayModeBar':False},
                                      key=f'country_map_{st.session_state.country_chart_nonce}',
                                      on_select='rerun',selection_mode='points')
            process_country_click(map_event,'customdata')
    with three:
        with st.container(key='chart_rating'):
            st.plotly_chart(bars(g,'genre_principal','valoracion','Géneros con mejor valoración',
                                 precision=2,height=385),
                            use_container_width=True,config={'displayModeBar':False})

    left,right=st.columns([1.15,1],gap='medium')
    with left:
        langs=languages_for_chart(filtered,min_titles=min_language)
        with st.container(key='chart_languages'):
            st.plotly_chart(bars(langs,'idioma_etiqueta','popularidad',
                                 'Idiomas con mayor popularidad media',
                                 horizontal=False,precision=1,height=365),
                            use_container_width=True,config={'displayModeBar':False})
    with right:
        with st.container(key='chart_scatter'):
            st.plotly_chart(quadrant(filtered,min_genre,min_median_votes),use_container_width=True,
                            config={'displayModeBar':False})
    st.markdown('<div class="sv-mini">📍 El mapa utiliza el país principal informado para cada título. El país se puede seleccionar desde el mapa o desde el filtro superior.</div>',unsafe_allow_html=True)

    ic1,ic2=st.columns(2,gap='medium')
    with ic1:
        high=g.sort_values('popularidad',ascending=False).iloc[0] if not g.empty else None
        if high is not None:
            insight('EVIDENCIA PARA PROGRAMACIÓN Y CONTENIDOS',
                    f'Entre los géneros que cumplen los filtros de muestra, '
                    f'{high["genre_principal"]} registra la mayor popularidad media '
                    f'({decimal(high["popularidad"],1)}), con {number(high["contenidos"])} títulos '
                    f'y una valoración promedio de {decimal(high["valoracion"],2)}. '
                    'Se recomienda evaluar el grupo junto con su volumen de votos y costos de adquisición.')
        else:
            insight('EVIDENCIA PARA PROGRAMACIÓN Y CONTENIDOS',
                    'Los criterios de muestra no dejan géneros comparables. Reduce los mínimos o amplía el periodo.')
    with ic2:
        insight('ALCANCE Y FIABILIDAD DE LOS RESULTADOS',
                'La popularidad y valoración son atributos de un catálogo de origen externo. '
                'Los umbrales de títulos y votos reducen el riesgo de comparaciones basadas en categorías pequeñas, '
                'pero no convierten estas medidas en reproducciones, satisfacción ni retención de StreamView. '
                'Los rankings por idioma utilizan un mínimo de títulos, pero requieren una revisión adicional del volumen de votos.')

    with st.expander('Explorar y comparar títulos',expanded=False):
        t1,t2,t3=st.columns([1.5,1,1])
        with t1: title_query=st.text_input('Buscar título',placeholder='Ej. Inception')
        with t2: min_votes=st.number_input('Votos mínimos',min_value=0,max_value=100000,value=100,step=100)
        with t3: order=st.selectbox('Ordenar por',['Popularidad','Valoración','Votos'])
        table_df=filtered.copy()
        if title_query:
            table_df=table_df[table_df.title.fillna('').str.contains(title_query,case=False,regex=False)]
        table_df=table_df.loc[table_df.vote_count.fillna(0).ge(min_votes)]
        order_col={'Popularidad':'popularity','Valoración':'vote_average','Votos':'vote_count'}[order]
        table_df=table_df.sort_values(order_col,ascending=False).head(80)
        view_cols=['title','type','release_year','genre_principal','country_principal',
                   'popularity','vote_average','vote_count']
        table_df=table_df[view_cols]
        table_df.columns=['Título','Tipo','Año','Género','País','Popularidad','Valoración','Votos']
        st.dataframe(table_df,use_container_width=True,hide_index=True)

else:
    # Decisiones con indicadores calculados sobre universos explícitos y comparables.
    eligible_genres=genre_evidence(filtered,min_titles=100)
    editorial=genre_decision_matrix(filtered,min_titles=100,min_median_votes=10)
    fin=comparable_movies(filtered,min_budget=1_000_000,min_votes=100)
    fin_kpi=financial_comparison_metrics(filtered,min_budget=1_000_000,min_votes=100)
    kp=st.columns(4,gap='small')
    with kp[0]:
        metric('Géneros con muestra suficiente',number(len(eligible_genres)),'blue',
               'Al menos 100 títulos por género principal')
    with kp[1]:
        metric('Películas comparables',number(fin_kpi['eligible']),'finance',
               'Presupuesto ≥ 1 millón; ingresos > 0; ≥100 votos')
    with kp[2]:
        coverage=fin_kpi['coverage']
        metric('Cobertura de la muestra financiera',decimal(coverage*100,1)+' %' if coverage is not None else '—','blue',
               'Películas comparables / películas del segmento')
    with kp[3]:
        multiple=fin_kpi['gross_multiple']
        metric('Recaudación / presupuesto',decimal(multiple)+'×' if multiple is not None else '—','finance',
               'Múltiplo bruto de la misma muestra comparable')

    st.markdown('<div class="sv-mini"><strong>Interpretación de los KPI:</strong> '
                f'{number(len(eligible_genres))} géneros con ≥100 títulos no significa que todos tengan respaldo suficiente de votos. '
                f'La matriz editorial incluye {number(len(editorial))} géneros, que cumplen además mediana de ≥10 votos por título. '
                'Los criterios financieros se aplican solo a películas y son iguales en los dos indicadores económicos de esta página.</div>',
                unsafe_allow_html=True)
    st.write('')

    p1,p2=st.columns(2,gap='medium')
    with p1:
        with st.container(key='chart_priority'):
            st.plotly_chart(priority_chart(editorial),use_container_width=True,config={'displayModeBar':False})
    with p2:
        with st.container(key='chart_financial'):
            st.plotly_chart(financial_chart(fin),use_container_width=True,config={'displayModeBar':False})
    st.markdown('<div class="sv-mini"><strong>Criterios:</strong> el análisis editorial requiere '
                '≥100 títulos por género y una mediana de ≥10 votos por título. '
                'La comparación de películas exige presupuesto ≥1 millón, ingresos positivos y ≥100 votos. '
                'El múltiplo expresa recaudación/presupuesto de producción, <strong>no ROI neto ni ganancias de StreamView</strong>.</div>',
                unsafe_allow_html=True)

    s1,s2=st.columns(2,gap='medium')
    with s1:
        expand=editorial.loc[editorial['Foco de revisión'].eq('Evaluar expansión')]
        lead=expand.iloc[0] if not expand.empty else (editorial.iloc[0] if not editorial.empty else None)
        if lead is not None:
            insight('RECOMENDACIÓN PRELIMINAR · EQUIPO DE CONTENIDOS',
                    f'Evaluar el género {lead["Género"]} como candidato de revisión editorial: '
                    f'{number(lead["Títulos"])} títulos ({decimal(lead["Participación (%)"],1)} % del segmento), '
                    f'popularidad media {decimal(lead["Popularidad media"],1)} y valoración '
                    f'{decimal(lead["Valoración media"],2)}. '
                    'Contrastar estos resultados con costos de licencia y consumo real antes de decidir una adquisición.')
        else:
            insight('RECOMENDACIÓN PRELIMINAR · EQUIPO DE CONTENIDOS',
                    'La selección no contiene géneros con muestra y respaldo de votos suficientes. '
                    'No corresponde emitir una recomendación de adquisición con la evidencia disponible.')
    with s2:
        if fin_kpi['total_films']:
            insight('COBERTURA Y CAUTELA · GERENCIA',
                    f'Solo {number(fin_kpi["eligible"])} de {number(fin_kpi["total_films"])} películas '
                    f'({decimal(fin_kpi["coverage"]*100,1)} %) cumplen los criterios comparativos. '
                    f'La relación agregada recaudación/presupuesto es {decimal(multiple,2)}× '
                    'en ese grupo. No debe interpretarse como beneficio de la plataforma; '
                    'se requiere validar la completitud y origen de los datos antes de usarlo para negociar.')
        else:
            insight('COBERTURA Y CAUTELA · GERENCIA',
                    'La selección no contiene películas; por lo tanto, no es posible comparar presupuesto y recaudación. '
                    'La revisión editorial puede continuar sin indicadores financieros.')

    st.markdown('<div class="sv-table-title">Matriz de evidencia para decisiones de contenido</div>',unsafe_allow_html=True)
    st.dataframe(editorial,use_container_width=True,hide_index=True,
                 column_config={'Títulos':st.column_config.NumberColumn(format='%d'),
                                'Participación (%)':st.column_config.NumberColumn(format='%.1f'),
                                'Popularidad media':st.column_config.NumberColumn(format='%.2f'),
                                'Valoración media':st.column_config.NumberColumn(format='%.2f'),
                                'Votos medianos':st.column_config.NumberColumn(format='%.0f')})
    st.markdown('<div class="sv-mini"><strong>Cómo se construye la matriz:</strong> cada fila representa '
                'un género principal con al menos 100 títulos y mediana de al menos 10 votos. '
                'El foco editorial se asigna comparando popularidad, valoración y presencia con '
                'las medianas de los géneros elegibles, siempre dentro de los filtros activos. '
                'Son señales exploratorias, <strong>no una clasificación de rentabilidad ni una predicción de éxito</strong>.</div>',
                unsafe_allow_html=True)

    val1,val2=st.columns(2,gap='medium')
    with val1:
        insight('VALOR PARA EL NEGOCIO · IMPACTO ESPERADO',
                'Reducir tiempo de exploración del catálogo, documentar criterios de selección '
                'y concentrar la revisión editorial en grupos con respaldo cuantitativo. '
                'Estos beneficios están propuestos, todavía no medidos en operación.')
    with val2:
        insight('CÓMO VALIDAREMOS EL RESULTADO',
                'Registrar una línea base del tiempo que tarda el equipo en evaluar un género; '
                'medir la proporción de recomendaciones con evidencia documentada y revisar '
                'la completitud de los metadatos en cada actualización del catálogo.')

    with st.expander('Evaluación crítica, mitigaciones y plan de mejora',expanded=False):
        st.markdown('''
**Fortalezas verificables**

- Catálogo integrado a nivel de título, con claves únicas.
- Cruce de cantidad, popularidad y valoración mediante filtros y navegación comunes.
- Selección geográfica aplicada a los demás gráficos y métricas.

**Limitaciones y mitigaciones**

- No hay registros de reproducciones, suscripciones ni retención: no atribuir resultados a engagement o fidelización real.
- Un solo país y género principales pueden simplificar títulos multivalor: documentar el criterio e incorporar tablas puente en una fase posterior.
- Presupuestos nulos o simbólicos pueden inflar multiplicadores: mostrar cobertura y umbrales explícitos, sin modificar la base.
- Los promedios pueden estar influidos por muestras pequeñas: exigir mínimos de títulos y considerar volumen de votos.

**Mejoras priorizadas**

1. Verificar calidad, cobertura y origen de cada variable (prioridad alta).
2. Incorporar datos de visualizaciones y comportamiento real de usuarios si están disponibles (prioridad alta).
3. Validar hipótesis editoriales con expertos y seguimiento de indicadores (prioridad media).
4. Ampliar atribución de géneros y países mediante relaciones multivalor (prioridad media).

**KPIs para evaluar el impacto futuro (propuestas, aún sin línea base)**

- Tiempo medio para preparar un análisis editorial (minutos).
- Porcentaje de recomendaciones respaldadas por evidencia documentada.
- Porcentaje de registros con metadatos completos.
- Si se integran datos operativos: reproducción por título, retención y uso de recomendaciones.
''')

# Se quitó el pie de página de fuente para evitar saturar la presentación.
# Las advertencias sobre el origen y alcance de los datos permanecen en el análisis.
