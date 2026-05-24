# Streamlit Integration Guide

Этот документ описывает, как Streamlit-фронтенду работать с текущим FastAPI API для MVP `Ember`.

## Визуальный ориентир

Ниже mockup рекомендуемой структуры экранов.

![Ember Streamlit Mockup](C:/Users/andre/.codex/generated_images/019e4fe9-5c76-74b2-85e3-ad0fafafa197/ig_0cab4280b66826bf016a12f5ab2aec8191ad36869191618002.png)

## Главный принцип

Не строить UI вокруг списка endpoint'ов из Swagger.  
Нужно строить UI вокруг пользовательских сценариев:

- просмотр списка сотрудников;
- просмотр профиля сотрудника;
- просмотр команды;
- запуск AI scoring;
- просмотр AI forecast;
- просмотр AI recommendations.

## Что считается источником данных

### Raw employee profile

Источник:

- `GET /api/v1/employees`
- `GET /api/v1/employees/{id}`
- `GET /api/v1/teams/{team}/employees`

Это базовые HR-данные сотрудника:

- `employee_id`
- `team`
- `job_role`
- `years_at_company`
- `work_life_balance`
- `job_satisfaction`
- `performance_rating`
- `number_of_promotions`
- `overtime_flag`
- `employee_recognition`
- `leadership_opportunities`
- `innovation_opportunities`
- `attrition`

### Derived team metrics

Источник:

- `GET /api/v1/metrics/team/{team}/summary`

Это не raw telemetry. Это derived/synthetic aggregate layer по команде:

- `avg_overtime_hours`
- `avg_sick_leave_days`
- `avg_vacation_gap_days`
- `avg_night_activity_pct`
- `avg_meeting_load`

### AI layers

Источники:

- `POST /api/v1/score/employee/{id}`
- `POST /api/v1/score/employee/{id}/recommendations`
- `POST /api/v1/forecast/employee/{id}?horizon_days=30`

Это AI-assisted endpoint'ы, которые вызываются только по выбранному сотруднику.

## Доступный API

### 1. Получить одного сотрудника

```http
GET /api/v1/employees/{id}
```

Где:

- `{id}` — внутренний `id` записи в SQLite, не `employee_id`

Использование:

- employee detail page
- основа для profile header

### 2. Получить список сотрудников

```http
GET /api/v1/employees?skip=0&limit=100
```

Параметры:

- `skip` — offset
- `limit` — размер страницы, максимум `500`

Использование:

- directory page
- paginated table

Важно:

- нельзя загружать все записи сразу
- список из 74k сотрудников нужно забирать страницами

### 3. Получить сотрудников команды

```http
GET /api/v1/teams/{team}/employees?skip=0&limit=100
```

Примеры `team`:

- `Engineering`
- `Marketing`
- `Operations`
- `People Operations`
- `Customer Success`

Если в команде есть пробел:

- использовать URL encoding, например `People%20Operations`

Использование:

- team drill-down page

### 4. Получить summary по команде

```http
GET /api/v1/metrics/team/{team}/summary
```

Возвращает:

- `team`
- `avg_overtime_hours`
- `avg_sick_leave_days`
- `avg_vacation_gap_days`
- `avg_night_activity_pct`
- `avg_meeting_load`

Использование:

- team dashboard
- KPI cards
- summary widgets

### 5. Запустить AI scoring

```http
POST /api/v1/score/employee/{id}
```

Возвращает:

- `risk_score`
- `risk_level`
- `key_factors`
- `summary`

Использование:

- AI Risk panel в профиле сотрудника

### 6. Получить рекомендации

```http
POST /api/v1/score/employee/{id}/recommendations
```

Возвращает:

- `priority`
- `manager_actions`
- `employee_support_actions`
- `watch_items`
- `summary`

Использование:

- recommendations panel
- manager action block

### 7. Получить forecast

```http
POST /api/v1/forecast/employee/{id}?horizon_days=30
```

Допустимые горизонты:

- `7`
- `14`
- `30`
- `60`

Возвращает:

- `horizon_days`
- `trend`
- `forecast_summary`
- `confidence_note`
- `forecast_points`

`forecast_points` подходит для line chart:

```json
{
  "day": 1,
  "predicted_score": 72,
  "risk_level": "moderate"
}
```

## Рекомендуемая структура Streamlit

### Страница 1. Employees Directory

Использовать:

- `GET /api/v1/employees`

Что показывать:

- search
- фильтр по `team`
- пагинированную таблицу
- кнопку `Open Profile`

Рекомендуемые колонки:

- `employee_id`
- `team`
- `job_role`
- `years_at_company`
- `work_life_balance`
- `job_satisfaction`
- `performance_rating`
- `attrition`

### Страница 2. Employee Profile

Использовать:

- `GET /api/v1/employees/{id}`
- `POST /api/v1/score/employee/{id}`
- `POST /api/v1/forecast/employee/{id}`
- `POST /api/v1/score/employee/{id}/recommendations`

Что показывать:

- header profile card
- AI score card
- forecast chart
- recommendations section

Рекомендация:

- сначала загружать raw profile
- AI endpoint'ы вызывать отдельно по действию пользователя или лениво по секциям

### Страница 3. Team Overview

Использовать:

- `GET /api/v1/teams/{team}/employees`
- `GET /api/v1/metrics/team/{team}/summary`

Что показывать:

- KPI cards
- список сотрудников команды
- derived team indicators

## Поведение UI

### Что грузить сразу

Сразу можно грузить:

- список сотрудников
- профиль сотрудника
- summary по команде

### Что не грузить автоматически массово

Не вызывать автоматически для всей таблицы:

- `POST /score/employee/{id}`
- `POST /forecast/employee/{id}`
- `POST /score/employee/{id}/recommendations`

Эти endpoint'ы должны вызываться только для выбранного сотрудника.

## Рекомендации по UX

### Employee Directory

- пагинация обязательна
- `limit=50` или `limit=100` по умолчанию
- team filter лучше строить как selectbox

### Employee Profile

- показывать score в отдельной card
- `risk_level` отрисовывать цветным badge
- `key_factors` показывать списком

### Forecast

- сделать selector горизонта: `7 / 14 / 30 / 60`
- строить chart по `forecast_points`
- рядом показывать `trend`, `forecast_summary`, `confidence_note`

### Recommendations

разделять на 3 блока:

- `manager_actions`
- `employee_support_actions`
- `watch_items`

и сверху показывать:

- `priority`
- `summary`

## Рекомендации по реализации API-клиента в Streamlit

Не вызывать `requests` хаотично из разных виджетов.

Лучше сделать единый маленький client layer:

```python
get_employees(skip: int, limit: int)
get_employee(id: int)
get_team_employees(team: str, skip: int, limit: int)
get_team_summary(team: str)
score_employee(id: int)
forecast_employee(id: int, horizon_days: int)
get_recommendations(id: int)
```

## Кэширование

Можно кэшировать:

- `GET /employees`
- `GET /employees/{id}`
- `GET /teams/{team}/employees`
- `GET /metrics/team/{team}/summary`

Осторожно кэшировать:

- `POST /score/employee/{id}`
- `POST /forecast/employee/{id}`
- `POST /score/employee/{id}/recommendations`

Если кэш нужен, кэшировать только по:

- `employee_id`
- `horizon_days`

## Обработка ошибок

Для AI endpoint'ов обязательно:

- `st.spinner(...)`
- `st.error(...)`
- локальная деградация UI, а не падение всей страницы

То есть если forecast упал, employee profile page всё равно должна продолжать работать.

## Важное замечание для UI copy

Нужно честно подписывать derived/AI слои:

- employee profile = source HR profile
- team metrics = derived workload indicators
- forecast = AI scenario-based forecast
- recommendations = AI-generated management recommendations

Это важно для корректного восприятия на demo и защите.

## Минимальный приоритет реализации

Рекомендуемый порядок:

1. Employees Directory
2. Employee Profile
3. Team Overview
4. AI Score panel
5. Forecast panel
6. Recommendations panel

## Короткая handoff-версия

Если кратко:

- `employees` endpoint'ы — источник raw HR данных
- `metrics/team/summary` — агрегированная team analytics
- scoring/forecast/recommendations — AI endpoint'ы только для выбранного сотрудника
- все списки сотрудников грузить только с пагинацией
- AI endpoint'ы не вызывать массово
