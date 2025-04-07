import streamlit as st
import pandas as pd
import numpy as np
import random

st.set_page_config(page_title="Análise Lotofácil", layout="wide")
st.title("🍀 Simulador Inteligente da Lotofácil")

uploaded_file = st.file_uploader("Envie o arquivo .xlsx com os resultados da Lotofácil", type="xlsx")
if uploaded_file:
    df = pd.read_excel(uploaded_file)
    dezenas_cols = [col for col in df.columns if "Bola" in col]
    concursos = df[['Concurso'] + dezenas_cols].dropna()

    st.subheader("🔢 Frequência das Dezenas")
    ultimos_n = st.slider("Quantos últimos concursos considerar?", 10, len(concursos), 50)
    dados_filtro = concursos.tail(ultimos_n)

    todas_dezenas = dados_filtro[dezenas_cols].values.ravel()
    freq = pd.Series(todas_dezenas).value_counts().sort_values(ascending=False)

    st.bar_chart(freq)

    top_n = st.slider("Quantas dezenas mais frequentes usar para gerar os jogos?", 15, 25, 20)
    dezenas_base = list(freq.head(top_n).index)

    st.subheader("🎲 Gerar Jogos Inteligentes")
    qtd_jogos = st.number_input("Quantos jogos deseja gerar?", min_value=1, max_value=10000, value=100)

    def gerar_jogos_balanceados(possiveis_dezenas, qtd):
        jogos = set()
        while len(jogos) < qtd:
            jogo = sorted(random.sample(possiveis_dezenas, 15))
            pares = len([n for n in jogo if n % 2 == 0])
            impares = 15 - pares
            if impares > pares:
                jogos.add(tuple(jogo))
        return list(jogos)

    if st.button("🎩 Gerar Jogos"):
        jogos_gerados = gerar_jogos_balanceados(dezenas_base, qtd_jogos)
        st.success(f"{len(jogos_gerados)} jogos gerados com mais ímpares que pares.")
        st.dataframe(jogos_gerados, use_container_width=True)

        st.subheader("✅ Simular Acertos com os últimos concursos")
        resultados = []
        concursos_lista = dados_filtro[dezenas_cols].values.tolist()

        for idx, jogo in enumerate(jogos_gerados, 1):
            for n, sorteio in enumerate(concursos_lista):
                acertos = len(set(jogo).intersection(set(sorteio)))
                if acertos >= 14:
                    resultados.append({
                        'Jogo Nº': idx,
                        'Dezenas': jogo,
                        'Acertos': acertos,
                        'Concurso': dados_filtro.iloc[n]['Concurso']
                    })
                    break

        if resultados:
            df_resultados = pd.DataFrame(resultados)
            st.dataframe(df_resultados, use_container_width=True)

            csv = df_resultados.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📁 Baixar resultados em CSV",
                data=csv,
                file_name='resultados_lotofacil.csv',
                mime='text/csv'
            )
        else:
            st.warning("Nenhum jogo gerado obteve 14 ou mais acertos nos últimos concursos.")
