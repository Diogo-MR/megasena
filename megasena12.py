import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random
import io

st.set_page_config(page_title="Análise Mega-Sena", layout="wide")
st.title("🍀 Simulador Inteligente da Mega-Sena")

# Upload do arquivo Excel
uploaded_file = st.file_uploader("Envie o arquivo .xlsx com os resultados da Mega-Sena", type="xlsx")
if uploaded_file:
    df = pd.read_excel(uploaded_file, sheet_name="MEGA SENA")
    dezenas_cols = ['Bola1', 'Bola2', 'Bola3', 'Bola4', 'Bola5', 'Bola6']
    concursos = df[['Concurso'] + dezenas_cols].dropna()

    st.subheader("🔢 Frequência das Dezenas")
    ultimos_n = st.slider("Quantos últimos concursos considerar?", 10, len(concursos), 100)
    dados_filtro = concursos.tail(ultimos_n)

    todas_dezenas = dados_filtro[dezenas_cols].values.ravel()
    freq = pd.Series(todas_dezenas).value_counts().sort_values(ascending=False)

    st.bar_chart(freq)

    top_n = st.slider("Quantas dezenas mais frequentes usar para gerar os jogos?", 6, 60, 30)
    dezenas_base = list(freq.head(top_n).index)

    st.subheader("🎲 Gerar Jogos Aleatórios")
    qtd_jogos = st.number_input("Quantos jogos deseja gerar?", min_value=1, max_value=10000, value=100)

    def gerar_jogos(possiveis_dezenas, qtd):
        jogos = set()
        while len(jogos) < qtd:
            jogo = tuple(sorted(random.sample(possiveis_dezenas, 6)))
            jogos.add(jogo)
        return list(jogos)

    if st.button("🎩 Gerar Jogos"):
        jogos_gerados = gerar_jogos(dezenas_base, qtd_jogos)
        st.success(f"{qtd_jogos} jogos gerados com base nas {top_n} dezenas mais frequentes.")
        st.dataframe(jogos_gerados, use_container_width=True)

        st.subheader("✅ Simular Acertos com os últimos concursos")
        resultados = []
        concursos_lista = dados_filtro[dezenas_cols].values.tolist()

        for idx, jogo in enumerate(jogos_gerados, 1):
            for n, sorteio in enumerate(concursos_lista):
                acertos = len(set(jogo).intersection(set(sorteio)))
                if acertos >= 4:
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
                file_name='resultados_megasena.csv',
                mime='text/csv'
            )
        else:
            st.warning("Nenhum jogo gerado obteve 4 ou mais acertos nos últimos concursos.")
