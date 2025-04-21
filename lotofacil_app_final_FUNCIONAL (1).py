
# ✅ LotoFácil App - Versão Final
# Gerador Inteligente com IA, estatísticas, simulação e gráfico comparativo
# Desenvolvido por LottoGPT (o verdadeiro parceiro de bolão)

import streamlit as st
import pandas as pd
import numpy as np
import random
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import plotly.graph_objects as go

st.set_page_config(page_title="Lotofácil IA Completa", layout="wide")
st.title("🍀 Simulador Inteligente da Lotofácil - IA & Estratégia Total")

uploaded_file = st.file_uploader("📤 Envie o arquivo .xlsx com os concursos da Lotofácil", type="xlsx")

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

    pares_ult = len([d for d in dezenas_ult if d % 2 == 0])
    pares_penult = len([d for d in dezenas_penult if d % 2 == 0])
    st.metric("🔄 Repetição de Pares", f"{len(dezenas_ult & dezenas_penult)} dezenas")
    st.metric("🎭 Padrão de Pares Último", f"{pares_ult} pares / {15 - pares_ult} ímpares")
    st.metric("🎭 Padrão Anterior", f"{pares_penult} pares / {15 - pares_penult} ímpares")

    ultimos_n = st.slider("Concursos para análise", 10, len(concursos), 50)
    dados_filtro = concursos.tail(ultimos_n)

    todas_dezenas = dados_filtro[dezenas_cols].values.ravel()
    freq = pd.Series(todas_dezenas).value_counts().sort_values(ascending=False)
    st.subheader("📊 Frequência das Dezenas")
    st.bar_chart(freq)

    moldura = {1,2,3,4,5,6,10,11,15,16,20,21,22,23,24,25}
    atrasadas = set(range(1,26)) - set(todas_dezenas)

    st.subheader("🎯 Geração de Jogos com IA")
    qtd_ia = st.number_input("Quantos jogos a IA deve sugerir?", 1, 1000, 10)
    qtd_simulacao = st.number_input("🔢 Quantos jogos deseja gerar?", 1, 10000, 1000, step=1, key="sim_aleatorio")
    filtro_rep = st.slider("Mínimo de dezenas iguais ao último concurso", 0, 15, 8)
    
    if st.button("🎯 Gerar Jogos com IA"):
        X, y = [], []
        from random import sample, random

        jogos = []
        while len(jogos) < qtd_simulacao:
            jogo = sorted(sample(range(1, 26), 15))
            pares = len([n for n in jogo if n % 2 == 0])
            impares = 15 - pares

            if impares > pares or random() > 0.9:
                jogos.append({
                    "Jogo": jogo,
                    "Pares": pares,
                    "Ímpares": impares,
                    "Soma": sum(jogo),
                    "Moldura": len(set(jogo) & moldura),
                    "Repetidas com Último": len(set(jogo) & dezenas_ult)
                })

        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X, y)
        importances = model.feature_importances_
        ranking = pd.Series(importances, index=range(1, 26)).sort_values(ascending=False)

        jogos = []
        while len(jogos) < qtd_simulacao:
            jogo = sorted(ranking.sample(15).index.tolist())
            pares = len([n for n in jogo if n % 2 == 0])
            impares = 15 - pares
            if impares > pares:
                if all(n not in atrasadas for n in jogo):
                    soma = sum(jogo)
                    if 180 <= soma <= 220:
                        mold = len(set(jogo) & moldura)
                        repetidas = len(set(jogo) & dezenas_ult)
                        padrao_ok = pares == pares_penult or impares == (15 - pares_penult)
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

    qtd_simulacao = st.number_input("🔢 Quantos jogos deseja simular até 15 acertos?", 1, 10000, 1000, step=1, key="sim15")

    if st.button("🧪 Simular até 15 acertos (todos os jogos)", key="simulador_full"):
        st.subheader("🔍 Rodando simulações...")
        resultados_sim = []
        from random import sample, random

        jogos = []
        while len(jogos) < qtd_simulacao:
            jogo = sorted(sample(range(1, 26), 15))
            pares = len([n for n in jogo if n % 2 == 0])
            impares = 15 - pares

            if impares > pares or random() > 0.9:
                jogos.append({
                    "Jogo": jogo,
                    "Pares": pares,
                    "Ímpares": impares,
                    "Soma": sum(jogo),
                    "Moldura": len(set(jogo) & moldura),
                    "Repetidas com Último": len(set(jogo) & dezenas_ult)
                })

            for i, linha in enumerate(concursos[dezenas_cols].values):
                linha_valida = [n for n in linha if not pd.isna(n)]
                acertos = len(set(jogo) & set(linha_valida))

                if acertos >= 11:  # considerar a partir de 11 acertos
                    resultados_sim.append({
                        "Jogo": jogo,
                        "Acertos": acertos,
                        "Concurso": concursos.iloc[i]["Concurso"],
                        "Data": concursos.iloc[i]["Data Sorteio"],
                        "Repetidas com Último": repetidas,
                        "Pares": pares,
                        "Ímpares": impares,
                        "Moldura": mold,
                        "Soma": soma
                    })
                    break

        if resultados_sim:
            df_sim = pd.DataFrame(resultados_sim)
            st.success(f"{len(df_sim)} jogos com 11+ acertos encontrados em {qtd_simulacao} simulados.")
            st.dataframe(df_sim)

            st.download_button("📥 Baixar resultado (CSV)", data=df_sim.to_csv(index=False).encode("utf-8"),
                               file_name="simulacoes_lotofacil.csv", mime="text/csv")

            st.markdown("📊 Distribuição de acertos:")
            st.bar_chart(df_sim["Acertos"].value_counts().sort_index())

        else:
            st.warning("Nenhum jogo obteve mais de 10 acertos nessa rodada.")

        
    qtd_simulacao = st.number_input("🔢 Quantos jogos deseja simular?", 1, 10000, 1000, step=1)

    if st.button("🧪 Simular Jogos Aleatórios"):
        resultados_sim = []
        from random import sample, random

        jogos = []
        while len(jogos) < qtd_simulacao:
            jogo = sorted(sample(range(1, 26), 15))
            pares = len([n for n in jogo if n % 2 == 0])
            impares = 15 - pares

            if impares > pares or random() > 0.9:
                jogos.append({
                    "Jogo": jogo,
                    "Pares": pares,
                    "Ímpares": impares,
                    "Soma": sum(jogo),
                    "Moldura": len(set(jogo) & moldura),
                    "Repetidas com Último": len(set(jogo) & dezenas_ult)
                })

            for i, linha in enumerate(concursos[dezenas_cols].values):
                linha_valida = [n for n in linha if not pd.isna(n)]
                acertos = len(set(jogo) & set(linha_valida))

                if acertos >= 13:  # você pode mudar esse corte
                    resultados_sim.append({
                        "Jogo": jogo,
                        "Concurso": concursos.iloc[i]["Concurso"],
                        "Data": concursos.iloc[i]["Data Sorteio"],
                        "Acertos": acertos,
                        "Repetidas com Último": repetidas,
                        "Pares": pares,
                        "Ímpares": impares,
                        "Moldura": mold,
                        "Soma": soma
                    })
                    break

        if resultados_sim:
            df_sim = pd.DataFrame(resultados_sim)
            st.success(f"{len(df_sim)} jogos com 13+ acertos encontrados.")
            st.dataframe(df_sim)
        else:
            st.warning("Nenhum jogo gerado atingiu 13 ou mais acertos.")

        
