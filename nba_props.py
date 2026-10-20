import pandas as pd
from nba_api.stats.endpoints import playergamelog
from nba_api.stats.static import players

def analizar_prop_jugador(nombre_jugador, stat_objetivo, linea_prop):
    print(f"\nBuscando estadísticas para: {nombre_jugador}...")
    
    # 1. Encontrar el ID del jugador por su nombre
    jugadores_encontrados = players.find_players_by_full_name(nombre_jugador)
    if not jugadores_encontrados:
        print("Jugador no encontrado. Verifica el nombre.")
        return
    
    jugador_id = jugadores_encontrados[0]['id']
    
    # 2. Obtener el registro de partidos de la temporada actual (2025-26 o 2026-27 según corresponda)
    # Usamos la temporada 2025-26 como referencia estándar
    gamelog = playergamelog.PlayerGameLog(player_id=jugador_id, season='2025-26')
    df = gamelog.get_data_frames()[0]
    
    if df.empty:
        print("No se encontraron registros de partidos para este jugador.")
        return

    # Mapeo de estadísticas en el DataFrame de la NBA API
    # 3PM = Triples anotados, PTS = Puntos, AST = Asistencias, REB = Rebotes
    mapa_stats = {
        'triples': 'FG3M',
        'puntos': 'PTS',
        'asistencias': 'AST',
        'rebotes': 'REB'
    }
    
    columna_stat = mapa_stats.get(stat_objetivo.lower())
    if not columna_stat:
        print("Estadística no válida. Usa: 'triples', 'puntos', 'asistencias' o 'rebotes'.")
        return

    # 3. Analizar últimas ventanas (L5, L10, L20)
    df_l5 = df.head(5)
    df_l10 = df.head(10)
    df_l20 = df.head(20)

    promedio_l5 = df_l5[columna_stat].mean()
    promedio_l10 = df_l10[columna_stat].mean()
    
    # Calcular aciertos (Hit Rate) sobre la línea propuesta
    aciertos_l5 = (df_l5[columna_stat] > linea_prop).sum()
    aciertos_l10 = (df_l10[columna_stat] > linea_prop).sum()
    
    # 4. Mostrar Resultados en pantalla
    print("=" * 50)
    print(f" REPORTE DE PROPS: {nombre_jugador.upper()}")
    print(f" Prop analizado: Más de {linea_prop} {stat_objetivo}")
    print("=" * 50)
    print(f" Proyección (Promedio L10): {promedio_l10:.2f}")
    print(f" Proyección (Promedio L5):  {promedio_l5:.2f}")
    print(f" Aciertos en últimos 5 partidos (L5):   {aciertos_l5} de 5 ({(aciertos_l5/5)*100:.0f}%)")
    print(f" Aciertos en últimos 10 partidos (L10): {aciertos_l10} de 10 ({(aciertos_l10/10)*100:.0f}%)")
    print("=" * 50)
    
    # Mostrar detalle de los últimos partidos
    print("\n Detalle de los últimos 5 partidos:")
    for index, row in df_l5.iterrows():
        fecha = row['GAME_DATE']
        matchup = row['MATCHUP']
        valor_obtenido = row[columna_stat]
        cumplio = "✅ ACERTÓ"_si_cumplio = "Sí" if valor_obtenido > linea_prop else "No"
        print(f"   [{fecha}] {matchup} -> {stat_objetivo.capitalize()}: {valor_obtenido} (Línea: {linea_prop}) -> Superó la línea: {_si_cumplio}")

# Ejemplo de prueba para ejecutar el script:
if __name__ == "__main__":
    # Puedes cambiar los valores para probar con cualquier jugador y prop
    analizar_prop_jugador(
        nombre_jugador="Cade Cunningham", 
        stat_objetivo="triples", 
        linea_prop=1.5
    )
