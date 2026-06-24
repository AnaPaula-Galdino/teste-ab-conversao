"""
Gera os dados de um teste A/B de página de checkout (30 dias).
Grupo A = controle, Grupo B = nova versão. Métrica: conversão.
Autora: Ana Paula Galdino
"""
import os
import numpy as np
import pandas as pd
from datetime import date, timedelta

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rng = np.random.default_rng(47)
inicio = date(2026, 5, 1)
dispositivos = ["Mobile", "Desktop"]
# conversão base por grupo e dispositivo
conv = {("A","Mobile"):0.108, ("A","Desktop"):0.142,
        ("B","Mobile"):0.131, ("B","Desktop"):0.160}
linhas = []
uid = 0
for d in range(30):
    dia = inicio + timedelta(days=d)
    n_dia = int(rng.integers(480, 620))   # visitantes/dia
    for _ in range(n_dia):
        uid += 1
        grupo = rng.choice(["A","B"])
        disp = rng.choice(dispositivos, p=[0.62, 0.38])
        p = conv[(grupo, disp)]
        converteu = int(rng.random() < p)
        linhas.append([uid, dia.isoformat(), grupo, disp, converteu])

df = pd.DataFrame(linhas, columns=["usuario_id","data","grupo","dispositivo","converteu"])
out = os.path.join(BASE, "dados", "experimento_ab.csv")
df.to_csv(out, index=False)
g = df.groupby("grupo")["converteu"].agg(["count","mean"])
print(f"Registros: {len(df)} -> {out}")
print(g)
