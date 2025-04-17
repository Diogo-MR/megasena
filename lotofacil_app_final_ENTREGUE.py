
import streamlit as st
import pandas as pd
import numpy as np
import random
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

st.set_page_config(page_title="Lotofácil - Simulador Inteligente", layout="wide")
st.title("🍀 Lotofácil com IA • Estatísticas • Simulação • Conferência de Jogos Salvos")

uploaded_file = st.file_uploader("Envie o arquivo .xlsx com os concursos da Lotofácil", type="xlsx")

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    dezenas_cols = [col for col in df.columns if "Bola" in col]
    concursos = df[["Concurso", "Data Sorteio"] + dezenas_cols].dropna()

    ult = concursos.iloc[-1]
    penult = concursos.iloc[-2]
    dezenas_ult = set(ult[dezenas_cols])
    dezenas_penult = set(penult[dezenas_cols])

    st.subheader(f"📅 Último concurso: {ult['Concurso']} ({pd.to_datetime(ult['Data Sorteio']).date()})")
    st.markdown("🔢 Dezenas sorteadas:")
    st.markdown(" ".join([f"`{int(n):02}`" for n in dezenas_ult]))

    moldura = {1,2,3,4,5,6,10,11,15,16,20,21,22,23,24,25}

    ultimos_n = st.slider("Concursos para análise", 10, len(concursos), 50)
    dados_filtro = concursos.tail(ultimos_n)

    todas_dezenas = dados_filtro[dezenas_cols].values.ravel()
    freq = pd.Series(todas_dezenas).value_counts().sort_values(ascending=False)
    st.subheader("📊 Frequência das Dezenas")
    st.bar_chart(freq)

    atrasadas = set(range(1,26)) - set(todas_dezenas)

    st.subheader("🎯 Geração de Jogos com IA")
    qtd_ia = st.number_input("Quantos jogos a IA deve sugerir?", 1, 1000, 10)
    filtro_rep = st.slider("Mínimo de dezenas iguais ao último concurso", 0, 15, 7)

    if st.button("🎯 Gerar Jogos com IA"):
        X, y = [], []
        for i in range(len(dados_filtro) - 1):
            atuais = set(dados_filtro.iloc[i][dezenas_cols])
            proximas = set(dados_filtro.iloc[i + 1][dezenas_cols])
            vetor = [1 if d in atuais else 0 for d in range(1, 26)]
            acertos = len(atuais & proximas)
            X.append(vetor)
            y.append(1 if acertos >= 12 else 0)

        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X, y)
        importances = model.feature_importances_
        ranking = pd.Series(importances, index=range(1, 26)).sort_values(ascending=False)

        jogos = []
        while len(jogos) < qtd_ia:
            jogo = sorted(ranking.sample(15).index.tolist())
            pares = len([n for n in jogo if n % 2 == 0])
            impares = 15 - pares
            if impares > pares:
                if all(n not in atrasadas for n in jogo):
                    soma = sum(jogo)
                    if 180 <= soma <= 220:
                        mold = len(set(jogo) & moldura)
                        repetidas = len(set(jogo) & dezenas_ult)
                        padrao_ok = pares == len([n for n in dezenas_penult if n % 2 == 0])
                        if repetidas >= filtro_rep and padrao_ok:
                            jogos.append({
                                "Dezenas": jogo,
                                "Repetidas com Último": repetidas,
                                "Pares": pares,
                                "Ímpares": impares,
                                "Moldura": mold,
                                "Soma": soma
                            })

        df_ia = pd.DataFrame(jogos)
        st.success(f"{len(jogos)} jogos gerados com base em validações estatísticas.")
        st.dataframe(df_ia)

        # ✅ BLOCO: Salvar jogos favoritos da IA
        st.subheader("📁 Meus Jogos Favoritos (selecionados da IA)")

        if "jogos_salvos" not in st.session_state:
            st.session_state.jogos_salvos = []

        if "Dezenas" in df_ia.columns:
            for idx, row in df_ia.iterrows():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**Jogo {idx+1}:** {' '.join([str(d).zfill(2) for d in row['Dezenas']])}")
                with col2:
                    if st.button(f"✅ Salvar jogo {idx+1}", key=f"salvar_{idx}"):
                        if row["Dezenas"] not in st.session_state.jogos_salvos:
                            st.session_state.jogos_salvos.append(row["Dezenas"])
                            st.success(f"Jogo {idx+1} salvo!")

        if st.session_state.jogos_salvos:
            st.subheader("🎯 Conferir Jogos Salvos com Último Concurso")
            resultados_fav = []
            for i, jogo in enumerate(st.session_state.jogos_salvos):
                acertos = len(set(jogo) & dezenas_ult)
                resultados_fav.append({
                    "Jogo Nº": i + 1,
                    "Dezenas": jogo,
                    "Acertos com Último Concurso": acertos
                })
            df_fav = pd.DataFrame(resultados_fav)
            st.dataframe(df_fav)
