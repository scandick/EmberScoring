import os

import requests
import streamlit as st


API_BASE_URL = os.getenv("EMBER_API_BASE_URL", "http://127.0.0.1:8000/api/v1")
REQUEST_TIMEOUT_SECONDS = 30


def _clean_params(**params):
    return {
        key: value
        for key, value in params.items()
        if value not in (None, "", [])
    }


def _handle_api_error(action: str, exc: Exception):
    st.error(f"{action}: {exc}")


@st.cache_data
def _fetch_teams():
    response = requests.get(f"{API_BASE_URL}/teams", timeout=REQUEST_TIMEOUT_SECONDS)
    response.raise_for_status()
    return response.json()


@st.cache_data
def _fetch_employees(skip: int, limit: int, team: str | None, job_role: str | None):
    response = requests.get(
        f"{API_BASE_URL}/employees",
        params=_clean_params(skip=skip, limit=limit, team=team, job_role=job_role),
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    return response.json()


@st.cache_data
def _fetch_employee(employee_id: int):
    response = requests.get(
        f"{API_BASE_URL}/employees/{employee_id}",
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    return response.json()


@st.cache_data
def _fetch_team_employees(team: str, skip: int, limit: int, job_role: str | None):
    response = requests.get(
        f"{API_BASE_URL}/teams/{team}/employees",
        params=_clean_params(skip=skip, limit=limit, job_role=job_role),
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    return response.json()


@st.cache_data
def _fetch_team_summary(team: str):
    response = requests.get(
        f"{API_BASE_URL}/metrics/team/{team}/summary",
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    return response.json()


@st.cache_data
def _fetch_latest_scores(skip: int, limit: int, team: str | None, job_role: str | None):
    response = requests.get(
        f"{API_BASE_URL}/score/latest",
        params=_clean_params(skip=skip, limit=limit, team=team, job_role=job_role),
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    return response.json()


@st.cache_data
def _fetch_latest_employee_score(employee_id: int):
    response = requests.get(
        f"{API_BASE_URL}/score/employee/{employee_id}/latest",
        timeout=REQUEST_TIMEOUT_SECONDS,
    )

    if response.status_code == 404:
        return None

    response.raise_for_status()
    return response.json()


@st.cache_data
def _fetch_score_stats(team: str | None, job_role: str | None):
    response = requests.get(
        f"{API_BASE_URL}/score/stats",
        params=_clean_params(team=team, job_role=job_role),
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    return response.json()


def _clear_score_caches():
    _fetch_latest_scores.clear()
    _fetch_latest_employee_score.clear()
    _fetch_score_stats.clear()


class DataManager:

    @property
    def api_base_url(self) -> str:
        return API_BASE_URL

    def get_teams(self):
        try:
            return _fetch_teams()
        except Exception as exc:
            _handle_api_error("API error while fetching teams", exc)
            return []

    def get_employees(self, *, skip: int = 0, limit: int = 25, team: str | None = None, job_role: str | None = None):
        try:
            return _fetch_employees(skip, limit, team, job_role)
        except Exception as exc:
            _handle_api_error("API error while fetching employees", exc)
            return []

    def get_employee(self, employee_id: int):
        try:
            return _fetch_employee(employee_id)
        except Exception as exc:
            _handle_api_error(f"API error while fetching employee {employee_id}", exc)
            return None

    def get_team_employees(self, team: str, *, skip: int = 0, limit: int = 25, job_role: str | None = None):
        try:
            return _fetch_team_employees(team, skip, limit, job_role)
        except Exception as exc:
            _handle_api_error(f"API error while fetching employees for team {team}", exc)
            return []

    def get_team_summary(self, team: str):
        try:
            return _fetch_team_summary(team)
        except Exception as exc:
            _handle_api_error(f"API error while fetching team summary for {team}", exc)
            return {}

    def get_cached_scores(self, *, skip: int = 0, limit: int = 25, team: str | None = None, job_role: str | None = None):
        try:
            return _fetch_latest_scores(skip, limit, team, job_role)
        except Exception as exc:
            _handle_api_error("API error while fetching latest scores", exc)
            return []

    def get_latest_score(self, employee_id: int):
        try:
            return _fetch_latest_employee_score(employee_id)
        except Exception as exc:
            _handle_api_error(f"API error while fetching latest score for employee {employee_id}", exc)
            return None

    def get_score_stats(self, *, team: str | None = None, job_role: str | None = None):
        try:
            return _fetch_score_stats(team, job_role)
        except Exception as exc:
            _handle_api_error("API error while fetching score statistics", exc)
            return {"scored_employees": 0, "at_risk_employees": 0}

    def generate_score(self, employee_id: int):
        try:
            response = requests.post(
                f"{API_BASE_URL}/score/employee/{employee_id}",
                timeout=REQUEST_TIMEOUT_SECONDS,
            )
            response.raise_for_status()
            _clear_score_caches()
            return response.json()
        except Exception as exc:
            _handle_api_error(f"API error while generating score for employee {employee_id}", exc)
            return None

    def generate_forecast(self, employee_id: int, horizon_days: int = 7):
        try:
            response = requests.post(
                f"{API_BASE_URL}/forecast/employee/{employee_id}",
                params={"horizon_days": horizon_days},
                timeout=REQUEST_TIMEOUT_SECONDS,
            )
            response.raise_for_status()
            return response.json()
        except Exception as exc:
            _handle_api_error(f"API error while generating forecast for employee {employee_id}", exc)
            return None

    def generate_recommendations(self, employee_id: int):
        try:
            response = requests.post(
                f"{API_BASE_URL}/score/employee/{employee_id}/recommendations",
                timeout=REQUEST_TIMEOUT_SECONDS,
            )
            response.raise_for_status()
            return response.json()
        except Exception as exc:
            _handle_api_error(f"API error while generating recommendations for employee {employee_id}", exc)
            return None


data = DataManager()
