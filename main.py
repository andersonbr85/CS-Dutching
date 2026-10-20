import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from scipy.stats import poisson

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY = "B7ae21f7f0e5920369e6cd9e7bc63ccc"
BASE_URL = "https://v3.football.api-sports.io"

def buscar_estatisticas_e_liga(time_nome: str):
    headers = {"x-apisports-key": API_KEY}
    liga_nome = "Competição Geral"
    
    try:
        url_busca = f"{BASE_URL}/teams?search={time_nome}"
        response = requests.get(url_busca, headers=headers, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            teams = data.get("response", [])
            if teams:
                team_id = teams[0].get("team", {}).get("id")
                url_fixtures = f"{BASE_URL}/fixtures?team={team_id}&last=10&status=FT"
                res_fixtures = requests.get(url_fixtures, headers=headers, timeout=5)
                
                if res_fixtures.status_code == 200:
                    fixtures_data = res_fixtures.json().get("response", [])
                    total_jogos = len(fixtures_data)
                    
                    if total_jogos > 0:
                        # Extrai o nome exato do campeonato da última partida
                        liga_nome = fixtures_data[0].get("league", {}).get("name", "Liga Principal")
                        gols_marcados = 0
                        gols_sofridos = 0
                        
                        for fix in fixtures_data:
                            home_id = fix.get("teams", {}).get("home", {}).get("id")
                            goals_home = fix.get("goals", {}).get("home") or 0
                            goals_away = fix.get("goals", {}).get("away") or 0
                            
                            if home_id == team_id:
                                gols_marcados += goals_home
                                gols_sofridos += goals_away
                            else:
                                gols_marcados += goals_away
                                gols_sofridos += goals_home
                                
                        media_ataque = float(round(gols_marcados / total_jogos, 2))
                        media_defesa = float(round(gols_sofridos / total_jogos, 2))
                        
                        return {
                            "ataque": max(media_ataque, 0.40),
                            "defesa": max(media_defesa, 0.40),
                            "forma": 1.05,
                            "liga": liga_nome
                        }
                        
        return {"ataque": 1.30, "defesa": 1.10, "forma": 1.00, "liga": liga_nome}
    except Exception:
        return {"ataque": 1.25, "defesa": 1.15, "forma": 1.00, "liga": "Competição Geral"}

def calcular_xg_real(time_casa: str, time_fora: str):
    stats_casa = buscar_estatisticas_e_liga(time_casa)
    stats_fora = buscar_estatisticas_e_liga(time_fora)
    
    fator_casa = 1.12
    xg_casa = (stats_casa["ataque"] + stats_fora["defesa"]) / 2 * fator_casa * stats_casa["forma"]
    xg_fora = (stats_fora["ataque"] + stats_casa["defesa"]) / 2 * stats_fora["forma"]
    
    campeonato = stats_casa.get("liga", "Competição Geral")
    
    return float(round(xg_casa, 2)), float(round(xg_fora, 2)), campeonato

@app.get("/analisar")
def analisar(home: str, away: str):
    xg_casa, xg_fora, campeonato = calcular_xg_real(home, away)
    total_xg_esperado = float(round(xg_casa + xg_fora, 2))
    
    if total_xg_esperado >= 2.80:
        linha_gols = "Over 2.5"
    elif total_xg_esperado <= 2.30:
        linha_gols = "Under 2.5"
    else:
        linha_gols = "Equilibrado (2.5)"
    
    max_gols = 5
    placares = []
    
    for c in range(max_gols + 1):
        for f in range(max_gols + 1):
            prob_c = float(poisson.pmf(c, xg_casa))
            prob_f = float(poisson.pmf(f, xg_fora))
            prob_total = prob_c * prob_f
            
            desc = "Casa vence" if c > f else ("Visitante vence" if f > c else "Empate")
            odd_estimada = float(round(1 / prob_total, 2)) if prob_total > 0 else 99.0
            
            placares.append({
                "placar": f"{c} - {f}",
                "descricao": desc,
                "probabilidade": float(prob_total),
                "odd_estimada": odd_estimada
            })
            
    top_5 = sorted(placares, key=lambda x: x["probabilidade"], reverse=True)[:5]
    
    soma_implicita = sum(1 / p["odd_estimada"] for p in top_5)
    tem_valor_dutching = bool(soma_implicita < 0.95)
    soma_prob = sum(p["probabilidade"] for p in top_5)
    
    cobertura_percentual = float(round(soma_prob * 100, 1))
    
    if cobertura_percentual < 40.0:
        alerta_volatilidade = "⚠️ Alerta: Jogo de Alta Volatilidade (Risco Elevado para Dutching)"
    elif cobertura_percentual >= 55.0:
        alerta_volatilidade = "✅ Jogo com Excelente Concentração Estatística (Favorável)"
    else:
        alerta_volatilidade = "ℹ️ Jogo de Volatilidade Moderada"

    return {
        "partida": f"{home} vs {away}",
        "campeonato": campeonato,
        "xg_casa": xg_casa,
        "xg_fora": xg_fora,
        "total_xg": total_xg_esperado,
        "linha_gols": linha_gols,
        "cobertura": cobertura_percentual,
        "alerta_volatilidade": alerta_volatilidade,
        "tem_valor_dutching": tem_valor_dutching,
        "soma_implicita": float(round(soma_implicita, 2)),
        "top_5": top_5
    }
