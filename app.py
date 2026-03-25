import streamlit as st
import json
import os
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

ARQUIVO = "progresso.json"

# -----------------------
# CONFIG + DARK MODE 🎮
# -----------------------
st.set_page_config(page_title="XP Fitness", layout="centered")

st.markdown("""
<style>
body { background-color: #0f172a; color: white; }
.stButton>button {
    background-color: #22c55e;
    color: black;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# -----------------------
# FUNÇÕES
# -----------------------

def calcular_xp(academia, corrida):
    xp = academia * 10 + corrida * 8
    if academia >= 4 and corrida >= 4:
        xp += 10
    return xp

def nivel(xp_total):
    if xp_total <= 300: return "🟢 Bronze"
    elif xp_total <= 800: return "🔵 Prata"
    elif xp_total <= 1400: return "🟣 Ouro"
    elif xp_total <= 2000: return "🟡 Platina"
    return "🔥 Diamante"

def carregar():
    if os.path.exists(ARQUIVO):
        with open(ARQUIVO, "r") as f:
            return json.load(f)
    return []

def salvar(dados):
    with open(ARQUIVO, "w") as f:
        json.dump(dados, f, indent=4)

# -----------------------
# SEMANA (SEG → DOM)
# -----------------------

def semana_str(data):
    inicio = data - timedelta(days=data.weekday())
    fim = inicio + timedelta(days=6)
    return inicio, fim, f"{inicio.strftime('%d/%m')} - {fim.strftime('%d/%m')}"

def semana_atual():
    return semana_str(datetime.now())

def semana_passada():
    return semana_str(datetime.now() - timedelta(days=7))

# -----------------------
# STREAK
# -----------------------

def calcular_streak(dados):
    streak = 0
    atual = datetime.now()

    for i in range(100):
        _, _, semana = semana_str(atual - timedelta(days=7*i))
        if any(d["semana"] == semana for d in dados):
            streak += 1
        else:
            break
    return streak

# -----------------------
# STATUS DA SEMANA
# -----------------------

def status_semana(acad, corr):
    if acad >= 4 and corr >= 3:
        return "🔥 Completa"
    elif acad >= 3 and corr >= 2:
        return "🟡 Em andamento"
    return "🔴 Atrasada"

def faltando(acad, corr):
    falta_acad = max(0, 4 - acad)
    falta_corr = max(0, 3 - corr)
    return falta_acad, falta_corr

# -----------------------
# APP
# -----------------------

st.title("🎮 XP Fitness")

dados = carregar()

abas = st.tabs(["➕ Registrar", "✏️ Editar", "📊 Dashboard"])

# -----------------------
# ABA 1 - REGISTRAR
# -----------------------

with abas[0]:
    inicio, fim, semana = semana_atual()
    st.subheader(f"📅 {semana}")

    academia = st.number_input("Academia", 0, 7)
    corrida = st.number_input("Corrida", 0, 7)

    # STATUS EM TEMPO REAL
    st.subheader("📊 Status da semana")

    st.write(status_semana(academia, corrida))

    falta_acad, falta_corr = faltando(academia, corrida)

    if falta_acad > 0 or falta_corr > 0:
        st.warning(f"Faltam {falta_acad} academia(s) e {falta_corr} corrida(s)")
    else:
        st.success("Meta semanal completa! 🔥")

    if st.button("Salvar Semana"):
        xp = calcular_xp(academia, corrida)

        dados = [d for d in dados if d["semana"] != semana]

        dados.append({
            "semana": semana,
            "academia": academia,
            "corrida": corrida,
            "xp": xp
        })

        salvar(dados)
        st.success(f"Salvo! XP: {xp}")

# -----------------------
# ABA 2 - EDITAR
# -----------------------

with abas[1]:
    _, _, semana = semana_passada()
    st.subheader(f"✏️ Editar {semana}")

    registro = next((d for d in dados if d["semana"] == semana), None)

    if registro:
        academia = st.number_input("Academia", 0, 7, value=registro["academia"])
        corrida = st.number_input("Corrida", 0, 7, value=registro["corrida"])

        if st.button("Atualizar"):
            xp = calcular_xp(academia, corrida)

            dados = [d for d in dados if d["semana"] != semana]
            dados.append({
                "semana": semana,
                "academia": academia,
                "corrida": corrida,
                "xp": xp
            })

            salvar(dados)
            st.success("Atualizado!")
    else:
        st.info("Nenhum registro da semana passada")

# -----------------------
# ABA 3 - DASHBOARD
# -----------------------

with abas[2]:
    st.subheader("📊 Resumo Geral")

    if dados:
        total_xp = sum(d["xp"] for d in dados)
        total_acad = sum(d["academia"] for d in dados)
        total_corr = sum(d["corrida"] for d in dados)

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("XP", total_xp)
        col2.metric("Nível", nivel(total_xp))
        col3.metric("🏋️", total_acad)
        col4.metric("🏃", total_corr)

        # PROGRESSO
        st.subheader("🎯 Progresso")
        st.progress(min(total_acad / 122, 1.0), text="Academia")
        st.progress(min(total_corr / 132, 1.0), text="Corrida")

        # STREAK
        streak = calcular_streak(dados)
        st.subheader(f"🔥 Streak: {streak} semanas seguidas")

        # HISTÓRICO
        st.subheader("📋 Histórico")
        st.dataframe(dados)

        # GRÁFICO
        st.subheader("📈 Evolução XP")
        semanas = [d["semana"] for d in dados]
        xp = [d["xp"] for d in dados]

        fig, ax = plt.subplots()
        ax.plot(semanas, xp, marker='o')
        plt.xticks(rotation=45)
        st.pyplot(fig)

    else:
        st.info("Sem dados ainda.")

        
# python -m streamlit run app.py