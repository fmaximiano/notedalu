# Nota da Lu — comparador de notebooks

Aplicação interativa em **Python + Streamlit** para comparar notebooks e montar um ranking de compra personalizado.

## Recursos

- página inicial orientando as principais ações;
- ficha técnica completa com todos os critérios levantados;
- **comparativo lado a lado de até 10 itens**;
- filtro por grupos de specs e opção de mostrar somente diferenças;
- pesos de 0 a 10 apenas para os critérios mais relevantes;
- notas editáveis de 0 a 10 com a **spec original visível ao lado**;
- ranking ponderado atualizado em tempo real;
- presets: equilibrado, mobilidade, produtividade, desempenho, tela/multimídia e expansão/longevidade;
- gestão de itens: cadastrar, editar e remover notebooks;
- cadastro guiado por grupos de especificações;
- backup e restauração dos cadastros em JSON;
- resumo executivo;
- exportação do ranking e comparativos em CSV;
- fontes e links dos anúncios preservados na base.

## Como funciona a pontuação

A nota final é uma média ponderada:

```
nota = soma(nota_do_critério × peso_do_critério) / soma(pesos)
```

Peso 0 remove o critério do ranking. As notas iniciais são heurísticas para servir como ponto de partida e podem ser alteradas livremente.

## Executar localmente

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy no Railway

O projeto inclui `Dockerfile`, `start.sh` e `railway.json`.

No Railway:

1. crie um projeto com **Deploy from GitHub Repo**;
2. selecione `fmaximiano/notedalu`;
3. mantenha o **Custom Start Command vazio**;
4. aguarde o build/deploy;
5. em **Networking**, gere um domínio público.

O container inicia o Streamlit usando a porta dinâmica `$PORT`.

## Persistência dos itens cadastrados

Os 7 notebooks originais fazem parte do código. Itens adicionados ou alterados pela interface ficam na sessão do Streamlit. Como containers do Railway podem ser reiniciados, a tela **Itens cadastrados → Importar / exportar** permite baixar e restaurar um backup JSON.

## Observação

“N/D” significa que a informação não foi confirmada com segurança. Specs incertas são mantidas explícitas em vez de serem tratadas como fatos.
