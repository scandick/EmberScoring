import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import datetime
from dataManager import data

### INIT DATA START ###

# Expand to full screen
st.set_page_config(page_title="Ops Dashboard", layout="wide")

# --- STATE MANAGEMENT (Routing) ---
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Dashboard"
if 'selected_team' not in st.session_state:
    st.session_state.selected_team = None
if 'selected_employee' not in st.session_state:
    st.session_state.selected_employee = None


def navigate_to(page):
    """Central routing function to change pages and clear sub-selections."""
    st.session_state.current_page = page
    st.session_state.selected_team = None
    st.session_state.selected_employee = None


def clear_team_selection():
    st.session_state.selected_team = None


def clear_employee_selection():
    st.session_state.selected_employee = None


today = datetime.date.today()

team_states = {
    "Engineering": {"status": "Healthy", "color": "#2e7b32"},
    "Marketing": {"status": "Warning", "color": "#f57c00"},
    "Sales": {"status": "⚠ Critical", "color": "#c62828"},
    "Customer Support": {"status": "Healthy", "color": "#2e7b32"}
}

team_events = {
    "Engineering": [
        {"Date": pd.to_datetime(today - datetime.timedelta(days=45)), "Event": "Project 1 Started"},
        {"Date": pd.to_datetime(today - datetime.timedelta(days=15)), "Event": "Major Release Deployed"}
    ],
    "Marketing": [
        {"Date": pd.to_datetime(today - datetime.timedelta(days=30)), "Event": "Rebranding Campaign Launched"}
    ],
    "Sales": [
        {"Date": pd.to_datetime(today - datetime.timedelta(days=60)), "Event": "Q1 Quota Reset"}
    ],
    "Customer Support": []
}


# --- DATA GENERATION (CACHED) ---
@st.cache_data
def load_company_data():
    start_date = today - datetime.timedelta(days=365 * 4)
    dates = pd.date_range(start=start_date, end=today)

    data_dict = {'Date': dates}
    seasonality = 8 * np.sin(2 * np.pi * dates.dayofyear / 365.25)

    for team in team_states.keys():
        base_score = 75
        noise = np.random.normal(loc=0, scale=10, size=len(dates))
        scores = base_score + seasonality + noise
        data_dict[team] = np.clip(scores, 0, 100)

    return pd.DataFrame(data_dict)


@st.cache_data
def build_employee_dataframe():
    """Builds the DataFrame from the API data manager and fetches scores."""
    employees = data.employees
    emp_list = []

    for emp_id, emp_data in employees.items():
        # Fetch the score for this specific employee
        score_data = data.get_score(emp_id)

        emp_list.append({
            "id": emp_id,
            "Name": emp_data.get("employee_id", f"EMP-{emp_id}"),  # API uses employee_id instead of Name
            "Team": emp_data.get("team", "Unknown"),
            "Job Role": emp_data.get("job_role", "N/A"),
            "Years at Company": emp_data.get("years_at_company", 0),
            "Work Life Balance": emp_data.get("work_life_balance", "N/A"),
            "Job Satisfaction": emp_data.get("job_satisfaction", "N/A"),
            "Performance Rating": emp_data.get("performance_rating", "N/A"),
            "Overtime": emp_data.get("overtime_flag", "N/A"),

            # Map score endpoint results
            "Current Ember": score_data.get("risk_score", 0),
            "Status": score_data.get("risk_level", "Unknown").title(),
            "Key Factors": score_data.get("key_factors", []),
            "Summary": score_data.get("summary", "No summary available.")
        })

    return pd.DataFrame(emp_list)


df = load_company_data()
emp_df = build_employee_dataframe()
min_available_date = df['Date'].min().date()


### INIT DATA END ###

### DRAW SEPARATE PAGES START ###

# --- DASHBOARD PAGE ---
def draw_dashboard_page():
    st.title("Company Overview 🌍")
    st.write("Critical metrics and cross-team alerts at a glance.")
    st.divider()

    # Calculate company-wide averages for the last 30 days
    recent_df = df[df['Date'].dt.date >= (today - datetime.timedelta(days=30))]
    company_avg = recent_df[list(team_states.keys())].mean().mean()

    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("Company-Wide Ember (30d)", f"{company_avg:.1f}")
    kpi2.metric("Total Employees", len(emp_df))
    kpi3.metric("Employees At Risk", len(emp_df[emp_df['Status'].isin(['High', 'Critical'])]))

    st.write("---")
    st.subheader("Critical Alerts")

    alert_c1, alert_c2 = st.columns(2)
    with alert_c1:
        st.error("**Sales Team** is marked as ⚠ Critical. Ember scores trending downwards.")
    with alert_c2:
        st.warning("**Marketing Team** ad spend approaching limit.")

    st.write("---")
    st.subheader("Recent Team Events")

    # Flatten and sort events
    all_events = []
    for team, events in team_events.items():
        for e in events:
            all_events.append({"Team": team, "Date": e["Date"], "Event": e["Event"]})

    events_df = pd.DataFrame(all_events).sort_values("Date", ascending=False).head(5)
    st.dataframe(events_df, hide_index=True, use_container_width=True)


# --- TEAM OVERVIEW ---
def draw_team_overview():
    st.title("Teams Overview 🏢")
    st.caption("Review 30-day summaries and click 'View' for detailed insights.")

    thirty_days_ago = today - datetime.timedelta(days=30)
    recent_df = df[df['Date'].dt.date >= thirty_days_ago]

    h1, h2, h3, h4, h5 = st.columns([2, 1.5, 3, 1.5, 1.5])
    h1.write("**Team**")
    h2.write("**Avg Score**")
    h3.write("**Trend (30d)**")
    h4.write("**At Risk**")
    h5.write("**Action**")

    st.divider()

    for team, state in team_states.items():
        team_data = recent_df[['Date', team]].rename(columns={team: 'Ember'})
        avg_score = team_data['Ember'].mean()

        # Calculate real at_risk from the API dataframe
        at_risk = len(emp_df[(emp_df['Team'] == team) & (emp_df['Status'].isin(['High', 'Critical']))])

        c1, c2, c3, c4, c5 = st.columns([2, 1.5, 3, 1.5, 1.5], vertical_alignment="center")

        c1.markdown(
            f"<span style='font-size:1.1rem; font-weight:600;'>{team}</span><br>"
            f"<span style='color:{state['color']}; font-size:0.9rem;'>{state['status']}</span>",
            unsafe_allow_html=True
        )

        c2.write(f"{avg_score:.1f} / 100")

        sparkline = alt.Chart(team_data).mark_line(
            color=state['color'], strokeWidth=2
        ).encode(
            x=alt.X('Date:T', axis=None),
            y=alt.Y('Ember:Q', axis=None, scale=alt.Scale(domain=[0, 100]))
        ).properties(height=40)

        with c3:
            st.altair_chart(sparkline, use_container_width=True)

        c4.write(f"{at_risk} emp.")

        with c5:
            if st.button("View ➡️", key=f"btn_{team}", use_container_width=True):
                st.session_state.selected_team = team
                st.rerun()
    st.write("---")


# --- DETAILED TEAM PAGE ---
def draw_main_team_page():
    team_name = st.session_state.selected_team
    status_color = team_states[team_name]["color"]

    st.button("⬅️ Back to Teams Directory", on_click=clear_team_selection)

    head_col1, head_col2 = st.columns([3, 1])
    with head_col1:
        st.markdown(f"<h1 style='color: {status_color}; margin-bottom: 0;'>📊 {team_name} Metrics</h1>",
                    unsafe_allow_html=True)
    with head_col2:
        st.write("")
        compare_history = st.toggle("Compare vs 3-Yr Avg", value=True)

    st.divider()

    control_col1, control_col2 = st.columns([1, 2])
    with control_col1:
        timeframe = st.date_input(
            "Select Timeframe (Start - End)",
            value=(today - datetime.timedelta(days=30), today),
            min_value=min_available_date,
            max_value=today
        )

    if len(timeframe) != 2:
        st.warning("Please select an end date on the calendar.")
        st.stop()

    current_start, current_end = timeframe
    period_length = (current_end - current_start).days

    current_mask = (df['Date'].dt.date >= current_start) & (df['Date'].dt.date <= current_end)
    current_df = df[current_mask][['Date', team_name]].rename(columns={team_name: 'Ember'})

    hist_dfs = []
    for i in range(1, 4):
        h_start = pd.to_datetime(current_start) - pd.DateOffset(years=i)
        h_end = pd.to_datetime(current_end) - pd.DateOffset(years=i)

        h_mask = (df['Date'] >= h_start) & (df['Date'] <= h_end)
        temp_df = df[h_mask][['Date', team_name]].rename(columns={team_name: 'Ember'}).copy()

        if not temp_df.empty:
            temp_df['Overlay_Date'] = temp_df['Date'] + pd.DateOffset(years=i)
            hist_dfs.append(temp_df)

    if hist_dfs:
        combined_hist = pd.concat(hist_dfs)
        hist_avg_df = combined_hist.groupby('Overlay_Date')['Ember'].mean().reset_index()
    else:
        hist_avg_df = pd.DataFrame(columns=['Overlay_Date', 'Ember'])

    current_avg = current_df['Ember'].mean() if not current_df.empty else 0
    hist_avg = hist_avg_df['Ember'].mean() if not hist_avg_df.empty else 0

    avg_delta = f"{current_avg - hist_avg:.1f} vs 3-yr avg" if (compare_history and not hist_avg_df.empty) else None

    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("Avg Ember Score", f"{current_avg:.1f}", delta=avg_delta)
    kpi2.metric("Days in Period", period_length + 1)
    kpi3.metric("Highest Daily Score", f"{current_df['Ember'].max():.1f}")

    # --- NEW: FASTAPI TEAM METRICS ---
    st.write("---")
    st.write("### ⚙️ Operational Workload & Health")

    with st.spinner("Loading operational metrics..."):
        team_summary = data.get_team_summary(team_name)

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric(
        "Overtime",
        f"{team_summary.get('avg_overtime_hours', 0):.1f} hrs",
        help="Average weekly overtime hours per employee"
    )
    m2.metric(
        "Sick Leave",
        f"{team_summary.get('avg_sick_leave_days', 0):.1f} days",
        help="Average sick leave taken in the period"
    )
    m3.metric(
        "Vacation Gap",
        f"{team_summary.get('avg_vacation_gap_days', 0):.0f} days",
        help="Average days since an employee's last taken vacation"
    )
    m4.metric(
        "Night Activity",
        f"{team_summary.get('avg_night_activity_pct', 0):.1f}%",
        help="Percentage of communications/activity outside standard working hours"
    )
    m5.metric(
        "Meeting Load",
        f"{team_summary.get('avg_meeting_load', 0):.1f} hrs",
        help="Average weekly hours spent in internal meetings"
    )

    st.write("")
    # ---------------------------------

    domain_start = current_start.strftime('%Y-%m-%d')
    domain_end = current_end.strftime('%Y-%m-%d')

    raw_line = alt.Chart(current_df).mark_line(
        color=status_color, strokeWidth=1.5, opacity=0.3, clip=True
    ).encode(
        x=alt.X('Date:T', title='', scale=alt.Scale(domain=[domain_start, domain_end])),
        y=alt.Y('Ember:Q', title='Ember Score', scale=alt.Scale(domain=[0, 100]))
    )

    trend_line = raw_line.transform_loess('Date', 'Ember', bandwidth=0.3).mark_line(color=status_color, strokeWidth=4,
                                                                                    clip=True)
    final_chart = raw_line + trend_line

    if compare_history and not hist_avg_df.empty:
        hist_overlay = alt.Chart(hist_avg_df).transform_loess(
            'Overlay_Date', 'Ember', bandwidth=0.3
        ).mark_line(
            color='gray', strokeWidth=2, strokeDash=[5, 5], opacity=0.6, clip=True
        ).encode(x='Overlay_Date:T', y='Ember:Q')
        final_chart += hist_overlay

    events_df = pd.DataFrame(team_events[team_name])
    if not events_df.empty:
        mask = (events_df['Date'].dt.date >= current_start) & (events_df['Date'].dt.date <= current_end)
        filtered_events = events_df[mask]

        if not filtered_events.empty:
            event_lines = alt.Chart(filtered_events).mark_rule(
                color='gray', strokeDash=[2, 2], strokeWidth=2, clip=True
            ).encode(x='Date:T')

            event_labels = alt.Chart(filtered_events).mark_text(
                align='left', dx=5, color='white', fontWeight='bold', fontSize=12, clip=True
            ).encode(x='Date:T', text='Event:N', y=alt.value(20))
            final_chart += event_lines + event_labels

    st.altair_chart(final_chart.interactive(bind_y=False).properties(height=400), use_container_width=True)

    if compare_history:
        st.caption("Solid line: Current Period | Dashed gray line: 3-Year Historical Average")

    st.divider()
    st.write("### Diagnostic Insights")

    current_df['Day_Name'] = current_df['Date'].dt.day_name()
    insight_col1, insight_col2 = st.columns(2)

    with insight_col1:
        st.write("##### Time Spent in Zones")
        bins = [0, 60, 80, 100]
        labels = ['Struggling (<60)', 'Stable (60-80)', 'Thriving (>80)']
        current_df['Zone'] = pd.cut(current_df['Ember'], bins=bins, labels=labels, include_lowest=True)
        donut_data = current_df['Zone'].value_counts().reset_index()
        donut_data.columns = ['Zone', 'Days']

        zone_colors = alt.Scale(
            domain=['Struggling (<60)', 'Stable (60-80)', 'Thriving (>80)'],
            range=['#c62828', '#f57c00', '#2e7b32']
        )

        donut_chart = alt.Chart(donut_data).mark_arc(innerRadius=65, stroke="#fff").encode(
            theta=alt.Theta('Days:Q'),
            color=alt.Color('Zone:N', scale=zone_colors, legend=alt.Legend(title="Health Zones", orient="bottom")),
            tooltip=['Zone', 'Days']
        ).properties(height=300)

        st.altair_chart(donut_chart, use_container_width=True)

    with insight_col2:
        st.write("##### Mood Consistency (Distribution)")
        histogram = alt.Chart(current_df).mark_bar(color=status_color, opacity=0.8).encode(
            x=alt.X('Ember:Q', bin=alt.Bin(maxbins=20), title='Ember Score Bucket'),
            y=alt.Y('count()', title='Number of Days')
        ).properties(height=300)

        avg_line = alt.Chart(pd.DataFrame({'mean': [current_avg]})).mark_rule(
            color='red', strokeDash=[5, 5], strokeWidth=2
        ).encode(x='mean:Q')

        st.altair_chart(histogram + avg_line, use_container_width=True)

    # --- TEAM MEMBERS SECTION ---
    st.divider()
    st.write("### Team Members")

    team_emps = emp_df[emp_df['Team'] == team_name]

    if team_emps.empty:
        st.info("No employees assigned to this team yet.")
    else:
        h1, h2, h3 = st.columns([3, 2, 2])
        h1.write("**Employee Name**")
        h2.write("**Status / Score**")
        h3.write("**Action**")
        st.write("---")

        for idx, row in team_emps.iterrows():
            c1, c2, c3 = st.columns([3, 2, 2], vertical_alignment="center")

            c1.write(f"**{row['Name']}**")

            # Updated Color Logic (High Score = High Risk = Red)
            score_color = "red" if row['Status'] in ["High", "Critical"] else (
                "orange" if row['Status'] == "Moderate" else "green")

            c2.markdown(
                f"{row['Status']} &nbsp;|&nbsp; <span style='color:{score_color}; font-weight:bold;'>{row['Current Ember']}</span>",
                unsafe_allow_html=True)

            with c3:
                if st.button("View Profile ➡️", key=f"team_emp_btn_{idx}", use_container_width=True):
                    st.session_state.current_page = "Employees"
                    st.session_state.selected_employee = row['Name']
                    st.rerun()


# --- EMPLOYEES OVERVIEW PAGE ---
def draw_employees_overview():
    st.title("Employees Directory 🧑‍💻")
    st.caption("View current status and Burnout Risk scores for all employees.")

    filter_col, _ = st.columns([1, 2])
    with filter_col:
        team_filter = st.selectbox("Filter by Team", ["All Teams"] + list(team_states.keys()))

    display_df = emp_df if team_filter == "All Teams" else emp_df[emp_df['Team'] == team_filter]

    h1, h2, h3, h4 = st.columns([2, 2, 2, 1.5])
    h1.write("**Employee ID**")
    h2.write("**Team**")
    h3.write("**Risk Level / Score**")
    h4.write("**Action**")
    st.divider()

    for idx, row in display_df.iterrows():
        c1, c2, c3, c4 = st.columns([2, 2, 2, 1.5], vertical_alignment="center")

        c1.write(f"**{row['Name']}**")
        c2.write(row['Team'])

        # Updated Color Logic (High Score = High Risk = Red)
        score_color = "red" if row['Status'] in ["High", "Critical"] else (
            "orange" if row['Status'] == "Moderate" else "green")

        c3.markdown(
            f"{row['Status']} &nbsp;|&nbsp; <span style='color:{score_color}; font-weight:bold;'>{row['Current Ember']}</span>",
            unsafe_allow_html=True)

        with c4:
            if st.button("Profile ➡️", key=f"emp_btn_{idx}", use_container_width=True):
                st.session_state.selected_employee = row['Name']
                st.rerun()
    st.write("---")


# --- EMPLOYEE VIEW PAGE ---
def draw_employee_view():
    emp_name = st.session_state.selected_employee
    emp_details = emp_df[emp_df['Name'] == emp_name].iloc[0]

    st.button("⬅️ Back to Employees Directory", on_click=clear_employee_selection)

    st.title(f"🧑‍💻 {emp_name}")
    st.write(f"**Team:** {emp_details['Team']}  |  **Current Status:** {emp_details['Status']}")
    st.divider()

    st.write("### Employee Profile")

    # Replaced mock charts with actual static API Data Metrics
    row1_cols = st.columns(3)
    row1_cols[0].metric("Job Role", str(emp_details['Job Role']))
    row1_cols[1].metric("Years at Company", str(emp_details['Years at Company']))
    row1_cols[2].metric("Performance Rating", str(emp_details['Performance Rating']))

    st.write("")

    row2_cols = st.columns(3)
    row2_cols[0].metric("Work/Life Balance", str(emp_details['Work Life Balance']))
    row2_cols[1].metric("Job Satisfaction", str(emp_details['Job Satisfaction']))
    row2_cols[2].metric("Overtime", str(emp_details['Overtime']))

    st.divider()

    st.write("### Burnout Risk Assessment")

    # Large formatted risk score
    score_color = "red" if emp_details['Status'] in ["High", "Critical"] else (
        "orange" if emp_details['Status'] == "Moderate" else "green")
    st.markdown(
        f"**Risk Score:** <span style='color:{score_color}; font-size:1.5rem; font-weight:bold;'>{emp_details['Current Ember']} / 100</span>",
        unsafe_allow_html=True)

    st.info("AI Assessment Summary:")
    st.write(emp_details['Summary'])

    # Display key factors if available
    if isinstance(emp_details['Key Factors'], list) and len(emp_details['Key Factors']) > 0:
        st.write("**Key Contributing Factors:**")
        for factor in emp_details['Key Factors']:
            st.write(f"- {factor}")


### DRAW PAGES END ###

### MAIN DRAW ###

# --- SIDEBAR ---
with st.sidebar:
    st.title("Navigation")

    st.button("📊 Dashboard", use_container_width=True,
              type="primary" if st.session_state.current_page == "Dashboard" else "secondary",
              on_click=navigate_to, args=("Dashboard",))

    st.button("🏢 Teams", use_container_width=True,
              type="primary" if st.session_state.current_page == "Teams" else "secondary",
              on_click=navigate_to, args=("Teams",))

    st.button("🧑‍💻 Employees", use_container_width=True,
              type="primary" if st.session_state.current_page == "Employees" else "secondary",
              on_click=navigate_to, args=("Employees",))

    st.divider()
    st.caption(f"Data synced through: {today.strftime('%b %d, %Y')}")

# --- PAGE ROUTER ---
if st.session_state.current_page == "Dashboard":
    draw_dashboard_page()

elif st.session_state.current_page == "Teams":
    if st.session_state.selected_team is None:
        draw_team_overview()
    else:
        draw_main_team_page()

elif st.session_state.current_page == "Employees":
    if st.session_state.selected_employee is None:
        draw_employees_overview()
    else:
        draw_employee_view()

### MAIN DRAW END ###