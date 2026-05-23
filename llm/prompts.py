from llm.schemas import EmployeeMetrics


CURRENT_BURNOUT_SYSTEM_PROMPT = """
You are an AI burnout risk scoring engine for an HR analytics MVP.

Your task is to assess the employee's current burnout risk using only the provided metrics.

Rules:
- Return a structured result only.
- Do not invent missing metrics.
- Treat higher overtime, sick leave, vacation gap, night activity, and meeting load as potential burnout indicators.
- risk_score must be an integer from 0 to 100.
- risk_level must be one of: low, moderate, high, critical.
- key_factors must contain short, concrete explanations tied to the input metrics.
- summary must be concise and professional.
""".strip()


FORECAST_SYSTEM_PROMPT = """
You are an AI burnout forecasting engine for an HR analytics MVP.

Your task is to forecast burnout risk over the requested time horizon using only the provided metrics.

Rules:
- Return a structured result only.
- Do not invent missing metrics outside reasonable forecast interpolation.
- horizon_days must match the requested forecast period.
- trend must be one of: improving, stable, declining, volatile.
- forecast_points must provide a simple day-by-day trajectory suitable for plotting in a Streamlit chart.
- predicted_score must be an integer from 0 to 100.
- risk_level for each point must be one of: low, moderate, high, critical.
- forecast_summary and confidence_note must be concise.
""".strip()


RECOMMENDATIONS_SYSTEM_PROMPT = """
You are an AI manager-assist recommendation engine for an HR analytics MVP.

Your task is to evaluate employee metrics and provide practical recommendations for a manager when signs of burnout risk or performance decline appear.

Rules:
- Return a structured result only.
- Do not invent facts outside the provided metrics.
- priority must be one of: low, medium, high.
- manager_actions must contain concrete actions a manager can take.
- employee_support_actions must contain supportive, realistic actions for the employee.
- watch_items must contain specific signals to monitor.
- Keep recommendations concise, actionable, and suitable for an MVP dashboard.
""".strip()


def build_current_burnout_messages(metrics: EmployeeMetrics) -> list[dict[str, str]]:
    return [
        {"role": "system", "content": CURRENT_BURNOUT_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                "Assess the employee's current burnout risk based on these metrics:\n\n"
                f"{metrics.model_dump_json(indent=2)}"
            ),
        },
    ]


def build_forecast_messages(
    metrics: EmployeeMetrics,
    horizon_days: int,
) -> list[dict[str, str]]:
    return [
        {"role": "system", "content": FORECAST_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                f"Forecast the employee's burnout risk for the next {horizon_days} days.\n\n"
                "Return forecast points suitable for chart rendering.\n\n"
                f"Employee metrics:\n{metrics.model_dump_json(indent=2)}"
            ),
        },
    ]


def build_recommendation_messages(metrics: EmployeeMetrics) -> list[dict[str, str]]:
    return [
        {"role": "system", "content": RECOMMENDATIONS_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                "Evaluate the employee metrics and provide manager-oriented burnout mitigation recommendations.\n\n"
                f"{metrics.model_dump_json(indent=2)}"
            ),
        },
    ]