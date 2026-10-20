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

# Configuração da API-Football
API_KEY = "B7ae21f7f0e5920369e6cd9e7bc63ccc"
BASE_URL = "https://v3.football.api-sports.io"

def buscar_estatisticas_reais(time_nome: str):
    """
    Busca estatísticas reais de desempenho diretamente da API-Football em tempo real.
    """
    headers = {
        "x-apisports-key": API_KEY
    }
    
    try:
        # 1. Pesquisar o ID da equipa pelo nome
        url_busca = f"{BASE_URL}/teams?search={time_nome}"
        response = requests.get(url_busca, headers=headers, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            teams = data.get("response", [])
            if teams:
                team_id = teams[0].get("team", {}).get("id")
                # Pegamos a temporada atual (ex: 2026)
                temporada = 2026
                
                # 2. Buscar estatísticas gerais da equipa na temporada
                url_stats = f"{BASE_URL}/teams/statistics?season={temporada}&team={team_id}&league=39" # Liga de exemplo ou geral
                res_stats = requests.get(url_stats, headers=headers, timeout=5)
                
                if res_stats.status_code == 200:
                    stats_data = res_stats.json().get("response", {})
                    gols_favor = stats_data.get("goals", {}).get("for", {}).get("average", {}).get("total", "1.3")
                    gols_contra = stats_data.get("goals", {}).get("against", {}).get("average", {}).get("total", "1.1")
                    
                    media_ataque = float(gols_favor) if str(gols_favor).replace('.', '', 1).isdigit() else 1.3
                    media_defesa = float(gols_contra) if str(gols_contra).replace('.', '', 1).isdigit() else 1.1
                    
                    return {
                        "ataque": max(media_ataque, 0.5),
                        "defesa": max(media_defesa, 0.5),
                        "forma": 1.05
                    }
                    
        # Fallback caso a equipa não seja encontrada de imediato
        return {"ataque": 1.35, "defesa": 1.10, "forma": 1.00}
        
    except Exception:
        # Fallback de segurança em caso de instabilidade na rede
        return {"ataque": 1.30, "defesa": 1.15, "forma": 1.00}

def calcular_xg_real(time_casa: str, time_fora: str):
    stats_casa = buscar_estatisticas_reais(time_casa)
    stats_fora = buscar_estatisticas_reais(time_fora)
    
    fator_casa = 1.12
    
    xg_casa = (stats_casa["ataque"] + stats_fora["defesa"]) / 2 * fator_casa * stats_casa["forma"]
    xg_fora = (stats_fora["ataque"] + stats_casa["defesa"]) / 2 * stats_fora["forma"]
    
    return float(round(xg_casa, 2)), float(round(xg_fora, 2))

@app.get("/analisar")
def analisar(home: str, away: str):
    xg_casa, xg_fora = calcular_xg_real(home, away)
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
    
    return {
        "partida": f"{home} vs {away}",
        "xg_casa": xg_casa,
        "xg_fora": xg_fora,
        "total_xg": total_xg_esperado,
        "linha_gols": linha_gols,
        "cobertura": float(round(soma_prob * 100, 1)),
        "tem_valor_dutching": tem_valor_dutching,
        "soma_implicita": float(round(soma_implicita, 2)),
        "top_5": top_5
    }
