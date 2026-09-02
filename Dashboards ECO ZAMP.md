PROJETO ECO ZAMP — dashboards de utilidades (Loja / Coordenador / Gerente Regional)

<Persona>

Seja extremamente proativo em encontrar problemas e inseguranças e sempre faça analises extremamente criticas, sempre falando a verdade e falando todas as inseguranças e problemas. Seja um especialista em estratégia de economia de tokens. Pense bastante em como fazer essa estratégia e aplicá-la e mesmo assim retornar os melhores resultados possíveis

<Roteiro>

Junte todas as alterações feitas nos diferentes códigos em apenas um código que funcione exatamente como foi definido. Depois de juntar tudo e você testar para você ser tudo deu certo, confira e teste mais uma vez analisando criticamente cada alteração feita e vendo se vai sair como o esperado

<Contexto Geral>

Anexei o código atual (eco_zamp_dashboards_v13.py) e as planilhas. O script roda 1x/mês, lê as bases, gera dashboards HTML por e-mail. Já está validado e rodando (117 coordenadores, 16 regionais, ~100 lojas, zero erros). Leia do código só os trechos que o pedido do dia exigir; não releia o arquivo inteiro.

Como quero trabalhar (regras de token, siga à risca):

Para cada item que eu pedir, primeiro responda SÓ com a análise/proposta em texto e PARE para eu decidir. Não rode código, não investigue dados, não gere arquivos até eu dizer "implementa".
Nunca rasterize/screenshot dashboard nem gere PDF a menos que eu peça explicitamente. Confie no teste de robustez para validar.
Quando eu disser "implementa", faça o lote inteiro e rode o pipeline UMA vez só no fim.
Uma pergunta por vez, sempre no chat (texto), nunca em formulário de botões.
Se um prompt tiver muitos itens, me diga quais fazer primeiro em vez de atacar todos de uma vez.
Seja conciso. Sem re-explicar o que já foi decidido, sem preâmbulo.

<Contexto Especifico>

Eu fiz os diversos temas separados em conversas diferentes. Agora vou te mandar:
1.Códigos alterados - vao ser vários porque fiz em conversas diferentes
2.Textos falando quais linhas foram alteradas: para você entender o que foi feito

Não quero que você mexa no que foi decidido, apenas caso dê algum bug e você e me pergunta

<Codigos>
 
TEMA 1 - Escala de Nível (decisão estrutural, fazer primeiro): Modo Novo: Índice/Nível. Já travamos a nomenclatura "Nível" (Nível A, A+ etc, no lugar de "bandeira"). Agora quero mudar a régua: hoje o Nível é um percentil relativo aos pares (proporção fixa em cada faixa). Quero trocar para faixas de valor ABSOLUTO do índice, onde 100% (na meta) já é considerado bom (Nível A ou B), e só quem for MAIS eficiente que 100% chega em A+. Isso porque um gerente de loja que consumiu menos que a meta e ainda assim aparece como "ofensor" não faz sentido. 

Linhas ~139-179: Constantes de percentil (BANDEIRAS_8/5/3 e esquema_faixas) substituídas por REGUA_CLUSTER (tabela de cortes absolutos por cluster) e REGUA_GRUPO (cortes para coordenador e gerente). As constantes antigas foram mantidas apenas para compatibilidade da escadinha e proxima_bandeira.

Linhas ~181-215: cluster_sol estendido para os 8 clusters, com suporte a bkn (detecta KSK) e formato_area (detecta SBUX Quiosque). Antes distinguia só 3 valores.

Linhas ~397-460: carregar_tudo recebeu duas funções auxiliares novas: _carregar_ksk (lê Possui_KSK/Status_KSK da Database e preenche _BKN_KSK) e _carregar_formato_area (lê Cadastro_Lojas e preenche _FORMATO_AREA_MAP). Falha silenciosa com aviso no log.

Linhas ~705-810: atribui_bandeiras mantida para compatibilidade. Adicionadas nivel_absoluto_loja, nivel_absoluto_grupo, fronteiras_absolutas_cluster, fronteiras_absolutas_grupo. bandeiras_por_cluster reescrita para usar régua absoluta por cluster nominal.

Linhas ~2158-2205: indices_por_grupo reescrita: substituiu atribui_bandeiras (percentil) por nivel_absoluto_grupo (régua absoluta por marca). Fronteiras passam a ser os cortes fixos.

Linhas ~2062-2132: simular_subida corrigida: a meta de cada loja na simulação é agora a fronteira da própria próxima nota (régua absoluta do cluster dela), não o p50_idx genérico da rede.

Linhas ~1734, 1867, 2266-2288: montar_grupo recebeu parâmetro cluster_loja e todas as suas chamadas foram atualizadas para passá-lo, fechando o fluxo da simulação.

CÓDIGO: eco_zamp_dashboards_v14 (4)


TEMA 2: Todos os Dashboards (gráficos, formato geral)
Nos gráficos de linha/barra dos últimos 12 meses (índice e consumo por utility): tire a grade de fundo e coloque o número exato acima de cada coluna/ponto (ex: "20.000 kWh" acima da barra). Aplique isso a todos os gráficos do sistema.

Item 2 (remover gráfico R$ x Meta): linhas ~1174-1176 (render_loja), ~1524-1525 (render_coordenador), ~1550-1551 (render_regional). Removidas as div de título e o bloco grafico_despesa_meta nos 3 renders. O título do gráfico de consumo físico foi renomeado para "Consumo por Meta - ultimos 12 meses" direto no render_loja.

Item 3 (grouped bar real vs meta): função grafico_consumo reescrita (~linha 915), função serie_consumo_12m reescrita para retornar (label, real, previsto_corrigido) (~linha 857).

Item 1 (sem grade, valor acima das barras): grafico_indice reescrita (~linha 922), grafico_consumo já recebe datalabels e gridLines:false no mesmo bloco do item 3.

Item 4 (Nível histórico no gráfico de índice): serie_indice_12m reescrita para retornar (label, indice, nivel_ou_None) (~linha 899), grafico_indice usa formatter JS para exibir "Nivel X / YY%" quando disponível (~linha 922), chamada em dados_loja passa band_loja e faixas_loja (~linha 1697).

Item 5 (alertas valorados): nova função _tarifa_map_fatura (~linha 510), carregar_alertas reescrito com excedente kWh/m³ e R$ (~linha 527), nova _frase_excedente (~linha 935), bloco_alerta_loja atualizado (~linha 940), montagem de en_rows/ag_rows em bloco_alerta_grupo atualizada (~linha 968), bloco HTML do grupo atualizado (~linha 981).

Item 6 (3 tabelas água): bloco_alerta_grupo agora separa ag_ativo_real vs ag_resolvido com títulos distintos (~linha 990).

Decisões travadas nesta conversa para incluir no prompt da próxima:

Excedente de alertas usa base_fatura_bi_latest / Fato_Loja_Recurso como fonte de tarifa (cascata tarifa_real observada/inferida -> tarifa_orcada). Alertas com Alerta_Baixa_Cobertura=True são filtrados antes de qualquer exibição. Excedente em kWh/m³ vem da coluna Excedente_Periodo_Alerta da planilha de alertas enriquecida. Baseline do esperado = mediana histórica. O histórico de Nível no gráfico de índice acumula a partir do mês de referência atual (sem dado retroativo).

CÓDIGO: eco_zamp_dashboards_v14 (5)

TEMA 3: Impacto Ambiental e Ego (só Loja): Modo Novo: Apenas no Dashboard de Loja, quero adicionar, como último elemento da página, um texto com ícone (árvore ou outro) comunicando impacto ambiental de forma tangível: "Esta loja economizou X árvores este mês" (ou equivalente). Antes de implementar: me dê várias opções de associação (não precisa ser só árvore), me explique a fórmula de conversão de energia para a métrica escolhida, a fonte dela, e as regras de quando esse texto aparece (ex: só quando a loja está economizando?).

Bloco Impacto Ambiental (linhas ~1740-1798)
Aqui fica toda a lógica que transforma "quanto a loja economizou" em frases que qualquer pessoa entende, sem precisar saber o que é kWh ou m³. Tem as constantes de conversão (160 kWh = 1 casa/mês, 0,5L = 1 copo, 13kg = 1 botijão), a função que arredonda meses de gás em "1 ano e 2 meses" em vez de "13,7 meses", e a função que monta o texto final de cada recurso, aplicando a regra de só aparecer quando a economia é real e o dado é confiável.

Campo economia_fisica em dados_loja
Antes, o código sabia quanto a loja consumiu e quanto era esperado, mas não guardava explicitamente "quanto ela economizou" como um número à parte. Adicionei esse cálculo (previsto corrigido menos real) porque o bloco de Impacto Ambiental precisa exatamente desse número para converter em casas, copos ou meses de gás.

Chamada no final de render_loja
É o gancho que efetivamente coloca o bloco de Impacto Ambiental na página, como você pediu: sempre por último, só no dashboard de Loja.

Bloco Ego/Autoimagem (linhas ~1810-1917)
Aqui é onde calculo, uma vez por rodada, quem são os "vencedores" de cada critério de destaque:

Quem tira o nome de exibição a partir do e-mail (função nome_de_email).
Quem é a loja mais eficiente de cada Nível, quem é a mais eficiente da marca no Brasil, e quem mais melhorou o índice no mês (as três funções de ranking de Loja).
Quem está no pódio de coordenadores por marca, e quem subiu de Nível no mês (ranking de Coordenador).
Qual regional teve o maior salto de índice, e qual teve mais lojas subindo de Nível (ranking de Regional).
E, por fim, as funções que pegam esses vencedores e escrevem a frase certa: uma versão "Parabéns" para quem venceu, outra citando o nome de quem venceu para todos os demais que vão ver o mesmo dashboard-tipo naquele mês.

Parâmetro ego_grupo em montar_grupo, e ego_lojas em dados_loja
Esses rankings de vencedores são calculados uma única vez para toda a rede (não faz sentido recalcular "quem é o 1º colocado" a cada loja/coordenador individualmente, isso seria caro e redundante). Então eu abri uma "porta de entrada" nessas duas funções para elas receberem o resultado já pronto e só descobrirem "e eu, sou o vencedor ou não?" na hora de montar a frase de cada pessoa.

Inserção nos templates HTML (render_coordenador, render_regional)
É o mesmo tipo de gancho do Loja: coloca o bloco de frases de ego logo abaixo do card de bandeira, no lugar que você validou.

Pré-cálculo único em main()
Esse é o ponto que amarra tudo: antes de começar a gerar os dashboards individuais, o script agora calcula os rankings de ego (loja, coordenador, regional) uma vez só, e essas listas de vencedores viajam para todas as ~1100 chamadas de dados_loja/montar_grupo que vêm depois. Isso evita recalcular a mesma coisa centenas de vezes e garante que todo mundo na rede está vendo o mesmo vencedor do mês, não versões divergentes.

CODIGO: eco_zamp_dashboards_v14 (7)

TEMA 4: Gráfico de Índice: enriquecimento (Loja) Modo Novo: no gráfico de Índice da Loja, adicione: (1) o Nível de cada mês mostrado; (2) 2 linhas tracejadas de referência: uma comparando com o P25 do cluster (mais eficiente) e outra com a melhor loja do Nível atual da loja.

Linha 858 — serie_consumo_12m (reescrita completa): janela expandida de 12 meses passados para jan-dez do ano. Retorna tupla de 4 elementos: (label, consumo, eh_projecao, meta). Meses FECHADO_COM_REAL usam consumo_real e consumo_previsto como meta. Meses PROJECAO usam consumo_projecao_fechamento e consumo_orcado como meta.

Linha 915 — grafico_consumo (expandida): aceita a nova tupla de 4 elementos e plota 3 datasets, barra real (cor do recurso), barra projeção ML (cor mais clara), e linha tracejada de meta. Mantém compatibilidade retroativa com tuplas de 2 ou 3 elementos usadas por coordenador e gerente.

Linha 898 (nova) — calc_serie_p25_cluster: calcula o índice equivalente ao P25 do cluster em cada um dos 12 meses, convertendo consumo_benchmark_p25 para a escala adimensional do índice via tarifa_orcada. Só usa recursos ativos (consumo_previsto > 0).

Linha 940 (nova) — calc_serie_melhor_cluster: envelope dinâmico mês a mês: melhor indice_eficiencia_mes do cluster (excluindo a própria loja), com filtro >= 0.10 e cobertura_score >= 0.5, mesmo crivo de bandeiras_por_cluster.

Linha 926 — grafico_indice (expandida): aceita dois parâmetros opcionais serie_p25 e serie_melhor. Plota linha tracejada verde escuro para P25 e linha tracejada roxa para melhor loja. Contém o TODO documentado para o Item 1.1 (nível por mês, que precisa de refactor de fronteiras históricas).

Linha 1697 — retorno de dados_loja: grafico_indice agora recebe as duas séries de referência calculadas na hora.

Regra nova para o prompt (adicionar a "Decisões e regras já travadas"):

Gráfico de índice da Loja (v14): duas linhas de referência tracejadas abaixo do índice principal. Verde escuro = P25 do cluster (consumo_benchmark_p25 convertido para escala do índice via tarifa_orcada, somente recursos com consumo_previsto > 0). Roxo = melhor loja do cluster no mês (envelope dinâmico, filtra indice >= 0.10 e cobertura_score >= 0.5, exclui a própria loja). Nível por mês: TODO pendente, documentado no código.
Gráfico de consumo da Loja (v14): expandido para jan-dez (12 meses passados + meses PROJECAO até dezembro). Barra real em cor do recurso, barra ML em cor mais clara, linha tracejada cinza de meta. Meta = consumo_previsto (meses FECHADO_COM_REAL) ou consumo_orcado (meses PROJECAO). Compatibilidade retroativa com série de 2/3 elementos (coordenador/gerente) mantida.

CÓDIGO: eco_zamp_dashboards_v14 (6)

TEMA 5: Dashboard de Loja: bugs e pareamento Bug: em "Ranking de Eficiência" aparece texto do tipo "reduzir o índice de 100% para 100%" (os dois valores iguais). Corrigir para sempre arredondar a meta em pelo menos 1 ponto percentual a menos (ex: 100% para 99%).

1677-1682 (bug do arredondamento): agora arredonda indice_mes e alvo_idx primeiro e força p_alvo = p_atual - 1 se empatarem. Não mexe em reducao_rs, só na exibição.

728-783 (comparavel_por_recurso): ordem de relaxamento invertida (área sai por último, tráfego é o primeiro a ser solto) e desempate trocado para distância de área em vez de tráfego. Testei isolado com a 15174/GÁS e bateu exatamente com o par validado antes (19524, área 1,9% de diferença).

CÓDIGO: eco_zamp_dashboards_v13.4 (1)

TEMA 6: - Dashboard de Coordenador e Gerente: bugs e ajustes - Adicione: em "Consumo acima do esperado por utility", logo abaixo do título, um "Resumo" listando cada loja da tabela "Lojas OFENSORAS" e qual utility foi o ofensor dela. Formato: "28370 - FS RIBEIRAO AV MAURILIO BIAGI 1394 (1) = Água e Energia", "18870 - FS RIB PRETO - AV PORTUGAL 810 (2) = Gás", etc.

Resumo (novo) — abaixo de 'Consumo acima do esperado por utility'
Novas funcoes resumo_ofensoras_por_utility() (linha 1395) e bloco_resumo_ofensoras() (linha 1423).
Chamadas em render_coordenador (linha ~1750) e render_regional (linha ~1780), logo apos o titulo da secao.
Formato: 'BKN - Nome da Loja (num) = Utility1 e Utility2'. Toda loja grifada tem por definicao >=1 utility acima
da meta (pct>0), sem fallback necessario.
Item 1 — Indice unico de referencia + card renomeado/reposicionado
Confirmado que ind_grupo (mes de referencia) ja era a unica fonte usada em bandeira, pares, meta, ranking e
simulacao (nenhuma mudanca de calculo necessaria). Card 'INDICE MEDIO 12M' removido da fileira do topo
em card_bandeira_grupo (linha ~1563; fileira passou de 4 para 3 colunas, 25%->33%). Nova funcao
card_indice_medio_12m() (linha 1552), renomeada 'Indice Medio ultimos 12 meses', reposicionada ao lado do
grafico de indice de 12 meses em render_coordenador e render_regional.
Item 2 — Graficos 'Consumo por Meta - ultimos 12 meses' (Coordenador e
Gerente)
Nova funcao serie_consumo_12m_grupo() (linha 2256): agregacao por soma dos bkns da carteira/regional,
reaproveitando as mesmas correcoes de consumo fantasma e orcamento errado ja usadas por loja.
Reaproveita grafico_consumo() (ja existente, formato grouped bar Real vs Meta) por recurso. Plugado em
montar_grupo (campo graficos_consumo_grupo) e renderizado em render_coordenador/render_regional,
mesmo formato do Dashboard de Loja.
GR-1 — Indice + Nivel por SETOR no grafico de indice (so Gerente Regional)
Nova funcao nivel_setores_regional() (linha 2385): indice medio atual e Nivel de cada setor da regional, com
esquema de faixas (8/5/3) calculado ENTRE OS SETORES da propria regional (nao BANDEIRAS_8 fixo). Nova
funcao bloco_indice_nivel_setores() (linha 1538) exibe a lista ao lado do grafico de indice das lojas, em
render_regional.
GR-2 — Bug corrigido: mais de 3 lojas grifadas nos graficos de consumo do
Regional
Causa raiz: 'grifadas' (usado nos 3 graficos de utility) era montado em montar_grupo a partir de detra_1x1 (1
loja por setor ofensor) sem limite, enquanto a tabela 'Lojas OFENSORAS' ja cortava em top_ofens=3
separadamente — duas listas deveriam ser a mesma e nao eram. Corrigido em montar_grupo (~linha
2170-2192): detra_1x1 agora e cortado em [:3] logo apos _uma_loja_por_setor, ANTES de somar com a
simulacao (sim_extra_1x1), que so preenche se ainda sobrar espaco dentro do limite de 3. Validado contra
dados reais nas 16 regionais em producao: nunca mais de 3 lojas grifadas em nenhuma.
GR-3 — Grafico de indice 12M por SETOR (so Gerente Regional)
Nova funcao serie_indice_12m_setores() (linha 2403): serie de 12 meses por setor, selecionando os 3 setores
mais ofensores + 3 mais eficientes (sem duplicar setor em caso de overlap, quando a regional tem poucos
setores). Nova funcao grafico_indice_setores() (linha 2431): grafico de linha com ate 6 series, sem grade, uma
cor por setor, linha de meta (100%) tracejada. Exibido no final de render_regional.
2o de 2 (posicao entre pares) — investigado, sem alteracao
Causa raiz confirmada contra de_para_roteamento: SBUX tem apenas 2 Gerentes Regionais cadastrados no
Brasil (abamonte e jmachia), PLK tem 3, BK tem 12. 'abamonte: 2o de 2' e dado real e correto, nao bug de
calculo. Decisao: manter como esta, sem alteracao de regra ou de código

CODIGO: eco_zamp_dashboard v15	

