import streamlit as st
import requests

API_BASE_URL = "http://127.0.0.1:8000/api/v1"

@st.cache_data
def _fetch_all_employees():
    """GET request to fetch the directory."""
    try:
        response = requests.get(f"{API_BASE_URL}/employees")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"API Error fetching employees: {e}")
        return []


@st.cache_data
def _generate_score(employee_id: int):
    """POST request to generate burnout score. Only runs if not cached."""
    try:
        response = requests.post(f"{API_BASE_URL}/score/employee/{employee_id}")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"API Error generating score for ID {employee_id}: {e}")
        return {}


@st.cache_data
def _generate_forecast(employee_id: int, horizon_days: int = 30):
    """POST request to generate forecast trend."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/forecast/employee/{employee_id}",
            params={"horizon_days": horizon_days}
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"API Error generating forecast for ID {employee_id}: {e}")
        return {}

@st.cache_data
def _generate_recommendations(employee_id: int):
    """POST request to generate burnout score. Only runs if not cached."""
    try:
        response = requests.post(f"{API_BASE_URL}/score/employee/{employee_id}/recommendations")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"API Error generating recommendations for ID {employee_id}: {e}")
        return {}

@st.cache_data
def _fetch_team_metrics(team_name: str):
    """GET request for aggregate team data."""
    try:
        response = requests.get(f"{API_BASE_URL}/metrics/team/{team_name}/summary")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"API Error fetching metrics for {team_name}: {e}")
        return {}


# --- PUBLIC DATA MANAGER ---
class DataManager:
    """
    A simple interface to access your API data using dictionary syntax.
    """

    @property
    def employees(self):
        """
        Returns a dictionary of employees keyed by their integer ID.
        Allows for: data.employees[5]["job_role"]
        """
        raw_list = _fetch_all_employees()
        # Convert the list of dicts into a dictionary mapped by 'id'
        return {emp["id"]: emp for emp in raw_list}

    def get_score(self, employee_id: int):
        return _generate_score(employee_id)

    def get_recommendations(self, employee_id: int):
        return _generate_recommendations(employee_id)

    def get_forecast(self, employee_id: int, horizon_days: int = 30):
        return _generate_forecast(employee_id, horizon_days)

    def get_team_summary(self, team_name: str):
        return _fetch_team_metrics(team_name)


# Instantiate a global instance to be imported by your main app
data = DataManager()