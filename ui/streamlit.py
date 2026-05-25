import altair as alt
import pandas as pd
import streamlit as st

from dataManager import data


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
        return "Not scored"
    return f"{score['risk_level'].title()} | {int(score['risk_score'])}"


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
            "Dashboard",
            use_container_width=True,
            type="primary" if st.session_state.current_page == "Dashboard" else "secondary",
            on_click=navigate_to,
            args=("Dashboard",),
        )
        st.button(
            "Teams",
            use_container_width=True,
            type="primary" if st.session_state.current_page == "Teams" else "secondary",
            on_click=navigate_to,
            args=("Teams",),
        )
        st.button(
            "Employees",
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
            st.caption("Current AI Focus")

            employee_label = (
                f"{employee['employee_id']} | {employee['team']}"
                if employee
                else f"Employee #{selected_employee_id}"
            )
            st.write(f"**{employee_label}**")

            if latest_score:
                color = score_color(latest_score.get("risk_level"))
                st.markdown(
                    f"<span style='color:{color}; font-weight:600;'>{latest_score['risk_level'].title()} | {int(latest_score['risk_score'])}</span>",
                    unsafe_allow_html=True,
                )
            else:
                st.caption("Not scored")

            st.button(
                f"Employee Profile: {employee['employee_id'] if employee else selected_employee_id}",
                use_container_width=True,
                type="primary" if st.session_state.current_page == "Employees" else "secondary",
                on_click=navigate_to,
                args=("Employees",),
            )

        recent_ids = st.session_state.recent_scored_employee_ids
        if recent_ids:
            st.divider()
            st.caption("Recent Scoring History")

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
                        f"<span style='color:{color}; font-size:0.9rem;'>{latest_score['risk_level'].title()} | {int(latest_score['risk_score'])}</span>",
                        unsafe_allow_html=True,
                    )
                else:
                    st.caption("Score unavailable")


def draw_dashboard():
    teams = get_teams()
    stats = data.get_score_stats()

    total_employees = sum(item["employee_count"] for item in teams)
    total_teams = len(teams)

    st.title("Company Dashboard")
    st.caption("API-driven overview of employees, teams, and cached AI scoring results.")

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Employees", total_employees)
    k2.metric("Teams", total_teams)
    k3.metric("Scored Employees", stats["scored_employees"])
    k4.metric("Employees At Risk", stats["at_risk_employees"])

    st.write("")

    teams_df = pd.DataFrame(teams)
    if teams_df.empty:
        st.info("No team data available.")
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
        st.subheader("Teams")
        st.dataframe(
            teams_df.rename(columns={"team": "Team", "employee_count": "Employees"}),
            hide_index=True,
            use_container_width=True,
        )


def draw_team_page():
    teams = get_teams()
    if not teams:
        st.info("No teams available.")
        return

    team_names = [item["team"] for item in teams]
    default_team = st.session_state.selected_team or team_names[0]
    selected_team = st.selectbox(
        "Team",
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

    st.title(f"Team Overview: {selected_team}")
    st.caption("Derived workload indicators plus current team roster.")

    k1, k2, k3 = st.columns(3)
    k1.metric("Employees", selected_team_meta["employee_count"])
    k2.metric("Scored Employees", team_scores["scored_employees"])
    k3.metric("Employees At Risk", team_scores["at_risk_employees"])

    if summary:
        s1, s2, s3, s4, s5 = st.columns(5)
        s1.metric("Avg Overtime", f"{summary.get('avg_overtime_hours', 0):.1f} hrs")
        s2.metric("Avg Sick Leave", f"{summary.get('avg_sick_leave_days', 0):.1f} days")
        s3.metric("Avg Vacation Gap", f"{summary.get('avg_vacation_gap_days', 0):.0f} days")
        s4.metric("Avg Night Activity", f"{summary.get('avg_night_activity_pct', 0):.1f}%")
        s5.metric("Avg Meeting Load", f"{summary.get('avg_meeting_load', 0):.1f} hrs")

    st.write("")
    st.subheader("Team Members")
    st.text_input(
        "Filter by job role",
        key="team_job_role_filter",
        placeholder="Exact job role match, e.g. Education",
    )

    if not team_employees:
        st.info("No employees matched this team filter.")
        return

    rows = []
    for employee in team_employees:
        latest_score = cached_scores.get(employee["id"])
        rows.append(
            {
                "ID": employee["id"],
                "Employee ID": employee["employee_id"],
                "Job Role": employee["job_role"],
                "Years": employee["years_at_company"],
                "Status": score_label(latest_score),
            }
        )

    st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)

    selected_employee = st.selectbox(
        "Open employee profile",
        options=team_employees,
        format_func=lambda emp: f"{emp['employee_id']} | {emp['job_role']}",
    )

    if st.button("Open Profile", use_container_width=False):
        st.session_state.selected_employee_id = selected_employee["id"]
        st.session_state.current_page = "Employees"
        st.rerun()


def draw_employee_directory():
    st.title("Employees Directory")
    st.caption("Raw HR profile data plus saved burnout scoring results.")

    teams = get_team_options()
    filter_col1, filter_col2 = st.columns([1, 1])

    with filter_col1:
        current_team = st.selectbox(
            "Filter by team",
            options=teams,
            key="employee_team_filter",
        )

    with filter_col2:
        st.text_input(
            "Filter by job role",
            key="employee_job_role_filter",
            placeholder="Exact job role match, e.g. Media",
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
        st.info("No employees matched the current filters.")
        return

    rows = []
    for employee in employees:
        latest_score = score_map.get(employee["id"])
        rows.append(
            {
                "ID": employee["id"],
                "Employee ID": employee["employee_id"],
                "Team": employee["team"],
                "Job Role": employee["job_role"],
                "Years": employee["years_at_company"],
                "Work-Life Balance": employee["work_life_balance"],
                "Job Satisfaction": employee["job_satisfaction"],
                "Performance": employee["performance_rating"],
                "Risk": score_label(latest_score),
            }
        )

    st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)

    selection_col1, selection_col2, selection_col3 = st.columns([1.2, 1, 1])
    with selection_col1:
        selected_employee = st.selectbox(
            "Open employee profile",
            options=employees,
            format_func=lambda emp: f"{emp['employee_id']} | {emp['team']} | {emp['job_role']}",
        )
        if st.button("Open Profile", use_container_width=True):
            st.session_state.selected_employee_id = selected_employee["id"]
            st.rerun()

    with selection_col2:
        prev_disabled = st.session_state.employees_skip == 0
        if st.button("Previous Page", use_container_width=True, disabled=prev_disabled):
            st.session_state.employees_skip = max(st.session_state.employees_skip - PAGE_SIZE, 0)
            st.rerun()

    with selection_col3:
        next_disabled = len(employees) < PAGE_SIZE
        if st.button("Next Page", use_container_width=True, disabled=next_disabled):
            st.session_state.employees_skip += PAGE_SIZE
            st.rerun()


def draw_forecast_section(employee_id: int):
    st.subheader("Forecast")
    forecast_horizon = st.selectbox(
        "Forecast horizon (days)",
        options=[7, 14, 30, 60],
        index=0,
        key=f"forecast_horizon_{employee_id}",
    )

    if st.button("Generate Forecast", key=f"forecast_button_{employee_id}"):
        with st.spinner("Generating forecast..."):
            result = data.generate_forecast(employee_id, forecast_horizon)
        if result:
            st.session_state.forecast_results[(employee_id, forecast_horizon)] = result

    forecast_result = st.session_state.forecast_results.get((employee_id, forecast_horizon))
    if not forecast_result:
        st.info("No forecast generated yet.")
        return

    st.caption(forecast_result["forecast_summary"])
    st.caption(forecast_result["confidence_note"])

    points_df = pd.DataFrame(forecast_result["forecast_points"])
    chart = (
        alt.Chart(points_df)
        .mark_line(point=True)
        .encode(
            x=alt.X("day:Q", title="Day"),
            y=alt.Y("predicted_score:Q", title="Predicted Risk Score", scale=alt.Scale(domain=[0, 100])),
            tooltip=["day", "predicted_score", "risk_level"],
        )
        .properties(height=280)
    )
    st.altair_chart(chart, use_container_width=True)


def draw_recommendations_section(employee_id: int):
    st.subheader("Recommendations")

    if st.button("Generate Recommendations", key=f"recommendations_button_{employee_id}"):
        with st.spinner("Generating recommendations..."):
            result = data.generate_recommendations(employee_id)
        if result:
            st.session_state.recommendation_results[employee_id] = result

    recommendations = st.session_state.recommendation_results.get(employee_id)
    if not recommendations:
        st.info("No recommendations generated yet.")
        return

    st.markdown(f"**Priority:** {recommendations['priority'].title()}")
    st.markdown(f"**Summary:** {recommendations['summary']}")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**Manager Actions**")
        for item in recommendations["manager_actions"]:
            st.write(f"- {item}")
    with col2:
        st.markdown("**Employee Support**")
        for item in recommendations["employee_support_actions"]:
            st.write(f"- {item}")
    with col3:
        st.markdown("**Watch Items**")
        for item in recommendations["watch_items"]:
            st.write(f"- {item}")


def draw_employee_profile():
    employee_id = st.session_state.selected_employee_id
    employee = data.get_employee(employee_id)

    if not employee:
        st.error("Employee not found.")
        return

    if st.button("Back to Directory"):
        st.session_state.selected_employee_id = None
        st.rerun()

    st.title(f"Employee Profile: {employee['employee_id']}")
    st.caption(f"{employee['team']} | {employee['job_role']}")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Years at Company", employee["years_at_company"])
    c2.metric("Work-Life Balance", employee["work_life_balance"])
    c3.metric("Job Satisfaction", employee["job_satisfaction"])
    c4.metric("Performance Rating", employee["performance_rating"])

    c5, c6, c7, c8 = st.columns(4)
    c5.metric("Promotions", employee["number_of_promotions"])
    c6.metric("Overtime Flag", employee["overtime_flag"])
    c7.metric("Recognition", employee["employee_recognition"])
    c8.metric("Attrition", employee["attrition"])

    st.divider()
    st.subheader("Current Risk")

    latest_score = st.session_state.latest_score_overrides.get(employee_id)
    if latest_score is None:
        latest_score = data.get_latest_score(employee_id)

    score_col1, score_col2 = st.columns([1, 2])
    with score_col1:
        if st.button("Run Current Score", key=f"score_button_{employee_id}"):
            with st.spinner("Generating current burnout score..."):
                result = data.generate_score(employee_id)
            if result:
                st.session_state.latest_score_overrides[employee_id] = result
                remember_scored_employee(employee_id)
                latest_score = result

    with score_col2:
        if latest_score:
            color = score_color(latest_score.get("risk_level"))
            st.markdown(
                f"<span style='color:{color}; font-size:1.4rem; font-weight:700;'>{latest_score['risk_level'].title()} | {int(latest_score['risk_score'])} / 100</span>",
                unsafe_allow_html=True,
            )
        else:
            st.warning("Not scored")

    if latest_score:
        st.markdown(f"**Summary:** {latest_score['summary']}")
        st.markdown("**Key Factors**")
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
