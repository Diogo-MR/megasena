
import streamlit as st
import pandas as pd
import numpy as np
import random
import plotly.graph_objects as go
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

st.set_page_config(page_title="Lotofácil Avançada", layout="wide")
st.title("🍀 Análise Inteligente da Lotofácil")

uploaded_file = st.file_uploader("Envie o arquivo .xlsx com os resultados da Lotofácil", type="xlsx")
if uploaded_file:
    df = pd.read_excel(uploaded_file)
    dezenas_cols = [col for col in df.columns if "Bola" in col]
    concursos = df[['Concurso', 'Data Sorteio'] + dezenas_cols].dropna()

    ultimos_n = st.slider("Quantos concursos usar na análise?", 10, len(concursos), 50)
    dados_filtro = concursos.tail(ultimos_n)
    todas_dezenas = dados_filtro[dezenas_cols].values.ravel()
    freq = pd.Series(todas_dezenas).value_counts().sort_values(ascending=False)
    dezenas_base = list(freq.head(20).index)

    st.subheader("📅 Último Concurso")
    ultimo = concursos.iloc[-1]
    st.markdown(f"**Concurso {int(ultimo['Concurso'])}** - {pd.to_datetime(ultimo['Data Sorteio']).date()}")
    st.write("🔢 Dezenas sorteadas:")
    st.markdown(" ".join([f"`{int(n):02}`" for n in ultimo[dezenas_cols]]))

    st.subheader("🧠 IA: Geração e Análise de Jogos")
    qtd_ia = st.number_input("Quantos jogos IA deve sugerir?", 1, 1000, 10)

    X, y = [], []
    for i in range(len(dados_filtro) - 1):
        atuais = set(dados_filtro.iloc[i][dezenas_cols])
        proximas = set(dados_filtro.iloc[i + 1][dezenas_cols])
        vetor = [1 if d in atuais else 0 for d in range(1, 26)]
        acertos = len(atuais.intersection(proximas))
        X.append(vetor)
        y.append(1 if acertos >= 12 else 0)

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)

    importances = model.feature_importances_
    ranking = pd.Series(importances, index=range(1, 26)).sort_values(ascending=False)
    base_jogo = set(ultimo[dezenas_cols])

    sugestoes = []
    while len(sugestoes) < qtd_ia:
        jogo = sorted(ranking.sample(15).index.tolist())
        pares = len([n for n in jogo if n % 2 == 0])
        impares = 15 - pares
        if impares > pares:
            moldura = {1,2,3,4,5,6,10,11,15,16,20,21,22,23,24,25}
            moldura_count = len(set(jogo).intersection(moldura))
            repetidas = len(set(jogo).intersection(base_jogo))
            soma = sum(jogo)
            sugestoes.append({
                "Dezenas": jogo,
                "Repetidas com Último": repetidas,
                "Soma": soma,
                "Pares": pares,
                "Ímpares": impares,
                "Moldura": moldura_count
            })

    df_ia = pd.DataFrame(sugestoes)

    filtro_rep = st.slider("🔍 Filtrar sugestões com pelo menos X repetições com o último concurso:", 0, 15, 7)
    df_filtrado = df_ia[df_ia["Repetidas com Último"] >= filtro_rep]

    st.dataframe(df_filtrado.reset_index(drop=True), use_container_width=True)

    csv_ia = df_filtrado.to_csv(index=False).encode("utf-8")
    st.download_button("📁 Baixar sugestões IA filtradas", csv_ia, "ia_filtradas.csv", "text/csv")

    st.subheader("📊 Comparativo IA x Manual (média dos jogos)")

    if "Jogos Manuais" not in st.session_state:
        st.session_state["Jogos Manuais"] = []

    with st.expander("➕ Adicionar jogo manual"):
        jogo_manual = st.text_input("Digite 15 dezenas separadas por espaço:")
        if st.button("Adicionar jogo"):
            numeros = [int(n) for n in jogo_manual.split() if n.isdigit()]
            if len(numeros) == 15:
                st.session_state["Jogos Manuais"].append(sorted(numeros))
                st.success("Jogo manual adicionado com sucesso.")
            else:
                st.error("Informe exatamente 15 dezenas.")

    jogos_man = st.session_state["Jogos Manuais"]
    if jogos_man:
        df_man = pd.DataFrame(jogos_man, columns=[f"D{i}" for i in range(1, 16)])
        df_man["Soma"] = df_man.sum(axis=1)
        df_man["Pares"] = df_man.apply(lambda x: len([n for n in x if n % 2 == 0]), axis=1)
        df_man["Ímpares"] = 15 - df_man["Pares"]
        df_man["Moldura"] = df_man.apply(lambda x: len(set(x) & moldura), axis=1)
        df_man["Repetidas com Último"] = df_man.apply(lambda x: len(set(x) & base_jogo), axis=1)

        st.dataframe(df_man, use_container_width=True)

        st.subheader("📈 Gráfico comparativo")
        categorias = ["Soma", "Pares", "Ímpares", "Moldura", "Repetidas com Último"]
        media_ia = df_filtrado[categorias].mean()
        media_man = df_man[categorias].mean()

        fig = go.Figure()
        fig.add_trace(go.Bar(x=categorias, y=media_ia, name="Sugestões IA"))
        fig.add_trace(go.Bar(x=categorias, y=media_man, name="Jogos Manuais"))
        fig.update_layout(barmode="group", title="Comparativo Estatístico: IA x Manual")
        st.plotly_chart(fig, use_container_width=True)
