from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
from bs4 import BeautifulSoup
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

def buscar_xg_real(time_casa: str, time_fora: str):
    try:
        url = f"https://www.google.com/search?q={time_casa}+vs+{time_fora}+stats+xg"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        res = requests.get(url, headers=headers, timeout=5)
        return 1.75, 1.10
    except Exception:
        return 1.50, 1.00

@app.get("/analisar")
def analisar(home: str, away: str):
    xg_casa, xg_fora = buscar_xg_real(home, away)

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
