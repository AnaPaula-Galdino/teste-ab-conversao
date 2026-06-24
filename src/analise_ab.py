"""
Análise de Teste A/B — Estatística
Compara a conversão dos grupos com teste de hipótese, intervalo de confiança e uplift.
Autora: Ana Paula Galdino
"""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats
from statsmodels.stats.proportion import (proportions_ztest, proportion_confint,
                                          confint_proportions_2indep)

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(BASE, "imagens"); os.makedirs(IMG, exist_ok=True)
C = {"escuro":"#1f4e79","medio":"#2e6da4","claro":"#5b9bd5","suave":"#a6c8e0",
     "destaque":"#4fc3f7","cinza":"#d9d9d9","alerta":"#c0392b","verde":"#2e7d32"}
FONTE = "Experimento A/B de checkout  ·  Análise: Ana Paula Galdino"
plt.rcParams.update({"font.size":11,"font.family":"DejaVu Sans","axes.edgecolor":"#9aa7b8",
    "axes.grid":True,"grid.color":"#eef2f7","axes.axisbelow":True,"figure.dpi":120,"savefig.bbox":"tight"})
def rodape(fig): fig.text(0.01,0.005,FONTE,fontsize=7.5,color="#7a8aa0")

df = pd.read_csv(os.path.join(BASE,"dados","experimento_ab.csv"), parse_dates=["data"])
g = df.groupby("grupo")["converteu"].agg(["sum","count"])
sA, nA = int(g.loc["A","sum"]), int(g.loc["A","count"])
sB, nB = int(g.loc["B","sum"]), int(g.loc["B","count"])
pA, pB = sA/nA, sB/nB
# Teste de hipótese (duas proporções)
z, pval = proportions_ztest([sB, sA], [nB, nA], alternative="larger")
ciA = proportion_confint(sA, nA, method="wilson")
ciB = proportion_confint(sB, nB, method="wilson")
dif = pB - pA
dlo, dhi = confint_proportions_2indep(sB, nB, sA, nA, method="wald")
uplift_rel = dif / pA * 100

# 1) Conversão por grupo com IC
def g1():
    fig,ax=plt.subplots(figsize=(7.5,5))
    grupos=["A (controle)","B (nova)"]; vals=[pA*100,pB*100]
    err=[[(pA-ciA[0])*100,(pB-ciB[0])*100],[(ciA[1]-pA)*100,(ciB[1]-pB)*100]]
    ax.bar(grupos, vals, color=[C["cinza"],C["escuro"]], yerr=err, capsize=8,
           error_kw=dict(ecolor="#33414f", lw=1.5))
    for i,v in enumerate(vals): ax.text(i,v,f" {v:.1f}%",ha="center",va="bottom",fontsize=12,fontweight="bold")
    ax.set_title("Taxa de conversão por grupo (com IC 95%)",fontweight="bold",color=C["escuro"],fontsize=13,pad=10)
    ax.set_ylabel("Conversão (%)"); ax.set_ylim(0, max(vals)*1.25)
    rodape(fig); fig.savefig(os.path.join(IMG,"01_conversao_por_grupo.png")); plt.close(fig)

# 2) Significância: H0 e z observado
def g2():
    fig,ax=plt.subplots(figsize=(9,5))
    x=np.linspace(-4,5,400); y=stats.norm.pdf(x)
    ax.plot(x,y,color=C["escuro"],lw=2)
    ax.fill_between(x[x>=1.645], y[x>=1.645], color=C["alerta"], alpha=0.3, label="região crítica (α=5%)")
    ax.axvline(z, color=C["verde"], lw=2.5, label=f"z observado = {z:.2f}")
    ax.axvline(1.645, color=C["alerta"], ls="--", lw=1.2)
    ax.set_title(f"Teste de hipótese — p-valor = {pval:.4f}",fontweight="bold",color=C["escuro"],fontsize=13,pad=10)
    ax.set_xlabel("Estatística z (sob H0: sem diferença)"); ax.set_ylabel("Densidade"); ax.legend(frameon=True)
    rodape(fig); fig.savefig(os.path.join(IMG,"02_significancia.png")); plt.close(fig)

# 3) Conversão acumulada por dia
def g3():
    d=df.sort_values("data").copy()
    fig,ax=plt.subplots(figsize=(11,4.8))
    for grp,cor,lab in [("A",C["cinza"],"A (controle)"),("B",C["escuro"],"B (nova)")]:
        s=d[d["grupo"]==grp].groupby("data")["converteu"].agg(["sum","count"])
        acum=s["sum"].cumsum()/s["count"].cumsum()*100
        ax.plot(acum.index, acum.values, color=cor, lw=2.2, label=lab)
    ax.set_title("Conversão acumulada ao longo do experimento",fontweight="bold",color=C["escuro"],fontsize=13,pad=10)
    ax.set_ylabel("Conversão acumulada (%)"); ax.legend(frameon=True)
    rodape(fig); fig.savefig(os.path.join(IMG,"03_conversao_acumulada.png")); plt.close(fig)

# 4) Conversão diária
def g4():
    diaria=df.groupby(["data","grupo"])["converteu"].mean().unstack()*100
    fig,ax=plt.subplots(figsize=(11,4.8))
    ax.plot(diaria.index, diaria["A"], color=C["cinza"], lw=1.8, marker="o", ms=3, label="A (controle)")
    ax.plot(diaria.index, diaria["B"], color=C["escuro"], lw=1.8, marker="o", ms=3, label="B (nova)")
    ax.set_title("Conversão diária por grupo",fontweight="bold",color=C["escuro"],fontsize=13,pad=10)
    ax.set_ylabel("Conversão (%)"); ax.legend(frameon=True)
    rodape(fig); fig.savefig(os.path.join(IMG,"04_conversao_diaria.png")); plt.close(fig)

# 5) Conversão por dispositivo
def g5():
    tab=df.groupby(["dispositivo","grupo"])["converteu"].mean().unstack()*100
    x=np.arange(len(tab)); w=0.38
    fig,ax=plt.subplots(figsize=(8.5,5))
    ax.bar(x-w/2, tab["A"], w, label="A (controle)", color=C["cinza"])
    ax.bar(x+w/2, tab["B"], w, label="B (nova)", color=C["escuro"])
    ax.set_xticks(x); ax.set_xticklabels(tab.index)
    for i,(a,b) in enumerate(zip(tab["A"],tab["B"])):
        ax.text(i-w/2,a,f"{a:.1f}%",ha="center",va="bottom",fontsize=9)
        ax.text(i+w/2,b,f"{b:.1f}%",ha="center",va="bottom",fontsize=9)
    ax.set_title("Conversão por dispositivo e grupo",fontweight="bold",color=C["escuro"],fontsize=13,pad=10)
    ax.set_ylabel("Conversão (%)"); ax.legend(frameon=True); ax.set_ylim(0, tab.values.max()*1.2)
    rodape(fig); fig.savefig(os.path.join(IMG,"05_conversao_dispositivo.png")); plt.close(fig)

# 6) Uplift com IC
def g6():
    fig,ax=plt.subplots(figsize=(8.5,3.6))
    ax.errorbar([dif*100],[0], xerr=[[(dif-dlo)*100],[(dhi-dif)*100]], fmt="o", ms=12,
                color=C["verde"], ecolor=C["escuro"], elinewidth=2, capsize=8)
    ax.axvline(0, color=C["alerta"], ls="--", lw=1.4, label="sem efeito")
    ax.set_yticks([]); ax.set_xlabel("Diferença de conversão B − A (pontos percentuais)")
    ax.set_title(f"Uplift: +{dif*100:.1f} p.p. (+{uplift_rel:.0f}% relativo) — IC 95% acima de zero",
                 fontweight="bold",color=C["escuro"],fontsize=12,pad=10)
    ax.legend(frameon=True, loc="upper right")
    rodape(fig); fig.savefig(os.path.join(IMG,"06_uplift_ic.png")); plt.close(fig)

def resumo():
    return {"pA":pA*100,"pB":pB*100,"uplift_pp":dif*100,"uplift_rel":uplift_rel,
            "pvalor":pval,"z":z,"nA":nA,"nB":nB,
            "significativo": pval < 0.05, "ic_dif":(dlo*100,dhi*100)}

def main():
    for gf in (g1,g2,g3,g4,g5,g6): gf()
    r=resumo()
    print(f"A={pA*100:.1f}% B={pB*100:.1f}% | uplift +{dif*100:.1f}pp (+{uplift_rel:.0f}%) | z={z:.2f} p={pval:.4f} | signif={r['significativo']}")
    print("Gráficos:", sorted(x for x in os.listdir(IMG) if x.startswith("0")))
    return r

if __name__=="__main__":
    main()
