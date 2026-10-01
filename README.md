# Nota da Lu — comparador de notebooks

Aplicação interativa em **Python + Streamlit** para comparar as 7 configurações de notebooks pesquisadas.

## Recursos

- ficha técnica completa com todos os critérios levantados;
- pesos de 0 a 10 para cada critério;
- notas editáveis de 0 a 10 por notebook e critério;
- ranking ponderado atualizado em tempo real;
- presets de compra: equilibrado, mobilidade, produtividade, desempenho, tela/multimídia e expansão/longevidade;
- comparação lado a lado;
- resumo executivo;
- exportação de ranking e especificações em CSV;
- fontes e links dos anúncios preservados na base.

## Executar

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Como funciona a pontuação

A nota final é uma média ponderada:

```
nota = soma(nota_do_critério × peso_do_critério) / soma(pesos)
```

Peso 0 remove o critério do ranking. As notas iniciais são apenas um ponto de partida e podem ser alteradas livremente na interface.

## Observação

“N/D” significa que a informação não foi confirmada com segurança. No ThinkPad E14, o anúncio não informa o submodelo/MTM completo, portanto alguns componentes são apresentados como variantes.
