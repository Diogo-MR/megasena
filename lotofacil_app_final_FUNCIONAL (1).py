
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

        st.subheader("🎯 Simular Acertos (buscando 15 dezenas)")
        resultados = []
        for jogo in df_ia["Dezenas"]:
            for i, linha in enumerate(concursos[dezenas_cols].values):
                acertos = len(set(jogo) & set(linha))
                if acertos == 15:
                    resultados.append({
                        "Jogo": jogo,
                        "Concurso": concursos.iloc[i]["Concurso"],
                        "Data": concursos.iloc[i]["Data Sorteio"],
                        "Acertos": acertos
                    })

        if resultados:
            st.success(f"{len(resultados)} jogos atingiram 15 dezenas na simulação histórica!")
            st.dataframe(pd.DataFrame(resultados))
        else:
            st.warning("Nenhum jogo IA bateu 15 dezenas com os dados simulados. Tente aumentar a quantidade.")

        st.subheader("📊 Comparar com Jogos Manuais")
        if "manuais" not in st.session_state:
            st.session_state.manuais = []

        with st.expander("➕ Adicionar jogo manual"):
            entrada = st.text_input("Digite 15 dezenas separadas por espaço")
            if st.button("Adicionar jogo manual"):
                nums = [int(n) for n in entrada.split() if n.isdigit()]
                if len(nums) == 15:
                    st.session_state.manuais.append(nums)
                    st.success("Jogo adicionado.")
                else:
                    st.error("Digite exatamente 15 números.")

        if st.session_state.manuais:
            df_manuais = pd.DataFrame(st.session_state.manuais)
            df_manuais.columns = [f"D{i}" for i in range(1,16)]
            df_manuais["Soma"] = df_manuais.sum(axis=1)
            df_manuais["Pares"] = df_manuais.apply(lambda x: len([n for n in x if n % 2 == 0]), axis=1)
            df_manuais["Ímpares"] = 15 - df_manuais["Pares"]
            df_manuais["Moldura"] = df_manuais.apply(lambda x: len(set(x) & moldura), axis=1)
            df_manuais["Repetidas com Último"] = df_manuais.apply(lambda x: len(set(x) & dezenas_ult), axis=1)

            st.dataframe(df_manuais)

            st.subheader("📈 Gráfico Comparativo IA x Manual")
            cat = ["Soma", "Pares", "Ímpares", "Moldura", "Repetidas com Último"]
            med_ia = df_ia[cat].mean()
            med_man = df_manuais[cat].mean()

            fig = go.Figure()
            fig.add_trace(go.Bar(x=cat, y=med_ia, name="IA"))
            fig.add_trace(go.Bar(x=cat, y=med_man, name="Manual"))
            fig.update_layout(barmode="group", title="Comparação Estatística IA x Manual")
            st.plotly_chart(fig)
    
    if st.button("🧪 Simular até acertar 15 dezenas"):
        st.subheader("🔍 Iniciando simulação por blocos até 15 acertos")
        tentativas = 0
        encontrados = []
        while True:
            tentativas += 100
            jogos_teste = []
            while len(jogos_teste) < 100:
                jogo = sorted(random.sample(range(1, 26), 15))
                pares = len([n for n in jogo if n % 2 == 0])
                if 6 <= pares <= 9:
                    jogos_teste.append(jogo)
            for jogo in jogos_teste:
                for i, linha in enumerate(concursos[dezenas_cols].values):
                    acertos = len(set(jogo) & set(linha))
                    if acertos == 15:
                        repetidas = len(set(jogo) & dezenas_ult)
                        moldura = len(set(jogo) & moldura)
                        soma = sum(jogo)
                        pares = len([n for n in jogo if n % 2 == 0])
                        impares = 15 - pares

                        encontrados.append({
                            "Jogo": jogo,
                            "Concurso": concursos.iloc[i]["Concurso"],
                            "Data": concursos.iloc[i]["Data Sorteio"],
                            "Acertos": acertos,
                            "Total Jogos Simulados": tentativas,
                            "Repetidas": repetidas,
                            "Pares": pares,
                            "Ímpares": impares,
                            "Moldura": moldura,
                            "Soma": soma
                        })
                        break
                if encontrados:
                    break
            if encontrados:
                break

        st.success(f"🎯 Jogo com 15 acertos encontrado após {tentativas} jogos simulados!")
        st.dataframe(pd.DataFrame(encontrados))