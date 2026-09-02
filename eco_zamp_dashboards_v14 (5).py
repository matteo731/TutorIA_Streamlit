# -*- coding: utf-8 -*-
"""
ECO ZAMP - GERADOR DE DASHBOARDS DE UTILIDADES v13 (Loja / Coordenador / Regional)

NOVIDADES v13.3 (4a rodada de revisao):
  10. Novos clusters de ranking de eficiencia (validados estatisticamente antes de criar):
      - BK: cluster 'KSK' para lojas convencionais (FC/FS/etc) que possuem quiosque
        SATELITE anexo aberto (Possui_KSK/Status_KSK da base Database-Utilities). Teste
        Mann-Whitney confirmou vies real (p=0,037): indice fisico mediano 0,96 vs 0,89 em
        lojas FC, porque o consumo do satelite fica embutido/rateado no BKN da loja mae e o
        modelo de previsao nao capta essa operacao extra. 219 lojas.
      - SBUX: cluster 'QUIOSQUE' para lojas cujo PROPRIO FORMATO e quiosque
        (formato_area=='KIOSK' no Cadastro_Lojas - campo que NAO existe no Fato_Loja_Recurso,
        precisou carregar a aba Cadastro_Lojas separadamente). 15 lojas.
      - PLK nao tem quiosque de nenhum tipo, sem cluster novo.
  11. Bloco Acao (simulacao de subida de bandeira) REDESENHADO: antes reduzia o indice das
      lojas priorizadas (por terem 'piorado' vs mes anterior) ate a MEDIANA GENERICA da
      rede (p50), sem relacao com nenhuma fronteira de bandeira real. Agora: ordena por
      loja mais ineficiente da carteira (indice atual, sem priorizar quem piorou), e simula
      cada uma subindo a PROPRIA bandeira individual (fronteira real do cluster dela: marca +
      exposicao ao sol/KSK/Quiosque), ate a carteira cruzar a fronteira da proxima bandeira do
      grupo. O texto cita um exemplo concreto (ex: "loja X sairia da bandeira D para D+,
      indice de 120% para 117%"). Corrigido tambem um bug de implementacao: a bandeira
      individual da loja NUNCA pode ser recalculada com uma serie de 1 elemento so (qcut com
      n=1 sempre cai na melhor faixa) - agora usa as fronteiras ja calculadas do cluster
      inteiro (bandeiras_por_cluster) para posicionar a loja corretamente.
  12. Comparacao entre lojas: tolerancia de area de vendas apertada de +-30% para +-10%
      (validado: cobertura final identica, 99,2%, porque o relaxamento progressivo absorve
      o aperto; mas pares no nivel mais restrito ficam bem mais justos - pares com diferenca
      de area <=10% sobe de 34,4% para 81,1% dos casos).

NOVIDADES v13.2 (3a rodada de revisao):
  8. Tabelas de lojas trocadas de 'PIORARAM/MELHORARAM o indice' (variacao vs mes anterior)
     para 'OFENSORAS/EFICIENTES' pelo NIVEL de indice atual (ofensora = indice > 100% =
     consome acima do esperado AGORA). Motivo: verificado em 12 lojas que ranquear por
     variacao descolava do consumo (3/11 incoerentes: loja 'piorava' mas estava abaixo do
     esperado). Ranquear por nivel atual da correlacao 100% (14/14 lojas coerentes) e alinha
     com a simulacao de subida de bandeira, que ja usava nivel atual. Mostra o indice da loja
     (100% = na meta). Mesma logica para os setores do Regional.
  9. Grafico de consumo excedente volta a mostrar CONSUMO FISICO (kWh/m3/kg) + % acima do
     esperado (em vez de R$), ranqueado por %. Motivo: o usuario quer que a loja veja o
     consumo fisico dela (acionavel no dia a dia). A correlacao com o indice se mantem porque
     custo_equivalente = consumo x tarifa FIXA, entao % acima em consumo == % acima em custo.
     O card financeiro do topo (ACIMA DO ORCADO em R$) permanece como resumo executivo.

NOVIDADES v13.1 (mesma versao v13, correcoes da 2a rodada de revisao):
  5. OBJETIVO CENTRAL redefinido com o usuario (3 personas, debate ate convergencia):
     coordenador/gerente devem olhar a loja que mais piorou o indice e IMEDIATAMENTE ver
     em qual utility (agua/energia/gas) ela estourou, para acionar o gerente da loja.
     Causa raiz do problema antigo: o grafico de acao usava consumo_previsto (ML) vs
     orcado_ajustado_rs (financeiro/rateios), uma base TOTALMENTE diferente do indice
     (custo_equivalente real/previsto, consumo x tarifa fixa) - as duas divergiam em ate
     56x, entao a loja que mais piorava o indice podia aparecer com consumo ABAIXO do
     orcado, sem correlacao nenhuma. CORRIGIDO: o grafico agora e 'R$ acima do esperado
     por utility', usando a MESMA BASE do indice (custo_equivalente_real menos
     custo_equivalente_previsto_score_rs). Por construcao matematica, indice>100% agora
     implica excesso positivo em pelo menos 1 utility, e o R$ ja embute o peso real de
     cada utility na despesa (energia ~50%, gas ~30%, agua ~20%) sem ponderacao manual.
  6. BUGFIX bandeira do grupo (Coordenador/Regional): a bandeira era calculada misturando
     TODAS as marcas (BK/PLK/SBUX) na mesma regua de percentil, entao um regional podia
     cair de bandeira so por existir regional de outra marca com indice estruturalmente
     melhor (SBUX nao tem gas, por exemplo), mesmo sendo o 1o colocado da PROPRIA marca
     (caso real: benigno.carcereri, 1o entre 11 regionais BK, caia para B+ so por
     comparacao indevida com SBUX/PLK). Corrigido: bandeira do grupo agora e calculada
     SEPARADA POR MARCA, mesmo padrao ja usado nas bandeiras de loja.
  7. BUGFIX flag REVISAR_FINANCEIRO_GD_CONSUMO_FISICO_PRESERVADO (energia solar/GD): o
     proprio nome do flag diz que o consumo FISICO foi preservado (confiavel), so o
     FINANCEIRO (SAP) diverge por causa de geracao distribuida. A funcao dado_fragil()
     tratava esse flag igual aos genuinamente fisicos-suspeitos (REVISAR_ALTO_VS_
     REFERENCIAS etc) e descartava a linha inteira dos graficos de acao - escondendo
     sistematicamente as lojas com GD solar (que pesam mais em energia) da correlacao
     indice x utility. Agora dado_fragil() so exclui flags genuinamente fisicos; uma
     funcao nova fragil_financeiro() cobre o caso GD/SAP para quem precisar dele.

NOVIDADES v13 (sobre a v12):
  1. Leitura ALTA implausivel (energia/gas): regua trocada de '4x mediana da MARCA' para
     '5x mediana dos OUTROS meses da PROPRIA loja + isolado' (nenhum mes vizinho no mesmo
     patamar). A regua antiga punia lojas estruturalmente grandes (consumo real alto
     recorrente) e deixava passar mudancas de patamar permanentes. A nova so pega erro de
     leitura pontual e inequivoco (67 casos vs 15 antes), validado por analise de series
     reais (ex: 17782 tinha mudanca de patamar real de ~1000 para ~10000 kWh/mes, que a
     regua antiga teria corrigido errado).
  2. SETOR agora vem da base oficial 'Database - Utilities' (coluna Setor / Regional_Operacao),
     nao mais do campo 'Regional' do de-para (que e a Regional inteira, identica p/ todas as
     lojas de um gerente = nao subdividia nada). Corrige: tabela 'Setores que PIORARAM/
     MELHORARAM' vazia, grifadas erradas, l\u00f3gica setor->loja no Regional. Arquivo NOVO
     obrigatorio: PATH_SETOR (script para com erro claro se nao encontrar).
  3. GRIFO consistente entre tabela de indice e os 3 graficos de consumo: toda loja grifada
     agora aparece OBRIGATORIAMENTE nos 3 graficos (energia/agua/gas), mesmo sem dado valido
     naquele recurso especifico (mostra 'sem dado confiavel neste recurso').
  4. Numeracao (asterisco) nas lojas de 'PIORARAM/MELHORARAM o indice' para cruzar com os
     graficos de consumo (mesmo numero = mesma loja). No Regional a numeracao e feita
     APOS o filtro de 1 loja por setor e e sequencial (sem lacunas).

NOVIDADES v12 (sobre a v11):
  1. INDICE OFICIAL UNICO com correcao de leitura implausivel, na fonte (rk), afetando
     TUDO (bandeira, ranking, escadinha, promotoras/detratoras, simulacao, os 2 graficos):
       - Consumo fantasma BAIXO (medidor parado): substitui o custo-equivalente real do
         recurso pela MEDIANA do custo-equivalente real dos meses BONS da propria loja.
       - Leitura ALTA implausivel (SO energia/gas): consumo > 4x previsto E > 4x mediana
         da marca -> mesma substituicao pela mediana da propria loja. Agua fica de fora
         (estouro de agua costuma ser vazamento real, ja capturado pelos alertas).
       - Recurso sem nenhum mes bom: baixo sai da conta; loja com todos recursos fantasma
         no mes -> sem indice (fora do ranking, 'sob revisao').
     Resolve o bug da 15173 (indice caia artificialmente por medidor quebrado) e alinha os
     2 graficos de 12 meses (mesmos meses, mesma logica).
  2. Coordenador/Regional: removidas as tabelas 'Lojas a cobrar'. As lojas ofensoras
     (GRIFADAS = uniao de 'pioraram o indice' + 'lojas da simulacao de subida de bandeira')
     aparecem destacadas nas tabelas de indice E nos graficos de 'Consumo acima do orcado'
     (energia e agua), com inclusao forcada mesmo fora do top-10.
  3. Regional: novas tabelas 'Setores que PIORARAM/MELHORARAM o indice' (variacao do indice
     medio do setor vs mes anterior); nas tabelas de lojas mostra 1 loja (a mais ofensora)
     por setor.
  4. Layout: meta + parabens a direita da escadinha; 'Acao' logo abaixo; PIORARAM a esquerda
     e MELHORARAM a direita; variacao do indice medio embutida no card 'INDICE MEDIO 12M';
     alertas de energia (esq) e agua (dir) lado a lado com titulo novo de energia; removidos
     'Pontos de Atencao do Mes', 'O que puxou seu indice' e a comparacao de setor redundante.

COMO RODAR
  1) pip install pandas openpyxl pyarrow requests
  2) Ajuste CAMINHOS e MES_REFERENCIA na secao CONFIG.
  3) python eco_zamp_dashboards.py
  4) Abra os HTML na pasta de saida (Downloads/dashboards_eco_zamp).
TEMPO: 1o run ~50s (cria cache); runs seguintes ~3-6s.
SEGURANCA: defina a env var ECOZAMP_SMTP_PASS localmente (nunca hardcode a senha).

INDICE DE CONSUMO POR META = custo-equivalente real (corrigido) / previsto (tarifa de
referencia fixa). Menor = melhor. 100% = na meta. Bandeira em faixas por cluster.
Despesa em R$ dos cards usa SAP (realizado_sap_rs) com fallback; o INDICE nao usa SAP.
"""
import os, time, json, unicodedata
from datetime import datetime
from urllib.parse import quote
import pandas as pd
import numpy as np

# ============================ CONFIG ============================
PATH_DEPARA    = r"C:\Users\matteo.onofrio\Downloads\de_para_roteamento (2).xlsx"
PATH_FATURA    = r"C:\Users\matteo.onofrio\Downloads\base_fatura_bi_latest.xlsx"
PATH_ORCAMENTO = r"C:\Users\matteo.onofrio\Downloads\DadosOrcamento_Database_Enriquecido_v6_classificado.xlsx"
PATH_HIST      = r"C:\Users\matteo.onofrio\Downloads\Consumo_Utilities_com_Tipo.xlsx"
PATH_ALERTA_MADRUGADA = r"C:\Users\matteo.onofrio\Downloads\Alerta_Alto_Consumo_P75.xlsx"
PATH_VAZAMENTO_AGUA   = r"C:\Users\matteo.onofrio\Downloads\Provavel_Vazamento_Agua.xlsx"
PATH_SETOR            = r"C:\Users\matteo.onofrio\Downloads\Database - Utilities 13-05.xlsx"  # coluna Setor/Regional_Operacao (obrigatorio p/ Regional)
DIA_HOJE_ALERTA = None  # None = usa o ultimo dia com dado na planilha; ou fixe um dia (ex: 1 = dia 01)
ALERTAS = {}  # bkn -> alertas de madrugada/vazamento (carregado no main)
SETOR_MAP = {}    # bkn -> setor (carregado no main, da base Database - Utilities)
REGIONAL_OP_MAP = {}  # bkn -> Regional_Operacao
KSK_MAP = {}  # bkn (BK) -> True se possui quiosque satelite ABERTO (v13.3)
QUIOSQUE_MAP = {}  # bkn (SBUX) -> True se a loja E quiosque (formato_area==KIOSK, v13.3)
ORCAMENTO_ERRADO = {}  # (bkn,recurso) -> mediana consumo_real (previsto corrigido; v13.2)
DIVERGENCIA_SAP = set()  # (bkn,recurso) com despesa cronicamente divergente do P&L

MES_REFERENCIA = "2026-07"
MODO_VALIDACAO = True
QTD_EXEMPLOS   = 3
ENVIAR_EMAIL   = False

SMTP_HOST = "smtp.office365.com"
SMTP_PORT = 587
SMTP_USER = "report.utilities@zamp.com.br"
SMTP_PASS = os.environ.get("ECOZAMP_SMTP_PASS", "")  # NUNCA hardcode. Defina a env var ECOZAMP_SMTP_PASS localmente.
SMTP_FROM = "report.utilities@zamp.com.br"

PASTA_SAIDA = os.path.join(os.path.expanduser("~"), "Downloads", "dashboards_eco_zamp")
PASTA_CACHE = os.path.join(os.path.expanduser("~"), "Downloads", "_cache_eco_zamp")
USAR_CACHE  = True

# Bandeira: 8 faixas do melhor (A+) ao pior (D)
BANDEIRAS = ["A+","A","B+","B","C+","C","D+","D"]

# Esquemas de faixa por tamanho do cluster (Bloco 4)
BANDEIRAS_8 = ["A+","A","B+","B","C+","C","D+","D"]
BANDEIRAS_5 = ["A","B","C","D","E"]
BANDEIRAS_3 = ["A","B","C"]
def esquema_faixas(n_lojas):
    if n_lojas>=40: return BANDEIRAS_8
    if n_lojas>=15: return BANDEIRAS_5
    return BANDEIRAS_3

# Cluster de exposicao ao sol (Bloco 4):
#  BK/PLK -> por tipo_loja ; SBUX -> por tipo_area
_BK_RUA={"FS","ILR"}                         # exposta ao sol
_BK_EMPREEND={"FC","ILS","EX","KSK"}         # coberta
_SBUX_RUA={"STREET","HIGHWAY","UNIVERSITY"}
_SBUX_AERO={"AIRPORT"}
def cluster_sol(marca, tipo_loja, tipo_area, bkn=None):
    """v13.3: alem de Rua/Empreendimento/Aeroporto, agora reconhece:
    - SBUX: cluster 'QUIOSQUE' quando tipo_area==Quiosque (loja cujo PROPRIO FORMATO e
      quiosque, ~15 lojas na rede) - checado ANTES dos demais clusters SBUX.
    - BK: cluster 'KSK' quando a loja (convencional, ex FC/FS) POSSUI um quiosque SATELITE
      anexo aberto (KSK_MAP, da base Database-Utilities), pois isso gera vies estrutural
      real e mensuravel no indice fisico (validado: p=0,037, indice mediano 0,96 vs 0,89
      em lojas FC). E um conceito DIFERENTE do SBUX (satelite anexo, nao formato proprio).
    bkn e opcional (None mantem o comportamento antigo, sem split de KSK)."""
    marca=str(marca).upper(); tl=str(tipo_loja).upper(); ta=str(tipo_area).upper()
    if marca=="SBUX":
        if bkn is not None and QUIOSQUE_MAP.get(str(bkn), False): return "QUIOSQUE"
        if ta in _SBUX_RUA: return "RUA"
        if ta in _SBUX_AERO: return "AEROPORTO"
        return "EMPREENDIMENTO"
    if marca=="PLK":
        return "EMPREENDIMENTO"
    # BK (e default)
    if bkn is not None and KSK_MAP.get(str(bkn), False):
        return "KSK"
    if tl in _BK_RUA: return "RUA"
    return "EMPREENDIMENTO"

def texto_cluster(marca, cluster):
    """Frase que explica o ranking, conforme a marca e o cluster."""
    marca=str(marca).upper()
    if marca=="PLK":
        return "comparacao apenas entre lojas de shopping"
    if marca=="BK":
        if cluster=="KSK": return "comparacao apenas entre lojas que possuem quiosque satelite anexo"
        if cluster=="RUA": return "comparacao apenas entre lojas de rua"
        return "comparacao apenas entre lojas de shopping, mercados e dentro de empreendimentos"
    if marca=="SBUX":
        if cluster=="QUIOSQUE": return "comparacao apenas entre lojas quiosque"
        if cluster=="RUA": return "comparacao apenas entre lojas de rua e universidade"
        if cluster=="AEROPORTO": return "comparacao apenas entre lojas de aeroporto"
        return "comparacao apenas entre lojas de shopping, escritorio e dentro de empreendimentos"
    return "comparacao entre lojas semelhantes"
MIN_LOJAS_COORD = 3
MIN_LOJAS_REG   = 5
BANDEIRA_EXEMPLO = "BK"

# ============================ PALETA ============================
COR = {"azul":"#1F3A5F","laranja":"#e78a2d","verde":"#1a7a45","verde_bg":"#e4f5e9",
       "vermelho":"#c0392b","vermelho_bg":"#fce4e4","amarelo_bg":"#fff8ef","cinza":"#6b7a8d",
       "cinza_bg":"#f6f8fb","borda":"#dde3ea","texto":"#1f2b3a","cinza_claro":"#9aa7b5",
       "grifo":"#ffe27a","grifo_borda":"#e0b400"}  # grifo (highlight) das lojas ofensoras
UNIDADE = {"ENERGIA":"kWh","AGUA":"m3","GAS":"kg"}
ROTULO  = {"ENERGIA":"Energia","AGUA":"Agua","GAS":"Gas (GLP)"}
COR_REC = {"ENERGIA":"#e78a2d","AGUA":"#2d7de7","GAS":"#e7452d"}
# escala de 10 cores (5 vermelhos fortes->fracos, 5 verdes fracos->fortes)
ESCALA10 = ["#c0392b","#d5544a","#e07b6f","# eaa398","#f2cabf",
            "#cfe8d6","#a9d9b8","#7cc99a","#4db97b","#1a7a45"]
ESCALA10 = [c.replace(" ","") for c in ESCALA10]
POPPINS = "'Poppins','Segoe UI',Arial,sans-serif"

# ============================ UTILS ============================
def log(m): print(f"[{datetime.now().strftime('%H:%M:%S')}] {m}")
def safe_name(s):
    s = unicodedata.normalize("NFKD", str(s)).encode("ASCII","ignore").decode()
    for ch in ' /\\:@.': s = s.replace(ch,"_")
    return s
def brl(v):
    try: return "R$ " + f"{int(round(v)):,}".replace(",",".")
    except: return "R$ 0"
def num(v):
    try: return f"{int(round(v)):,}".replace(",",".")
    except: return "0"
def bkn_de_chave(c):
    s=str(c); return s.split(":")[1] if ":" in s else s

# ============================ CARGA ============================
COLS_FATURA=["competencia","bkn","recurso","bandeira","nome","cidade","estado","regional",
  "tipo_loja","tipo_area","status_periodo","consumo_real","consumo_previsto","realizado_sap_rs","valor_real_rs",
  "tarifa_real","unidade_consumo","flag_qualidade_consumo","orcado_ajustado_rs","trafego_real",
  "consumo_orcado_energia_ar_condicionado_kwh","tarifa_conversao_ar_condicionado_rs_kwh",
  "custo_equivalente_real_score_rs","custo_equivalente_previsto_score_rs","area_vendas_m2"]
COLS_COMPARAVEIS=["competencia","chave_loja","nome","regional","score_composto",
  "posicao_regional_mes","total_regional_mes","nome_comparavel","regional_comparavel",
  "trafego_comparavel","indice_eficiencia_mes_loja","indice_eficiencia_mes_comparavel",
  "economia_potencial_indice_mes"]
COLS_RANKING=["competencia","chave_loja","indice_eficiencia_mes",
  "custo_equivalente_real_score_rs","custo_equivalente_previsto_score_rs"]

def _cache(n): return os.path.join(PASTA_CACHE, n+".parquet")
def carregar_aba(path, sheet, usecols, nome):
    c=_cache(nome)
    if USAR_CACHE and os.path.exists(c):
        try:
            if os.path.getmtime(c)>=os.path.getmtime(path):
                df=pd.read_parquet(c)
                # auto-invalida se as colunas pedidas mudaram desde que o cache foi gravado
                if usecols is None or set(usecols).issubset(set(df.columns)):
                    log(f"  cache: {nome}"); return df
                log(f"  cache {nome} desatualizado (colunas mudaram): relendo")
        except: pass
    log(f"  lendo xlsx: {sheet} (1o run demora)")
    df=pd.read_excel(path, sheet_name=sheet, usecols=usecols)
    if USAR_CACHE:
        os.makedirs(PASTA_CACHE, exist_ok=True)
        try: df.to_parquet(c, index=False)
        except Exception as e: log(f"  (aviso) cache {nome}: {e}")
    return df

def corrigir_indice_por_mediana(flr, rk):
    """INDICE OFICIAL UNICO com correcao de consumo fantasma (v12).

    Um recurso fantasma (leitura implausivel, Regra A) faz o custo-equivalente real
    daquele recurso despencar. Como a meta (previsto) segue somando os 3 recursos, o
    indice cai artificialmente e a loja parece eficiente sem ter feito nada.

    Correcao (dois lados, mesmo tratamento):
    - Consumo fantasma BAIXO (Regra A): consumo implausivelmente baixo (medidor parado).
    - Leitura ALTA implausivel (v12, SO energia e gas): consumo > 4x previsto E > 4x a
      mediana da marca. Agua fica de fora de proposito (estouros de agua costumam ser
      vazamento real, que os alertas ja capturam; perdoar mascararia o problema).
    Em ambos os casos substitui o custo-equivalente REAL do recurso pela MEDIANA do
    custo-equivalente real dos meses BONS (nem baixos nem altos) da propria loja. Depois
    recalcula o indice = real/previsto e sobrescreve no rk (alimenta TUDO: bandeira,
    ranking, escadinha, promotoras/detratoras, simulacao e os 2 graficos de 12 meses).

    Regras de borda (confirmadas):
    - Recurso a corrigir SEM nenhum mes bom na loja: mantem como esta (o baixo sai da
      conta; o alto raramente ocorre sem historico).
    - Loja com TODOS os recursos fantasma no mes: fica sem indice (NaN) -> fora do
      ranking, card 'sob revisao'.
    """
    t=time.time()
    f=flr[flr["status_periodo"]=="FECHADO_COM_REAL"].copy()
    for c in ["consumo_real","consumo_previsto","custo_equivalente_real_score_rs",
              "custo_equivalente_previsto_score_rs"]:
        f[c]=pd.to_numeric(f[c],errors="coerce")
    # mediana marca+recurso (mesmo criterio das outras Regras A do codigo)
    medb=f[f["consumo_real"]>0].groupby(["marca","recurso"])["consumo_real"].median().to_dict()
    f["_fant"]=f.apply(lambda r: consumo_fantasma(r["consumo_real"], r["consumo_previsto"],
                                                  medb.get((r["marca"], r["recurso"]))), axis=1)
    # leitura ALTA implausivel (SO energia/gas), regua final (consenso 3 especialistas):
    #  (a) consumo do mes > ALTO_FATOR_LOJA x mediana dos OUTROS meses da propria loja, E
    #  (b) ISOLADO: nenhum mes vizinho (anterior/posterior) tambem estoura (senao e mudanca
    #      de patamar ou padrao real, nao erro de leitura).
    # Base: mediana da PROPRIA loja (nao da marca) - so isso separa erro de consumo alto real.
    altos=set()  # (bkn,recurso,competencia_ts) marcados como leitura alta implausivel
    fe=f[(f["consumo_real"]>0) & (f["recurso"].isin(["ENERGIA","GAS"]))]
    for (b,rec),sub in fe.groupby(["bkn","recurso"]):
        if len(sub)<4: continue  # precisa de historico p/ saber o normal da loja
        vals=sub.set_index("competencia")["consumo_real"].sort_index()
        idx=list(vals.index)
        for i,(comp,v) in enumerate(vals.items()):
            outros=vals.drop(comp)
            med=outros.median()
            if med<=0 or v <= ALTO_FATOR_LOJA*med: continue
            viz=[]
            if i>0: viz.append(vals.iloc[i-1])
            if i<len(vals)-1: viz.append(vals.iloc[i+1])
            if not any(x > ALTO_FATOR_LOJA*med for x in viz):  # isolado
                altos.add((b,rec,comp))
    f["_alto"]=f.apply(lambda r: (r["bkn"],r["recurso"],r["competencia"]) in altos, axis=1)
    # ORCAMENTO cronicamente errado (v13.2, SO energia/gas): quando a mediana da razao
    # consumo_real/consumo_previsto ao longo dos meses > ORCADO_RAZAO_MAX, o PREVISTO esta
    # quebrado (denominador errado, nao o consumo). Ex: loja com solar cujo previsto capturou
    # so o consumo liquido (~260 kWh) enquanto o real e ~10000 kWh, dando indice de 3700%.
    # Correcao: substitui consumo_previsto pela MEDIANA do consumo_real da propria loja
    # (todos os meses fechados) -> custo_previsto corrigido = mediana(real) x tarifa_orcada.
    # Diferente das outras 2 regras: estas corrigem o REAL (numerador); esta corrige o
    # PREVISTO (denominador).
    orc_errado={}  # (bkn,recurso) -> mediana do consumo_real (novo previsto fisico)
    fe2=f[(f["consumo_real"]>0)&(f["consumo_previsto"]>0)&(f["recurso"].isin(["ENERGIA","GAS"]))]
    for (b,rec),sub in fe2.groupby(["bkn","recurso"]):
        razao_med=(sub["consumo_real"]/sub["consumo_previsto"]).median()
        if razao_med>ORCADO_RAZAO_MAX:
            orc_errado[(b,rec)]=float(sub["consumo_real"].median())
    global ORCAMENTO_ERRADO
    ORCAMENTO_ERRADO=dict(orc_errado)  # exposto p/ rank_consumo (previsto fisico corrigido)
    # tarifa orcada por (bkn,recurso,mes) para reconstruir custo_previsto corrigido
    def _prev_corr(r):
        key=(r["bkn"],r["recurso"])
        if key not in orc_errado: return r["custo_equivalente_previsto_score_rs"]
        cp=r["custo_equivalente_previsto_score_rs"]; pv=r["consumo_previsto"]
        if pd.notna(cp) and pd.notna(pv) and pv>0:
            tarifa=cp/pv  # tarifa orcada implicita
            return orc_errado[key]*tarifa   # mediana(real) x tarifa
        return cp
    f["_prev_corr"]=f.apply(_prev_corr, axis=1)
    # linhas a substituir por mediana da propria loja: baixo OU alto
    f["_subst"]=f["_fant"] | f["_alto"]
    # mediana do custo-equiv real dos meses BONS (nem baixo nem alto), por (bkn,recurso)
    ok=f[(~f["_subst"]) & f["custo_equivalente_real_score_rs"].notna()]
    med_real=ok.groupby(["bkn","recurso"])["custo_equivalente_real_score_rs"].median().to_dict()

    # custo real corrigido por linha (recurso)
    def _real_corr(r):
        if not r["_subst"]:
            return r["custo_equivalente_real_score_rs"]
        m=med_real.get((r["bkn"], r["recurso"]))
        if m is not None:
            return m
        # sem mediana: baixo sai da soma (None); alto sem historico mantem o proprio valor
        return None if r["_fant"] else r["custo_equivalente_real_score_rs"]
    f["_real_corr"]=f.apply(_real_corr, axis=1)
    # marca linhas que continuam sem valor (baixo sem mediana) p/ saber se a loja-mes tem recurso valido
    f["_ainda_fant"]=f["_subst"] & f["_real_corr"].isna()

    # agrega por loja-mes: soma real corrigido (ignora recurso sem mediana) e previsto de recursos considerados
    def _agg(g):
        # recursos que entram: os nao-fantasma + os fantasma-corrigidos (com mediana)
        entra=g[~g["_ainda_fant"]]
        real=entra["_real_corr"].dropna().sum()
        prev=entra["_prev_corr"].dropna().sum()   # previsto corrigido p/ orcamento errado
        n_val=entra["_real_corr"].notna().sum()
        return pd.Series({"real_corr":real,"prev_corr":prev,"n_val":n_val})
    agg=f.groupby(["bkn","competencia"]).apply(_agg).reset_index()
    # indice corrigido: real/prev quando ha >=1 recurso valido e previsto>0; senao NaN (sob revisao)
    agg["indice_corrigido"]=np.where((agg["n_val"]>0)&(agg["prev_corr"]>0),
                                     agg["real_corr"]/agg["prev_corr"], np.nan)

    # sobrescreve no rk
    rk=rk.merge(agg[["bkn","competencia","real_corr","prev_corr","indice_corrigido"]],
                on=["bkn","competencia"], how="left")
    # onde houve recalculo, usa o corrigido; senao mantem o original (meses sem flr fechado)
    rk["indice_eficiencia_mes"]=rk["indice_corrigido"].where(rk["indice_corrigido"].notna()
                                                             | rk["real_corr"].notna(),
                                                             rk["indice_eficiencia_mes"])
    rk["custo_equivalente_real_score_rs"]=rk["real_corr"].where(rk["real_corr"].notna(),
                                                    rk["custo_equivalente_real_score_rs"])
    rk["custo_equivalente_previsto_score_rs"]=rk["prev_corr"].where(rk["prev_corr"].notna(),
                                                    rk["custo_equivalente_previsto_score_rs"])
    rk=rk.drop(columns=["real_corr","prev_corr","indice_corrigido"])
    n_baixo=int((f["_fant"] & f["_real_corr"].notna()).sum())
    n_alto=int((f["_alto"] & f["_real_corr"].notna()).sum())
    n_semind=int((agg["indice_corrigido"].isna()).sum())
    log(f"  indice corrigido em {time.time()-t:.1f}s; baixo(fantasma): {n_baixo}, "
        f"alto(energia/gas): {n_alto}; orcamento errado (loja-recurso): {len(orc_errado)}; "
        f"loja-mes sem indice: {n_semind}")
    return rk

def carregar_tudo():
    t=time.time(); log("Carregando bases...")
    flr=carregar_aba(PATH_FATURA,"Fato_Loja_Recurso",COLS_FATURA,"fato_loja")
    cmp=carregar_aba(PATH_FATURA,"Comparaveis_Loja",COLS_COMPARAVEIS,"comparaveis")
    rk =carregar_aba(PATH_FATURA,"Ranking_Loja",COLS_RANKING,"ranking")
    dp =carregar_aba(PATH_DEPARA,"Roteamento",None,"depara")
    for df in (flr,cmp,rk): df["competencia"]=pd.to_datetime(df["competencia"])
    # 'bandeira' na fatura = MARCA (BK/PLK/SBUX); renomeia p/ nao colidir com bandeira de eficiencia (A+..D)
    flr=flr.rename(columns={"bandeira":"marca"})
    flr["bkn"]=flr["bkn"].astype(str).str.strip()
    cmp["bkn"]=cmp["chave_loja"].map(bkn_de_chave).astype(str).str.strip()
    rk["bkn"]=rk["chave_loja"].map(bkn_de_chave).astype(str).str.strip()
    dp["BKN"]=dp["BKN"].astype(str).str.strip()
    # v13.3: formato_area (Cadastro_Lojas) -> identifica lojas SBUX cujo PROPRIO FORMATO e
    # quiosque (formato_area=='KIOSK'). Nao vem do Fato_Loja_Recurso (tipo_area la NAO tem
    # esse valor p/ SBUX - so existe no Cadastro). So 15 lojas na rede, so SBUX.
    try:
        cad=carregar_aba(PATH_FATURA,"Cadastro_Lojas",None,"cadastro")
        cad["bkn"]=cad["bkn"].astype(str).str.strip()
        global QUIOSQUE_MAP
        QUIOSQUE_MAP={b: (str(fa).strip().upper()=="KIOSK")
                     for b,fa in zip(cad["bkn"],cad.get("formato_area",[]))}
        log(f"  cadastro carregado: {sum(QUIOSQUE_MAP.values())} lojas quiosque (formato proprio)")
    except Exception as ex:
        log(f"  (aviso) Cadastro_Lojas nao pode ser lido ({ex}); cluster Quiosque SBUX ficara vazio")
    # v12: recalcula o indice oficial corrigindo consumo fantasma pela mediana da propria loja
    rk=corrigir_indice_por_mediana(flr, rk)
    log(f"Bases carregadas em {time.time()-t:.1f}s")
    return flr,cmp,rk,dp

def _formata_dias(dias):
    """[5,6,7,8,9,10,11,13,14,18,19,20] -> 'dias 5 a 11, 13 e 14, 18 a 20'."""
    dias=sorted(set(int(d) for d in dias))
    if not dias: return ""
    grupos=[]; ini=prev=dias[0]
    for d in dias[1:]+[None]:
        if d is not None and d==prev+1: prev=d; continue
        grupos.append((ini,prev))
        if d is not None: ini=prev=d
    partes=[]
    for a,b in grupos:
        if a==b: partes.append(f"{a}")
        elif b==a+1: partes.append(f"{a} e {b}")
        else: partes.append(f"{a} a {b}")
    prefixo="dia" if (len(partes)==1 and grupos[0][0]==grupos[0][1]) else "dias"
    return f"{prefixo} "+", ".join(partes)

def carregar_setores():
    """Carrega o mapa BKN -> Setor, BKN -> Regional_Operacao e BKN -> possui KSK aberto
    (quiosque satelite) da base Database - Utilities. Setor e a subdivisao real dentro da
    Regional (a carteira). OBRIGATORIO para o painel do Gerente Regional (agrupa lojas por
    setor). Cabecalho real fica na 2a linha (header=1). Levanta erro claro se nao existir.

    KSK (v13.3): 'Possui_KSK'/'Status_KSK' descrevem uma loja CONVENCIONAL (FC/FS/etc) que
    tem um quiosque SATELITE anexo (consumo geralmente rateado via condominio, embutido no
    mesmo BKN da loja mae) - conceito so existe para BK nesta base (0 casos em PLK/SBUX).
    Validado estatisticamente (Mann-Whitney, p=0,037): lojas BK tipo FC com KSK aberto tem
    indice fisico mediano maior (0,96 vs 0,89) que as sem KSK - vies estrutural real, nao
    apenas ruido, o que justifica cluster proprio (ver cluster_sol())."""
    if not os.path.exists(PATH_SETOR):
        raise FileNotFoundError(
            f"Base de Setor nao encontrada: {PATH_SETOR}\n"
            f"  O painel do Gerente Regional depende da coluna 'Setor' dessa base "
            f"(Database - Utilities). Coloque o arquivo na pasta e rode de novo.")
    df=pd.read_excel(PATH_SETOR, sheet_name="Database", header=1)
    df=df[[c for c in df.columns if str(c) in ("BKN","Setor","Regional_Operacao","Status_KSK")]].copy()
    df["BKN"]=df["BKN"].astype(str).str.strip()
    df=df[df["BKN"].notna() & (df["BKN"]!="nan")]
    def _norm(b):
        try: return str(int(float(b)))
        except: return str(b).strip()
    df["BKN"]=df["BKN"].map(_norm)
    setor={}; regop={}; ksk={}
    for _,r in df.iterrows():
        b=r["BKN"]
        s=r.get("Setor")
        ro=r.get("Regional_Operacao")
        sk=r.get("Status_KSK")
        if pd.notna(s) and str(s).strip(): setor.setdefault(b, str(s).strip())
        if pd.notna(ro) and str(ro).strip(): regop.setdefault(b, str(ro).strip())
        if pd.notna(sk): ksk.setdefault(b, str(sk).strip().upper()=="ABERTO")
    global KSK_MAP
    KSK_MAP=dict(ksk)
    log(f"  setores carregados: {len(setor)} lojas, "
        f"{len(set(setor.values()))} setores, {len(set(regop.values()))} regionais de operacao, "
        f"{sum(ksk.values())} lojas BK com KSK satelite aberto")
    return setor, regop

def _tarifa_map_fatura(recurso_alvo):
    """Item 5 (v14): carrega tarifa_real por (bkn, recurso) do Fato_Loja_Recurso.
    Cascata: tarifa_real observada/inferida -> tarifa_orcada como fallback.
    Retorna dict (bkn_str, recurso_upper) -> (tarifa_float, confiavel_bool)."""
    try:
        cols=["bkn","recurso","tarifa_real","flag_tarifa_real","tarifa_orcada","competencia"]
        df=pd.read_excel(PATH_FATURA, sheet_name="Fato_Loja_Recurso", usecols=cols)
        df=df[df["recurso"].str.upper()==recurso_alvo.upper()].copy()
        df["competencia"]=pd.to_datetime(df["competencia"],errors="coerce")
        df=df.sort_values("competencia",ascending=False)
        df=df.drop_duplicates(subset=["bkn"],keep="first")
        out={}
        for _,r in df.iterrows():
            b=str(r["bkn"]).strip()
            try: b=str(int(float(b)))
            except: pass
            tr=r.get("tarifa_real"); flag=str(r.get("flag_tarifa_real",""))
            to=r.get("tarifa_orcada")
            if pd.notna(tr) and float(tr)>0 and "OK_TARIFA_REAL" in flag:
                out[(b,recurso_alvo.upper())]=(float(tr),True)
            elif pd.notna(to) and float(to)>0:
                out[(b,recurso_alvo.upper())]=(float(to),False)
        return out
    except Exception as e:
        log(f"  aviso: tarifa_map indisponivel para {recurso_alvo} ({e})")
        return {}

def carregar_alertas():
    """Alertas de madrugada (energia) e vazamento (agua).
    Item 5 (v14): enriquece cada alerta com excedente em unidade fisica e R$.
    Filtra Alerta_Baixa_Cobertura=True (dado fragil de telemetria).
    Cascata tarifa: tarifa_real observada/inferida -> tarifa_orcada (marcada como aproximada).
    Agua: so m3 (tarifa calculada de fatura quando disponivel, orcada como fallback).
    Retorna dict bkn -> {energia_dias, energia_excedente_kwh, energia_excedente_rs,
                         energia_tarifa_aprox, agua_dias, agua_continua, agua_ultimo_dia,
                         agua_excedente_m3, agua_excedente_rs, agua_tarifa_aprox}."""
    out={}
    tar_en=_tarifa_map_fatura("ENERGIA")
    tar_ag=_tarifa_map_fatura("AGUA")
    try:
        a=pd.read_excel(PATH_ALERTA_MADRUGADA, sheet_name="Alertas")
        # filtra cobertura fragil
        if "Alerta_Baixa_Cobertura" in a.columns:
            a=a[a["Alerta_Baixa_Cobertura"]!=True]
        en=a[a["Recurso"].astype(str).str.upper().str.startswith("ENERG")]
        for bkn,g in en.groupby("BKN"):
            b=str(bkn).strip()
            try: b=str(int(float(b)))
            except: pass
            out.setdefault(b,{})
            out[b]["energia_dias"]=sorted(set(int(x) for x in g["Dia"].dropna()))
            # excedente fisico: soma Excedente_Periodo_Alerta (kWh) > 0
            if "Excedente_Periodo_Alerta" in g.columns:
                exc=pd.to_numeric(g["Excedente_Periodo_Alerta"],errors="coerce")
                exc_kwh=float(exc[exc>0].sum()) if not exc[exc>0].empty else 0.0
            else:
                exc_kwh=0.0
            out[b]["energia_excedente_kwh"]=exc_kwh
            # conversao R$
            tar_info=tar_en.get((b,"ENERGIA"))
            if tar_info and exc_kwh>0:
                out[b]["energia_excedente_rs"]=exc_kwh*tar_info[0]
                out[b]["energia_tarifa_aprox"]=(not tar_info[1])
            else:
                out[b]["energia_excedente_rs"]=None
                out[b]["energia_tarifa_aprox"]=False
    except Exception as e:
        log(f"  aviso: alerta madrugada indisponivel ({e})")
    try:
        v=pd.read_excel(PATH_VAZAMENTO_AGUA, sheet_name="Detalhe_Diario")
        dia_hoje=DIA_HOJE_ALERTA if DIA_HOJE_ALERTA else int(v["Dia"].max())
        corte=dia_hoje-2
        # excedentes do nivel Vazamentos (grão loja)
        vaz=pd.read_excel(PATH_VAZAMENTO_AGUA, sheet_name="Vazamentos")
        if "Alerta_Baixa_Cobertura" in vaz.columns:
            vaz=vaz[vaz["Alerta_Baixa_Cobertura"]!=True]
        exc_vaz={}
        for _,r in vaz.iterrows():
            b=str(r["BKN"]).strip()
            try: b=str(int(float(b)))
            except: pass
            exc=r.get("Excedente_Volume_Periodo_Alerta")
            exc_vaz[b]=float(exc) if pd.notna(exc) and float(exc)>0 else 0.0
        # excedentes alto consumo agua da planilha de alertas
        try:
            ag_alt=pd.read_excel(PATH_ALERTA_MADRUGADA, sheet_name="Alertas")
            if "Alerta_Baixa_Cobertura" in ag_alt.columns:
                ag_alt=ag_alt[ag_alt["Alerta_Baixa_Cobertura"]!=True]
            ag_alt=ag_alt[ag_alt["Recurso"].astype(str).str.upper().str.startswith("AG")]
            exc_ac={}
            for bkn,g in ag_alt.groupby("BKN"):
                b2=str(bkn).strip()
                try: b2=str(int(float(b2)))
                except: pass
                if "Excedente_Periodo_Alerta" in g.columns:
                    exc=pd.to_numeric(g["Excedente_Periodo_Alerta"],errors="coerce")
                    exc_ac[b2]=float(exc[exc>0].sum()) if not exc[exc>0].empty else 0.0
        except:
            exc_ac={}
        for bkn,g in v.groupby("BKN"):
            b=str(bkn).strip()
            try: b=str(int(float(b)))
            except: pass
            dias=sorted(set(int(x) for x in g["Dia"].dropna()))
            ultimo=max(dias) if dias else 0
            out.setdefault(b,{})
            out[b]["agua_dias"]=dias; out[b]["agua_ultimo_dia"]=ultimo
            out[b]["agua_continua"]=(ultimo>=corte)
            # excedente m3: usa vazamento se disponivel, senao alto consumo
            exc_m3=exc_vaz.get(b) or exc_ac.get(b) or 0.0
            out[b]["agua_excedente_m3"]=exc_m3
            tar_info=tar_ag.get((b,"AGUA"))
            if tar_info and exc_m3>0:
                out[b]["agua_excedente_rs"]=exc_m3*tar_info[0]
                out[b]["agua_tarifa_aprox"]=(not tar_info[1])
            else:
                out[b]["agua_excedente_rs"]=None
                out[b]["agua_tarifa_aprox"]=False
    except Exception as e:
        log(f"  aviso: vazamento agua indisponivel ({e})")
    return out

def carregar_historico():
    c=_cache("historico")
    if USAR_CACHE and os.path.exists(c):
        try:
            if os.path.getmtime(c)>=os.path.getmtime(PATH_HIST):
                log("  cache: historico"); return pd.read_parquet(c)
        except: pass
    log("  lendo historico")
    xls=pd.ExcelFile(PATH_HIST); regs=[]
    for sheet in xls.sheet_names:
        s=sheet.upper()
        rec=("GAS" if ("GAS" in s or "GÁS" in s) else
             ("AGUA" if ("AGUA" in s or "ÁGUA" in s) else
              ("ENERGIA" if "ENERGIA" in s else None)))
        if not rec: continue
        df=xls.parse(sheet)
        col_bkn=next((cc for cc in df.columns if str(cc).strip().upper() in ("BKN","COD","CODIGO")), df.columns[0])
        mes_cols=[cc for cc in df.columns if isinstance(cc,str) and "/" in cc and len(cc)==7]
        for _,row in df.iterrows():
            bkn=str(row[col_bkn]).strip()
            if bkn in ("nan","None",""): continue
            try: bkn=str(int(float(bkn)))
            except: pass
            for mc in mes_cols:
                v=row[mc]
                if pd.notna(v) and float(v)>0:
                    regs.append({"bkn":bkn,"recurso":rec,"mes":mc,"consumo":float(v)})
    hist=pd.DataFrame(regs)
    if USAR_CACHE and len(hist):
        os.makedirs(PASTA_CACHE, exist_ok=True)
        try: hist.to_parquet(c, index=False)
        except: pass
    return hist

# ============================ REGRAS DE NEGOCIO ============================
def dado_fragil(flag):
    """True quando o CONSUMO FISICO da linha e suspeito (deve sair do indice, rankings e
    graficos de acao). v13: REVISAR_FINANCEIRO_GD_CONSUMO_FISICO_PRESERVADO NAO entra aqui
    -- o proprio nome do flag diz que o consumo fisico foi preservado (confiavel); so o
    financeiro (SAP) diverge por causa de geracao distribuida solar. Tratar essa linha como
    'sem dado' escondia sistematicamente as lojas com GD solar (que pesam mais em energia,
    50% da despesa) dos graficos de acao, quebrando a correlacao entre 'quem piorou o
    indice' e 'em qual utility'. Usar fragil_financeiro() para o caso SAP/GD."""
    f=str(flag)
    if f.startswith("REVISAR_FINANCEIRO_GD"): return False
    return f.startswith("REVISAR")

def fragil_financeiro(flag):
    """True quando so o valor FINANCEIRO (SAP) e' suspeito, mas o consumo fisico foi
    preservado (GD solar). Usar para decidir sobre despesa_recurso()/SAP, nao sobre
    consumo fisico ou indice."""
    return str(flag).startswith("REVISAR_FINANCEIRO_GD")

def flag_gd(flag):
    """True se a loja tem Geracao Distribuida / AC-condominio (SAP infla, usar valor_real_rs)."""
    return str(flag).startswith("REVISAR_FINANCEIRO_GD")

# ---- Regra A: consumo fantasma (leitura implausivel -> 'Ainda sem dado') ----
# Limiar CONSERVADOR: consumo < 10% da mediana (marca+recurso) E < 30% do previsto.
FANTASMA_FRAC_MEDIANA = 0.10
FANTASMA_FRAC_PREVISTO = 0.30
# Leitura ALTA implausivel (v12, so ENERGIA e GAS): consumo do mes > 5x a mediana dos
# OUTROS meses da PROPRIA loja E isolado (vizinhos nao estouram). Base = propria loja, nao
# a marca (so isso separa erro de leitura de consumo real alto). Agua NAO entra (estouro de
# agua costuma ser vazamento real, capturado pelos alertas).
ALTO_FATOR_LOJA = 5.0
# ORCAMENTO cronicamente errado (v13.2, so energia/gas): mediana da razao real/previsto
# ao longo dos meses > este fator -> previsto quebrado, substitui por mediana(real) da loja.
ORCADO_RAZAO_MAX = 5.0

def consumo_fantasma(consumo, previsto, mediana_marca_rec):
    """True quando o consumo real e implausivelmente baixo (leitura fantasma)."""
    if consumo is None or pd.isna(consumo): return True   # sem leitura = sem dado
    c=float(consumo)
    if c <= 0: return True
    cond_med = (mediana_marca_rec and c < FANTASMA_FRAC_MEDIANA*mediana_marca_rec)
    cond_prev = (previsto and pd.notna(previsto) and previsto>0 and c < FANTASMA_FRAC_PREVISTO*float(previsto))
    return bool(cond_med and cond_prev)

# ---- Regra B+C: despesa (SAP; fallback valor_real_rs; senao 'sob revisao') ----
def _ac_condominio_estimado(row):
    """Custo estimado do ar-condicionado de condominio (so energia).
    AC = kWh orcado do AC x tarifa de conversao do AC. 0 quando nao ha AC."""
    if str(row.get("recurso","")).upper()!="ENERGIA": return 0.0
    kwh=row.get("consumo_orcado_energia_ar_condicionado_kwh")
    tar=row.get("tarifa_conversao_ar_condicionado_rs_kwh")
    if pd.notna(kwh) and pd.notna(tar) and float(kwh)>0 and float(tar)>0:
        return float(kwh)*float(tar)
    return 0.0

def despesa_recurso(row):
    """Retorna (valor_float_ou_None, origem_str).
    Regra: realizado_sap_rs para todas as lojas (o que aparece no P&L da loja).
    Se SAP<=0/invalido (estorno/credito contabil, nao a despesa do mes):
      -> (consumo x tarifa) + AC-condominio estimado. Depois valor_real_rs.
    Se nada valido -> None ('sob revisao')."""
    sap=row.get("realizado_sap_rs")
    if pd.notna(sap) and float(sap) > 0:
        return float(sap), "sap"
    c,t=row.get("consumo_real"),row.get("tarifa_real")
    if pd.notna(c) and pd.notna(t) and float(c)>0 and float(t)>0:
        return float(c)*float(t) + _ac_condominio_estimado(row), "consumo_tarifa_ac"
    vr=row.get("valor_real_rs")
    if pd.notna(vr) and float(vr) > 0:
        return float(vr), "fallback_valor_real"
    return None, "sob_revisao"

def divergencia_cronica_sap(flr, ref_ts):
    """Mediana da razao (consumo*tarifa)/SAP por (bkn,recurso) ao longo dos meses fechados.
    Retorna set de (bkn,recurso) cuja despesa em R$ diverge cronicamente >20% do P&L (SAP).
    Causa tipica: GD (solar) e AC-condominio, que fazem o SAP diferir do custo teorico."""
    d=flr[(flr["competencia"]<=ref_ts)&(flr["status_periodo"]=="FECHADO_COM_REAL")].copy()
    for c in ["consumo_real","tarifa_real","realizado_sap_rs"]:
        d[c]=pd.to_numeric(d[c],errors="coerce")
    d["ct"]=d["consumo_real"]*d["tarifa_real"]
    d=d[(d["realizado_sap_rs"]>0)&(d["ct"]>0)]
    d["razao"]=d["ct"]/d["realizado_sap_rs"]
    med=d.groupby(["bkn","recurso"])["razao"].median()
    diverge=med[(med<0.8)|(med>1.2)]
    return set(diverge.index)

def medianas_marca_recurso(flr, ref_ts):
    """Mediana de consumo_real por (marca, recurso) sobre dados FECHADOS e <= ref_ts."""
    base=flr[(flr["competencia"]<=ref_ts)&(flr["status_periodo"]=="FECHADO_COM_REAL")].copy()
    base["consumo_real"]=pd.to_numeric(base["consumo_real"],errors="coerce")
    base=base[base["consumo_real"]>0]
    return base.groupby(["marca","recurso"])["consumo_real"].median().to_dict()

# ---- Categoria de area (comparar shopping com shopping, rua com rua) ----
_AREA_SHOPPING={"SHOPPING","MALL","STRIP MALL","HIPER","OFFICE","TERMINAIS","DESCONHECIDO"}
_AREA_RUA={"RUA","STREET","DRIVE","HIGHWAY","UNIVERSITY","POSTO"}
def categoria_area(tipo_area):
    t=str(tipo_area).strip().upper()
    if t=="AIRPORT": return "AIRPORT"      # so compara com airport
    if t in _AREA_RUA: return "RUA"
    return "SHOPPING"                        # inclui DESCONHECIDO e default

def carregar_temperatura(ref_ts):
    """Mapa bkn -> temperatura media do mes de referencia (do DadosOrcamento).
    Usado no pareamento de ENERGIA para lojas de RUA."""
    try:
        d=pd.read_excel(PATH_ORCAMENTO, sheet_name="Sheet1", usecols=["BKN","Ano","Mes_Num","Temperatura"])
    except Exception as e:
        log(f"  aviso: temperatura indisponivel ({e})"); return {}
    d=d[(d["Ano"]==ref_ts.year)&(d["Mes_Num"]==ref_ts.month)]
    d=d.dropna(subset=["Temperatura"]).drop_duplicates("BKN")
    out={}
    for b,t in zip(d["BKN"],d["Temperatura"]):
        if pd.isna(b): continue
        bs=str(b).strip()
        try: bs=str(int(float(bs)))
        except: pass
        out[bs]=float(t)
    return out

def construir_pools_comparaveis(flr, ref_ts, medianas, temp_map=None):
    """Pool por recurso (mes ref, FECHADO, sem fragil/fantasma) com cluster de exposicao
    ao sol, area (m2) e temperatura, para o pareamento do Bloco 5."""
    ref=flr[(flr["competencia"]==ref_ts)&(flr["status_periodo"]=="FECHADO_COM_REAL")].copy()
    for c in ["consumo_real","trafego_real","consumo_previsto","area_vendas_m2"]:
        ref[c]=pd.to_numeric(ref[c],errors="coerce")
    ref["cluster"]=ref.apply(lambda r: cluster_sol(r["marca"],r["tipo_loja"],r["tipo_area"],r["bkn"]),axis=1)
    ref["temp"]=ref["bkn"].astype(str).map(temp_map or {})
    pools={}
    for recurso in ["ENERGIA","AGUA","GAS"]:
        sub=ref[ref["recurso"]==recurso].copy()
        sub=sub[(sub["trafego_real"]>0)&(sub["consumo_real"]>0)]
        sub=sub[~sub["flag_qualidade_consumo"].map(dado_fragil)]
        def _fant(row):
            return consumo_fantasma(row["consumo_real"],row["consumo_previsto"],
                                    medianas.get((row["marca"],recurso)))
        sub=sub[~sub.apply(_fant,axis=1)]
        pools[recurso]=sub[["bkn","marca","nome","regional","trafego_real","consumo_real",
                            "cluster","temp","area_vendas_m2"]].reset_index(drop=True)
    pools["_temp_map"]=temp_map or {}
    return pools

# tolerancias do pareamento (Bloco 5)
COMP_DIFF_MIN = 0.05     # consome >=5% menos
COMP_TRAFEGO_TOL = 0.20  # trafego +-20%
COMP_TEMP_TOL = 2.0      # temperatura +-2 C (energia rua)
COMP_AREA_TOL = 0.10    # area +-10% (v13.3: apertado de 30% para 10%, validado: cobertura
                         # final identica 99,2% (o relaxamento absorve), mas pares no nivel
                         # mais restrito ficam muito mais justos - mediana da diferenca de
                         # area cai de 15,9% para 6,1%; pares com diferenca <=10% sobe de
                         # 34,4% para 81,1%)

def comparavel_por_recurso(alvo_bkn, marca, recurso, consumo_alvo, trafego_alvo, despesa_alvo,
                           pool_rec, cluster_alvo=None, temp_alvo=None, area_alvo=None):
    """Par por recurso DENTRO do mesmo cluster (marca + exposicao ao sol) que consome >=5% menos.
    Filtros preferenciais: trafego +-20%, area +-30%, (energia rua) temperatura +-2C.
    Relaxa progressivamente para garantir pelo menos 1 par (a loja SEMPRE tem par se existir
    alguem no cluster consumindo menos), como pedido: o obrigatorio e ter par."""
    if not consumo_alvo or consumo_alvo<=0: return None
    # universo base: mesmo cluster, mesma marca, consome >=5% menos
    base=pool_rec[(pool_rec["marca"]==marca)&
                  (pool_rec["cluster"]==cluster_alvo)&
                  (pool_rec["consumo_real"] <= consumo_alvo*(1-COMP_DIFF_MIN))&
                  (pool_rec["bkn"]!=alvo_bkn)].copy()
    if base.empty: return None
    usa_temp = (recurso=="ENERGIA" and cluster_alvo=="RUA" and temp_alvo is not None and pd.notna(temp_alvo))
    # niveis de filtro, do mais restrito ao mais frouxo
    def aplica(cand, usar_traf, usar_area, usar_temp_f):
        c=cand
        if usar_traf and trafego_alvo and trafego_alvo>0:
            lo,hi=trafego_alvo*(1-COMP_TRAFEGO_TOL),trafego_alvo*(1+COMP_TRAFEGO_TOL)
            c=c[c["trafego_real"].between(lo,hi)]
        if usar_area and area_alvo and area_alvo>0:
            lo,hi=area_alvo*(1-COMP_AREA_TOL),area_alvo*(1+COMP_AREA_TOL)
            c=c[c["area_vendas_m2"].between(lo,hi)]
        if usar_temp_f:
            c=c[c["temp"].notna() & ((c["temp"]-temp_alvo).abs()<=COMP_TEMP_TOL)]
        return c
    tentativas=[
        (True,  True,  usa_temp),   # tudo
        (True,  False, usa_temp),   # sem area
        (True,  True,  False),      # sem temp
        (True,  False, False),      # so trafego
        (False, True,  False),      # so area
        (False, False, False),      # so cluster (garante par)
    ]
    cand=None
    for ut,ua,utf in tentativas:
        c=aplica(base,ut,ua,utf)
        if not c.empty: cand=c; break
    if cand is None or cand.empty: return None
    # escolhe o de trafego mais proximo (ou area, se trafego ausente)
    if trafego_alvo and trafego_alvo>0:
        cand=cand.assign(dist=(cand["trafego_real"]-trafego_alvo).abs())
    elif area_alvo and area_alvo>0:
        cand=cand.assign(dist=(cand["area_vendas_m2"]-area_alvo).abs())
    else:
        cand=cand.assign(dist=0)
    best=cand.sort_values("dist").iloc[0]
    pct=(1-best["consumo_real"]/consumo_alvo)*100
    economia=(despesa_alvo*pct/100) if (despesa_alvo is not None) else None
    return {"nome":best["nome"],"regional":best.get("regional",""),
            "pct":pct,"trafego":float(best["trafego_real"]),
            "economia":economia,
            "temp_alvo":(float(temp_alvo) if usa_temp else None),
            "temp_comp":(float(best["temp"]) if usa_temp and pd.notna(best["temp"]) else None),
            "area_alvo":(float(area_alvo) if area_alvo and area_alvo>0 else None),
            "area_comp":(float(best["area_vendas_m2"]) if pd.notna(best.get("area_vendas_m2")) else None)}

def proxima_loja_menos_consumo(bkn, marca, ref_ts, flr, rk, medianas):
    """Para lojas A+: aponta a proxima loja (mesma marca) com indice imediatamente melhor."""
    ind=rk[(rk["bkn"]==bkn)&(rk["competencia"]==ref_ts)]
    if ind.empty or pd.isna(ind.iloc[0]["indice_eficiencia_mes"]): return None
    meu=ind.iloc[0]["indice_eficiencia_mes"]
    prov=rk[(rk["competencia"]==ref_ts)&(rk["bkn"]!=bkn)].copy()
    prov=prov[pd.notna(prov["indice_eficiencia_mes"])&(prov["indice_eficiencia_mes"]<meu)]
    if prov.empty: return None
    marcas=flr[(flr["competencia"]==ref_ts)][["bkn","marca","nome"]].drop_duplicates("bkn")
    prov=prov.merge(marcas,on="bkn",how="left")
    prov=prov[prov["marca"]==marca]
    if prov.empty: return None
    best=prov.sort_values("indice_eficiencia_mes",ascending=False).iloc[0]
    p_best=best["indice_eficiencia_mes"]*100; p_meu=meu*100
    # se arredondam igual, separa somando 1% no maior (o proprio, que e pior)
    if round(p_best)==round(p_meu):
        p_meu=round(p_best)+1; p_best=round(p_best)
    return (f'A proxima loja mais eficiente e <b>{best["nome"]}</b> '
            f'(indice {p_best:.0f}% vs seu {p_meu:.0f}%). '
            f'Supere-a para assumir a lideranca.')

def atribui_bandeiras(indice_series, faixas=None):
    """Recebe Series de indice (menor=melhor). Retorna Series de bandeira por quantis.
    faixas: lista de rotulos (default 8). Adapta o nº de bins ao tamanho da amostra."""
    faixas=faixas or BANDEIRAS_8
    n=len(indice_series); k=len(faixas)
    if n<k:  # menos lojas que faixas: rank simples
        r=indice_series.rank(method="first")
        return r.apply(lambda x: faixas[min(int((x-1)/max(n,1)*k),k-1)])
    try:
        return pd.qcut(indice_series, k, labels=faixas, duplicates="drop")
    except Exception:
        r=indice_series.rank(pct=True)
        return r.apply(lambda x: faixas[min(int(x*k),k-1)])

def bandeiras_por_cluster(ref_ts, flr, rk):
    """Atribui bandeira a cada loja DENTRO do seu (marca, cluster), com esquema de
    faixas que depende do tamanho do cluster (Bloco 4). So marca cada loja pela sua
    posicao relativa entre pares comparaveis (mesma marca + exposicao ao sol).
    Retorna: band_por_bkn{bkn->faixa}, faixas_por_bkn{bkn->lista de faixas do cluster},
             fronteiras_por_cluster{(marca,cluster)->{faixa:idx_max}}, cluster_por_bkn."""
    rk_ref=rk[rk["competencia"]==ref_ts][["bkn","indice_eficiencia_mes"]].dropna()
    info=flr[flr["competencia"]==ref_ts][["bkn","marca","tipo_loja","tipo_area"]].drop_duplicates("bkn")
    m=rk_ref.merge(info,on="bkn",how="left").dropna(subset=["marca"])
    m["cluster"]=m.apply(lambda r: cluster_sol(r["marca"],r["tipo_loja"],r["tipo_area"],r["bkn"]),axis=1)
    # remove fantasma do ranking (indice implausivel)
    m=m[m["indice_eficiencia_mes"]>=0.10]
    band={}; faixas_bkn={}; fronteiras={}; cluster_bkn={}
    for (marca,cluster),g in m.groupby(["marca","cluster"]):
        faixas=esquema_faixas(len(g))
        s=g.set_index("bkn")["indice_eficiencia_mes"]
        b=atribui_bandeiras(s, faixas)
        for bkn,fx in b.items():
            band[bkn]=fx; faixas_bkn[bkn]=faixas; cluster_bkn[bkn]=(marca,cluster)
        df=pd.DataFrame({"idx":s,"b":b})
        fronteiras[(marca,cluster)]={"faixas":faixas,
            "fronteira":df.groupby("b",observed=True)["idx"].max().to_dict()}
    return band, faixas_bkn, fronteiras, cluster_bkn

def fronteiras_bandeira(indice_series, faixas=None):
    """Retorna dict bandeira -> indice maximo (fronteira superior da faixa)."""
    df=pd.DataFrame({"idx":indice_series})
    df["b"]=atribui_bandeiras(df["idx"], faixas)
    return df.groupby("b",observed=True)["idx"].max().to_dict()

def proxima_bandeira(atual, faixas=None):
    faixas=faixas or BANDEIRAS_8
    if atual not in faixas: return None
    i=faixas.index(atual)
    return faixas[i-1] if i>0 else None

# ============================ SERIES 12M ============================
def serie_consumo_12m(bkn, recurso, ref_ts, flr, hist, medianas=None, marca=None):
    """Serie de consumo real dos ultimos 12 meses. Omite meses sem leitura confiavel.
    Item 3 (v14): retorna (label, real, previsto_corrigido) para o grouped bar Real vs Meta.
    previsto_corrigido usa ORCAMENTO_ERRADO quando aplicavel (mesmo denominador do indice).
    Historico externo retorna previsto=None (nao temos a meta historica)."""
    meses=pd.date_range(end=ref_ts, periods=12, freq="MS"); val={}; prev={}
    sub=flr[(flr["bkn"]==bkn)&(flr["recurso"]==recurso)&
            (flr["competencia"]<=ref_ts)&(flr["status_periodo"]=="FECHADO_COM_REAL")]
    med=(medianas or {}).get((marca,recurso))
    for _,r in sub.iterrows():
        c=r["consumo_real"]
        if consumo_fantasma(c, r.get("consumo_previsto"), med):
            continue
        k=pd.Timestamp(r["competencia"]).strftime("%Y-%m")
        val[k]=float(c)
        # previsto corrigido (mesmo denominador do indice)
        cp_corr=ORCAMENTO_ERRADO.get((str(bkn),recurso))
        cp=cp_corr if cp_corr is not None else r.get("consumo_previsto")
        prev[k]=(float(cp) if pd.notna(cp) and float(cp)>0 else None)
    if hist is not None and len(hist):
        h=hist[(hist["bkn"]==bkn)&(hist["recurso"]==recurso)]
        for _,r in h.iterrows():
            mm,aa=r["mes"].split("/"); k=f"{aa}-{mm}"
            if k not in val and pd.notna(r["consumo"]) and r["consumo"]>0:
                if med and r["consumo"] < 0.10*med: continue
                val.setdefault(k, float(r["consumo"]))
                prev.setdefault(k, None)  # sem meta para historico externo
    serie=[]
    for m in meses:
        k=m.strftime("%Y-%m")
        if k in val:
            serie.append((m.strftime("%b/%y"), val[k], prev.get(k)))
    return serie

def _meses_fantasma(bkn, ref_ts, flr, medianas):
    """Conjunto de 'YYYY-MM' em que a loja teve consumo fantasma em ALGUM recurso
    (indice desses meses e nao-confiavel)."""
    sub=flr[(flr["bkn"]==bkn)&(flr["competencia"]<=ref_ts)&(flr["status_periodo"]=="FECHADO_COM_REAL")]
    ruins=set()
    for _,r in sub.iterrows():
        med=(medianas or {}).get((r.get("marca"), r["recurso"]))
        if consumo_fantasma(r["consumo_real"], r.get("consumo_previsto"), med):
            ruins.add(pd.Timestamp(r["competencia"]).strftime("%Y-%m"))
    return ruins

def serie_indice_12m(bkn, ref_ts, rk, flr=None, medianas=None, band_loja=None, faixas_loja=None):
    """v12: usa o indice OFICIAL ja corrigido no rk (fantasma->mediana).
    Item 4 (v14): retorna (label, indice, nivel_str_ou_None). nivel so e preenchido para
    o mes de referencia em diante (historico acumula mês a mes a partir do lancamento).
    Meses anteriores ao ref_ts retornam nivel=None (sem dado historico de nivel)."""
    meses=pd.date_range(end=ref_ts, periods=12, freq="MS")
    sub=rk[(rk["bkn"]==bkn)&(rk["competencia"]<=ref_ts)]
    val={pd.Timestamp(r["competencia"]).strftime("%Y-%m"):r["indice_eficiencia_mes"]
         for _,r in sub.iterrows() if pd.notna(r["indice_eficiencia_mes"])}
    ref_k=ref_ts.strftime("%Y-%m")
    nivel_mes=(band_loja or {}).get(bkn) if band_loja else None
    out=[]
    for m in meses:
        k=m.strftime("%Y-%m")
        if k not in val: continue
        nivel=(nivel_mes if k==ref_k else None)
        out.append((m.strftime("%b/%y"), float(val[k]), nivel))
    return out

# ============================ GRAFICOS ============================
def _chart(chart,w=520,h=180):
    c=quote(json.dumps(chart))
    return f'<img src="https://quickchart.io/chart?w={w}&h={h}&c={c}" style="max-width:100%;display:block;" width="{w}" height="{h}"/>'
def grafico_consumo(serie, recurso):
    """Item 3 (v14): grouped bar Real vs Meta (consumo_previsto corrigido) por mes.
    Dois datasets por mes: azul=real, cinza=meta. Grade removida. Labels acima das barras."""
    if not serie:
        return f'<div style="color:{COR["cinza_claro"]};font-size:12px;padding:20px 0;text-align:center;">Sem historico de consumo confiavel para {ROTULO[recurso]}.</div>'
    labels=[s[0] for s in serie]
    reais=[round(s[1]) for s in serie]
    metas=[round(s[2]) if len(s)>2 and s[2] is not None else None for s in serie]
    datasets=[{"label":"Real","data":reais,"backgroundColor":COR_REC[recurso]}]
    if any(m is not None for m in metas):
        datasets.append({"label":"Meta","data":metas,"backgroundColor":"#b9c4d4"})
    return _chart({
        "type":"bar",
        "data":{"labels":labels,"datasets":datasets},
        "options":{
            "title":{"display":True,"text":f"Consumo por Meta - {ROTULO[recurso]} ({UNIDADE[recurso]})"},
            "legend":{"display":True,"position":"bottom"},
            "plugins":{"datalabels":{"anchor":"end","align":"top","font":{"size":9},
                                     "formatter":"function(v){return v!=null?v.toLocaleString('pt-BR'):'';}"}},
            "scales":{
                "xAxes":[{"gridLines":{"display":False}}],
                "yAxes":[{"ticks":{"beginAtZero":True},"gridLines":{"display":False}}]}}},
        w=520,h=220)
def grafico_indice(serie):
    """Items 1 e 4 (v14): sem grade, valor exato acima de cada ponto.
    Quando a tupla tem 3 elementos (label, indice, nivel), exibe 'Nivel X\nYY%' no datalabel
    do mes em que o nivel esta disponivel; nos demais meses exibe so o percentual."""
    if not serie: return ""
    labels=[s[0] for s in serie]
    vals=[round(s[1]*100) for s in serie]
    niveis=[s[2] if len(s)>2 else None for s in serie]
    meta=[100]*len(labels)
    cores=[COR["verde"] if v<=100 else COR["vermelho"] for v in vals]
    cor_linha=COR["vermelho"] if vals and vals[-1]>100 else COR["azul"]
    # datalabels: se ha nivel no mes, mostra "Nivel X / YY%", senao so "YY%"
    niveis_js=json.dumps(niveis)
    formatter=(f"function(v,ctx){{var n={niveis_js}[ctx.dataIndex];"
               f"return n?'Nivel '+n+'\\n'+v+'%':v+'%';}}")
    return _chart({"type":"line","data":{"labels":labels,"datasets":[
      {"label":"Indice de Consumo por Meta (%)","data":vals,"borderColor":cor_linha,
       "pointBackgroundColor":cores,"pointBorderColor":cores,"pointRadius":4,"fill":False,
       "datalabels":{"anchor":"top","align":"top","font":{"size":9},"formatter":formatter}},
      {"label":"Meta (100%)","data":meta,"borderColor":COR["cinza"],"borderDash":[6,4],
       "pointRadius":0,"fill":False,"datalabels":{"display":False}}]},
      "options":{"title":{"display":True,"text":"Indice de Consumo por Meta (%) - abaixo de 100% e melhor"},
      "legend":{"display":True,"position":"bottom"},
      "scales":{"xAxes":[{"gridLines":{"display":False}}],
                "yAxes":[{"gridLines":{"display":False}}]}}},w=520,h=240)

# ============================ HTML BASE ============================
def _frase_excedente(exc_fis, unidade, exc_rs, aprox):
    """Item 5 (v14): monta a frase de impacto 'Excedente: X kWh = R$ Y'."""
    if not exc_fis: return ""
    fis=f'Consumo excedente: <b>{num(exc_fis)} {unidade}</b>'
    if exc_rs:
        aprox_txt=" (tarifa orcada, aproximado)" if aprox else ""
        return f'{fis} = <b>{brl(exc_rs)}</b>{aprox_txt}'
    return fis

def bloco_alerta_loja(bkn, alertas):
    """Retangulo de alertas acionaveis da LOJA (energia madrugada + agua vazamento).
    Item 5 (v14): exibe excedente em kWh/m3 e R$ quando disponivel."""
    a=alertas.get(str(bkn))
    if not a: return ""
    linhas=[]
    en=a.get("energia_dias")
    if en:
        exc_html=""
        exc_kwh=a.get("energia_excedente_kwh",0)
        if exc_kwh and exc_kwh>0:
            exc_html=(f'<div style="font-size:11px;color:{COR["texto"]};margin-top:3px;">'
                      f'{_frase_excedente(exc_kwh,"kWh",a.get("energia_excedente_rs"),a.get("energia_tarifa_aprox",False))}'
                      f'</div>')
        linhas.append(
            f'<div style="margin-bottom:10px;">'
            f'<b style="color:{COR["laranja"]};">Energia: Alertas de Alto Consumo na Madrugada:</b> {_formata_dias(en)}<br>'
            f'{exc_html}'
            f'<span style="font-size:12px;color:{COR["texto"]};">Siga os horarios de ligar e desligar dos equipamentos no Checklist do Coordenador de Turno.</span>'
            f'</div>')
    ag=a.get("agua_dias")
    if ag:
        if a.get("agua_continua"):
            sub_txt='<b>Provavel Vazamento de Agua: acione manutencao.</b>'
            sub_cor=COR["vermelho"]
        else:
            sub_txt='<b>Provavel Vazamento de Agua, porem parou nos ultimos dias. Fique atento.</b>'
            sub_cor=COR["texto"]
        exc_kwh=a.get("agua_excedente_m3",0)
        exc_html=""
        if exc_kwh and exc_kwh>0:
            exc_html=(f'<div style="font-size:11px;color:{COR["texto"]};margin-top:3px;">'
                      f'{_frase_excedente(exc_kwh,"m3",a.get("agua_excedente_rs"),a.get("agua_tarifa_aprox",False))}'
                      f'</div>')
        linhas.append(
            f'<div><b style="color:{COR["azul"]};">Agua: Alertas de Alto Consumo na Madrugada:</b> {_formata_dias(ag)}<br>'
            f'{exc_html}'
            f'<span style="font-size:12px;color:{sub_cor};">{sub_txt}</span></div>')
    if not linhas: return ""
    return (f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin:8px 0 16px;">'
            f'<tr><td style="background:{COR["amarelo_bg"]};border:1px solid #f2d9b5;border-radius:10px;padding:14px 18px;">'
            f'<div style="font-weight:700;color:{COR["azul"]};margin-bottom:8px;">Pontos de Atencao do Mes</div>'
            f'{"".join(linhas)}</td></tr></table>')

def bloco_alerta_grupo(bkns, alertas, flr, ref_ts, max_lojas=None):
    """Retangulo de alertas para COORDENADOR/GERENTE.
    Lista lojas com alerta (energia: N dias; agua: N dias + ultimo dia).
    max_lojas: limita quantas lojas mostrar (regional=3)."""
    nomes=flr[(flr["competencia"]==ref_ts)][["bkn","nome"]].drop_duplicates("bkn").set_index("bkn")["nome"].to_dict()
    en_rows=[]; ag_rows=[]
    for b in bkns:
        a=alertas.get(str(b))
        if not a: continue
        nome=nomes.get(str(b),str(b))
        if a.get("energia_dias"):
            en_rows.append((nome,len(a["energia_dias"]),
                            a.get("energia_excedente_kwh",0),
                            a.get("energia_excedente_rs"),
                            a.get("energia_tarifa_aprox",False)))
        if a.get("agua_dias"):
            ag_rows.append((nome,len(a["agua_dias"]),a.get("agua_ultimo_dia",0),
                            a.get("agua_continua",False),
                            a.get("agua_excedente_m3",0),
                            a.get("agua_excedente_rs"),
                            a.get("agua_tarifa_aprox",False)))
    en_rows.sort(key=lambda x:x[1],reverse=True)
    ag_rows.sort(key=lambda x:x[1],reverse=True)
    if max_lojas:
        en_rows=en_rows[:max_lojas]; ag_rows=ag_rows[:max_lojas]
    if not en_rows and not ag_rows: return ""
    # v12 (item 9): energia a ESQUERDA, agua a DIREITA, lado a lado. Sem titulo 'Pontos de Atencao'.
    if en_rows:
        li=""
        for nome,dias,exc_kwh,exc_rs,aprox in en_rows:
            exc_txt=""
            if exc_kwh and exc_kwh>0:
                exc_txt=" &mdash; "+_frase_excedente(exc_kwh,"kWh",exc_rs,aprox)
            li+=f'<li>{nome}: {dias} dias{exc_txt}</li>'
        en_html=(f'<b style="color:{COR["laranja"]};">Energia: Alertas de Alto Consumo na Madrugada: '
                 f'provavelmente equipamentos nao foram desligados no fechamento</b>'
                 f'<ul style="margin:6px 0 0 18px;padding:0;font-size:13px;">{li}</ul>')
    else:
        en_html=f'<span style="font-size:12px;color:{COR["cinza_claro"]};">Sem alertas de energia na madrugada.</span>'
    # Item 6 (v14): separa agua em alto consumo, vazamento ativo e vazamento provavelmente resolvido
    ag_alto=[r for r in ag_rows if not r[3]]   # agua_continua=False -> alto consumo sem continuidade
    ag_ativo=[r for r in ag_rows if r[3]]       # agua_continua=True  -> vazamento ativo
    # reclassifica: vazamento ativo = continua nos ultimos 2 dias; resolvido = tinha alerta mas parou
    ag_ativo_real=[r for r in ag_rows if r[3]]
    ag_resolvido=[r for r in ag_rows if not r[3] and r[1]>0]
    def _li_agua(rows):
        li=""
        for nome,dias,ultimo,continua,exc_m3,exc_rs,aprox in rows:
            exc_txt=""
            if exc_m3 and exc_m3>0:
                exc_txt=" &mdash; "+_frase_excedente(exc_m3,"m3",exc_rs,aprox)
            li+=f'<li>{nome}: {dias} dias (ultimo dia {ultimo:02d}){exc_txt}</li>'
        return li
    ag_html=""
    if ag_ativo_real:
        li=_li_agua(ag_ativo_real)
        ag_html+=(f'<div style="margin-bottom:8px;"><b style="color:{COR["vermelho"]};">Agua: Vazamento ATIVO (acione manutencao):</b>'
                  f'<ul style="margin:4px 0 0 18px;padding:0;font-size:13px;">{li}</ul></div>')
    if ag_resolvido:
        li=_li_agua(ag_resolvido)
        ag_html+=(f'<div style="margin-bottom:8px;"><b style="color:{COR["azul"]};">Agua: Vazamento muito provavelmente resolvido (fique atento):</b>'
                  f'<ul style="margin:4px 0 0 18px;padding:0;font-size:13px;">{li}</ul></div>')
    if not ag_html:
        ag_html=f'<span style="font-size:12px;color:{COR["cinza_claro"]};">Sem alertas de agua na madrugada.</span>'
    return (f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin:8px 0 16px;">'
            f'<tr><td style="background:{COR["amarelo_bg"]};border:1px solid #f2d9b5;border-radius:10px;padding:14px 18px;"><table role="presentation" width="100%" cellpadding="0" cellspacing="0"><tr>'
            f'<td width="50%" valign="top" style="padding-right:14px;border-right:1px solid #f2d9b5;">{en_html}</td>'
            f'<td width="50%" valign="top" style="padding-left:14px;">{ag_html}</td>'
            f'</tr></table></td></tr></table>')

def html_doc(corpo):
    return f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width">
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
</head><body style="margin:0;padding:16px;background:#eef1f5;font-family:{POPPINS};color:{COR['texto']};">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0"><tr><td align="center">
<table role="presentation" width="820" cellpadding="0" cellspacing="0" style="max-width:820px;background:#fff;border-radius:14px;">
<tr><td style="padding:26px 30px;">{corpo}</td></tr></table></td></tr></table></body></html>"""
def h1(t): return f'<div style="font-size:24px;font-weight:700;color:{COR["azul"]};">{t}</div>'
def sub(t): return f'<div style="color:{COR["cinza"]};font-size:13px;margin:2px 0 16px;">{t}</div>'
def linha_fina(): return f'<div style="border-top:1px solid {COR["borda"]};margin:22px 0;"></div>'

def cor_bandeira(b, faixas=None):
    """Verde no topo, vermelho na base, laranja no meio - para qualquer esquema."""
    faixas=faixas or BANDEIRAS_8
    if b not in faixas:
        return COR["cinza"]
    i=faixas.index(b); n=len(faixas)
    if i < n/3: return COR["verde"]
    if i < 2*n/3: return COR["laranja"]
    return COR["vermelho"]

_ESCADA_CORES_BASE=["#1a9850","#66bd63","#a6d96a","#d9ef8b","#fee08b","#fdae61","#f46d43","#d73027"]
def _cores_faixas(faixas):
    """Mapeia N faixas em N cores do verde ao vermelho."""
    n=len(faixas)
    if n<=1: return {faixas[0]:"#1a9850"} if faixas else {}
    idx=[round(i*(len(_ESCADA_CORES_BASE)-1)/(n-1)) for i in range(n)]
    return {faixas[i]:_ESCADA_CORES_BASE[idx[i]] for i in range(n)}

def escada_eficiencia(band_atual, faixas=None):
    """Escadinha compacta (Outlook-safe) adaptada ao esquema de faixas do cluster."""
    faixas=faixas or BANDEIRAS_8
    cores=_cores_faixas(faixas)
    linhas=""
    for i,b in enumerate(faixas):
        larg=40+i*(48/max(len(faixas)-1,1))
        atual=(b==band_atual)
        cor=cores.get(b,"#999")
        marca=(f'<td style="padding-left:6px;font-weight:700;color:{COR["texto"]};font-size:10px;white-space:nowrap;">&#9664; sua loja</td>'
               if atual else '<td></td>')
        borda="border:2px solid #111;" if atual else ""
        linhas+=f"""<tr>
          <td width="24" style="font-weight:700;font-size:10px;color:{COR['texto']};text-align:right;padding-right:5px;">{b}</td>
          <td width="150">
            <table role="presentation" cellpadding="0" cellspacing="0" style="width:{larg:.0f}%;"><tr>
              <td style="background:{cor};height:9px;border-radius:2px;{borda}">&nbsp;</td>
            </tr></table>
          </td>{marca}</tr>"""
    return f"""<table role="presentation" cellpadding="0" cellspacing="0" style="width:100%;">
      <tr><td colspan="3" style="font-size:9px;color:{COR['cinza']};padding-bottom:2px;">Mais eficiente &#9650;</td></tr>
      {linhas}
      <tr><td colspan="3" style="font-size:9px;color:{COR['cinza']};padding-top:2px;">Menos eficiente &#9660;</td></tr>
    </table>"""

def grafico_despesa_meta(serie):
    """Barras agrupadas Consumo em R$ (custo-equivalente) x Meta por mes. serie: [(label, real, meta)]."""
    if not serie:
        return f'<div style="color:{COR["cinza_claro"]};font-size:12px;padding:14px 0;text-align:center;">Sem historico de consumo em R$ x meta.</div>'
    labels=[s[0] for s in serie]
    desp=[round(s[1]) for s in serie]; meta=[round(s[2]) for s in serie]
    return _chart({"type":"bar","data":{"labels":labels,"datasets":[
        {"label":"Consumo em R$","data":desp,"backgroundColor":COR["laranja"]},
        {"label":"Meta (R$)","data":meta,"backgroundColor":"#b9c4d4"}]},
      "options":{"title":{"display":True,"text":"Consumo em R$ x Meta (R$/mes)"},
      "legend":{"display":True,"position":"bottom"},
      "scales":{"yAxes":[{"ticks":{"beginAtZero":True}}]}}},w=520,h=200)

def serie_despesa_meta_12m(bkn, ref_ts, rk, medianas=None, marca=None):
    """v12: Consumo em R$ (real corrigido) x Meta (previsto) por mes, lido do rk JA
    corrigido (fantasma->mediana). Mesma fonte do indice, entao os dois graficos ficam
    perfeitamente consistentes: mesmos meses, mesma logica. Um mes so fica de fora quando
    nao ha total valido (indice NaN)."""
    meses=pd.date_range(end=ref_ts, periods=12, freq="MS")
    sub=rk[(rk["bkn"]==bkn)&(rk["competencia"]<=ref_ts)]
    val={}
    for _,r in sub.iterrows():
        cr=r.get("custo_equivalente_real_score_rs"); cp=r.get("custo_equivalente_previsto_score_rs")
        idx=r.get("indice_eficiencia_mes")
        if pd.notna(idx) and pd.notna(cr) and pd.notna(cp):
            val[pd.Timestamp(r["competencia"]).strftime("%Y-%m")]=(float(cr),float(cp))
    out=[]
    for m in meses:
        k=m.strftime("%Y-%m")
        if k in val:
            out.append((m.strftime("%b/%y"), val[k][0], val[k][1]))
    return out

# ============================ RENDER LOJA ============================
def render_loja(d):
    celulas=""
    for recurso in ["ENERGIA","AGUA","GAS"]:
        info=d["recursos"].get(recurso)
        if not info: continue
        delta=info["delta"]
        seta="&#9650;" if delta>1 else ("&#9660;" if delta<-1 else "=")
        cor_d=COR["vermelho"] if delta>1 else (COR["verde"] if delta<-1 else COR["cinza"])
        # card loja semelhante deste recurso
        comp=info.get("comp")
        comp_html=""
        if comp:
            econ_frase=(f"Alcancando essa loja voce pode economizar ~<b>{brl(comp['economia'])}/mes</b>."
                        if comp.get("economia") is not None else "")
            temp_frase=""
            if comp.get("temp_alvo") is not None and comp.get("temp_comp") is not None:
                temp_frase=(f'Temperatura parecida (afeta o gasto com ar-condicionado): '
                            f'{comp["temp_comp"]:.0f}&deg;C contra {comp["temp_alvo"]:.0f}&deg;C. ')
            if comp.get("area_alvo") and comp.get("area_comp"):
                area_frase=f'e area parecida ({comp["area_comp"]:.0f} vs {comp["area_alvo"]:.0f} m2). '
            else:
                area_frase='e area (m2) parecida. '
            comp_html=f"""<div style="margin-top:8px;background:{COR['cinza_bg']};border-radius:8px;padding:8px 10px;">
              <div style="font-size:11px;color:{COR['texto']};">
                <b>{comp['nome']}</b> ({comp['regional']}) consumiu <b style="color:{COR['verde']};">{comp['pct']:.0f}% menos</b>.
                Trafego parecido: {num(comp['trafego'])} vs {num(info['trafego'])} pagamentos {area_frase}
                {temp_frase}{econ_frase}</div></div>"""
        # consumo fantasma -> "Ainda sem dado"; despesa None -> "sob revisao"
        if info.get("fantasma"):
            valor_consumo=f'<span style="font-size:16px;color:{COR["cinza_claro"]};font-weight:600;">Ainda sem dado</span>'
            linha_var=f'<div style="color:{COR["cinza_claro"]};font-size:11px;margin-top:4px;">Leitura em validacao.</div>'
        else:
            valor_consumo=f'{num(info["consumo"])}<span style="font-size:13px;color:{COR["cinza"]};"> {UNIDADE[recurso]}</span>'
            linha_var=f'<div style="color:{cor_d};font-size:13px;font-weight:600;margin-top:4px;">{seta} {abs(delta):.0f}% vs mes anterior</div>'
        desp_html=(f'<span style="font-size:12px;color:{COR["cinza_claro"]};font-weight:400;"> &middot; {brl(info["despesa"])}</span>'
                   if info.get("despesa") is not None
                   else f'<span style="font-size:11px;color:{COR["cinza_claro"]};font-weight:400;"> &middot; Despesa sob revisao</span>')
        diverge_html=(f'<div style="font-size:10px;color:{COR["cinza"]};margin-top:6px;font-style:italic;">'
                      f'A despesa em R$ deste recurso costuma divergir do valor final do P&L. Considere-a uma aproximacao.</div>'
                      if info.get("diverge_sap") else "")
        celulas+=f"""<td width="33%" valign="top" style="padding:6px;">
          <table role="presentation" width="100%" cellpadding="0" cellspacing="0"
            style="border:1px solid {COR['borda']};border-left:5px solid {COR_REC[recurso]};border-radius:10px;">
            <tr><td style="padding:14px 16px;">
            <div style="color:{COR['cinza']};font-size:12px;letter-spacing:.5px;">{ROTULO[recurso].upper()}</div>
            <div style="font-size:28px;font-weight:700;color:{COR['azul']};line-height:1.1;">
              {valor_consumo}{desp_html}</div>
            {linha_var}
            {diverge_html}
            {comp_html}
          </td></tr></table></td>"""
    resumo="".join(f'<div style="margin-bottom:8px;font-size:14px;">{l}</div>' for l in d["resumo"])
    graf_consumo="".join(f'<div style="margin:10px 0;">{g}</div>' for g in d["graficos_consumo"])
    corpo=f"""
    {h1('Fatura Unica de Utilidades')}
    {sub(f"{d['nome']} &middot; {d['cidade']} &middot; {d['mes_label']}")}
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0"
      style="background:{COR['amarelo_bg']};border:1px solid #f2d9b5;border-radius:10px;">
      <tr><td style="padding:16px 20px;"><div style="font-weight:700;color:#c9781f;margin-bottom:10px;">RESUMO CHAVE</div>{resumo}</td></tr></table>
    {d.get('bloco_alerta','')}
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin-top:16px;">
      <tr><td style="font-size:13px;color:{COR['cinza']};">CUSTO TOTAL DO MES</td>
      <td align="right" style="font-size:28px;font-weight:700;color:{COR['laranja']};">{brl(d['custo_total'])}</td></tr></table>
    <div style="font-size:11px;color:{COR['cinza']};margin-top:4px;background:{COR['cinza_bg']};border-radius:6px;padding:6px 10px;">
      Os valores de despesa (energia, agua e gas) podem ser alterados, pois ainda ocorrera o fechamento financeiro do mes.</div>
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin-top:8px;"><tr>{celulas}</tr></table>
    <div style="font-size:10px;color:{COR['cinza_claro']};margin-top:2px;">1 trafego = 1 pagamento no PDV.</div>
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin-top:16px;"><tr>
      <td width="100%" valign="top" style="padding:6px;">
        <table role="presentation" width="100%" style="background:{COR['verde_bg']};border-radius:10px;"><tr><td style="padding:12px 16px;">
        <div style="color:{cor_bandeira(d['bandeira'])};font-weight:700;font-size:12px;">EFICIENCIA DA LOJA</div>
        <div style="font-size:10px;color:{COR['cinza']};margin-bottom:6px;">{d.get('texto_ranking','')}</div>
        <table role="presentation" width="100%" cellpadding="0" cellspacing="0"><tr>
          <td width="42%" valign="middle">
            <div style="font-size:34px;font-weight:700;color:{cor_bandeira(d['bandeira'])};line-height:1;">{d['bandeira']}</div>
            <div style="font-size:11px;color:{COR['cinza']};margin-top:4px;">{d['posicao']} &middot; Indice: <b>{d['indice_txt']}</b> &middot; {d['variacao_txt']}</div>
            <div style="font-size:11px;color:{COR['texto']};margin-top:4px;">{d['meta_txt']}</div>
          </td>
          <td width="58%" valign="middle" style="padding-left:10px;">{d['escada']}</td>
        </tr></table>
      </td></tr></table></td></tr></table>
    {linha_fina()}
    <div style="font-weight:700;color:{COR['azul']};margin-bottom:4px;">Indice de Consumo por Meta - ultimos 12 meses</div>
    <div style="font-size:12px;color:{COR['cinza']};margin-bottom:8px;">O indice compara seu consumo com a meta da loja. Abaixo de 100% (linha tracejada) e melhor. A tarifa nao entra nessa conta.</div>
    <div style="margin-bottom:16px;">{d['grafico_indice']}</div>
    <div style="font-weight:700;color:{COR['azul']};margin-bottom:8px;">Consumo por Meta - ultimos 12 meses</div>
    {graf_consumo}
    <div style="font-size:11px;color:{COR['cinza']};">Meses sem leitura confiavel sao omitidos.</div>
    <div style="margin-top:16px;font-size:11px;color:{COR['cinza']};">Acoes conduzidas junto a Manutencao e Operacoes.</div>"""
    return html_doc(corpo)

# ============================ RENDER GRUPO (coord/regional) ============================
def tabela_acima_orcado(titulo, linhas):
    """linhas: dict nome, acima, real, orcado. Top5 pior + Top5 melhor, escala 10 cores."""
    ordenado=sorted(linhas,key=lambda x:x["acima"],reverse=True); n=len(ordenado)
    sel=ordenado[:5]+ordenado[-5:] if n>10 else ordenado
    # mapear rank -> cor (0=pior=vermelho forte)
    body=""
    for row in sel:
        rank=ordenado.index(row)
        # posicao relativa 0..1
        pos=rank/(n-1) if n>1 else 0
        cor=ESCALA10[min(int(pos*10),9)]
        body+=f"""<tr>
          <td style="padding:5px 8px;border:1px solid {COR['borda']};font-size:12px;border-left:4px solid {cor};">{row['nome']}</td>
          <td align="right" style="padding:5px 8px;border:1px solid {COR['borda']};font-size:12px;">{brl(row['acima'])}</td>
          <td align="right" style="padding:5px 8px;border:1px solid {COR['borda']};font-size:12px;color:{COR['cinza']};">{brl(row['real'])}</td>
          <td align="right" style="padding:5px 8px;border:1px solid {COR['borda']};font-size:12px;color:{COR['cinza']};">{brl(row['orcado'])}</td></tr>"""
    return f"""<div style="margin-bottom:18px;"><div style="font-weight:700;color:{COR['azul']};margin-bottom:6px;">{titulo}</div>
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;">
      <tr><th style="background:{COR['azul']};color:#fff;font-size:11px;padding:5px 8px;text-align:left;">Loja</th>
      <th style="background:{COR['azul']};color:#fff;font-size:11px;padding:5px 8px;text-align:right;">Acima do Orcado</th>
      <th style="background:{COR['azul']};color:#fff;font-size:11px;padding:5px 8px;text-align:right;">Despesa Real</th>
      <th style="background:{COR['azul']};color:#fff;font-size:11px;padding:5px 8px;text-align:right;">Despesa Orcada</th></tr>
      {body}</table></div>"""

def tabelas_consumo_lado_a_lado(rank_consumo, grifadas=None, um_por_setor=False,
                                so_ofensoras_grifadas=False):
    """3 tabelas de consumo FISICO acima do esperado (kWh/m3/kg + % acima), uma por recurso.
    v13.2: so_ofensoras_grifadas (Regional) mostra APENAS as lojas ofensoras grifadas, sem o
    top5/bottom5. Senao, top5 pior + top5 melhor + grifadas forcadas. Ranqueado por % acima."""
    grifadas=grifadas or set()
    cols=""
    for recurso in ["ENERGIA","AGUA","GAS"]:
        linhas=rank_consumo.get(recurso)
        if not linhas: continue
        un=UNIDADE[recurso]
        com_dado=[r for r in linhas if not r.get("sem_dado")]
        ordenado=sorted(com_dado,key=lambda x:x["pct"],reverse=True); n=len(ordenado)
        grif_rows=[r for r in linhas if r.get("grifada") and str(r.get("bkn","")) in grifadas]
        if um_por_setor:
            vistos=set(); filtr=[]
            for r in sorted(grif_rows,key=lambda x:(x.get("sem_dado",False), -x.get("pct",0))):
                s=r.get("setor","")
                if s in vistos: continue
                vistos.add(s); filtr.append(r)
            grif_rows=filtr
        if so_ofensoras_grifadas:
            sel=list(grif_rows)   # so as grifadas (ofensoras), sem top/bottom
        else:
            base_sel=ordenado[:5]+ordenado[-5:] if n>10 else list(ordenado)
            sel=list(base_sel)
            for r in grif_rows:
                if r not in sel: sel.append(r)
        sel=sorted(sel,key=lambda x:(x.get("sem_dado",False), -x.get("pct",0)))
        body=""
        for row in sel:
            grif=(row.get("grifada") and str(row.get("bkn","")) in grifadas)
            if um_por_setor and grif and row not in grif_rows: grif=False
            bg=f'background:{COR["grifo"]};' if grif else ""
            if row in ordenado:
                rank=ordenado.index(row); pos=rank/(n-1) if n>1 else 0; cor=ESCALA10[min(int(pos*10),9)]
            else:
                cor=COR["cinza_claro"]
            ldb=COR["grifo_borda"] if grif else cor
            n_tag=(f' <b style="color:{COR["azul"]};">({row.get("num")})</b>' if row.get("num") else "")
            if row.get("sem_dado"):
                body+=f"""<tr><td style="padding:3px 5px;border:1px solid {COR['borda']};font-size:9px;border-left:3px solid {ldb};{bg}">{row['nome']}{n_tag}</td>
                  <td colspan="3" align="center" style="padding:3px 4px;border:1px solid {COR['borda']};font-size:8px;color:{COR['cinza_claro']};{bg}">sem dado confiavel neste recurso</td></tr>"""
            else:
                pct=row["pct"]; pcor=COR['vermelho'] if pct>0 else COR['verde']
                body+=f"""<tr><td style="padding:3px 5px;border:1px solid {COR['borda']};font-size:9px;border-left:3px solid {ldb};{bg}">{row['nome']}{n_tag}</td>
                  <td align="right" style="padding:3px 4px;border:1px solid {COR['borda']};font-size:9px;font-weight:600;color:{pcor};{bg}">{pct:+.0f}%</td>
                  <td align="right" style="padding:3px 4px;border:1px solid {COR['borda']};font-size:9px;color:{COR['cinza']};{bg}">{num(row.get('real',0))}</td>
                  <td align="right" style="padding:3px 4px;border:1px solid {COR['borda']};font-size:9px;color:{COR['cinza']};{bg}">{num(row.get('orcado',0))}</td></tr>"""
        cols+=f"""<td width="33%" valign="top" style="padding:3px;">
          <div style="font-weight:700;font-size:11px;color:{COR_REC[recurso]};margin-bottom:4px;">{ROTULO[recurso]} ({un})</div>
          <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;border-top:2px solid {COR_REC[recurso]};">
          <tr><th style="font-size:8px;color:{COR['cinza']};text-align:left;padding:2px 5px;">Loja</th>
          <th style="font-size:8px;color:{COR['cinza']};text-align:right;padding:2px 4px;">Acima</th>
          <th style="font-size:8px;color:{COR['cinza']};text-align:right;padding:2px 4px;">Real</th>
          <th style="font-size:8px;color:{COR['cinza']};text-align:right;padding:2px 4px;">Esperado</th></tr>
          {body}</table></td>"""
    return f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0"><tr>{cols}</tr></table>'

def _tabela_lojas_acao(lojas):
    """Tabela simples das lojas que devem bater a meta (Acao)."""
    if not lojas: return ""
    body=""
    for x in lojas:
        setor=f' <span style="color:{COR["cinza"]};font-size:10px;">({x["setor"]})</span>' if x.get("setor") else ""
        body+=(f'<tr><td style="padding:4px 8px;border:1px solid {COR["borda"]};font-size:11px;">{x["nome"]}{setor}</td></tr>')
    return (f'<div style="font-weight:700;font-size:12px;color:{COR["azul"]};margin:8px 0 4px;">Lojas para cobrar</div>'
            f'<table role="presentation" width="100%" style="border-collapse:collapse;">{body}</table>')

def _tabelas_regional_acao(lojas, setores_indice, marca_grupo, setor_grupo, ind_grupo):
    """Regional: tabela de SETORES a cobrar + tabela de LOJAS (2 por setor) relacionadas.
    So mostra lojas cujos setores estao na tabela de setores (relacao garantida)."""
    if not lojas: return ""
    # setores presentes entre as lojas da acao, ordenados por pior contribuicao
    from collections import defaultdict
    por_setor=defaultdict(list)
    for x in lojas:
        if x.get("setor"): por_setor[x["setor"]].append(x)
    if not por_setor:
        return _tabela_lojas_acao(lojas)
    # tabela de setores: indice do setor (se disponivel)
    setor_rows=""
    setores_ordenados=sorted(por_setor.keys(),
        key=lambda s: setores_indice.get((marca_grupo,s), 1.0) if setores_indice else 1.0, reverse=True)
    for s in setores_ordenados:
        vi=setores_indice.get((marca_grupo,s)) if setores_indice else None
        vtxt=f'{vi*100:.0f}%' if vi is not None else '-'
        setor_rows+=(f'<tr><td style="padding:4px 8px;border:1px solid {COR["borda"]};font-size:11px;">{s}</td>'
                     f'<td align="right" style="padding:4px 8px;border:1px solid {COR["borda"]};font-size:11px;">{vtxt}</td></tr>')
    # tabela de lojas: ate 2 por setor
    loja_rows=""
    for s in setores_ordenados:
        for x in por_setor[s][:2]:
            loja_rows+=(f'<tr><td style="padding:4px 8px;border:1px solid {COR["borda"]};font-size:11px;">{x["nome"]}</td>'
                        f'<td style="padding:4px 8px;border:1px solid {COR["borda"]};font-size:10px;color:{COR["cinza"]};">{s}</td></tr>')
    return (f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0"><tr>'
            f'<td width="45%" valign="top" style="padding:4px;">'
            f'<div style="font-weight:700;font-size:12px;color:{COR["azul"]};margin-bottom:4px;">Setores a cobrar (reduzir indice)</div>'
            f'<table role="presentation" width="100%" style="border-collapse:collapse;">'
            f'<tr><th style="text-align:left;font-size:10px;color:{COR["cinza"]};padding:2px 8px;">Setor</th>'
            f'<th style="text-align:right;font-size:10px;color:{COR["cinza"]};padding:2px 8px;">Indice</th></tr>{setor_rows}</table></td>'
            f'<td width="55%" valign="top" style="padding:4px;">'
            f'<div style="font-weight:700;font-size:12px;color:{COR["azul"]};margin-bottom:4px;">Lojas relacionadas (2 por setor)</div>'
            f'<table role="presentation" width="100%" style="border-collapse:collapse;">'
            f'<tr><th style="text-align:left;font-size:10px;color:{COR["cinza"]};padding:2px 8px;">Loja</th>'
            f'<th style="text-align:left;font-size:10px;color:{COR["cinza"]};padding:2px 8px;">Setor</th></tr>{loja_rows}</table></td>'
            f'</tr></table>')

def card_bandeira_grupo(d, tipo, is_regional=False):
    sim=d.get("simulacao",{}) or {}
    sim_txt=sim.get("texto","")
    mg=d.get("msg_grupo")
    meta_setor=d.get("meta_setor")   # item 4: comp_setor removido (redundante com meta_setor)
    # item 5: parabens (mudanca de bandeira) + META ficam a DIREITA da escadinha
    lado_partes=[p for p in [mg, meta_setor] if p]
    lado_html=""
    if lado_partes:
        lado_html="<br><br>".join(lado_partes)
    else:
        lado_html=(f'<span style="color:{COR["cinza"]};font-size:12px;">'
                   f'Voce esta na melhor posicao entre os pares da sua marca. Mantenha o desempenho.</span>')
    # item 6/7: acao (com grifo, sem tabela 'Lojas a cobrar') fica DIRETAMENTE abaixo da escadinha
    acao_bloco=""
    if sim_txt:
        acao_bloco=(f'<div style="background:{COR["amarelo_bg"]};border:1px solid #f2d9b5;border-radius:10px;'
                    f'padding:12px 16px;margin:14px 0 16px;font-size:13px;">{sim_txt}</div>')
    # cards do topo (item 8: INDICE MEDIO 12M com a variacao vs mes anterior embutida)
    ind_ant=d.get("ind_medio_ant"); ind12=d.get("indice_12m")
    var_html=""
    if ind_ant is not None and ind12 is not None and ind_ant>0:
        dpp=(ind12-ind_ant)*100
        cor=COR["verde"] if dpp<0 else (COR["vermelho"] if dpp>0 else COR["cinza"])
        seta="&#9660;" if dpp<0 else ("&#9650;" if dpp>0 else "=")
        if abs(dpp)>=0.5:
            var_html=(f'<div style="font-size:11px;color:{cor};font-weight:600;margin-top:2px;">'
                      f'{seta} {abs(dpp):.0f}% vs mes anterior</div>')
    return f"""<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:16px;"><tr>
      <td width="25%" style="padding:6px;"><table role="presentation" width="100%" style="background:{COR['verde_bg']};border-radius:10px;"><tr><td style="padding:12px 14px;">
        <div style="font-size:11px;color:{COR['cinza']};">BANDEIRA {tipo}</div>
        <div style="font-size:30px;font-weight:700;color:{cor_bandeira(d['bandeira'])};">{d['bandeira']}</div></td></tr></table></td>
      <td width="25%" style="padding:6px;"><table role="presentation" width="100%" style="background:{COR['cinza_bg']};border-radius:10px;"><tr><td style="padding:12px 14px;">
        <div style="font-size:11px;color:{COR['cinza']};">POSICAO ENTRE PARES</div>
        <div style="font-size:20px;font-weight:700;color:{COR['azul']};">{d['posicao_pares']}</div></td></tr></table></td>
      <td width="25%" style="padding:6px;"><table role="presentation" width="100%" style="background:{COR['cinza_bg']};border-radius:10px;"><tr><td style="padding:12px 14px;">
        <div style="font-size:11px;color:{COR['cinza']};">INDICE MEDIO 12M</div>
        <div style="font-size:20px;font-weight:700;color:{COR['azul']};">{d['indice_12m']*100:.0f}%</div>{var_html}</td></tr></table></td>
      <td width="25%" style="padding:6px;"><table role="presentation" width="100%" style="background:{COR['vermelho_bg']};border-radius:10px;"><tr><td style="padding:12px 14px;">
        <div style="font-size:11px;color:{COR['cinza']};">ACIMA DO ORCADO</div>
        <div style="font-size:20px;font-weight:700;color:{COR['vermelho']};">{brl(d['acima_total'])}</div></td></tr></table></td>
    </tr></table>
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:6px;"><tr>
      <td width="58%" valign="top" style="padding-right:14px;">{d.get('escada','')}</td>
      <td width="42%" valign="middle" style="padding-left:10px;">
        <div style="background:{COR['cinza_bg']};border-radius:10px;padding:12px 16px;font-size:13px;">{lado_html}</div>
      </td>
    </tr></table>
    {acao_bloco}"""

def tabela_por_tipo_loja(por_tipo):
    """Tabela de consumo medio + despesa media por tipo de loja (Rua/Shopping/Airport)."""
    if not por_tipo: return ""
    linhas=""
    for tipo in ["RUA","SHOPPING","AIRPORT"]:
        dd=por_tipo.get(tipo)
        if not dd: continue
        cels=f'<td style="padding:5px 8px;border:1px solid {COR["borda"]};font-weight:600;font-size:11px;">{tipo.title()}</td>'
        for rec in ["ENERGIA","AGUA","GAS"]:
            v=dd.get(rec)
            if v:
                cels+=f'<td align="right" style="padding:5px 8px;border:1px solid {COR["borda"]};font-size:11px;">{num(v["consumo"])} {UNIDADE[rec]}<br><span style="color:{COR["cinza"]};">{brl(v["despesa"])}</span></td>'
            else:
                cels+=f'<td align="center" style="padding:5px 8px;border:1px solid {COR["borda"]};font-size:11px;color:{COR["cinza_claro"]};">-</td>'
        linhas+=f"<tr>{cels}</tr>"
    if not linhas: return ""
    return (f'<div style="font-weight:700;color:{COR["azul"]};margin:12px 0 6px;font-size:13px;">Media por tipo de loja (consumo / despesa)</div>'
            f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;">'
            f'<tr><th style="text-align:left;font-size:10px;color:{COR["cinza"]};padding:4px 8px;">Tipo</th>'
            f'<th style="text-align:right;font-size:10px;color:{COR["cinza"]};padding:4px 8px;">Energia</th>'
            f'<th style="text-align:right;font-size:10px;color:{COR["cinza"]};padding:4px 8px;">Agua</th>'
            f'<th style="text-align:right;font-size:10px;color:{COR["cinza"]};padding:4px 8px;">Gas</th></tr>{linhas}</table>')

def cards_consumo_medio(cons_medio):
    """Cards de consumo medio por recurso (energia/agua/gas) com despesa media."""
    if not cons_medio: return ""
    cel=""
    for recurso in ["ENERGIA","AGUA","GAS"]:
        cm=cons_medio.get(recurso)
        if not cm: continue
        cel+=f"""<td width="33%" valign="top" style="padding:6px;">
          <table role="presentation" width="100%" style="border:1px solid {COR['borda']};border-left:5px solid {COR_REC[recurso]};border-radius:10px;"><tr><td style="padding:12px 14px;">
          <div style="color:{COR['cinza']};font-size:11px;letter-spacing:.5px;">{ROTULO[recurso].upper()} - MEDIA POR LOJA</div>
          <div style="font-size:22px;font-weight:700;color:{COR['azul']};">{num(cm['consumo'])} <span style="font-size:12px;color:{COR['cinza']};">{UNIDADE[recurso]}</span></div>
          <div style="font-size:12px;color:{COR['cinza']};">Despesa media: <b>{brl(cm['despesa'])}</b> &middot; {cm['n']} lojas</div>
          </td></tr></table></td>"""
    return f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0"><tr>{cel}</tr></table>'

def _uma_loja_por_setor(lista, setor_por_bkn):
    """Regional: mantem apenas a loja mais ofensora (maior |delta|) de cada setor."""
    vistos={}; out=[]
    for x in lista:  # lista ja vem ordenada por relevancia
        s=setor_por_bkn.get(str(x.get("bkn","")),"")
        if s in vistos: continue
        vistos[s]=True; out.append(x)
    return out

def tabela_promo_detra(promotoras, detratoras, grifadas=None, um_por_setor=False,
                       setor_por_bkn=None, top_ofens=None, top_efic=None):
    """Tabelas lado a lado (v13.1): OFENSORAS (esq, indice acima da carteira) e EFICIENTES
    (dir, na media ou abaixo). Coluna 'vs mes anterior' mostra se a loja melhorou/piorou.
    Grifadas destacadas. Regional: 1 loja por setor + limites top_ofens/top_efic."""
    grifadas=grifadas or set()
    if um_por_setor and setor_por_bkn is not None:
        promotoras=_uma_loja_por_setor(promotoras, setor_por_bkn)
        detratoras=_uma_loja_por_setor(detratoras, setor_por_bkn)
    if top_ofens: detratoras=detratoras[:top_ofens]
    if top_efic: promotoras=promotoras[:top_efic]
    def _linhas(lista, cor):
        if not lista: return f'<tr><td colspan="3" style="padding:6px;font-size:11px;color:{COR["cinza_claro"]};">Sem lojas neste grupo.</td></tr>'
        out=""
        for x in lista:
            grif=(str(x.get("bkn","")) in grifadas)
            bg=f'background:{COR["grifo"]};' if grif else ""
            bd=f'border-left:3px solid {COR["grifo_borda"]};' if grif else ""
            n=x.get("num")
            tag=(f' <b style="color:{COR["azul"]};">({n})</b>' if n else "")
            indice=x.get("indice", 100+x["delta"])  # indice absoluto da loja
            vm=x.get("var_mes")
            if vm is None:
                vm_html=f'<span style="color:{COR["cinza_claro"]};">-</span>'
            else:
                vcor=COR["verde"] if vm<0 else (COR["vermelho"] if vm>0 else COR["cinza"])
                seta="&#9660;" if vm<0 else ("&#9650;" if vm>0 else "=")
                vm_html=f'<span style="color:{vcor};">{seta} {abs(vm):.0f} p.p.</span>'
            out+=(f'<tr><td style="padding:4px 8px;border:1px solid {COR["borda"]};font-size:11px;{bg}{bd}">{x["nome"]}{tag}</td>'
                  f'<td align="right" style="padding:4px 8px;border:1px solid {COR["borda"]};font-size:11px;color:{cor};font-weight:600;{bg}">{indice:.0f}%</td>'
                  f'<td align="right" style="padding:4px 8px;border:1px solid {COR["borda"]};font-size:10px;{bg}">{vm_html}</td></tr>')
        return out
    cab=(f'<tr><th style="text-align:left;font-size:9px;color:{COR["cinza"]};padding:2px 8px;">Loja</th>'
         f'<th style="text-align:right;font-size:9px;color:{COR["cinza"]};padding:2px 8px;">Indice</th>'
         f'<th style="text-align:right;font-size:9px;color:{COR["cinza"]};padding:2px 8px;">vs mes ant.</th></tr>')
    detra=_linhas(detratoras, COR["vermelho"])
    promo=_linhas(promotoras, COR["verde"])
    return (f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0"><tr>'
            f'<td width="50%" valign="top" style="padding:4px;">'
            f'<div style="font-weight:700;font-size:12px;color:{COR["vermelho"]};margin-bottom:4px;">Lojas OFENSORAS <span style="font-weight:400;color:{COR["cinza"]};">(indice acima da carteira)</span></div>'
            f'<table role="presentation" width="100%" style="border-collapse:collapse;">{cab}{detra}</table></td>'
            f'<td width="50%" valign="top" style="padding:4px;">'
            f'<div style="font-weight:700;font-size:12px;color:{COR["verde"]};margin-bottom:4px;">Lojas EFICIENTES <span style="font-weight:400;color:{COR["cinza"]};">(indice na media ou abaixo)</span></div>'
            f'<table role="presentation" width="100%" style="border-collapse:collapse;">{cab}{promo}</table></td>'
            f'</tr></table>')

def tabela_setores_mov(setores_mov, top_ofens=None, top_efic=None):
    """Regional (v13.2): 'Setores OFENSORES' (esq, indice medio acima da carteira) e
    'Setores EFICIENTES' (dir). Mostra o indice medio do setor. Limites separados."""
    pior=setores_mov.get("pioraram",[]); melh=setores_mov.get("melhoraram",[])
    if top_ofens: pior=pior[:top_ofens]
    if top_efic: melh=melh[:top_efic]
    def _linhas(lista, cor):
        if not lista: return f'<tr><td colspan="2" style="padding:6px;font-size:11px;color:{COR["cinza_claro"]};">Sem setores neste grupo.</td></tr>'
        out=""
        for x in lista:
            indice=x.get("idx_now",0)*100
            out+=(f'<tr><td style="padding:4px 8px;border:1px solid {COR["borda"]};font-size:11px;">{x["setor"]}</td>'
                  f'<td align="right" style="padding:4px 8px;border:1px solid {COR["borda"]};font-size:11px;color:{cor};font-weight:600;">'
                  f'{indice:.0f}%</td></tr>')
        return out
    d=_linhas(pior, COR["vermelho"]); mm=_linhas(melh, COR["verde"])
    return (f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:6px;"><tr>'
            f'<td width="50%" valign="top" style="padding:4px;">'
            f'<div style="font-weight:700;font-size:12px;color:{COR["vermelho"]};margin-bottom:4px;">Setores OFENSORES <span style="font-weight:400;color:{COR["cinza"]};">(indice medio acima da carteira)</span></div>'
            f'<table role="presentation" width="100%" style="border-collapse:collapse;">{d}</table></td>'
            f'<td width="50%" valign="top" style="padding:4px;">'
            f'<div style="font-weight:700;font-size:12px;color:{COR["verde"]};margin-bottom:4px;">Setores EFICIENTES <span style="font-weight:400;color:{COR["cinza"]};">(na media ou abaixo)</span></div>'
            f'<table role="presentation" width="100%" style="border-collapse:collapse;">{mm}</table></td>'
            f'</tr></table>')

def tabela_por_tipo_loja_real(por_tipo_loja):
    """Media consumo/despesa por tipo_loja REAL (FC, FS, Core, etc.), so os que o gestor tem."""
    if not por_tipo_loja: return ""
    linhas=""
    for tl,dd in sorted(por_tipo_loja.items(), key=lambda x:-x[1]["n"]):
        rec=dd["rec"]
        cels=f'<td style="padding:5px 8px;border:1px solid {COR["borda"]};font-weight:600;font-size:11px;">{tl} ({dd["n"]})</td>'
        for r in ["ENERGIA","AGUA","GAS"]:
            v=rec.get(r)
            if v:
                cels+=f'<td align="right" style="padding:5px 8px;border:1px solid {COR["borda"]};font-size:11px;">{num(v["consumo"])} {UNIDADE[r]}<br><span style="color:{COR["cinza"]};">{brl(v["despesa"])}</span></td>'
            else:
                cels+=f'<td align="center" style="padding:5px 8px;border:1px solid {COR["borda"]};font-size:11px;color:{COR["cinza_claro"]};">-</td>'
        linhas+=f"<tr>{cels}</tr>"
    return (f'<div style="font-weight:700;color:{COR["azul"]};margin:12px 0 6px;font-size:13px;">Media por tipo de loja (consumo / despesa)</div>'
            f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;">'
            f'<tr><th style="text-align:left;font-size:10px;color:{COR["cinza"]};padding:4px 8px;">Tipo (n lojas)</th>'
            f'<th style="text-align:right;font-size:10px;color:{COR["cinza"]};padding:4px 8px;">Energia</th>'
            f'<th style="text-align:right;font-size:10px;color:{COR["cinza"]};padding:4px 8px;">Agua</th>'
            f'<th style="text-align:right;font-size:10px;color:{COR["cinza"]};padding:4px 8px;">Gas</th></tr>{linhas}</table>')

def render_coordenador(d):
    grif=d.get("grifadas",set())
    # item 8: promo/detra direto abaixo da 'Acao' (que ja esta no card). PIORARAM esq, MELHORARAM dir.
    # item 10: 'Consumo acima do orcado' imediatamente abaixo de PIORARAM/MELHORARAM.
    corpo=f"""{h1('Painel de Utilidades - Coordenador')}
    {sub(f"{d['nome']} &middot; {d['mes_label']}")}
    {card_bandeira_grupo(d,'DO COORDENADOR')}
    {tabela_promo_detra(promotoras=d.get('promotoras',[]), detratoras=d.get('detratoras',[]), grifadas=grif)}
    <div style="font-weight:700;color:{COR['azul']};margin:12px 0 6px;">Consumo acima do esperado por utility (% e unidade fisica)</div>
    {tabelas_consumo_lado_a_lado(d["rank_consumo"], grifadas=grif)}
    {d.get('bloco_alerta_coord','')}
    {linha_fina()}
    <div style="font-weight:700;color:{COR['azul']};margin:10px 0 6px;">Consumo medio por recurso</div>
    {cards_consumo_medio(d.get('cons_medio',{}))}
    {tabela_por_tipo_loja_real(d.get('por_tipo_loja',{}))}
    {linha_fina()}
    <div style="font-weight:700;color:{COR['azul']};margin-bottom:8px;">Indice de Consumo por Meta das lojas - ultimos 12 meses</div>
    <div style="margin-bottom:4px;">{d.get('grafico_indice','')}</div>
    {("<div style='font-size:11px;color:"+chr(35)+"6b7a8d;margin-bottom:16px;'>Neste mes, "+d['legenda_movimentadores']+".</div>") if d.get('legenda_movimentadores') else ''}
    <div style="font-size:12px;color:{COR['cinza']};margin-top:10px;">Cobertura de dados: {d['cobertura']} lojas nos rankings (demais com dado fragil).</div>"""
    return html_doc(corpo)

def render_regional(d):
    grif=d.get("grifadas",set())
    spb=d.get("setor_por_bkn",{})
    # item 3: tabelas de SETORES que pioraram/melhoraram acima das tabelas de lojas.
    # Lojas: 1 por setor (a mais ofensora). Grifo nas ofensoras. Consumo abaixo, com grifo 1/setor.
    corpo=f"""{h1('Painel de Utilidades - Gerente Regional')}
    {sub(f"{d['nome']} &middot; {d['mes_label']}")}
    {card_bandeira_grupo(d,'DA REGIONAL',is_regional=True)}
    {tabela_setores_mov(d.get('setores_mov',{'pioraram':[],'melhoraram':[]}), top_ofens=3, top_efic=2)}
    {tabela_promo_detra(promotoras=d.get('promotoras',[]), detratoras=d.get('detratoras',[]), grifadas=grif, um_por_setor=True, setor_por_bkn=spb, top_ofens=3, top_efic=3)}
    <div style="font-weight:700;color:{COR['azul']};margin:12px 0 6px;">Consumo acima do esperado por utility (% e unidade fisica)</div>
    {tabelas_consumo_lado_a_lado(d["rank_consumo"], grifadas=grif, um_por_setor=True, so_ofensoras_grifadas=True)}
    {d.get('bloco_alerta_reg','')}
    {linha_fina()}
    <div style="font-weight:700;color:{COR['azul']};margin:10px 0 6px;">Consumo medio por recurso</div>
    {cards_consumo_medio(d.get('cons_medio',{}))}
    {tabela_por_tipo_loja_real(d.get('por_tipo_loja',{}))}
    {linha_fina()}
    <div style="font-weight:700;color:{COR['azul']};margin-bottom:8px;">Indice de Consumo por Meta das lojas - ultimos 12 meses</div>
    <div style="margin-bottom:4px;">{d.get('grafico_indice','')}</div>
    {("<div style='font-size:11px;color:"+chr(35)+"6b7a8d;margin-bottom:16px;'>Neste mes, "+d['legenda_movimentadores']+".</div>") if d.get('legenda_movimentadores') else ''}"""
    return html_doc(corpo)

# ============================ MONTAGEM LOJA ============================
def _frase_indice(indice_mes, variacao_txt):
    """Trecho padrao com o indice e sua variacao, usado em todas as mensagens de bandeira."""
    if indice_mes is None:
        return ""
    pi=indice_mes*100
    return (f' Seu Indice de Consumo por Meta foi <b>{pi:.0f}%</b> (quanto menor, melhor)'
            f' e {variacao_txt} em relacao ao mes passado.')

def mensagem_bandeira(bkn, band_atual, band_prev_map, indice_mes, prev_ts, rk,
                      variacao_txt="", loja_nova=False, faixas=None):
    """Linha unica do Resumo Chave com bandeira + indice + variacao (item 2).
    Cobre: subiu / caiu-mas-eficiente / caiu-de-fato / manteve / loja nova.
    Sempre retorna uma frase (nunca None) quando ha bandeira valida."""
    faixas=faixas or BANDEIRAS_8
    if band_atual not in faixas:
        return None
    frase_idx=_frase_indice(indice_mes, variacao_txt)
    if loja_nova:
        return (f'<span style="color:{COR["azul"]};font-weight:700;">Bem-vinda!</span> '
                f'Esta e a primeira analise da sua loja. Sua bandeira inicial e <b>{band_atual}</b>.'
                f'{frase_idx}')
    prev=band_prev_map.get(bkn)
    if not prev or prev not in faixas:
        return (f'<b>Geral:</b> sua loja esta na bandeira <b>{band_atual}</b>.{frase_idx}')
    i_atual=faixas.index(band_atual); i_prev=faixas.index(prev)
    if i_atual < i_prev:  # SUBIU
        return (f'<span style="color:{COR["verde"]};font-weight:700;">Parabens!</span> '
                f'Sua loja subiu da bandeira <b>{prev}</b> para <b>{band_atual}</b>.{frase_idx} '
                f'Continue com o bom desempenho e siga o Manual de Boas Praticas de Utilidades.')
    if i_atual > i_prev:  # CAIU
        prev_ind=rk[(rk["bkn"]==bkn)&(rk["competencia"]==prev_ts)]
        piorou_propria=False
        if indice_mes is not None and not prev_ind.empty and pd.notna(prev_ind.iloc[0]["indice_eficiencia_mes"]):
            piorou_propria = indice_mes > prev_ind.iloc[0]["indice_eficiencia_mes"] + 0.01
        if not piorou_propria:
            return (f'<span style="color:{COR["laranja"]};font-weight:700;">Aviso:</span> '
                    f'sua loja passou da bandeira <b>{prev}</b> para <b>{band_atual}</b>, mas isso ocorreu '
                    f'porque outras lojas melhoraram mais neste mes.{frase_idx} '
                    f'Continue assim para recuperar a posicao.')
        return (f'<span style="color:{COR["vermelho"]};font-weight:700;">Atencao:</span> '
                f'sua loja caiu da bandeira <b>{prev}</b> para <b>{band_atual}</b>.{frase_idx} '
                f'Reforce a rotina do Manual de Boas Praticas de Utilidades para recuperar o desempenho.')
    # MANTEVE (item CUSTO TOTAL: notificar mesmo assim, com o indice)
    return (f'<b>Geral:</b> sua loja manteve a bandeira <b>{band_atual}</b>.{frase_idx} '
            f'Siga o Manual de Boas Praticas para buscar a proxima faixa.')


def dados_loja(bkn, ref_ts, prev_ts, flr, cmp, rk, hist, band_loja, fronteiras_cluster, band_loja_prev,
               medianas=None, pools_comp=None, faixas_loja=None, cluster_loja=None,
               texto_ranking=None):
    ref=flr[(flr["bkn"]==bkn)&(flr["competencia"]==ref_ts)]
    if ref.empty: return None
    base=ref.iloc[0]; recursos={}; custo_total=0.0; grafs=[]
    c=cmp[(cmp["bkn"]==bkn)&(cmp["competencia"]==ref_ts)]
    comp_row=c.iloc[0] if not c.empty else None
    marca=base.get("marca","")
    meu_cl=(cluster_loja or {}).get(bkn)
    cluster_alvo=meu_cl[1] if meu_cl else cluster_sol(marca, base.get("tipo_loja"), base.get("tipo_area"), bkn)
    area_alvo=pd.to_numeric(base.get("area_vendas_m2"),errors="coerce")
    temp_alvo=(pools_comp or {}).get("_temp_map",{}).get(str(bkn)) if pools_comp else None
    for recurso in ["ENERGIA","AGUA","GAS"]:
        r=ref[ref["recurso"]==recurso]
        if r.empty: continue
        r=r.iloc[0]
        fragil=dado_fragil(r["flag_qualidade_consumo"])
        # --- Regra A: consumo fantasma ---
        med=(medianas or {}).get((marca,recurso))
        fantasma=consumo_fantasma(r.get("consumo_real"), r.get("consumo_previsto"), med)
        consumo_val = None if fantasma else float(r["consumo_real"])
        # --- Regra B/C: despesa ---
        desp, desp_origem = despesa_recurso(r)
        if desp is not None: custo_total+=desp
        # variacao mes anterior (so se ambos meses tem consumo valido)
        delta=0.0
        if not fantasma:
            p=flr[(flr["bkn"]==bkn)&(flr["competencia"]==prev_ts)&(flr["recurso"]==recurso)]
            if not p.empty:
                pc=p.iloc[0]["consumo_real"]
                if pd.notna(pc) and pc>0:
                    delta=(consumo_val/pc-1)*100
        # --- comparavel por recurso (nao mostra se fragil ou fantasma) ---
        comp=None
        if not fragil and not fantasma and pools_comp is not None:
            comp=comparavel_por_recurso(bkn, marca, recurso, consumo_val,
                                        r.get("trafego_real"), desp, pools_comp[recurso],
                                        cluster_alvo=cluster_alvo, temp_alvo=temp_alvo,
                                        area_alvo=(float(area_alvo) if pd.notna(area_alvo) else None))
        recursos[recurso]={"consumo":consumo_val,"delta":delta,"despesa":desp,
                           "despesa_origem":desp_origem,
                           "diverge_sap":((str(bkn),recurso) in DIVERGENCIA_SAP),
                           "trafego":(float(r["trafego_real"]) if pd.notna(r.get("trafego_real")) else 0),
                           "comp":comp,"fragil":fragil,"fantasma":fantasma}
        grafs.append(grafico_consumo(serie_consumo_12m(bkn,recurso,ref_ts,flr,hist,medianas,marca),recurso))
    # indice / bandeira / variacao
    ind_row=rk[(rk["bkn"]==bkn)&(rk["competencia"]==ref_ts)]
    indice_mes=float(ind_row.iloc[0]["indice_eficiencia_mes"]) if not ind_row.empty and pd.notna(ind_row.iloc[0]["indice_eficiencia_mes"]) else None
    indice_txt=f"{indice_mes*100:.0f}%" if indice_mes is not None else "-"
    bandeira=band_loja.get(bkn,"-")
    faixas=(faixas_loja or {}).get(bkn, BANDEIRAS_8)
    meu_cluster=(cluster_loja or {}).get(bkn)
    fr=(fronteiras_cluster or {}).get(meu_cluster,{}) if meu_cluster else {}
    front_faixas=fr.get("fronteira",{})
    # variacao do proprio indice
    prev_ind=rk[(rk["bkn"]==bkn)&(rk["competencia"]==prev_ts)]
    variacao_txt="sem base de comparacao"
    if indice_mes is not None and not prev_ind.empty and pd.notna(prev_ind.iloc[0]["indice_eficiencia_mes"]):
        pv=prev_ind.iloc[0]["indice_eficiencia_mes"]
        d_ind=(indice_mes-pv)*100  # negativo = melhorou (indice caiu)
        if d_ind<-1: variacao_txt=f'sua eficiencia <span style="color:{COR["verde"]};font-weight:600;">melhorou {abs(d_ind):.0f}%</span>'
        elif d_ind>1: variacao_txt=f'sua eficiencia <span style="color:{COR["vermelho"]};font-weight:600;">piorou {d_ind:.0f}%</span>'
        else: variacao_txt="eficiencia estavel"
    # meta para proxima bandeira
    meta_txt=""
    prox=proxima_bandeira(bandeira, faixas) if bandeira in faixas else None
    if prox and indice_mes is not None and not ind_row.empty:
        alvo_idx=front_faixas.get(prox)
        if alvo_idx and indice_mes>alvo_idx:
            real=ind_row.iloc[0]["custo_equivalente_real_score_rs"]
            prev_c=ind_row.iloc[0]["custo_equivalente_previsto_score_rs"]
            if pd.notna(real) and pd.notna(prev_c) and prev_c>0:
                real_alvo=alvo_idx*prev_c
                reducao_rs=real-real_alvo
                meta_txt=(f'Para a bandeira <b>{prox}</b>: reduzir o indice de {indice_mes*100:.0f}% para {alvo_idx*100:.0f}%, '
                          f'equivalente a ~<b>{brl(reducao_rs)}/mes</b> em consumo.')
    melhor_faixa=faixas[0]
    if not meta_txt and bandeira==melhor_faixa:
        meta_txt="Voce esta na melhor bandeira do seu grupo. Mantenha o desempenho."
        prox_af=proxima_loja_menos_consumo(bkn, marca, ref_ts, flr, rk, medianas)
        if prox_af:
            meta_txt+=f" {prox_af}"
    score,posicao="-",""
    if comp_row is not None:
        posicao=f"{int(comp_row['posicao_regional_mes'])}o de {int(comp_row['total_regional_mes'])} na regional"
    # resumo chave (Economia/Despesa dos recursos)
    resumo=resumo_chave_loja(bkn, ref_ts, prev_ts, flr, indice_mes, variacao_txt, recursos)
    # mensagem principal: bandeira + indice + variacao unificados (item 2)
    msg_band=mensagem_bandeira(bkn, bandeira, band_loja_prev, indice_mes, prev_ts, rk, variacao_txt, faixas=faixas)
    if msg_band:
        resumo=[msg_band]+resumo
    txt_rank=texto_ranking if texto_ranking else texto_cluster(marca, (meu_cluster[1] if meu_cluster else ""))
    return {"nome":base["nome"],"cidade":base["cidade"],"mes_label":ref_ts.strftime("%b/%Y"),
      "custo_total":custo_total,"recursos":recursos,"graficos_consumo":grafs,
      "grafico_indice":grafico_indice(serie_indice_12m(bkn,ref_ts,rk,flr,medianas,band_loja,faixas_loja)),
      "escada":escada_eficiencia(bandeira, faixas),
      "texto_ranking":txt_rank,
      "bloco_alerta":bloco_alerta_loja(bkn, ALERTAS),
      "indice_txt":indice_txt,"bandeira":bandeira,"posicao":posicao,
      "variacao_txt":variacao_txt,"meta_txt":meta_txt,"resumo":resumo}

def resumo_chave_loja(bkn, ref_ts, prev_ts, flr, indice_mes, variacao_txt, recursos):
    deltas={rec:info["delta"] for rec,info in recursos.items()}
    linhas=[]
    quedas={k:v for k,v in deltas.items() if v<-1}
    if quedas:
        rec=min(quedas,key=quedas.get)
        linhas.append(f'<span style="color:{COR["verde"]};font-weight:700;">Economia:</span> {ROTULO[rec]} foi a principal reducao, com <b>{abs(quedas[rec]):.0f}%</b> a menos de consumo. Continue com sua rotina!')
    altas={k:v for k,v in deltas.items() if v>1}
    if altas:
        rec=max(altas,key=altas.get)
        linhas.append(f'<span style="color:{COR["vermelho"]};font-weight:700;">Despesa:</span> {ROTULO[rec]} foi o maior aumento, com <b>{altas[rec]:.0f}%</b> a mais de consumo. Reforce a rotina do Manual de Boas Praticas de Utilidades.')
    if not linhas:
        linhas.append(f'<span style="color:{COR["cinza"]};">Consumo estavel no mes, sem desvios relevantes por recurso.</span>')
    return linhas

# ============================ MONTAGEM GRUPO ============================
def _bandeira_grupo(indices_lojas, todos_indices_grupos):
    """Retorna bandeira do grupo comparando seu indice medio com os demais grupos."""
    s=pd.Series(todos_indices_grupos)
    faixa=atribui_bandeiras(s)
    return faixa

def montar_grupo(email, col_email, ref_ts, flr, rk, dp, indices_todos_grupos, front_grupos, p50_idx,
                 medianas=None, hist=None, setores_indice=None,
                 cluster_por_bkn=None, fronteiras_por_cluster=None):
    bkns=dp[(dp[col_email]==email)&(dp["Dispara Dashboard Loja"]=="SIM")]["BKN"].tolist()
    ref=flr[(flr["competencia"]==ref_ts)&(flr["bkn"].isin(bkns))]
    ref=ref[~ref["flag_qualidade_consumo"].map(dado_fragil)]
    # v13.2 (item 4): Starbucks nao consome gas -> remove GAS de todas as visualizacoes.
    marca_pred=ref["marca"].mode().iloc[0] if "marca" in ref.columns and len(ref) else None
    if str(marca_pred).upper()=="SBUX":
        ref=ref[ref["recurso"]!="GAS"]
    # despesa acima do orcado por loja (regra B/C, nao SAP cru)
    linhas=[]
    for bkn,g in ref.groupby("bkn"):
        nome=g.iloc[0]["nome"]; marca=g.iloc[0].get("marca","")
        real=0.0
        for _,r in g.iterrows():
            dv,_=despesa_recurso(r)
            if dv is not None: real+=dv
        orc=pd.to_numeric(g["orcado_ajustado_rs"],errors="coerce").sum()
        linhas.append({"nome":nome,"acima":real-orc,"real":real,"orcado":orc})
    acima_total=sum(max(0,l["acima"]) for l in linhas)
    # v13.1: rank_consumo em CONSUMO FISICO (kWh/m3/kg) + % acima do esperado. O usuario quer
    # que a loja veja o consumo fisico dela (acionavel: desligar equipamento, vazamento), nao
    # R$. A base e a MESMA do indice (consumo_real vs consumo_previsto): como custo_equivalente
    # = consumo x tarifa_orcada FIXA, o % acima em consumo fisico == % acima em custo, entao a
    # correlacao com o indice se mantem perfeita. Ranqueado por % (comparavel entre lojas; e
    # os rankings ja sao separados por marca+tipo, entao portes diferentes nao se misturam).
    rank_consumo={}; cons_medio={}
    for recurso in ["ENERGIA","AGUA","GAS"]:
        rr=ref[ref["recurso"]==recurso]
        if rr.empty: continue
        rows=[]; soma_cons=0.0; soma_desp=0.0; ncons=0
        for _,r in rr.iterrows():
            med=(medianas or {}).get((r.get("marca"),recurso))
            if consumo_fantasma(r.get("consumo_real"),r.get("consumo_previsto"),med): continue
            cr=r.get("consumo_real"); cp=r.get("consumo_previsto")
            # v13.2: se o orcamento desta loja-recurso e cronicamente errado, usa a mediana
            # do consumo real da propria loja como previsto (denominador realista).
            cp_corr=ORCAMENTO_ERRADO.get((str(r.get("bkn","")),recurso))
            if cp_corr is not None: cp=cp_corr
            if pd.notna(cr) and pd.notna(cp) and cp>0:
                pct=(float(cr)/float(cp)-1.0)*100.0
                rows.append({"nome":r["nome"],"exc":float(cr)-float(cp),"pct":pct,
                             "real":float(cr),"orcado":float(cp)})
                soma_cons+=float(cr); ncons+=1
                dv,_=despesa_recurso(r)
                if dv is not None: soma_desp+=dv
        if rows: rank_consumo[recurso]=rows
        if ncons: cons_medio[recurso]={"consumo":soma_cons/ncons,"despesa":soma_desp/ncons,"n":ncons}
    # media por tipo de loja (Rua/Shopping/Airport) x recurso
    por_tipo={}
    ref2=ref.copy(); ref2["cat_area"]=ref2["tipo_area"].map(categoria_area)
    for tipo in ["RUA","SHOPPING","AIRPORT"]:
        sub_t=ref2[ref2["cat_area"]==tipo]; por_tipo[tipo]={}
        for recurso in ["ENERGIA","AGUA","GAS"]:
            rr=sub_t[sub_t["recurso"]==recurso]; sc=0.0; sd=0.0; n=0
            for _,r in rr.iterrows():
                med=(medianas or {}).get((r.get("marca"),recurso))
                if consumo_fantasma(r.get("consumo_real"),r.get("consumo_previsto"),med): continue
                if pd.notna(r["consumo_real"]):
                    sc+=float(r["consumo_real"]); n+=1
                    dv,_=despesa_recurso(r)
                    if dv is not None: sd+=dv
            if n: por_tipo[tipo][recurso]={"consumo":sc/n,"despesa":sd/n}
    # ---- Bloco 6: tabela por tipo_loja REAL (nomenclatura correta), so tipos que o gestor tem ----
    por_tipo_loja={}
    for tl,g in ref.groupby("tipo_loja"):
        rec_d={}
        for recurso in ["ENERGIA","AGUA","GAS"]:
            rr=g[g["recurso"]==recurso]; sc=0.0; sd=0.0; n=0
            for _,r in rr.iterrows():
                med=(medianas or {}).get((r.get("marca"),recurso))
                if consumo_fantasma(r.get("consumo_real"),r.get("consumo_previsto"),med): continue
                if pd.notna(r["consumo_real"]):
                    sc+=float(r["consumo_real"]); n+=1
                    dv,_=despesa_recurso(r)
                    if dv is not None: sd+=dv
            if n: rec_d[recurso]={"consumo":sc/n,"despesa":sd/n}
        if rec_d: por_tipo_loja[str(tl)]={"rec":rec_d,"n":g["bkn"].nunique()}

    # ---- Bloco 6: OFENSORAS / EFICIENTES (v13.1) ----
    # MUDANCA CONCEITUAL: antes a tabela listava quem VARIOU pra pior/melhor vs mes anterior,
    # o que descolava do consumo (uma loja podia 'piorar' 5pp e ainda estar bem abaixo do
    # esperado). Verificado em 12 lojas: 3/11 ficavam incoerentes. Agora lista por NIVEL DE
    # INEFICIENCIA ATUAL: ofensoras = indice > 100% (consome acima do esperado AGORA),
    # eficientes = indice <= 100%. Isso alinha 100% com o grafico de consumo excedente e com
    # a simulacao de subida de bandeira (que ja usava nivel atual). 'delta' agora guarda
    # (indice_atual - 100%) em pontos percentuais: positivo = quanto esta acima do esperado.
    prev_ts_g=[mm for mm in sorted(flr["competencia"].unique()) if mm<ref_ts]
    prev_ts_g=pd.Timestamp(prev_ts_g[-1]) if prev_ts_g else ref_ts
    rk_now=rk[(rk["competencia"]==ref_ts)&(rk["bkn"].isin(bkns))][["bkn","indice_eficiencia_mes"]].dropna()
    rk_old=rk[(rk["competencia"]==prev_ts_g)&(rk["bkn"].isin(bkns))][["bkn","indice_eficiencia_mes"]].dropna()
    nomes_map=flr[flr["competencia"]==ref_ts][["bkn","nome"]].drop_duplicates("bkn").set_index("bkn")["nome"].to_dict()
    niv=rk_now[rk_now["indice_eficiencia_mes"]>=0.10].copy()
    niv["nome"]=niv["bkn"].map(nomes_map)
    # v13.2: ofensor = indice da loja ACIMA do indice medio da CARTEIRA (relativo), nao 100% fixo.
    # Assim 'ofensora' significa 'puxa a carteira pra cima' no contexto do proprio gestor.
    ind_carteira=float(niv["indice_eficiencia_mes"].mean()) if len(niv) else 1.0
    niv["desvio"]=(niv["indice_eficiencia_mes"]-ind_carteira)*100  # >0 acima da carteira (ofensora)
    niv["indice_loja"]=niv["indice_eficiencia_mes"]*100  # p/ exibir o indice absoluto da loja
    # ofensoras: indice > media da carteira; eficientes: <= media. Ordena por indice.
    detratoras=[{"nome":r["nome"],"delta":r["desvio"],"indice":r["indice_loja"],"bkn":r["bkn"]}
                for _,r in niv[niv["desvio"]>0].sort_values("indice_eficiencia_mes",ascending=False).iterrows()]
    promotoras=[{"nome":r["nome"],"delta":r["desvio"],"indice":r["indice_loja"],"bkn":r["bkn"]}
                for _,r in niv[niv["desvio"]<=0].sort_values("indice_eficiencia_mes").iterrows()]
    ind_medio_ant=float(rk_old["indice_eficiencia_mes"].mean()) if len(rk_old) else None
    # v13.2 (item 2): variacao de cada loja vs mes anterior (coluna 'vs mes anterior' e
    # movimentadores). delta_mes>0 = piorou (indice subiu); <0 = melhorou.
    rk_old_idx=rk_old.set_index("bkn")["indice_eficiencia_mes"].to_dict() if len(rk_old) else {}
    var_mes={}
    for _,r in niv.iterrows():
        old=rk_old_idx.get(r["bkn"])
        if old is not None and old>0:
            var_mes[str(r["bkn"])]=(r["indice_eficiencia_mes"]-old)*100
    for x in detratoras: x["var_mes"]=var_mes.get(str(x["bkn"]))
    for x in promotoras: x["var_mes"]=var_mes.get(str(x["bkn"]))
    # v13.2 (item 2): maiores movimentadores do indice vs mes anterior (2 pra cima, 2 pra baixo)
    movs=sorted(var_mes.items(), key=lambda kv: kv[1])
    subiu=[(b,v) for b,v in movs if v>0.5][-2:][::-1]   # maiores altas (pioraram)
    caiu=[(b,v) for b,v in movs if v<-0.5][:2]           # maiores quedas (melhoraram)
    def _mv(lst):
        return ", ".join(f'{nomes_map.get(b,b)} ({"+" if v>0 else ""}{v:.0f} p.p.)' for b,v in lst)
    partes_mov=[]
    if subiu: partes_mov.append(f'<span style="color:{COR["vermelho"]};">puxaram o indice para cima:</span> {_mv(subiu)}')
    if caiu: partes_mov.append(f'<span style="color:{COR["verde"]};">puxaram para baixo:</span> {_mv(caiu)}')
    legenda_movimentadores=(" &middot; ".join(partes_mov)) if partes_mov else ""

    cobertura=ref["bkn"].nunique()
    ind_grupo=indices_todos_grupos.get(email,np.nan)
    faixa=front_grupos["faixa"].get(email,"-")
    rk_grupo=rk[rk["bkn"].isin(bkns)]
    ult12=rk_grupo.groupby("bkn")["indice_eficiencia_mes"].mean()
    indice_12m=float(ult12.mean()) if len(ult12) else 1.0
    # serie indice 12m do grupo (media das lojas por mes)
    serie_idx_grupo=[]
    for m in pd.date_range(end=ref_ts, periods=12, freq="MS"):
        mm=rk_grupo[rk_grupo["competencia"]==m]["indice_eficiencia_mes"].dropna()
        if len(mm): serie_idx_grupo.append((m.strftime("%b/%y"), float(mm.mean())))
    # serie despesa x meta 12m do grupo (soma das lojas)
    serie_dm_grupo=serie_despesa_meta_grupo(bkns, ref_ts, rk, medianas)
    serie=pd.Series(indices_todos_grupos).dropna().sort_values()
    serie=serie[~serie.index.duplicated(keep="first")]
    # v13.2: posicao DENTRO DA MARCA (nao misturando BK/PLK/SBUX), consistente com a bandeira
    marca_grupo=ref["marca"].mode().iloc[0] if "marca" in ref.columns and len(ref) else None
    peers=front_grupos.get("peers",{})
    serie_marca=pd.Series({e:v for e,v in serie.items()
                           if peers.get(e,{}).get("marca")==marca_grupo}).sort_values()
    pos=int(serie_marca.index.get_indexer([email])[0])+1 if email in serie_marca.index else 0
    n_marca=len(serie_marca)
    posicao_pares=f"{pos}o de {n_marca}" if pos else f"- de {n_marca}"
    eh_primeiro_marca=(pos==1)
    faixa_prev=front_grupos.get("faixa_prev",{}).get(email)
    msg_grupo=None
    if faixa_prev and faixa in BANDEIRAS and faixa_prev in BANDEIRAS:
        ia=BANDEIRAS.index(faixa); ip=BANDEIRAS.index(faixa_prev)
        if ia<ip:
            msg_grupo=(f'<span style="color:{COR["verde"]};font-weight:700;">Parabens!</span> '
                       f'Suas lojas subiram da bandeira <b>{faixa_prev}</b> para <b>{faixa}</b>. Otimo trabalho de gestao.')
        elif ia>ip:
            msg_grupo=(f'<span style="color:{COR["laranja"]};font-weight:700;">Aviso:</span> '
                       f'suas lojas passaram da bandeira <b>{faixa_prev}</b> para <b>{faixa}</b> neste mes.')
        else:
            # v13.2 (item Erro 1): bandeira PERMANECEU -> avisa explicitamente
            msg_grupo=(f'<span style="color:{COR["azul"]};font-weight:700;">Status:</span> '
                       f'suas lojas permaneceram na bandeira <b>{faixa}</b> neste mes.')
    elif faixa in BANDEIRAS:
        # sem mes anterior comparavel: informa a bandeira atual
        msg_grupo=(f'<span style="color:{COR["azul"]};font-weight:700;">Status:</span> '
                   f'suas lojas estao na bandeira <b>{faixa}</b> neste mes.')
    # comparacao com PARES do mesmo tipo e marca (coord vs coord / regional vs regional)
    setor_grupo=setor_do_email(email, col_email, dp)
    marca_grupo=ref["marca"].mode().iloc[0] if "marca" in ref.columns and len(ref) else None
    peers=front_grupos.get("peers",{})
    comp_setor=comparacao_pares(email, marca_grupo, ind_grupo, peers)
    # meta de eficiencia ate alcancar o par imediatamente acima (so o 1o lugar nao tem)
    meta_setor=meta_ate_proximo_par(email, marca_grupo, ind_grupo, peers)
    # v13.3: Bloco Acao reformulado. Ordena por loja mais ineficiente (indice atual), simula
    # cada uma subindo a PROPRIA bandeira (cluster dela), ate a carteira cruzar a fronteira.
    # NAO prioriza mais 'quem piorou vs mes anterior' - o criterio e sempre nivel atual.
    fronteiras_marca=front_grupos["fronteiras"].get(marca_grupo, {})
    sim=simular_subida(bkns, ref_ts, rk, ind_grupo, faixa, fronteiras_marca, p50_idx, ref,
                       dp=dp, cluster_por_bkn=cluster_por_bkn,
                       fronteiras_por_cluster=fronteiras_por_cluster)
    # ---- v12: conjunto de lojas GRIFADAS (ofensoras) ----
    # Definicao confirmada: uniao de (a) lojas que PIORARAM o indice (detratoras) +
    # (b) lojas da simulacao de subida de bandeira.
    bkns_detra=set(str(x["bkn"]) for x in detratoras)
    bkns_sim=set(str(b) for b in sim.get("bkns_sim",[]))
    grifadas=bkns_detra | bkns_sim
    setor_por_bkn={str(b): SETOR_MAP.get(str(b), "Sem setor") for b in bkns}

    # ---- Numeracao das ofensoras (asterisco) p/ cruzar tabela de indice x graficos de consumo ----
    # Ordem: 1 = a que MAIS piorou o indice, depois em ordem decrescente de piora; lojas da
    # simulacao que nao pioraram entram no fim. No REGIONAL a numeracao e feita APOS o filtro
    # de '1 loja por setor' (para nao ter lacunas tipo 1,3,4,7...) e SEQUENCIAL (1,2,3...);
    # essa mesma numeracao e usada nos graficos de consumo, entao a lista que entra nos
    # graficos tambem precisa ser filtrada a 1/setor no Regional.
    is_regional=(col_email=="Email Gerente Regional")
    if is_regional:
        detra_1x1=_uma_loja_por_setor(sorted(detratoras,key=lambda x:-x["delta"]), setor_por_bkn)
        bkns_detra_num=[str(x["bkn"]) for x in detra_1x1]
        # sim bkns que nao sao detratoras 1x1: adiciona 1 por setor tambem
        sim_extra=[b for b in bkns_sim if b not in bkns_detra_num]
        sim_extra_1x1=[]
        vistos={setor_por_bkn.get(b) for b in bkns_detra_num}
        for b in sim_extra:
            s=setor_por_bkn.get(b)
            if s in vistos: continue
            vistos.add(s); sim_extra_1x1.append(b)
        ordenadas=bkns_detra_num+sim_extra_1x1
        grifadas=set(ordenadas)  # no Regional, grifado = so as 1/setor selecionadas
    else:
        delta_por_bkn={str(x["bkn"]):x["delta"] for x in detratoras}
        ordenadas=sorted(grifadas, key=lambda b: delta_por_bkn.get(b, -1e9), reverse=True)
    num_por_bkn={b:i+1 for i,b in enumerate(ordenadas)}

    # numero tambem nas linhas de promotoras/detratoras (para exibir junto do nome)
    for x in detratoras: x["num"]=num_por_bkn.get(str(x["bkn"]))
    for x in promotoras: x["num"]=num_por_bkn.get(str(x["bkn"]))

    # anexa bkn/setor/grifada/num as linhas de rank_consumo existentes
    nome2bkn=flr[flr["competencia"]==ref_ts][["nome","bkn"]].drop_duplicates("nome").set_index("nome")["bkn"].to_dict()
    nomes_ref=flr[flr["competencia"]==ref_ts][["bkn","nome"]].drop_duplicates("bkn").set_index("bkn")["nome"].to_dict()
    for recurso,linhas_r in rank_consumo.items():
        for row in linhas_r:
            b=str(nome2bkn.get(row["nome"],""))
            row["bkn"]=b; row["grifada"]=(b in grifadas)
            row["setor"]=setor_por_bkn.get(b,""); row["num"]=num_por_bkn.get(b)
            row["sem_dado"]=False
    # INJECAO: toda loja grifada precisa aparecer nos 3 graficos. Se nao tem dado valido
    # naquele recurso (fragil/fantasma), entra marcada como 'sem dado confiavel'.
    for recurso in ["ENERGIA","AGUA","GAS"]:
        linhas_r=rank_consumo.setdefault(recurso, [])
        presentes=set(str(r.get("bkn","")) for r in linhas_r)
        for b in grifadas:
            if b in presentes: continue
            linhas_r.append({"nome":nomes_ref.get(b,b),"exc":0.0,"pct":0.0,"real":0,"orcado":0,
                             "bkn":b,"grifada":True,"setor":setor_por_bkn.get(b,""),
                             "num":num_por_bkn.get(b),"sem_dado":True})
    # setores promotores/detratores (Regional, item 3): variacao do indice medio do setor
    setores_mov=variacao_indice_por_setor(bkns, ref_ts, prev_ts_g, rk, setor_por_bkn)
    return {"nome":email,"n_lojas":len(bkns),"mes_label":ref_ts.strftime("%b/%Y"),
      "rank_despesa":linhas,"rank_consumo":rank_consumo,"acima_total":acima_total,
      "cobertura":cobertura,"bandeira":faixa,"indice_12m":indice_12m,
      "cons_medio":cons_medio,"comp_setor":comp_setor,"por_tipo":por_tipo,
      "por_tipo_loja":por_tipo_loja,"promotoras":promotoras,"detratoras":detratoras,
      "ind_medio_ant":ind_medio_ant,"meta_setor":meta_setor,
      "escada":escada_eficiencia(faixa),
      "bloco_alerta_coord":bloco_alerta_grupo(bkns, ALERTAS, flr, ref_ts, max_lojas=None),
      "bloco_alerta_reg":bloco_alerta_grupo(bkns, ALERTAS, flr, ref_ts, max_lojas=3),
      "grafico_indice":grafico_indice(serie_idx_grupo),
      "grafico_despesa_meta":grafico_despesa_meta(serie_dm_grupo),
      "posicao_pares":posicao_pares,"simulacao":sim,"msg_grupo":msg_grupo,
      "legenda_movimentadores":legenda_movimentadores,
      "setores_indice":setores_indice,"marca_grupo":marca_grupo,"setor_grupo":setor_grupo,
      "grifadas":grifadas,"setor_por_bkn":setor_por_bkn,"setores_mov":setores_mov,
      "prev_ts_g":prev_ts_g,"bkns":list(bkns)}

def serie_despesa_meta_grupo(bkns, ref_ts, rk, medianas=None):
    """v12: soma dos totais corrigidos (real/prev do rk) das lojas do grupo por mes."""
    meses=pd.date_range(end=ref_ts, periods=12, freq="MS")
    sub=rk[(rk["bkn"].isin(bkns))&(rk["competencia"]<=ref_ts)]
    out=[]
    for m in meses:
        mm=sub[sub["competencia"]==m]
        mm=mm[mm["indice_eficiencia_mes"].notna()]
        if mm.empty: continue
        real=pd.to_numeric(mm["custo_equivalente_real_score_rs"],errors="coerce").sum()
        meta=pd.to_numeric(mm["custo_equivalente_previsto_score_rs"],errors="coerce").sum()
        if meta>0: out.append((m.strftime("%b/%y"),float(real),float(meta)))
    return out

def meta_ate_proximo_setor(setor_grupo, marca_grupo, ind_grupo, setores_indice):
    """Meta de eficiencia para alcancar o setor imediatamente MAIS eficiente que o seu,
    dentro da mesma marca. Se voce ja e o 1o lugar, retorna None (sem meta)."""
    if not setores_indice or pd.isna(ind_grupo): return None
    mesma_marca=sorted([(s,v) for (mk,s),v in setores_indice.items()
                        if mk==marca_grupo and pd.notna(v)], key=lambda x:x[1])
    if not mesma_marca: return None
    if mesma_marca[0][0]==setor_grupo:
        return None  # 1o lugar da marca: sem meta
    # setor imediatamente acima
    acima=[(s,v) for s,v in mesma_marca if v<ind_grupo and s!=setor_grupo]
    if not acima: return None
    s_alvo,v_alvo=acima[-1]  # o mais proximo abaixo do meu indice (o menos distante)
    p_meu=ind_grupo*100; p_alvo=v_alvo*100
    if round(p_meu)==round(p_alvo): p_meu=round(p_alvo)+1; p_alvo=round(p_alvo)
    return (f'Meta: reduza seu indice de {p_meu:.0f}% para <b>{p_alvo:.0f}%</b> '
            f'para alcancar o setor <b>{s_alvo}</b>, o proximo mais eficiente da sua marca.')

def comparacao_pares(email, marca_grupo, ind_grupo, peers):
    """Compara o grupo com o PAR (mesmo tipo, mesma marca) imediatamente mais eficiente.
    Anonimiza: mostra so o setor/regional do par, nunca email/nome."""
    if not peers or pd.isna(ind_grupo): return None
    melhores=[(e,p) for e,p in peers.items()
              if p.get("marca")==marca_grupo and pd.notna(p.get("idx"))
              and p["idx"]<ind_grupo and e!=email]
    if not melhores: return None
    melhores.sort(key=lambda x:x[1]["idx"])
    _,p=melhores[-1]  # o mais proximo abaixo (menos distante)
    p_meu=ind_grupo*100; p_alvo=p["idx"]*100
    if round(p_meu)==round(p_alvo): p_meu=round(p_alvo)+1; p_alvo=round(p_alvo)
    return (f'O par mais eficiente logo acima de voce e o setor <b>{p["nome"]}</b> ({p_alvo:.0f}%), '
            f'contra os seus {p_meu:.0f}%. Observe as praticas dessa carteira.')

def meta_ate_proximo_par(email, marca_grupo, ind_grupo, peers):
    """Meta para alcancar o par (mesma marca, mesmo tipo) imediatamente acima.
    Se voce ja e o 1o lugar entre os pares da marca, retorna None."""
    if not peers or pd.isna(ind_grupo): return None
    mesma_marca=sorted([(e,p) for e,p in peers.items()
                        if p.get("marca")==marca_grupo and pd.notna(p.get("idx"))],
                       key=lambda x:x[1]["idx"])
    if not mesma_marca: return None
    if mesma_marca[0][0]==email:
        return None  # 1o lugar: sem meta
    acima=[(e,p) for e,p in mesma_marca if p["idx"]<ind_grupo and e!=email]
    if not acima: return None
    _,p=acima[-1]
    p_meu=ind_grupo*100; p_alvo=p["idx"]*100
    if round(p_meu)==round(p_alvo): p_meu=round(p_alvo)+1; p_alvo=round(p_alvo)
    return (f'Meta: reduza seu indice de {p_meu:.0f}% para <b>{p_alvo:.0f}%</b> '
            f'para alcancar o setor <b>{p["nome"]}</b>, o proximo mais eficiente da sua marca.')

def comparacao_setores(setor_grupo, marca_grupo, ind_grupo, setores_indice):
    """Compara com o UNICO setor mais eficiente da MESMA MARCA. Identifica so pelo setor."""
    if not setores_indice or pd.isna(ind_grupo): return None
    melhores=[(s,v) for (mk,s),v in setores_indice.items()
              if mk==marca_grupo and pd.notna(v) and v<ind_grupo and s!=setor_grupo]
    if not melhores: return None
    melhores.sort(key=lambda x:x[1])
    s,v=melhores[0]
    p_setor=v*100; p_meu=ind_grupo*100
    if round(p_setor)==round(p_meu):
        p_meu=round(p_setor)+1; p_setor=round(p_setor)
    return (f'O setor mais eficiente da sua marca e <b>{s}</b> ({p_setor:.0f}%), '
            f'contra os seus {p_meu:.0f}%. Observe as praticas dessa carteira.')

def indice_por_setor(ref_ts, flr, rk, dp):
    """Indice medio por (marca, Regional) no mes ref. Exclui fantasma e setores invalidos."""
    rk_ref=rk[rk["competencia"]==ref_ts][["bkn","indice_eficiencia_mes"]].dropna()
    rk_ref=rk_ref[rk_ref["indice_eficiencia_mes"]>=0.10]
    mapa=dp[["BKN","Regional"]].rename(columns={"BKN":"bkn"})
    mapa["bkn"]=mapa["bkn"].astype(str).str.strip()
    marcas=flr[flr["competencia"]==ref_ts][["bkn","marca"]].drop_duplicates("bkn")
    m=rk_ref.merge(mapa,on="bkn",how="left").merge(marcas,on="bkn",how="left").dropna(subset=["Regional","marca"])
    invalidos={"INATIVA","INATIVO","VAGO","DESCONHECIDO","NAN","NONE","",
               "SEM_REGIONAL","SEM REGIONAL","SEM_SETOR","N/A","NA"}
    m=m[~m["Regional"].astype(str).str.strip().str.upper().isin(invalidos)]
    cont=m.groupby(["marca","Regional"])["indice_eficiencia_mes"].agg(["mean","count"])
    cont=cont[cont["count"]>=3]
    return {idx:row["mean"] for idx,row in cont.iterrows()}

def setor_do_email(email, col_email, dp):
    """Regional predominante das lojas daquele coordenador/gerente."""
    sub=dp[dp[col_email]==email]["Regional"].dropna()
    return sub.mode().iloc[0] if len(sub) else None

def variacao_indice_por_setor(bkns, ref_ts, prev_ts, rk, setor_por_bkn):
    """Regional (v13.1): setores OFENSORES / EFICIENTES pelo NIVEL do indice medio do setor
    no mes atual (nao mais variacao vs mes anterior, para alinhar com as tabelas de lojas e
    o consumo excedente). ofensores = indice medio do setor > 100% (consome acima do
    esperado); eficientes = <= 100%. Retorna dois grupos ordenados:
      pioraram (ofensores, do que mais estoura para o menos) e melhoraram (eficientes).
    Cada item: {setor, idx_now, delta} com delta = (indice_medio - 100%) em p.p."""
    now=rk[(rk["competencia"]==ref_ts)&(rk["bkn"].isin(bkns))][["bkn","indice_eficiencia_mes"]].dropna()
    if now.empty: return {"pioraram":[],"melhoraram":[]}
    now["setor"]=now["bkn"].astype(str).map(setor_por_bkn)
    invalidos={"INATIVA","INATIVO","VAGO","DESCONHECIDO","NAN","NONE","","SEM_REGIONAL",
               "SEM REGIONAL","SEM_SETOR","SEM SETOR","N/A","NA"}
    def _ok(s): return str(s).strip().upper() not in invalidos and pd.notna(s)
    now=now[now["setor"].map(_ok)]
    gn=now.groupby("setor")["indice_eficiencia_mes"].mean()
    ind_carteira=float(now["indice_eficiencia_mes"].mean()) if len(now) else 1.0
    rows=[{"setor":s,"idx_now":float(v),"delta":float((v-ind_carteira)*100)} for s,v in gn.items()]
    pioraram=sorted([r for r in rows if r["delta"]>0], key=lambda x:-x["idx_now"])
    melhoraram=sorted([r for r in rows if r["delta"]<=0], key=lambda x:x["idx_now"])
    return {"pioraram":pioraram,"melhoraram":melhoraram}

def simular_subida(bkns, ref_ts, rk, ind_atual, faixa_atual, fronteiras, p50_idx, ref,
                   dp=None, faixas_grupo=None, cluster_por_bkn=None, fronteiras_por_cluster=None):
    """v13.3 Bloco Acao (redesenhado): ordena as lojas da carteira da MAIS INEFICIENTE
    (maior indice atual) para a menos, SEM priorizar quem 'piorou vs mes anterior' (esse
    criterio saiu). Para cada loja, simula ela subindo a PROPRIA bandeira individual (do
    cluster dela: marca + exposicao ao sol/KSK/Quiosque), usando a fronteira real daquele
    cluster - nao mais 'reduzir ate a mediana da rede' (p50 generico), que nao correspondia
    a nenhuma fronteira de bandeira de verdade. Adiciona lojas uma a uma (cada uma subindo
    a sua propria bandeira) ate a carteira cruzar a fronteira da PROXIMA bandeira do grupo.
    Retorna dict: {texto, lojas:[{nome,bkn,setor,bandeira_de,bandeira_para,indice_de,
    indice_para}], subiu_ok:bool, prox, bkns_sim}."""
    faixas=faixas_grupo or BANDEIRAS_8
    vazio={"texto":"", "lojas":[], "subiu_ok":False, "prox":None, "bkns_sim":[]}
    if faixa_atual not in faixas:
        return vazio
    prox=proxima_bandeira(faixa_atual, faixas)
    if prox is None:  # ja e a melhor bandeira do grupo
        return {"texto":"", "lojas":[], "subiu_ok":True, "prox":None, "bkns_sim":[]}
    rk_ref=rk[(rk["competencia"]==ref_ts)&(rk["bkn"].isin(bkns))][["bkn","indice_eficiencia_mes"]].dropna()
    rk_ref=rk_ref[rk_ref["indice_eficiencia_mes"]>=0.10]
    if rk_ref.empty: return vazio
    idx=rk_ref.set_index("bkn")["indice_eficiencia_mes"].copy()
    alvo_grupo=fronteiras.get(prox)
    if not alvo_grupo: return vazio
    nomes_map=ref[["bkn","nome"]].drop_duplicates("bkn").set_index("bkn")["nome"].to_dict()
    setor_map={str(b): SETOR_MAP.get(str(b), "Sem setor") for b in bkns}
    cluster_por_bkn=cluster_por_bkn or {}
    fronteiras_por_cluster=fronteiras_por_cluster or {}

    def _faixa_por_fronteira(atual_idx, faixas_loja, fronteira_loja):
        """Acha em qual faixa o indice se encaixa, usando as fronteiras JA CALCULADAS do
        cluster inteiro (bandeiras_por_cluster). NUNCA recalcular percentil com 1 elemento
        so (pd.Series de tamanho 1 sempre cai na melhor faixa via qcut - bug corrigido).
        faixas_loja vai da MELHOR (A+) para a PIOR (D); testa nessa ordem e para na 1a cujo
        teto (fronteira) e >= o indice."""
        for fx in faixas_loja:  # A+, A, B+, ... D (ja na ordem melhor->pior)
            teto=fronteira_loja.get(fx)
            if teto is not None and atual_idx<=teto:
                return fx
        return faixas_loja[-1] if faixas_loja else None  # acima de todas as fronteiras -> pior faixa

    def _proxima_bandeira_loja(b):
        """Retorna (faixa_atual_loja, faixa_seguinte_loja, indice_alvo_loja) simulando essa
        loja individual subindo 1 degrau na propria escadinha (cluster dela). None se a loja
        nao tiver cluster mapeado ou ja estiver no topo do proprio cluster."""
        cl=cluster_por_bkn.get(b)
        if not cl: return None
        info=fronteiras_por_cluster.get(cl)
        if not info: return None
        faixas_loja=info.get("faixas") or BANDEIRAS_8
        fronteira_loja=info.get("fronteira",{})
        atual_idx=idx.get(b)
        if atual_idx is None: return None
        faixa_loja_atual=_faixa_por_fronteira(atual_idx, faixas_loja, fronteira_loja)
        if faixa_loja_atual not in faixas_loja: return None
        prox_loja=proxima_bandeira(faixa_loja_atual, faixas_loja)
        if prox_loja is None: return None  # loja ja e a melhor do proprio cluster
        alvo_idx_loja=fronteira_loja.get(prox_loja)
        if not alvo_idx_loja or alvo_idx_loja>=atual_idx: return None
        return (faixa_loja_atual, prox_loja, alvo_idx_loja)

    # ordem: SEMPRE do indice atual mais alto (mais ineficiente) para o mais baixo
    ordem=list(idx.sort_values(ascending=False).index)
    idx_sim=idx.copy(); usadas=[]; lojas=[]
    for b in ordem:
        salto=_proxima_bandeira_loja(b)
        if salto is None: continue  # loja ja no topo do proprio cluster ou sem cluster mapeado
        faixa_de, faixa_para, idx_alvo = salto
        idx_de=idx_sim[b]
        idx_sim[b]=idx_alvo; usadas.append(b)
        lojas.append({"nome":nomes_map.get(b,b),"bkn":b,"setor":setor_map.get(str(b),""),
                     "bandeira_de":faixa_de,"bandeira_para":faixa_para,
                     "indice_de":float(idx_de)*100,"indice_para":float(idx_alvo)*100})
        if idx_sim.mean()<=alvo_grupo: break
    subiu_ok=idx_sim.mean()<=alvo_grupo
    # economia total das lojas usadas (baseada no salto real ate a propria bandeira)
    eco_total=0.0
    for L in lojas:
        b=L["bkn"]; i_at=idx.get(b); i_me=L["indice_para"]/100
        if i_at and i_at>0 and i_me<i_at:
            g=ref[ref["bkn"]==b]; dl=0.0
            for _,r in g.iterrows():
                dv,_=despesa_recurso(r)
                if dv is not None: dl+=dv
            eco_total+=dl*(1-i_me/i_at)
    eco_txt=(f' Isso representaria uma economia total de aproximadamente '
             f'<b>{brl(eco_total)}/mes</b> somando essas lojas.') if eco_total>0 else ""
    # texto cita o salto individual da 1a loja (a mais ineficiente usada) como exemplo concreto
    exemplo=""
    if lojas:
        L=lojas[0]
        exemplo=(f' Por exemplo, a loja <b>{L["nome"]}</b> sairia da bandeira <b>{L["bandeira_de"]}</b> '
                 f'para <b>{L["bandeira_para"]}</b> (indice de {L["indice_de"]:.0f}% para {L["indice_para"]:.0f}%).')
    if subiu_ok and usadas:
        texto=(f'<b>Acao:</b> se as lojas <span style="background:{COR["grifo"]};padding:0 3px;'
               f'border-radius:3px;">grifadas</span> subirem a PROPRIA bandeira (cada uma reduzindo '
               f'seu indice ate a fronteira do proximo patamar do seu cluster), voce sobe de '
               f'<b>{faixa_atual}</b> para <b>{prox}</b>.{exemplo}{eco_txt}')
    else:
        texto=(f'<b>Acao:</b> para subir de bandeira de <b>{faixa_atual}</b> para <b>{prox}</b>, '
               f'foque nas lojas <span style="background:{COR["grifo"]};padding:0 3px;'
               f'border-radius:3px;">grifadas</span> (as mais ineficientes da carteira, comecando '
               f'pela sua propria subida de bandeira).{exemplo}{eco_txt}')
    return {"texto":texto, "lojas":lojas, "subiu_ok":subiu_ok, "prox":prox,
            "bkns_sim":list(usadas)}

# ============================ ENVIO / SALVAR ============================
def enviar_email(dest, assunto, html):
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    if not SMTP_PASS: log("  (ERRO) SMTP_PASS vazio."); return False
    msg=MIMEMultipart(); msg["From"],msg["To"],msg["Subject"]=SMTP_FROM,",".join(dest),assunto
    msg.attach(MIMEText(html,"html"))
    try:
        s=smtplib.SMTP(SMTP_HOST,SMTP_PORT); s.ehlo(); s.starttls(); s.login(SMTP_USER,SMTP_PASS)
        s.sendmail(SMTP_FROM,dest,msg.as_string()); s.quit(); return True
    except Exception as e: log(f"  (ERRO) SMTP: {e}"); return False
def salvar(nome, html):
    os.makedirs(PASTA_SAIDA, exist_ok=True)
    p=os.path.join(PASTA_SAIDA,nome)
    with open(p,"w",encoding="utf-8") as f: f.write(html)
    return p
def tamanho_kb(html): return len(html.encode("utf-8"))/1024
INVALIDOS={"","contatar o go","vago","inativa","nan","none"}
def email_valido(e):
    if e is None: return False
    s=str(e).strip().lower(); return "@" in s and s not in INVALIDOS

# ============================ INDICES DE GRUPO (pre-calculo) ============================
def indices_por_grupo(col_email, ref_ts, prev_ts, flr, rk, dp, min_lojas):
    """Indice medio por grupo (email) no mes ref + bandeiras, fronteiras, marca e nome.
    BUGFIX v13: a bandeira do grupo (Coordenador/Regional) e calculada POR MARCA, nao
    misturando BK/PLK/SBUX na mesma régua de percentil. Antes disso, um regional BK
    podia cair de bandeira so por existirem regionais SBUX/PLK com indice estruturalmente
    melhor (proporcao de recursos diferente), mesmo sendo o 1o colocado dentro da propria
    marca (caso real: benigno.carcereri, 1o entre os 11 regionais BK, caia p/ B+ por
    comparacao indevida com SBUX/PLK). Mesmo padrao ja usado em bandeiras_por_cluster."""
    rk_ref=rk[rk["competencia"]==ref_ts][["bkn","indice_eficiencia_mes"]].dropna()
    dp2=dp[dp["Dispara Dashboard Loja"]=="SIM"][["BKN",col_email]].rename(columns={"BKN":"bkn"})
    m=rk_ref.merge(dp2,on="bkn")
    m=m[m[col_email].map(email_valido)]
    g=m.groupby(col_email).agg(idx=("indice_eficiencia_mes","mean"), n=("bkn","count"))
    g=g[g["n"]>=min_lojas]
    # marca predominante por grupo (precisa vir ANTES da bandeira, pra particionar por marca)
    marca_col=flr[flr["competencia"]==ref_ts][["bkn","marca"]].drop_duplicates("bkn")
    mm=m.merge(marca_col,on="bkn",how="left")
    marca_grupo=mm.groupby(col_email)["marca"].agg(lambda s: s.mode().iloc[0] if len(s.mode()) else None).to_dict()
    marca_por_grupo_idx=pd.Series({e:marca_grupo.get(e) for e in g.index})
    faixa=pd.Series(index=g.index, dtype=object); fronteiras={}
    for marca_g, idxs in marca_por_grupo_idx.groupby(marca_por_grupo_idx):
        emails_marca=idxs.index
        sub=g.loc[emails_marca,"idx"]
        fx=atribui_bandeiras(sub)
        faixa.loc[emails_marca]=fx.values
        fronteiras[marca_g]=pd.DataFrame({"idx":sub,"b":fx}).groupby("b",observed=True)["idx"].max().to_dict()
    rk_prev=rk[rk["competencia"]==prev_ts][["bkn","indice_eficiencia_mes"]].dropna()
    mp=rk_prev.merge(dp2,on="bkn")
    mp=mp[mp[col_email].map(email_valido)]
    gp=mp.groupby(col_email).agg(idx=("indice_eficiencia_mes","mean"),n=("bkn","count"))
    gp=gp[gp["n"]>=min_lojas]
    faixa_prev={}
    if len(gp):
        mpm=mp.merge(marca_col,on="bkn",how="left")
        marca_grupo_prev=mpm.groupby(col_email)["marca"].agg(lambda s: s.mode().iloc[0] if len(s.mode()) else None)
        for marca_g, idxs in marca_grupo_prev.groupby(marca_grupo_prev):
            emails_marca=[e for e in idxs.index if e in gp.index]
            if not emails_marca: continue
            fxp=atribui_bandeiras(gp.loc[emails_marca,"idx"])
            faixa_prev.update(fxp.to_dict())
    # nome de exibicao: usa a Regional predominante do grupo (anonimiza o email)
    nome_col=dp[["BKN",col_email,"Regional"]].rename(columns={"BKN":"bkn"})
    nome_col["bkn"]=nome_col["bkn"].astype(str)
    reg_grupo=nome_col.groupby(col_email)["Regional"].agg(lambda s: s.mode().iloc[0] if len(s.dropna().mode()) else "").to_dict()
    peers={e:{"idx":g.loc[e,"idx"],"marca":marca_grupo.get(e),"nome":reg_grupo.get(e,e)}
           for e in g.index}
    return g["idx"].to_dict(), {"faixa":faixa.to_dict(),"fronteiras":fronteiras,"faixa_prev":faixa_prev,
                                "peers":peers}

# ============================ MAIN ============================
def main():
    t0=time.time(); ref_ts=pd.Timestamp(MES_REFERENCIA+"-01")
    log(f"Mes de referencia: {ref_ts.strftime('%Y-%m')}")
    flr,cmp,rk,dp=carregar_tudo()
    hist=carregar_historico()
    global ALERTAS
    ALERTAS=carregar_alertas()
    log(f"  alertas carregados: {len(ALERTAS)} lojas")
    global SETOR_MAP, REGIONAL_OP_MAP
    SETOR_MAP, REGIONAL_OP_MAP=carregar_setores()
    meses=sorted(flr["competencia"].unique()); ant=[m for m in meses if m<ref_ts]
    prev_ts=pd.Timestamp(ant[-1]) if ant else ref_ts
    log(f"Mes anterior: {prev_ts.strftime('%Y-%m')}")

    # bandeiras de LOJA por CLUSTER (marca + exposicao ao sol), faixas variaveis (Bloco 4)
    band_loja, faixas_loja, fronteiras_cluster, cluster_loja = bandeiras_por_cluster(ref_ts, flr, rk)
    band_loja_prev, faixas_loja_prev, _, _ = bandeiras_por_cluster(prev_ts, flr, rk)
    # p50 por cluster (para a simulacao usar a mediana do cluster certo)
    rk_ref=rk[rk["competencia"]==ref_ts][["bkn","indice_eficiencia_mes"]].dropna()
    p50_idx=float(rk_ref["indice_eficiencia_mes"].median())

    # medianas marca+recurso (p/ Regra A) e pools de comparaveis por recurso (p/ card loja-semelhante)
    medianas=medianas_marca_recurso(flr, ref_ts)
    global DIVERGENCIA_SAP
    DIVERGENCIA_SAP=divergencia_cronica_sap(flr, ref_ts)
    log(f"  divergencias cronicas SAP: {len(DIVERGENCIA_SAP)} loja-recurso")
    temp_map=carregar_temperatura(ref_ts)
    pools_comp=construir_pools_comparaveis(flr, ref_ts, medianas, temp_map)

    # bandeiras de grupo
    idx_coord, front_coord = indices_por_grupo("Email Coordenador", ref_ts, prev_ts, flr, rk, dp, MIN_LOJAS_COORD)
    idx_reg,   front_reg   = indices_por_grupo("Email Gerente Regional", ref_ts, prev_ts, flr, rk, dp, MIN_LOJAS_REG)

    # indice medio por SETOR (Regional) p/ comparacao anonima (item 7)
    setores_indice=indice_por_setor(ref_ts, flr, rk, dp)

    if MODO_VALIDACAO:
        log(f"MODO_VALIDACAO: {QTD_EXEMPLOS} de cada nivel, sem e-mail.")
        disparo=set(dp[dp["Dispara Dashboard Loja"]=="SIM"]["BKN"])
        bkns_cmp=set(cmp[cmp["competencia"]==ref_ts]["bkn"])
        cand=flr[(flr["competencia"]==ref_ts)&(flr["marca"]==BANDEIRA_EXEMPLO)&(~flr["flag_qualidade_consumo"].map(dado_fragil))]
        elegiveis=[b for b in cand["bkn"].unique() if b in disparo and b in bkns_cmp] or list(bkns_cmp&disparo)
        max_kb=0
        for bkn in elegiveis[:QTD_EXEMPLOS]:
            d=dados_loja(bkn,ref_ts,prev_ts,flr,cmp,rk,hist,band_loja,fronteiras_cluster,band_loja_prev,medianas,pools_comp,faixas_loja,cluster_loja)
            if not d: continue
            html=render_loja(d); max_kb=max(max_kb,tamanho_kb(html))
            log(f"  loja: {salvar(f'dashboard_LOJA_{safe_name(bkn)}.html',html)}")
        coords=[e for e in idx_coord.keys()][:QTD_EXEMPLOS]
        for email in coords:
            d=montar_grupo(email,"Email Coordenador",ref_ts,flr,rk,dp,idx_coord,front_coord,p50_idx,medianas,hist,setores_indice,cluster_loja,fronteiras_cluster)
            html=render_coordenador(d); max_kb=max(max_kb,tamanho_kb(html))
            log(f"  coord: {salvar(f'dashboard_COORD_{safe_name(email)}.html',html)} ({d['n_lojas']} lojas, {d['bandeira']})")
        regs=[e for e in idx_reg.keys()][:QTD_EXEMPLOS]
        for email in regs:
            d=montar_grupo(email,"Email Gerente Regional",ref_ts,flr,rk,dp,idx_reg,front_reg,p50_idx,medianas,hist,setores_indice,cluster_loja,fronteiras_cluster)
            html=render_regional(d); max_kb=max(max_kb,tamanho_kb(html))
            log(f"  regional: {salvar(f'dashboard_REGIONAL_{safe_name(email)}.html',html)} ({d['n_lojas']} lojas, {d['bandeira']})")
        log(f"Maior HTML: {max_kb:.0f} KB ({'OK Outlook' if max_kb<100 else 'ATENCAO >100KB'})")
        log(f"Concluido em {time.time()-t0:.1f}s. Arquivos em: {PASTA_SAIDA}")
        return

    log("MODO MASSA.")
    dfd=dp[dp["Dispara Dashboard Loja"]=="SIM"]
    for bkn in dfd["BKN"].unique():
        d=dados_loja(bkn,ref_ts,prev_ts,flr,cmp,rk,hist,band_loja,fronteiras_cluster,band_loja_prev,medianas,pools_comp,faixas_loja,cluster_loja)
        if d: salvar(f"dashboard_LOJA_{safe_name(bkn)}.html",render_loja(d))
    for email in [e for e in idx_coord.keys()]:
        d=montar_grupo(email,"Email Coordenador",ref_ts,flr,rk,dp,idx_coord,front_coord,p50_idx,medianas,hist,setores_indice,cluster_loja,fronteiras_cluster)
        html=render_coordenador(d); salvar(f"dashboard_COORD_{safe_name(email)}.html",html)
        if ENVIAR_EMAIL: enviar_email([email],f"Painel de Utilidades - {ref_ts.strftime('%b/%Y')}",html)
    for email in [e for e in idx_reg.keys()]:
        d=montar_grupo(email,"Email Gerente Regional",ref_ts,flr,rk,dp,idx_reg,front_reg,p50_idx,medianas,hist,setores_indice,cluster_loja,fronteiras_cluster)
        html=render_regional(d); salvar(f"dashboard_REGIONAL_{safe_name(email)}.html",html)
        if ENVIAR_EMAIL: enviar_email([email],f"Painel de Utilidades - {ref_ts.strftime('%b/%Y')}",html)
    log(f"Concluido em {time.time()-t0:.1f}s.")

if __name__=="__main__":
    main()
