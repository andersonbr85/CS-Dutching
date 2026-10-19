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

    # --- HOLANDA (Eredivisie) ---
    "ajax": {"ataque": 2.10, "defesa": 0.90, "forma": 1.08, "tendencia_empate": 0.95},
    "psv": {"ataque": 2.30, "defesa": 0.80, "forma": 1.12, "tendencia_empate": 0.90},
    "feyenoord": {"ataque": 2.05, "defesa": 0.85, "forma": 1.10, "tendencia_empate": 0.92},
    "az alkmaar": {"ataque": 1.70, "defesa": 1.00, "forma": 1.02, "tendencia_empate": 1.00},
    "utrecht": {"ataque": 1.45, "defesa": 1.15, "forma": 1.00, "tendencia_empate": 1.05},

    # --- PORTUGAL (Primeira Liga) ---
    "benfica": {"ataque": 2.10, "defesa": 0.75, "forma": 1.12, "tendencia_empate": 0.90},
    "sporting": {"ataque": 2.20, "defesa": 0.75, "forma": 1.15, "tendencia_empate": 0.88},
    "fc porto": {"ataque": 2.00, "defesa": 0.78, "forma": 1.10, "tendencia_empate": 0.92},
    "braga": {"ataque": 1.65, "defesa": 1.05, "forma": 1.02, "tendencia_empate": 1.00},
    "vitoria guimaraes": {"ataque": 1.35, "defesa": 1.10, "forma": 1.00, "tendencia_empate": 1.05},

    # --- TURQUIA (Süper Lig) ---
    "galatasaray": {"ataque": 2.15, "defesa": 0.80, "forma": 1.12, "tendencia_empate": 0.90},
    "fenerbahce": {"ataque": 2.10, "defesa": 0.82, "forma": 1.10, "tendencia_empate": 0.92},
    "besiktas": {"ataque": 1.70, "defesa": 1.05, "forma": 1.00, "tendencia_empate": 1.00},
    "trabzonspor": {"ataque": 1.55, "defesa": 1.10, "forma": 0.98, "tendencia_empate": 1.05},

    # --- ARÁBIA SAUDITA (Saudi Pro League) ---
    "al hilal": {"ataque": 2.30, "defesa": 0.75, "forma": 1.15, "tendencia_empate": 0.85},
    "al nassr": {"ataque": 2.20, "defesa": 0.85, "forma": 1.12, "tendencia_empate": 0.90},
    "al ahli": {"ataque": 1.80, "defesa": 1.00, "forma": 1.05, "tendencia_empate": 0.98},
    "al ittihad": {"ataque": 1.85, "defesa": 0.95, "forma": 1.05, "tendencia_empate": 0.95},

    # --- SUÉCIA (Allsvenskan) ---
    "malmo ff": {"ataque": 1.80, "defesa": 0.85, "forma": 1.10, "tendencia_empate": 0.95},
    "aik": {"ataque": 1.40, "defesa": 1.05, "forma": 1.00, "tendencia_empate": 1.10},
    "djurgarden": {"ataque": 1.50, "defesa": 1.00, "forma": 1.02, "tendencia_empate": 1.05},

    # --- NORUEGA (Eliteserien) ---
    "bodo/glimt": {"ataque": 2.10, "defesa": 0.85, "forma": 1.12, "tendencia_empate": 0.90},
    "molde": {"ataque": 1.80, "defesa": 0.95, "forma": 1.05, "tendencia_empate": 0.98},
    "rosenborg": {"ataque": 1.50, "defesa": 1.10, "forma": 0.98, "tendencia_empate": 1.05},

    # --- DINAMARCA (Superliga) ---
    "fc copenhagen": {"ataque": 1.90, "defesa": 0.85, "forma": 1.08, "tendencia_empate": 0.95},
    "midtjylland": {"ataque": 1.85, "defesa": 0.90, "forma": 1.06, "tendencia_empate": 0.98},
    "brondby": {"ataque": 1.60, "defesa": 1.05, "forma": 1.00, "tendencia_empate": 1.02},

    # --- JAPÃO (J1 League) ---
    "vissel kobe": {"ataque": 1.65, "defesa": 0.90, "forma": 1.05, "tendencia_empate": 1.05},
    "sanfrecce hiroshima": {"ataque": 1.60, "defesa": 0.85, "forma": 1.04, "tendencia_empate": 1.08},
    "yokohama f marinos": {"ataque": 1.75, "defesa": 1.10, "forma": 1.00, "tendencia_empate": 1.00},

    # --- AUSTRÁLIA (A-League) ---
    "melbourne city": {"ataque": 1.70, "defesa": 1.10, "forma": 1.02, "tendencia_empate": 1.00},
    "sydney fc": {"ataque": 1.65, "defesa": 1.15, "forma": 1.00, "tendencia_empate": 1.02},

    # --- MLS (EUA / Canadá) ---
    "inter miami": {"ataque": 2.05, "defesa": 1.15, "forma": 1.10, "tendencia_empate": 0.90},
    "LA galaxy": {"ataque": 1.75, "defesa": 1.10, "forma": 1.05, "tendencia_empate": 0.98},
    "columbus crew": {"ataque": 1.80, "defesa": 0.95, "forma": 1.08, "tendencia_empate": 0.95},

    # --- EQUADOR ---
    "independiente del valle": {"ataque": 1.75, "defesa": 0.85, "forma": 1.08, "tendencia_empate": 0.98},
    "liga de quito": {"ataque": 1.70, "defesa": 0.90, "forma": 1.05, "tendencia_empate": 1.00},
    "barcelona sc": {"ataque": 1.60, "defesa": 0.95, "forma": 1.02, "tendencia_empate": 1.02},

    # --- COLÔMBIA ---
    "millonarios": {"ataque": 1.50, "defesa": 0.90, "forma": 1.02, "tendencia_empate": 1.10},
    "atletico nacional": {"ataque": 1.60, "defesa": 0.95, "forma": 1.05, "tendencia_empate": 1.05},
    "junior": {"ataque": 1.45, "defesa": 1.00, "forma": 1.00, "tendencia_empate": 1.08},

    # --- PARAGUAI ---
    "olimpia": {"ataque": 1.60, "defesa": 0.90, "forma": 1.05, "tendencia_empate": 1.05},
    "cerro porteno": {"ataque": 1.55, "defesa": 0.95, "forma": 1.02, "tendencia_empate": 1.05},
    "libertad": {"ataque": 1.65, "defesa": 0.88, "forma": 1.08, "tendencia_empate": 1.00},

    # --- URUGUAI ---
    "peñarol": {"ataque": 1.60, "defesa": 0.85, "forma": 1.05, "tendencia_empate": 1.05},
    "nacional": {"ataque": 1.58, "defesa": 0.88, "forma": 1.04, "tendencia_empate": 1.05},

    # --- CHILE ---
    "colocolo": {"ataque": 1.55, "defesa": 0.90, "forma": 1.05, "tendencia_empate": 1.05},
    "universidad de chile": {"ataque": 1.50, "defesa": 0.92, "forma": 1.02, "tendencia_empate": 1.08},
    "universidad catolica": {"ataque": 1.45, "defesa": 0.98, "forma": 1.00, "tendencia_empate": 1.05},

    # --- CHINA ---
    "shanghai port": {"ataque": 1.95, "defesa": 0.90, "forma": 1.10, "tendencia_empate": 0.95},
    "shandong taishan": {"ataque": 1.70, "defesa": 1.00, "forma": 1.02, "tendencia_empate": 1.02},

    # --- COREIA DO SUL ---
    "ulsan hyundai": {"ataque": 1.65, "defesa": 0.90, "forma": 1.05, "tendencia_empate": 1.05},
    "jeonbuk motors": {"ataque": 1.60, "defesa": 0.95, "forma": 1.02, "tendencia_empate": 1.05},

    # --- SUÍÇA ---
    "young boys": {"ataque": 1.85, "defesa": 1.00, "forma": 1.05, "tendencia_empate": 1.00},
    "basel": {"ataque": 1.60, "defesa": 1.05, "forma": 1.00, "tendencia_empate": 1.05},

    # --- ÁUSTRIA ---
    "red bull salzburg": {"ataque": 2.05, "defesa": 0.85, "forma": 1.10, "tendencia_empate": 0.90},
    "sturm graz": {"ataque": 1.65, "defesa": 0.95, "forma": 1.04, "tendencia_empate": 1.00},

    # --- BOLÍVIA ---
    "bolivar": {"ataque": 1.90, "defesa": 0.95, "forma": 1.10, "tendencia_empate": 0.95},
    "the strongest": {"ataque": 1.80, "defesa": 1.00, "forma": 1.05, "tendencia_empate": 1.00},

    # --- PERU ---
    "universitario": {"ataque": 1.55, "defesa": 0.85, "forma": 1.05, "tendencia_empate": 1.10},
    "alianza lima": {"ataque": 1.50, "defesa": 0.90, "forma": 1.02, "tendencia_empate": 1.08},
    "sporting cristal": {"ataque": 1.60, "defesa": 0.95, "forma": 1.04, "tendencia_empate": 1.05},

    # --- ESCÓCIA ---
    "celtic": {"ataque": 2.20, "defesa": 0.75, "forma": 1.15, "tendencia_empate": 0.85},
    "rangers": {"ataque": 2.05, "defesa": 0.80, "forma": 1.12, "tendencia_empate": 0.90},

    # --- IRLANDA ---
    "shamrock rovers": {"ataque": 1.60, "defesa": 0.90, "forma": 1.05, "tendencia_empate": 1.05},
    "st patrick's": {"ataque": 1.35, "defesa": 1.05, "forma": 1.00, "tendencia_empate": 1.10},

    # --- PAÍS DE GALES ---
    "the new saints": {"ataque": 2.10, "defesa": 0.75, "forma": 1.15, "tendencia_empate": 0.85},
    "connah's quay": {"ataque": 1.40, "defesa": 1.05, "forma": 1.00, "tendencia_empate": 1.10},
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
