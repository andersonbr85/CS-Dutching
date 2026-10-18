from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
from scipy.stats import poisson

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Banco de dados simulado de força ofensiva e defensiva das principais equipes (xG Médio Ajustado)
# Quanto maior o índice ofensivo, mais gols a equipe cria.
ESTATISTICAS_TIMES = {
    "arsenal": {"ataque": 2.15, "defesa": 0.70},
    "manchester city": {"ataque": 2.40, "defesa": 0.75},
    "liverpool": {"ataque": 2.25, "defesa": 0.80},
    "chelsea": {"ataque": 1.70, "defesa": 1.05},
    "tottenham": {"ataque": 1.80, "defesa": 1.20},
    "manchester united": {"ataque": 1.55, "defesa": 1.15},
    "nottingham": {"ataque": 1.20, "defesa": 1.10},
    "aston villa": {"ataque": 1.75, "defesa": 1.10},
    "newcastle": {"ataque": 1.65, "defesa": 1.15},
    "real madrid": {"ataque": 2.45, "defesa": 0.70},
    "barcelona": {"ataque": 2.35, "defesa": 0.75},
    "atletico madrid": {"ataque": 1.60, "defesa": 0.80},
    "bayern munich": {"ataque": 2.60, "defesa": 0.80},
    "dortmund": {"ataque": 1.90, "defesa": 1.25},
    "psg": {"ataque": 2.40, "defesa": 0.85},
    "inter milan": {"ataque": 1.95, "defesa": 0.75},
    "juventus": {"ataque": 1.50, "defesa": 0.80},
    "ac milan": {"ataque": 1.65, "defesa": 1.05},
    "flamengo": {"ataque": 1.85, "defesa": 0.85},
    "palmeiras": {"ataque": 1.80, "defesa": 0.80},
    "botafogo": {"ataque": 1.75, "defesa": 0.90},
    "sao paulo": {"ataque": 1.40, "defesa": 0.95},
    "corinthians": {"ataque": 1.30, "defesa": 1.05},
    "fluminense": {"ataque": 1.45, "defesa": 1.10},
}

def calcular_xg_dinamico(time_casa: str, time_fora: str):
    casa_key = time_casa.strip().lower()
    fora_key = time_fora.strip().lower()
    
    # Pega os dados do time da casa ou usa padrão intermediário se não estiver na lista
    stats_casa = ESTATISTICAS_TIMES.get(casa_key, {"ataque": 1.50, "defesa": 1.10})
    stats_fora = ESTATISTICAS_TIMES.get(fora_key, {"ataque": 1.20, "defesa": 1.30})
    
    # Fator casa no futebol (geralmente acrescenta cerca de 15% a 20% no xG do mandante)
    fator_casa = 1.15
    
    # Cálculo cruzado de xG (Ataque do mandante vs Defesa do visitante e vice-versa)
    xg_casa = round((stats_casa["ataque"] + stats_fora["defesa"]) / 2 * fator_casa, 2)
    xg_fora = round((stats_fora["ataque"] + stats_casa["defesa"]) / 2, 2)
    
    return xg_casa, xg_fora

@app.get("/analisar")
def analisar(home: str, away: str):
    xg_casa, xg_fora = calcular_xg_dinamico(home, away)
    
    max_gols = 5
    placares = []
    
    for c in range(max_gols + 1):
        for f in range(max_gols + 1):
            prob_c = poisson.pmf(c, xg_casa)
            prob_f = poisson.pmf(f, xg_fora)
            prob_total = prob_c * prob_f
            
            if c > f:
                desc = "Casa vence"
            elif f > c:
                desc = "Visitante vence"
            else:
                desc = "Empate"
                
            placares.append({
                "placar": f"{c} - {f}",
                "descricao": desc,
                "probabilidade": float(prob_total)
            })
            
    top_5 = sorted(placares, key=lambda x: x["probabilidade"], reverse=True)[:5]
    soma_prob = sum(p["probabilidade"] for p in top_5)
    
    return {
        "partida": f"{home} vs {away}",
        "xg_casa": xg_casa,
        "xg_fora": xg_fora,
        "cobertura": round(soma_prob * 100, 1),
        "top_5": top_5
    }
