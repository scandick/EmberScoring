import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go


st.set_page_config(
    page_title="Дашборд риска выгорания",
    layout="wide"
)

st.title("Скоринг риска выгорания сотрудников")

st.markdown("---")


# СИНТЕТИЧЕСКИЕ ДАННЫЕ

np.random.seed(42)

n_employees = 120
n_weeks = 12

teams = ["Backend", "Frontend", "QA", "Data Science", "DevOps", "Product", "HR"]

base = pd.DataFrame({
    "employee_id": range(1001, 1001 + n_employees),
    "team": np.random.choice(teams, n_employees),
    "base_overtime": np.random.normal(8, 3, n_employees).clip(0),
    "base_meetings": np.random.normal(18, 5, n_employees).clip(0),
    "base_night": np.random.normal(4, 2, n_employees).clip(0)
})

rows = []

for _, r in base.iterrows():
    for w in range(n_weeks):
        trend = 1 + (w / n_weeks) * 0.25
        noise = np.random.normal(0, 1.5)

        burnout = (
            r["base_overtime"] * 2.4 +
            r["base_night"] * 2.1 +
            r["base_meetings"] * 1.2
        ) * trend + noise

        rows.append({
            "employee_id": r["employee_id"],
            "team": r["team"],
            "week": w,
            "burnout_score": np.clip(burnout, 0, 100),
            "overtime": r["base_overtime"] * trend
        })

df = pd.DataFrame(rows)

latest = df[df["week"] == df["week"].max()]

# -----------------------------
# Фильтры

st.sidebar.header("Фильтры")

selected_team = st.sidebar.multiselect(
    "Выберите команды",
    teams,
    default=teams
)

view_mode = st.sidebar.selectbox(
    "Уровень анализа",
    ["Компания", "Команда", "Сотрудник"]
)

forecast_horizon = st.sidebar.selectbox(
    "Прогнозный период",
    ["7 дней", "14 дней", "30 дней", "60 дней"]
)

horizon_map = {
    "7 дней": 7,
    "14 дней": 14,
    "30 дней": 30,
    "60 дней": 60
}

horizon = horizon_map[forecast_horizon]

filtered = df[df["team"].isin(selected_team)]

selected_employee = None
if view_mode == "Сотрудник":
    selected_employee = st.sidebar.selectbox("Выберите сотрудника", filtered["employee_id"].unique())

# -----------------------------
# KPI

latest_f = filtered[filtered["week"] == filtered["week"].max()]

st.subheader("Ключевые метрики")

col1, col2, col3 = st.columns(3)

col1.metric("Сотрудников в выборке", latest_f["employee_id"].nunique())
col2.metric("Средний риск выгорания", f"{latest_f['burnout_score'].mean():.1f}")
col3.metric("Средние переработки", f"{latest_f['overtime'].mean():.1f}")

st.markdown("---")

# -----------------------------
# РАСПРЕДЕЛЕНИЕ + КОМАНДЫ

st.subheader("Распределение и анализ команд")

col1, col2 = st.columns(2)

with col1:
    fig = px.histogram(
        latest_f,
        x="burnout_score",
        nbins=20,
        title="Распределение риска выгорания (последняя неделя)"
    )
    fig.update_layout(
        xaxis_title="Риск выгорания",
        yaxis_title="Количество сотрудников",
        template="plotly_white"
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    team_avg = latest_f.groupby("team")["burnout_score"].mean().reset_index()

    fig = px.bar(
        team_avg,
        x="team",
        y="burnout_score",
        title="Средний риск по командам"
    )

    fig.update_layout(
        xaxis_title="Команда",
        yaxis_title="Риск выгорания",
        template="plotly_white"
    )

    st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# ТРЕНД + ПРОГНОЗ

st.subheader("Динамика риска выгорания + прогноз")

if view_mode == "Компания":
    trend = filtered.groupby("week")["burnout_score"].mean().reset_index()

elif view_mode == "Команда":
    trend = filtered.groupby(["week", "team"])["burnout_score"].mean().reset_index()

else:
    trend = filtered[filtered["employee_id"] == selected_employee]

fig = go.Figure()

# historical
fig.add_trace(go.Scatter(
    x=trend["week"],
    y=trend["burnout_score"],
    mode="lines+markers",
    name="Фактический риск"
))

# forecast (synthetic extension)
last_week = trend["week"].max()
future_weeks = np.arange(last_week + 1, last_week + horizon + 1)

last_value = trend["burnout_score"].mean()

forecast = last_value + np.cumsum(np.random.normal(0.5, 0.8, len(future_weeks)))

fig.add_trace(go.Scatter(
    x=future_weeks,
    y=forecast,
    mode="lines",
    name=f"Прогноз на {forecast_horizon}"
))

fig.update_layout(
    xaxis_title="Период",
    yaxis_title="Риск выгорания",
    template="plotly_white",
    xaxis=dict(showgrid=True),
    yaxis=dict(showgrid=True),
    title="Динамика риска и прогноз"
)

st.plotly_chart(fig, use_container_width=True)


# -----------------------------
# ТОП РИСКА

st.subheader("Сотрудники с максимальным риском")

top = latest_f.sort_values("burnout_score", ascending=False).head(10)

st.dataframe(
    top[["employee_id", "team", "burnout_score"]],
    use_container_width=True
)
