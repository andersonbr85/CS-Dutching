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

ESTATISTICAS_TIMES = {
    "arsenal": {"ataque": 2.15, "defesa": 0.70, "forma": 1.10, "tendencia_empate": 0.90},
    "manchester city": {"ataque": 2.40, "defesa": 0.75, "forma": 1.15, "tendencia_empate": 0.85},
    "liverpool": {"ataque": 2.25, "defesa": 0.80, "forma": 1.12, "tendencia_empate": 0.88},
    "chelsea": {"ataque": 1.70, "defesa": 1.05, "forma": 1.00, "tendencia_empate": 1.05},
    "tottenham": {"ataque": 1.80, "defesa": 1.20, "forma": 0.95, "tendencia_empate": 0.95},
    "coventry": {"ataque": 1.30, "defesa": 1.15, "forma": 1.00, "tendencia_empate": 1.10},
    "manchester united": {"ataque": 1.55, "defesa": 1.15, "forma": 0.90, "tendencia_empate": 1.00},
    "nottingham": {"ataque": 1.20, "defesa": 1.10, "forma": 1.05, "tendencia_empate": 1.10},
    "aston villa": {"ataque": 1.75, "defesa": 1.10, "forma": 1.08, "tendencia_empate": 0.95},
    "newcastle": {"ataque": 1.65, "defesa": 1.15, "forma": 0.98, "tendencia_empate": 1.00},
    "real madrid": {"ataque": 2.45, "defesa": 0.70, "forma": 1.20, "tendencia_empate": 0.80},
    "barcelona": {"ataque": 2.35, "defesa": 0.75, "forma": 1.15, "tendencia_empate": 0.85},
    "atletico madrid": {"ataque": 1.60, "defesa": 0.80, "forma": 1.00, "tendencia_empate": 1.15},
    "bayern munich": {"ataque": 2.60, "defesa": 0.80, "forma": 1.10, "tendencia_empate": 0.80},
    "dortmund": {"ataque": 1.90, "defesa": 1.25, "forma": 1.00, "tendencia_empate": 0.95},
    "psg": {"ataque": 2.40, "defesa": 0.85, "forma": 1.10, "tendencia_empate": 0.90},
    "inter milan": {"ataque": 1.95, "defesa": 0.75, "forma": 1.12, "tendencia_empate": 0.95},
    "juventus": {"ataque": 1.50, "defesa": 0.80, "forma": 1.05, "tendencia_empate": 1.20},
    "ac milan": {"ataque": 1.65, "defesa": 1.05, "forma": 0.98, "tendencia_empate": 1.05},
    "flamengo": {"ataque": 1.85, "defesa": 0.85, "forma": 1.10, "tendencia_empate": 0.90},
    "palmeiras": {"ataque": 1.80, "defesa": 0.80, "forma": 1.08, "tendencia_empate": 0.95},
    "botafogo": {"ataque": 1.75, "defesa": 0.90, "forma": 1.05, "tendencia_empate": 1.00},
    "sao paulo": {"ataque": 1.40, "defesa": 0.95, "forma": 0.95, "tendencia_empate": 1.10},
    "corinthians": {"ataque": 1.30, "defesa": 1.05, "forma": 0.90, "tendencia_empate": 1.15},
    "fluminense": {"ataque": 1.45, "defesa": 1.10, "forma": 0.92, "tendencia_empate": 1.05},
    "crb": {"ataque": 1.25, "defesa": 1.10, "forma": 1.00, "tendencia_empate": 1.10},
    "botafogo sp": {"ataque": 1.10, "defesa": 1.20, "forma": 0.95, "tendencia_empate": 1.15},
}

def calcular_xg_avancado(time_casa: str, time_fora: str):
    casa_key = time_casa.strip().lower()
    fora_key = time_fora.strip().lower()
    
    stats_casa = ESTATISTICAS_TIMES.get(casa_key, {"ataque": 1.45, "defesa": 1.15, "forma": 1.00, "tendencia_empate": 1.00})
    stats_fora = ESTATISTICAS_TIMES.get(fora_key, {"ataque": 1.20, "defesa": 1.25, "forma": 1.00, "tendencia_empate": 1.00})
    
    fator_casa = 1.15
    
    xg_casa = (stats_casa["ataque"] + stats_fora["defesa"]) / 2 * fator_casa * stats_casa["forma"]
    xg_fora = (stats_fora["ataque"] + stats_casa["defesa"]) / 2 * stats_fora["forma"]
    fator_empate_h2h = (stats_casa["tendencia_empate"] + stats_fora["tendencia_empate"]) / 2
    
    return float(round(xg_casa, 2)), float(round(xg_fora, 2)), float(round(fator_empate_h2h, 2))

@app.get("/analisar")
def analisar(home: str, away: str):
    xg_casa, xg_fora, fator_h2h = calcular_xg_avancado(home, away)
    total_xg_esperado = float(round(xg_casa + xg_fora, 2))
    
    linha_gols = "Over 2.5" if total_xg_esperado >= 2.60 else ("Under 2.5" if total_xg_esperado <= 2.20 else "Neutro (2 a 3 gols)")
    
    max_gols = 5
    placares = []
    
    for c in range(max_gols + 1):
        for f in range(max_gols + 1):
            prob_c = float(poisson.pmf(c, xg_casa))
            prob_f = float(poisson.pmf(f, xg_fora))
            prob_total = prob_c * prob_f
            
            if c == f:
                prob_total *= fator_h2h
                
            gols_jogo = c + f
            if linha_gols == "Under 2.5" and gols_jogo > 3:
                prob_total *= 0.70
            elif linha_gols == "Over 2.5" and gols_jogo < 2:
                prob_total *= 0.75

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
