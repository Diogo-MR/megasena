
# ✅ SIMULAÇÃO OTIMIZADA: até encontrar jogo com 15 acertos
st.subheader("🧪 Simular até acertar 15 dezenas (modo otimizado)")
max_blocos = 50
blocos_rodados = 0
tentativas = 0
encontrados = []

progress_bar = st.progress(0, text="Simulando...")

while blocos_rodados < max_blocos:
    blocos_rodados += 1
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
                pares = len([n for n in jogo if n % 2 == 0])
                impares = 15 - pares
                mold = len(set(jogo) & moldura)
                soma = sum(jogo)

                encontrados.append({
                    "Jogo": jogo,
                    "Concurso": concursos.iloc[i]["Concurso"],
                    "Data": concursos.iloc[i]["Data Sorteio"],
                    "Acertos": acertos,
                    "Total Jogos Simulados": tentativas,
                    "Repetidas": repetidas,
                    "Pares": pares,
                    "Ímpares": impares,
                    "Moldura": mold,
                    "Soma": soma
                })
                break
        if encontrados:
            break

    progress_bar.progress(blocos_rodados / max_blocos)

    if encontrados:
        break

if encontrados:
    st.success(f"🎯 Jogo com 15 acertos encontrado após {tentativas} jogos simulados!")
    st.dataframe(pd.DataFrame(encontrados))
else:
    st.warning("🚫 Nenhum jogo com 15 acertos encontrado após 5.000 simulações.")
