import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from relatorio_exec import construir
import analise_ab as A

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(BASE, "imagens")
def img(n): return os.path.join(IMG, n)
r = A.resumo()
verdito = "estatisticamente significativo" if r["significativo"] else "não significativo"

config = {
 "eyebrow": "RELATÓRIO DE EXPERIMENTO A/B",
 "titulo": "Teste A/B de Checkout",
 "subtitulo": "Avaliação estatística de uma nova versão de página — conversão e significância",
 "meta": "Ana Paula Galdino · Data Analytics (POSTECH/FIAP) · Junho de 2026",
 "fonte": "Experimento A/B de checkout  ·  Análise: Ana Paula Galdino",
 "sumario": [
   f"Testamos uma nova versão da página de checkout (grupo B) contra a atual (grupo A), com cerca de "
   f"<b>{r['nA']+r['nB']:,}</b> visitantes divididos entre os grupos. A versão B converteu "
   f"<b>{r['pB']:.1f}%</b> contra <b>{r['pA']:.1f}%</b> da versão A.".replace(",", "."),
   f"A diferença é <b>{verdito}</b>: uplift de <b>+{r['uplift_pp']:.1f} ponto percentual</b> "
   f"(<b>+{r['uplift_rel']:.0f}%</b> em termos relativos), com p-valor de <b>{r['pvalor']:.4f}</b> — "
   "bem abaixo do limite de 5%. Recomenda-se implementar a nova versão.",
 ],
 "kpis": [
   (f"{r['pA']:.1f}%", "conversão A (controle)"),
   (f"{r['pB']:.1f}%", "conversão B (nova)"),
   (f"+{r['uplift_rel']:.0f}%", "uplift relativo"),
   (f"{r['pvalor']:.4f}", "p-valor"),
 ],
 "secoes": [
   {"titulo": "1. O resultado principal",
    "texto": [
      "A nova versão (B) apresentou conversão maior que a atual (A). Os intervalos de confiança de 95% "
      "das duas taxas quase não se sobrepõem, o primeiro sinal de que a diferença é real e não acaso.",
      "Para confirmar, apliquei um teste de hipótese de duas proporções. A estatística z observada cai "
      "claramente na região crítica, e o p-valor fica muito abaixo de 5%.",
    ],
    "imagens": [(img("01_conversao_por_grupo.png"), "Conversão de cada grupo com intervalo de confiança"),
                (img("02_significancia.png"), "Teste de hipótese: z observado na região crítica")]},
   {"titulo": "2. Estabilidade ao longo do tempo",
    "texto": [
      "Um bom resultado de A/B precisa ser estável, não um pico de um dia. A conversão acumulada mostra "
      "que a vantagem da versão B se mantém e converge ao longo das semanas.",
      "A visão diária reforça: salvo a variação natural, a versão B fica consistentemente acima da A "
      "durante o experimento.",
    ],
    "imagens": [(img("03_conversao_acumulada.png"), "Conversão acumulada estabiliza com B acima"),
                (img("04_conversao_diaria.png"), "Conversão diária por grupo")]},
   {"titulo": "3. Onde o ganho acontece",
    "texto": [
      "Quebrar por dispositivo evita a Falácia de Simpson e mostra que o ganho não vem de um único nicho: "
      "a versão B melhora a conversão tanto no mobile quanto no desktop.",
      f"O tamanho do efeito, com intervalo de confiança inteiramente acima de zero, confirma o uplift de "
      f"<b>+{r['uplift_pp']:.1f} p.p.</b> como um resultado confiável para decidir.",
    ],
    "imagens": [(img("05_conversao_dispositivo.png"), "Ganho consistente em mobile e desktop"),
                (img("06_uplift_ic.png"), "Uplift com intervalo de confiança acima de zero")]},
 ],
 "conclusao_titulo": "Decisão e próximos passos",
 "conclusoes": [
   f"<b>Implementar a versão B:</b> o ganho de +{r['uplift_rel']:.0f}% é significativo e consistente.",
   "<b>Estimar o impacto:</b> aplicar o uplift sobre o volume mensal para projetar a receita incremental.",
   "<b>Monitorar pós-lançamento:</b> acompanhar a conversão real após o rollout para confirmar o efeito.",
   "<b>Próximo experimento:</b> testar novas hipóteses (ex.: formas de pagamento) a partir desta base.",
 ],
}

if __name__ == "__main__":
    construir(config, os.path.join(BASE, "Analise_Executiva_Teste_AB.pdf"))
