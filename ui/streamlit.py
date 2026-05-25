import altair as alt
import pandas as pd
import streamlit as st

from dataManager import data

try:
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ModuleNotFoundError:
    px = None
    PLOTLY_AVAILABLE = False


st.set_page_config(page_title="Ember", layout="wide")

PAGE_SIZE = 25


def init_state():
    defaults = {
        "current_page": "Dashboard",
        "selected_team": None,
        "selected_employee_id": None,
        "employees_skip": 0,
        "employee_team_filter": "All Teams",
        "employee_job_role_filter": "",
        "team_job_role_filter": "",
        "forecast_results": {},
        "recommendation_results": {},
        "latest_score_overrides": {},
        "recent_scored_employee_ids": [],
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def navigate_to(page: str):
    st.session_state.current_page = page
    if page != "Employees":
        st.session_state.selected_employee_id = None
    if page != "Teams":
        st.session_state.selected_team = None


def score_color(risk_level: str | None) -> str:
    normalized = (risk_level or "").lower()
    return {
        "low": "#2e7d32",
        "moderate": "#ef6c00",
        "high": "#c62828",
        "critical": "#7f0000",
    }.get(normalized, "#546e7a")


def score_label(score: dict | None) -> str:
    if not score:
        return "Не оценен"
    level_map = {
        "low": "Низкий",
        "moderate": "Средний",
        "high": "Высокий",
        "critical": "Критический",
    }
    level = level_map.get(score["risk_level"].lower(), score["risk_level"])
    return f"{level} | {int(score['risk_score'])}"


def remember_scored_employee(employee_id: int):
    current = [value for value in st.session_state.recent_scored_employee_ids if value != employee_id]
    current.insert(0, employee_id)
    st.session_state.recent_scored_employee_ids = current[:10]


def get_teams():
    return data.get_teams()


def get_team_options():
    teams = get_teams()
    return ["All Teams"] + [item["team"] for item in teams]


def list_employees(team: str | None, job_role: str | None, skip: int):
    return data.get_employees(
        skip=skip,
        limit=PAGE_SIZE,
        team=None if team == "All Teams" else team,
        job_role=job_role or None,
    )


def list_employee_scores(team: str | None, job_role: str | None, skip: int):
    scores = data.get_cached_scores(
        skip=skip,
        limit=PAGE_SIZE,
        team=None if team == "All Teams" else team,
        job_role=job_role or None,
    )
    return {item["employee_id"]: item for item in scores}


def draw_sidebar():
    with st.sidebar:
        st.title("Ember")
        st.caption(f"API: `{data.api_base_url}`")

        st.button(
            "Дашборд",
            use_container_width=True,
            type="primary" if st.session_state.current_page == "Dashboard" else "secondary",
            on_click=navigate_to,
            args=("Dashboard",),
        )
        st.button(
            "Команды",
            use_container_width=True,
            type="primary" if st.session_state.current_page == "Teams" else "secondary",
            on_click=navigate_to,
            args=("Teams",),
        )
        st.button(
            "Сотрудники",
            use_container_width=True,
            type="primary" if st.session_state.current_page == "Employees" else "secondary",
            on_click=navigate_to,
            args=("Employees",),
        )

        selected_employee_id = st.session_state.selected_employee_id
        if selected_employee_id is not None:
            employee = data.get_employee(selected_employee_id)
            latest_score = (
                st.session_state.latest_score_overrides.get(selected_employee_id)
                or data.get_latest_score(selected_employee_id)
            )

            st.divider()
            st.caption("Текущий AI-фокус")

            employee_label = (
                f"{employee['employee_id']} | {employee['team']}"
                if employee
                else f"Employee #{selected_employee_id}"
            )
            st.write(f"**{employee_label}**")

            if latest_score:
                color = score_color(latest_score.get("risk_level"))
                st.markdown(
                    f"<span style='color:{color}; font-weight:600;'>{score_label(latest_score)}</span>",
                    unsafe_allow_html=True,
                )
            else:
                st.caption("Не оценен")

            st.button(
                f"Профиль сотрудника: {employee['employee_id'] if employee else selected_employee_id}",
                use_container_width=True,
                type="primary" if st.session_state.current_page == "Employees" else "secondary",
                on_click=navigate_to,
                args=("Employees",),
            )

        recent_ids = st.session_state.recent_scored_employee_ids
        if recent_ids:
            st.divider()
            st.caption("Последние результаты скоринга")

            for employee_id in recent_ids:
                employee = data.get_employee(employee_id)
                latest_score = (
                    st.session_state.latest_score_overrides.get(employee_id)
                    or data.get_latest_score(employee_id)
                )

                if employee is None:
                    continue

                button_label = f"{employee['employee_id']} | {employee['team']}"
                if st.button(button_label, key=f"recent_scored_{employee_id}", use_container_width=True):
                    st.session_state.selected_employee_id = employee_id
                    st.session_state.current_page = "Employees"
                    st.rerun()

                if latest_score:
                    color = score_color(latest_score.get("risk_level"))
                    st.markdown(
                        f"<span style='color:{color}; font-size:0.9rem;'>{score_label(latest_score)}</span>",
                        unsafe_allow_html=True,
                    )
                else:
                    st.caption("Результат недоступен")


def draw_dashboard():
    teams = get_teams()
    stats = data.get_score_stats()

    total_employees = sum(item["employee_count"] for item in teams)
    total_teams = len(teams)

    st.title("Общий дашборд компании")
    st.caption("Обзор сотрудников, команд и сохранённых AI-результатов скоринга.")

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Всего сотрудников", total_employees)
    k2.metric("Команд", total_teams)
    k3.metric("Оценено", stats["scored_employees"])
    k4.metric("В зоне риска", stats["at_risk_employees"])

    st.write("")

    alert_col1, alert_col2 = st.columns(2)
    with alert_col1:
        if stats["at_risk_employees"] > 0:
            st.error(
                f"В сохранённом кеше уже есть {stats['at_risk_employees']} сотрудников с высоким или критическим риском."
            )
        else:
            st.info("Сохранённых high-risk сотрудников пока нет. Запусти скоринг из профиля сотрудника.")
    with alert_col2:
        if stats["scored_employees"] > 0:
            st.success(
                f"Для {stats['scored_employees']} сотрудников уже сохранены результаты burnout scoring."
            )
        else:
            st.warning("Кеш скоринга пуст. Начни с профиля сотрудника и запусти текущий скоринг.")

    teams_df = pd.DataFrame(teams)
    if teams_df.empty:
        st.info("Данные по командам пока недоступны.")
        return

    left, right = st.columns([1.4, 1])

    with left:
        chart = (
            alt.Chart(teams_df)
            .mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6)
            .encode(
                x=alt.X("team:N", title="Team", sort="-y"),
                y=alt.Y("employee_count:Q", title="Employees"),
                color=alt.value("#1f77b4"),
                tooltip=["team", "employee_count"],
            )
            .properties(height=340)
        )
        st.altair_chart(chart, use_container_width=True)

    with right:
        st.subheader("Команды")
        st.dataframe(
            teams_df.rename(columns={"team": "Команда", "employee_count": "Сотрудники"}),
            hide_index=True,
            use_container_width=True,
        )


def draw_team_page():
    teams = get_teams()
    if not teams:
        st.info("Команды пока недоступны.")
        return

    team_names = [item["team"] for item in teams]
    default_team = st.session_state.selected_team or team_names[0]
    selected_team = st.selectbox(
        "Команда",
        options=team_names,
        index=team_names.index(default_team) if default_team in team_names else 0,
    )
    st.session_state.selected_team = selected_team

    selected_team_meta = next(item for item in teams if item["team"] == selected_team)
    summary = data.get_team_summary(selected_team)
    team_scores = data.get_score_stats(team=selected_team)
    team_employees = data.get_team_employees(
        selected_team,
        skip=0,
        limit=PAGE_SIZE,
        job_role=st.session_state.team_job_role_filter or None,
    )
    cached_scores = {
        item["employee_id"]: item
        for item in data.get_cached_scores(
            skip=0,
            limit=PAGE_SIZE,
            team=selected_team,
            job_role=st.session_state.team_job_role_filter or None,
        )
    }

    st.title(f"Обзор команды: {selected_team}")
    st.caption("Сводные производные метрики нагрузки и текущий состав команды.")

    k1, k2, k3 = st.columns(3)
    k1.metric("Сотрудники", selected_team_meta["employee_count"])
    k2.metric("Оценено", team_scores["scored_employees"])
    k3.metric("В зоне риска", team_scores["at_risk_employees"])

    if summary:
        s1, s2, s3, s4, s5 = st.columns(5)
        s1.metric("Переработка", f"{summary.get('avg_overtime_hours', 0):.1f} ч")
        s2.metric("Больничные", f"{summary.get('avg_sick_leave_days', 0):.1f} дн")
        s3.metric("Перерыв без отпуска", f"{summary.get('avg_vacation_gap_days', 0):.0f} дн")
        s4.metric("Ночная активность", f"{summary.get('avg_night_activity_pct', 0):.1f}%")
        s5.metric("Встречи", f"{summary.get('avg_meeting_load', 0):.1f} ч")

    st.write("")
    chart_col, table_col = st.columns([1.15, 1])

    with chart_col:
        metrics_df = pd.DataFrame(
            [
                {"Metric": "Переработка", "Value": summary.get("avg_overtime_hours", 0), "Unit": "ч"},
                {"Metric": "Больничные", "Value": summary.get("avg_sick_leave_days", 0), "Unit": "дн"},
                {"Metric": "Перерыв без отпуска", "Value": summary.get("avg_vacation_gap_days", 0), "Unit": "дн"},
                {"Metric": "Ночная активность", "Value": summary.get("avg_night_activity_pct", 0), "Unit": "%"},
                {"Metric": "Встречи", "Value": summary.get("avg_meeting_load", 0), "Unit": "ч"},
            ]
        )
        metrics_chart = (
            alt.Chart(metrics_df)
            .mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6)
            .encode(
                x=alt.X("Metric:N", sort=None, title="Метрика"),
                y=alt.Y("Value:Q"),
                tooltip=["Metric", "Value", "Unit"],
                color=alt.value("#00acc1"),
            )
            .properties(height=260, title="Производные метрики команды")
        )
        st.altair_chart(metrics_chart, use_container_width=True)

    with table_col:
        st.subheader("Статус скоринга")
        scoring_status_df = pd.DataFrame(
            [
                {"Signal": "Сотрудники", "Value": selected_team_meta["employee_count"]},
                {"Signal": "Оценено", "Value": team_scores["scored_employees"]},
                {"Signal": "В зоне риска", "Value": team_scores["at_risk_employees"]},
            ]
        )
        st.dataframe(scoring_status_df, hide_index=True, use_container_width=True)

    st.subheader("Состав команды")
    st.text_input(
        "Фильтр по роли",
        key="team_job_role_filter",
        placeholder="Точное совпадение роли, например Education",
    )

    if not team_employees:
        st.info("По текущему фильтру сотрудники не найдены.")
        return

    rows = []
    for employee in team_employees:
        latest_score = cached_scores.get(employee["id"])
        rows.append(
            {
                "ID": employee["id"],
                "Код сотрудника": employee["employee_id"],
                "Роль": employee["job_role"],
                "Стаж": employee["years_at_company"],
                "Статус": score_label(latest_score),
            }
        )

    st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)

    selected_employee = st.selectbox(
        "Открыть профиль сотрудника",
        options=team_employees,
        format_func=lambda emp: f"{emp['employee_id']} | {emp['job_role']}",
    )

    if st.button("Открыть профиль", use_container_width=False):
        st.session_state.selected_employee_id = selected_employee["id"]
        st.session_state.current_page = "Employees"
        st.rerun()


def draw_employee_directory():
    st.title("Каталог сотрудников")
    st.caption("Базовый HR-профиль и сохранённые результаты burnout scoring.")

    teams = get_team_options()
    filter_col1, filter_col2 = st.columns([1, 1])

    with filter_col1:
        current_team = st.selectbox(
            "Фильтр по команде",
            options=teams,
            key="employee_team_filter",
        )

    with filter_col2:
        st.text_input(
            "Фильтр по роли",
            key="employee_job_role_filter",
            placeholder="Точное совпадение роли, например Media",
        )

    employees = list_employees(
        current_team,
        st.session_state.employee_job_role_filter,
        st.session_state.employees_skip,
    )
    score_map = list_employee_scores(
        current_team,
        st.session_state.employee_job_role_filter,
        st.session_state.employees_skip,
    )

    if not employees:
        st.info("По текущим фильтрам сотрудники не найдены.")
        return

    rows = []
    for employee in employees:
        latest_score = score_map.get(employee["id"])
        rows.append(
            {
                "ID": employee["id"],
                "Код сотрудника": employee["employee_id"],
                "Команда": employee["team"],
                "Роль": employee["job_role"],
                "Стаж": employee["years_at_company"],
                "Баланс работа/жизнь": employee["work_life_balance"],
                "Удовлетворённость": employee["job_satisfaction"],
                "Эффективность": employee["performance_rating"],
                "Риск": score_label(latest_score),
            }
        )

    st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)

    selection_col1, selection_col2, selection_col3 = st.columns([1.2, 1, 1])
    with selection_col1:
        selected_employee = st.selectbox(
            "Открыть профиль сотрудника",
            options=employees,
            format_func=lambda emp: f"{emp['employee_id']} | {emp['team']} | {emp['job_role']}",
        )
        if st.button("Открыть профиль", use_container_width=True):
            st.session_state.selected_employee_id = selected_employee["id"]
            st.rerun()

    with selection_col2:
        prev_disabled = st.session_state.employees_skip == 0
        if st.button("Предыдущая страница", use_container_width=True, disabled=prev_disabled):
            st.session_state.employees_skip = max(st.session_state.employees_skip - PAGE_SIZE, 0)
            st.rerun()

    with selection_col3:
        next_disabled = len(employees) < PAGE_SIZE
        if st.button("Следующая страница", use_container_width=True, disabled=next_disabled):
            st.session_state.employees_skip += PAGE_SIZE
            st.rerun()


def draw_forecast_section(employee_id: int):
    st.subheader("Прогноз")
    forecast_horizon = st.selectbox(
        "Горизонт прогноза (дни)",
        options=[7, 14, 30, 60],
        index=0,
        key=f"forecast_horizon_{employee_id}",
    )

    if st.button("Построить прогноз", key=f"forecast_button_{employee_id}"):
        with st.spinner("Строю прогноз..."):
            result = data.generate_forecast(employee_id, forecast_horizon)
        if result:
            st.session_state.forecast_results[(employee_id, forecast_horizon)] = result

    forecast_result = st.session_state.forecast_results.get((employee_id, forecast_horizon))
    if not forecast_result:
        st.info("Прогноз ещё не построен.")
        return

    st.caption(forecast_result["forecast_summary"])
    st.caption(forecast_result["confidence_note"])

    points_df = pd.DataFrame(forecast_result["forecast_points"])
    points_df["risk_level_label"] = points_df["risk_level"].map(
        {
            "low": "Низкий",
            "moderate": "Средний",
            "high": "Высокий",
            "critical": "Критический",
        }
    ).fillna(points_df["risk_level"])

    if PLOTLY_AVAILABLE:
        figure = px.line(
            points_df,
            x="day",
            y="predicted_score",
            markers=True,
            labels={
                "day": "День",
                "predicted_score": "Прогнозируемый риск-скор",
                "risk_level_label": "Уровень риска",
            },
            hover_data={
                "day": True,
                "predicted_score": True,
                "risk_level_label": True,
                "risk_level": False,
            },
        )
        figure.update_traces(
            line={"color": "#ff6b6b", "width": 3},
            marker={"size": 8, "color": "#ff6b6b"},
        )
        figure.update_layout(
            height=320,
            margin={"l": 20, "r": 20, "t": 30, "b": 20},
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis_title="День",
            yaxis_title="Прогнозируемый риск-скор",
            yaxis={"range": [0, 100]},
            hovermode="x unified",
        )
        st.plotly_chart(figure, use_container_width=True)
    else:
        st.warning("Plotly недоступен в текущем окружении. Использую резервный график Altair.")
        fallback_chart = (
            alt.Chart(points_df)
            .mark_line(point=True)
            .encode(
                x=alt.X("day:Q", title="День"),
                y=alt.Y("predicted_score:Q", title="Прогнозируемый риск-скор", scale=alt.Scale(domain=[0, 100])),
                tooltip=["day", "predicted_score", "risk_level_label"],
            )
            .properties(height=280)
        )
        st.altair_chart(fallback_chart, use_container_width=True)


def draw_recommendations_section(employee_id: int):
    st.subheader("Рекомендации")

    if st.button("Сгенерировать рекомендации", key=f"recommendations_button_{employee_id}"):
        with st.spinner("Генерирую рекомендации..."):
            result = data.generate_recommendations(employee_id)
        if result:
            st.session_state.recommendation_results[employee_id] = result

    recommendations = st.session_state.recommendation_results.get(employee_id)
    if not recommendations:
        st.info("Рекомендации ещё не сгенерированы.")
        return

    priority_map = {"low": "Низкий", "medium": "Средний", "high": "Высокий"}
    st.markdown(f"**Приоритет:** {priority_map.get(recommendations['priority'].lower(), recommendations['priority'])}")
    st.markdown(f"**Кратко:** {recommendations['summary']}")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**Действия менеджера**")
        for item in recommendations["manager_actions"]:
            st.write(f"- {item}")
    with col2:
        st.markdown("**Поддержка сотрудника**")
        for item in recommendations["employee_support_actions"]:
            st.write(f"- {item}")
    with col3:
        st.markdown("**На что смотреть**")
        for item in recommendations["watch_items"]:
            st.write(f"- {item}")


def draw_employee_profile():
    employee_id = st.session_state.selected_employee_id
    employee = data.get_employee(employee_id)

    if not employee:
        st.error("Сотрудник не найден.")
        return

    if st.button("Назад в каталог"):
        st.session_state.selected_employee_id = None
        st.rerun()

    st.title(f"Профиль сотрудника: {employee['employee_id']}")
    st.caption(f"{employee['team']} | {employee['job_role']}")

    st.subheader("Профиль")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Лет в компании", employee["years_at_company"])
    c2.metric("Баланс работа/жизнь", employee["work_life_balance"])
    c3.metric("Удовлетворённость", employee["job_satisfaction"])
    c4.metric("Эффективность", employee["performance_rating"])

    c5, c6, c7, c8 = st.columns(4)
    c5.metric("Повышения", employee["number_of_promotions"])
    c6.metric("Флаг переработки", employee["overtime_flag"])
    c7.metric("Признание", employee["employee_recognition"])
    c8.metric("Attrition", employee["attrition"])

    st.divider()
    st.subheader("Текущий риск")

    latest_score = st.session_state.latest_score_overrides.get(employee_id)
    if latest_score is None:
        latest_score = data.get_latest_score(employee_id)

    score_col1, score_col2 = st.columns([1, 2])
    with score_col1:
        if st.button("Запустить текущий скоринг", key=f"score_button_{employee_id}"):
            with st.spinner("Считаю текущий риск выгорания..."):
                result = data.generate_score(employee_id)
            if result:
                st.session_state.latest_score_overrides[employee_id] = result
                remember_scored_employee(employee_id)
                latest_score = result

    with score_col2:
        if latest_score:
            color = score_color(latest_score.get("risk_level"))
            st.markdown(
                f"<span style='color:{color}; font-size:1.4rem; font-weight:700;'>{score_label(latest_score)} / 100</span>",
                unsafe_allow_html=True,
            )
        else:
            st.warning("Скоринг ещё не запускался")

    if latest_score:
        st.markdown(f"**Кратко:** {latest_score['summary']}")
        st.markdown("**Ключевые факторы**")
        for factor in latest_score.get("key_factors", []):
            st.write(f"- {factor}")

    st.divider()
    draw_forecast_section(employee_id)

    st.divider()
    draw_recommendations_section(employee_id)


def draw_employees_page():
    if st.session_state.selected_employee_id is None:
        draw_employee_directory()
    else:
        draw_employee_profile()


def main():
    init_state()
    draw_sidebar()

    if st.session_state.current_page == "Dashboard":
        draw_dashboard()
    elif st.session_state.current_page == "Teams":
        draw_team_page()
    else:
        draw_employees_page()


main()
