# Nota da Lu — comparador racional de notebooks

Aplicação em **Python + Streamlit** para comparar notebooks, estabelecer requisitos mínimos e construir um ranking de compra personalizado.

## Fluxo de decisão

O sistema separa quatro etapas:

1. **Especificações** — o que cada equipamento realmente oferece.
2. **Requisitos mínimos** — condições obrigatórias que podem eliminar uma opção.
3. **Pesos e notas** — importância de cada critério e qualidade da configuração correspondente.
4. **Ranking** — média ponderada apenas como apoio à decisão.

A página inicial funciona como menu visual e os cards levam diretamente a cada área.

## Recursos

- home com cards clicáveis;
- comparação lado a lado de até 10 equipamentos;
- filtro por grupos de specs;
- opção de mostrar somente diferenças;
- critério unificado **GPU**, compatível com gráficos integrados ou dedicados;
- campos técnicos separados de GPU integrada e GPU dedicada mantidos na ficha;
- **Preço atual (R$)** como dado e critério opcional de decisão;
- presets de perfil de compra;
- pesos apenas para critérios relevantes;
- notas editáveis com a **spec original visível ao lado**;
- requisitos mínimos para preço, RAM, SSD, peso e USB-C com carregamento;
- indicador de **cobertura dos dados** para reduzir falsa precisão;
- ranking ponderado;
- gestão de itens: cadastrar, editar e remover;
- backup/restauração dos cadastros em JSON;
- resumo executivo;
- exportação em CSV.

## Pontuação

A nota final é uma média ponderada:

```
nota = soma(nota_do_critério × peso_do_critério) / soma(pesos)
```

Critérios com peso 0 são ignorados.

Os requisitos mínimos são tratados separadamente: um equipamento que não atende a um requisito continua visível, mas aparece como **Não atende** no ranking.

## GPU

O campo **GPU** é usado no ranking.

Ao cadastrar um equipamento:

- se houver GPU dedicada, ela pode ser usada como GPU principal;
- caso contrário, o sistema usa a GPU integrada;
- os campos técnicos `GPU integrada` e `GPU dedicada` continuam disponíveis na ficha completa.

As notas automáticas de GPUs são heurísticas e podem ser alteradas manualmente.

## Preço

O campo **Preço atual (R$)** é opcional. Quando informado, entra no ranking como critério em que valores menores recebem notas maiores em relação às opções cadastradas.

Sem preços cadastrados, o sistema informa que a avaliação de custo-benefício está incompleta.

## Executar localmente

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy no Railway

O projeto inclui `Dockerfile`, `start.sh` e `railway.json`.

No Railway:

1. use **Deploy from GitHub Repo**;
2. selecione `fmaximiano/notedalu`;
3. deixe **Custom Start Command** vazio;
4. gere um domínio em **Networking**.

O container usa automaticamente a porta `$PORT`.

## Persistência

Os notebooks originais fazem parte do código. Alterações feitas pela interface ficam na sessão do Streamlit.

Para preservar cadastros entre reinicializações/redeploys do Railway, use **Itens cadastrados → Importar / exportar** e salve um backup JSON.

## Dados incompletos

“N/D” indica informação não confirmada. O ranking também exibe a **cobertura dos dados** de cada equipamento, evitando tratar uma opção com muitas lacunas como se tivesse a mesma confiabilidade de outra com ficha bem documentada.
