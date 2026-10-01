# Note da Lu — comparador racional de notebooks

Aplicação em **Python + Streamlit** para comparar notebooks, definir requisitos mínimos, ponderar o que importa e chegar a um ranking explicado — com cada nota rastreável até a especificação que a originou.

## Páginas

| Página | Para quê |
|---|---|
| **Início** | Situação da decisão (líder, margem, preços faltando), roteiro em 5 passos e panorama do ranking. |
| **Comparar** | Ficha lado a lado (essencial ou completa), colunas em ordem de ranking, células coloridas pela nota do critério; aba **Duelo** compara dois notebooks critério a critério, em pontos do total. |
| **Pesos** | Peso de 0 a 10 por critério, distribuição da importância por grupo, perfis prontos e personalizados, nota para dados ausentes. |
| **Notas** | Mapa de calor de todas as notas, regra de cada critério e ajuste manual (com indicação do que é manual ou ausente). |
| **Ranking** | Pódio, composição da nota por grupo, nota técnica (sem preço), requisitos, robustez entre perfis e gráfico de custo-benefício (fronteira de Pareto). |
| **Resumo** | Um cartão por notebook: resumo, specs-chave, pontos fortes/fracos relativos e links. |
| **Equipamentos** | Lista, edição rápida de preços e links, cadastro/edição completo (inclusive “novo a partir de outro”), backup e restauração. |

A barra lateral fica disponível em todas as páginas: **perfil de pesos**, **notebooks em análise** e **requisitos mínimos** (preço máximo, RAM, teto de RAM, SSD, peso, tamanho de tela, carga via USB‑C, RJ‑45).

## Modelo de decisão

1. **Requisitos mínimos** são eliminatórios: quem não atende continua visível, mas vai para o fim do ranking.
2. **Notas (0–10)** usam **escalas absolutas** com âncoras explícitas — uma diferença pequena na ficha gera uma diferença pequena na nota.
3. **Pesos (0–10)** expressam prioridades.
4. **Nota final (0–100)** = média das notas ponderada pelos pesos.

Regras gerais:

- cada característica é contada **uma vez** (16:10 só em *Proporção*; Thunderbolt, vídeo e carga via USB‑C formam um único critério; tipo de RAM e dual-channel formam *Velocidade da RAM*);
- quando a ficha traz alternativas (“Wi‑Fi 5 ou Wi‑Fi 6”, “220 ou 250 nits”, “TN ou IPS”), vale a **pior hipótese**;
- dado ausente (“N/D”, “Não informado”, “Não confirmado”) **não** é tratado como “Não”: recebe a nota configurável de dado ausente (padrão 4, levemente conservadora);
- **preço** é o único critério relativo: a opção mais barata entre as analisadas recebe 10 e as demais `10 × (menor preço ÷ preço)²`;
- a coluna **Dados conhecidos** mostra quanto do peso de cada notebook está apoiado em informação real.

| Grupo | Critério | Base da nota |
|---|---|---|
| Preço | Preço | relativo ao mais barato |
| Desempenho | Processador | PassMark (60% multinúcleo + 40% núcleo único, escala log) |
| Desempenho | Gráficos (GPU) | estimativa de 3DMark Time Spy; iGPU Intel considera a CPU e se a RAM é dual-channel |
| Memória | RAM instalada · Velocidade da RAM · Teto de RAM (upgrade) | GB · tipo + canais · maior RAM alcançável oficialmente |
| Armazenamento | SSD instalado · Expansão | GB · slots M.2 livres / baia 2,5" |
| Tela | Resolução · Proporção · Painel · Brilho · Cores · Hz | linhas verticais · 16:10/3:2 · OLED > IPS > WVA > TN · nits · equivalente sRGB · Hz |
| Conectividade | Webcam · Wi‑Fi · USB‑C · RJ‑45 | resolução · geração (−0,7 para 1×1) · TB/USB4 ou vídeo + carga · possui/não |
| Mobilidade e construção | Bateria · Peso · Construção | Wh · kg · metal / misto / plástico |

A regra completa de cada critério aparece na página **Notas** e no “?” de cada controle em **Pesos**. Qualquer nota pode ser ajustada manualmente; ao editar a especificação de origem, a nota manual daquele critério é descartada.

### Processador

O cadastro aceita os campos **CPU PassMark (multi)** e **CPU PassMark (single)** (valores de [cpubenchmark.net](https://www.cpubenchmark.net)). Sem eles, o app usa uma referência interna para as CPUs da base e, para outras, uma estimativa pelo nome (indicada como estimativa na página Notas).

## Persistência e backup

- As alterações (notebooks, pesos, perfis, requisitos e notas manuais) são **salvas automaticamente** em `NOTEDALU_DATA_DIR/estado.json` (padrão `.data/`). Sessões abertas em paralelo se sincronizam ao interagir.
- `NOTEDALU_PERSIST=0` desliga a gravação em disco (tudo fica só na sessão).
- **Equipamentos → Backup** baixa/restaura um JSON completo. O formato antigo (lista de notebooks) também é aceito.
- **Equipamentos → Backup → Restaurar dados originais** volta à base embutida.

## Executar localmente

```bash
pip install -r requirements.txt
streamlit run app.py
```

Testes:

```bash
pip install pytest
python -m pytest -q
```

## Deploy no Railway

O projeto inclui `Dockerfile`, `start.sh` e `railway.json`.

1. **Deploy from GitHub Repo** → selecione `fmaximiano/notedalu`;
2. deixe **Custom Start Command** vazio;
3. gere um domínio em **Networking**;
4. para os dados sobreviverem a redeploys, crie um **Volume** montado em `/app/.data` (sem volume, o arquivo se perde a cada redeploy — mantenha um backup JSON).

O container usa automaticamente a porta `$PORT`.

## Estrutura

```
app.py                  interface Streamlit (páginas, gráficos, estado)
notedalu/data.py        base inicial de notebooks e grupos de especificações
notedalu/scoring.py     leitura das fichas, critérios, notas, ranking (sem Streamlit)
notedalu/storage.py     persistência em disco e formato de backup
tests/                  testes do modelo de decisão e testes de fumaça da interface
```

Links de anúncios e fontes técnicas de cada notebook ficam na ficha (grupo *Compra* e *Observações e fontes*). Preços não vêm cadastrados: informe-os em **Equipamentos → Preços**.
