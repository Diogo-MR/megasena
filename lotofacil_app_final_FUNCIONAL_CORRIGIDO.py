
    st.subheader("🎯 Geração de Jogos com IA")
    qtd_ia = st.number_input("Quantos jogos a IA deve sugerir?", 1, 1000, 10)
    filtro_rep = st.slider("Mínimo de dezenas iguais ao último concurso", 0, 15, 7)

    if len(dados_filtro) >= 10:
        if st.button("🎯 Gerar Jogos com IA"):
            try:
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

            except Exception as e:
                st.error(f"Erro ao gerar jogos com IA: {e}")
    else:
        st.warning("Número insuficiente de concursos para treinar a IA.")
