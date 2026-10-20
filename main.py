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

# Base de dados global ampliada (Grandes Ligas + Ligas Internacionais de 1ª Divisão)
ESTATISTICAS_TIMES = {
    # --- INGLATERRA ---
    "arsenal": {"ataque": 2.15, "defesa": 0.70, "forma": 1.10, "tendencia_empate": 0.90},
    "manchester city": {"ataque": 2.40, "defesa": 0.75, "forma": 1.15, "tendencia_empate": 0.85},
    "liverpool": {"ataque": 2.25, "defesa": 0.80, "forma": 1.12, "tendencia_empate": 0.88},
    "chelsea": {"ataque": 1.70, "defesa": 1.05, "forma": 1.00, "tendencia_empate": 1.05},
    "tottenham": {"ataque": 1.80, "defesa": 1.20, "forma": 0.95, "tendencia_empate": 0.95},
    "manchester united": {"ataque": 1.55, "defesa": 1.15, "forma": 0.90, "tendencia_empate": 1.00},
    "aston villa": {"ataque": 1.75, "defesa": 1.10, "forma": 1.08, "tendencia_empate": 0.95},
    "newcastle": {"ataque": 1.65, "defesa": 1.15, "forma": 0.98, "tendencia_empate": 1.00},
    "coventry": {"ataque": 1.20, "defesa": 1.20, "forma": 1.00, "tendencia_empate": 1.10},

    # --- ESPANHA ---
    "real madrid": {"ataque": 2.45, "defesa": 0.70, "forma": 1.20, "tendencia_empate": 0.80},
    "barcelona": {"ataque": 2.35, "defesa": 0.75, "forma": 1.15, "tendencia_empate": 0.85},
    "atletico madrid": {"ataque": 1.60, "defesa": 0.80, "forma": 1.00, "tendencia_empate": 1.15},

    # --- ITÁLIA ---
    "inter milan": {"ataque": 1.95, "defesa": 0.75, "forma": 1.12, "tendencia_empate": 0.95},
    "juventus": {"ataque": 1.50, "defesa": 0.80, "forma": 1.05, "tendencia_empate": 1.20},
    "ac milan": {"ataque": 1.65, "defesa": 1.05, "forma": 0.98, "tendencia_empate": 1.05},

    # --- ALEMANHA ---
    "bayern munich": {"ataque": 2.60, "defesa": 0.80, "forma": 1.10, "tendencia_empate": 0.80},
    "dortmund": {"ataque": 1.90, "defesa": 1.25, "forma": 1.00, "tendencia_empate": 0.95},

    # --- FRANÇA ---
    "psg": {"ataque": 2.40, "defesa": 0.85, "forma": 1.10, "tendencia_empate": 0.90},
    "marseille": {"ataque": 1.65, "defesa": 1.05, "forma": 1.02, "tendencia_empate": 1.00},

    # --- BRASIL ---
    "flamengo": {"ataque": 1.85, "defesa": 0.85, "forma": 1.10, "tendencia_empate": 0.90},
    "palmeiras": {"ataque": 1.80, "defesa": 0.80, "forma": 1.08, "tendencia_empate": 0.95},
    "botafogo": {"ataque": 1.75, "defesa": 0.90, "forma": 1.05, "tendencia_empate": 1.00},
    "sao paulo": {"ataque": 1.40, "defesa": 0.95, "forma": 0.95, "tendencia_empate": 1.10},
    "corinthians": {"ataque": 1.30, "defesa": 1.05, "forma": 0.90, "tendencia_empate": 1.15},
    "fluminense": {"ataque": 1.45, "defesa": 1.10, "forma": 0.92, "tendencia_empate": 1.05},
    "crb": {"ataque": 1.20, "defesa": 1.10, "forma": 1.00, "tendencia_empate": 1.15},
    "botafogo sp": {"ataque": 1.00, "defesa": 1.15, "forma": 0.95, "tendencia_empate": 1.20},

    # --- ARGENTINA ---
    "river plate": {"ataque": 1.80, "defesa": 0.85, "forma": 1.10, "tendencia_empate": 0.95},
    "boca juniors": {"ataque": 1.65, "defesa": 0.90, "forma": 1.05, "tendencia_empate": 1.00},
    "newell's old boys": {"ataque": 1.15, "defesa": 1.05, "forma": 0.95, "tendencia_empate": 1.15},
    "central córdoba": {"ataque": 1.05, "defesa": 1.20, "forma": 0.90, "tendencia_empate": 1.15},

    # --- OUTROS ---
    "ajax": {"ataque": 2.10, "defesa": 0.90, "forma": 1.08, "tendencia_empate": 0.95},
    "psv": {"ataque": 2.30, "defesa": 0.80, "forma": 1.12, "tendencia_empate": 0.90},
    "feyenoord": {"ataque": 2.05, "defesa": 0.85, "forma": 1.10, "tendencia_empate": 0.92},
    "benfica": {"ataque": 2.10, "defesa": 0.75, "forma": 1.12, "tendencia_empate": 0.90},
    "sporting": {"ataque": 2.20, "defesa": 0.75, "forma": 1.15, "tendencia_empate": 0.88},
    "fc porto": {"ataque": 2.00, "defesa": 0.78, "forma": 1.10, "tendencia_empate": 0.92},
    "galatasaray": {"ataque": 2.15, "defesa": 0.80, "forma": 1.12, "tendencia_empate": 0.90},
    "fenerbahce": {"ataque": 2.10, "defesa": 0.82, "forma": 1.10, "tendencia_empate": 0.92},
    "al hilal": {"ataque": 2.30, "defesa": 0.75, "forma": 1.15, "tendencia_empate": 0.85},
    "al nassr": {"ataque": 2.20, "defesa": 0.85, "forma": 1.12, "tendencia_empate": 0.90},
    "inter miami": {"ataque": 2.05, "defesa": 1.15, "forma": 1.10, "tendencia_empate": 0.90},
    "celtic": {"ataque": 2.20, "defesa": 0.75, "forma": 1.15, "tendencia_empate": 0.85},
    "rangers": {"ataque": 2.05, "defesa": 0.80, "forma": 1.12, "tendencia_empate": 0.90},
}

def calcular_xg_avancado(time_casa: str, time_fora: str):
    casa_key = time_casa.strip().lower()
    fora_key = time_fora.strip().lower()
    
    stats_casa = ESTATISTICAS_TIMES.get(casa_key, {"ataque": 1.25, "defesa": 1.15, "forma": 1.00, "tendencia_empate": 1.00})
    stats_fora = ESTATISTICAS_TIMES.get(fora_key, {"ataque": 1.10, "defesa": 1.20, "forma": 1.00, "tendencia_empate": 1.00})
    
    fator_casa = 1.10
    
    xg_casa = (stats_casa["ataque"] + stats_fora["defesa"]) / 2 * fator_casa * stats_casa["forma"]
    xg_fora = (stats_fora["ataque"] + stats_casa["defesa"]) / 2 * stats_fora["forma"]
    fator_empate_h2h = (stats_casa["tendencia_empate"] + stats_fora["tendencia_empate"]) / 2
    
    return float(round(xg_casa, 2)), float(round(xg_fora, 2)), float(round(fator_empate_h2h, 2))

@app.get("/analisar")
def analisar(home: str, away: str):
    xg_casa, xg_fora, fator_h2h = calcular_xg_avancado(home, away)
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
            
    # Ordenar por maior probabilidade pura
    placares_ordenados = sorted(placares, key=lambda x: x["probabilidade"], reverse=True)
    
    # Pegamos os 4 placares mais prováveis do topo
    top_4 = placares_ordenados[:4]
    placares_ja_inclusos = {p["placar"] for p in top_4}
    
    # Seleção inteligente do 5º placar de proteção elástica:
    # Procuramos nos restantes o placar com maior elasticidade (soma de gols >= 3 ou variação de golo extra)
    # que tenha uma probabilidade viável para atuar como seguro de volatilidade.
    quinto_placar = None
    for item in placares_ordenados[4:]:
        gols_c, gols_f = map(int, item["placar"].split(" - "))
        # Consideramos como excelente proteção elástica placares de 3 gols ou mais (goleadas/jogos abertos)
        if (gols_c + gols_f) >= 3 or abs(gols_c - gols_f) >= 2:
            if item["placar"] not in placares_ja_inclusos:
                # Marcar visualmente que este é o placar de proteção/seguro
                item["descricao"] += " (🛡️ Proteção Elástica)"
                quinto_placar = item
                break
                
    # Fallback caso encontre todos muito restritos: pega simplesmente o 5º natural
    if not quinto_placar:
        quinto_placar = placares_ordenados[4]
        quinto_placar["descricao"] += " (🛡️ Proteção Elástica)"
        
    top_5 = top_4 + [quinto_placar]
    
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
