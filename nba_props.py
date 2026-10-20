import streamlit as st
import pandas as pd
from nba_api.stats.endpoints import playergamelog
from nba_api.stats.static import players

# Configuración de la página de Streamlit
st.set_page_config(page_title="NBA Props Analizador", page_icon="🏀", layout="wide")

st.title("🏀 Analizador de Props NBA (Uso Personal)")
st.markdown("Filtra y analiza el rendimiento reciente de los jugadores frente a líneas específicas.")

# --- BARRA LATERAL (CONTROLES) ---
st.sidebar.header("Parámetros de Búsqueda")
nombre_jugador = st.sidebar.text_input("Nombre del Jugador", value="Cade Cunningham")
stat_objetivo = st.sidebar.selectbox(
    "Estadística a Analizar",
    options=["triples", "puntos", "asistencias", "rebotes"]
)
linea_prop = st.sidebar.number_input("Línea del Prop", value=1.5, step=0.5)

# Mapeo para la API de la NBA
mapa_stats = {
    'triples': 'FG3M',
    'puntos': 'PTS',
    'asistencias': 'AST',
    'rebotes': 'REB'
}
columna_stat = mapa_stats[stat_objetivo]

# --- FUNCIÓN PARA OBTENER DATOS ---
@st.cache_data(ttl=3600)
def cargar_datos_jugador(nombre):
    jugadores = players.find_players_by_full_name(nombre)
    if not jugadores:
        return None, None
    
    jugador_id = jugadores[0]['id']
    nombre_completo = jugadores[0]['full_name']
    
    try:
        gamelog = playergamelog.PlayerGameLog(player_id=jugador_id, season='2025-26', timeout=30)
        df = gamelog.get_data_frames()[0]
        return nombre_completo, df
    except Exception as e:
        return nombre_completo, None

# --- PROCESAMIENTO Y VISTA PRINCIPAL ---
if st.sidebar.button("Analizar Jugador"):
    with st.spinner(f"Buscando estadísticas para {nombre_jugador}..."):
        nombre_oficial, df = cargar_datos_jugador(nombre_jugador)
        
        if df is None:
            st.error("⚠️ Ocurrió un error al conectar con la API de la NBA. Inténtalo de nuevo.")
        elif df.empty:
            st.warning(f"No se encontraron registros de partidos para '{nombre_oficial}' en esta temporada.")
        else:
            # Ventanas de análisis
            df_l5 = df.head(5)
            df_l10 = df.head(10)
            
            promedio_l5 = df_l5[columna_stat].mean()
            promedio_l10 = df_l10[columna_stat].mean()
            
            aciertos_l5 = (df_l5[columna_stat] > linea_prop).sum()
            aciertos_l10 = (df_l10[columna_stat] > linea_prop).sum()
            
            # --- MÉTRICAS SUPERIORES ---
            st.subheader(f"Resultados para: {nombre_oficial}")
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric(label="Proyección (Prom. L10)", value=f"{promedio_l10:.2f}")
            col2.metric(label="Promedio L5", value=f"{promedio_l5:.2f}")
            col3.metric(label="Aciertos (L10)", value=f"{aciertos_l10} / 10", delta=f"{(aciertos_l10/10)*100:.0f}%")
            col4.metric(label="Aciertos (L5)", value=f"{aciertos_l5} / 5", delta=f"{(aciertos_l5/5)*100:.0f}%")
            
            st.divider()
            
            # --- GRÁFICA DE BARRAS ---
            st.markdown(f"### Comportamiento en los últimos 10 partidos (Línea: {linea_prop})")
            
            df_grafica = df_l10[['GAME_DATE', 'MATCHUP', columna_stat]].copy()
            df_grafica = df_grafica.rename(columns={columna_stat: 'Valor', 'GAME_DATE': 'Fecha', 'MATCHUP': 'Enfrentamiento'})
            df_grafica = df_grafica.set_index('Fecha')
            
            st.bar_chart(df_grafica['Valor'])
            
            # --- TABLA DE DETALLE ---
            st.markdown("### Detalle Partido a Partido (L10)")
            
            df_detalle = df_l10[['GAME_DATE', 'MATCHUP', columna_stat']].copy()
            df_detalle['Superó Línea'] = df_detalle[columna_stat].apply(lambda x: "✅ Sí" if x > linea_prop else "❌ No")
            df_detalle = df_detalle.rename(columns={'GAME_DATE': 'Fecha', 'MATCHUP': 'Enfrentamiento', columna_stat: stat_objetivo.capitalize()})
            
            st.dataframe(df_detalle, use_container_width=True)
