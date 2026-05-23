# Инструкция по интеграции `llm` модуля в FastAPI

Этот документ описывает, как FastAPI-часть проекта должна взаимодействовать с модулем `llm`.

## Назначение модуля

Модуль `llm` уже реализует AI-логику MVP:

- расчёт текущего риска выгорания;
- прогноз выгорания на заданный срок;
- генерацию рекомендаций для руководителя.

FastAPI-слой не должен дублировать эту логику.

## Что уже реализовано в `llm`

В модуле уже есть 3 публичные функции:

```python
score_current_burnout(metrics: EmployeeMetrics) -> BurnoutScoreResult
forecast_burnout(metrics: EmployeeMetrics, horizon_days: int) -> BurnoutForecastResult
generate_recommendations(metrics: EmployeeMetrics) -> RecommendationResult
```

Также внутри модуля уже реализованы:

- prompt builder;
- вызов OpenAI API;
- structured parsing ответа модели;
- валидация ответа через `Pydantic`.

## Что FastAPI-разработчику делать не нужно

Не нужно:

- вызывать OpenAI API напрямую;
- писать или изменять prompts внутри роутов;
- вручную парсить JSON-ответ от модели;
- собирать `dict` из raw text ответа;
- дублировать `Pydantic`-валидацию LLM-ответа.

Всё это уже делает модуль `llm`.

## Что должен делать FastAPI-слой

FastAPI-часть должна:

1. принять HTTP-запрос;
2. получить метрики сотрудника из request body или из БД;
3. собрать объект `EmployeeMetrics`;
4. вызвать нужную функцию из `llm.scorer`;
5. вернуть результат через `response_model`.

## Какие импорты использовать

Импорт функций:

```python
from llm.scorer import (
    score_current_burnout,
    forecast_burnout,
    generate_recommendations,
)
```

Импорт схем:

```python
from llm.schemas import (
    EmployeeMetrics,
    BurnoutScoreResult,
    BurnoutForecastResult,
    RecommendationResult,
)
```

## Входная схема метрик

Все три функции работают с объектом:

```python
EmployeeMetrics(
    employee_id: str,
    team_id: str,
    overtime: float,
    sick_leave: int,
    vacation_gap: int,
    night_activity: int,
    meeting_load: float,
)
```

Если endpoint получает `employee_id`, а не готовые метрики, FastAPI/service layer должен сначала достать данные сотрудника из БД, затем собрать `EmployeeMetrics`.

## Рекомендуемые endpoint'ы

### 1. Текущий риск выгорания

Назначение:
вернуть текущую AI-оценку состояния сотрудника.

Пример:

```python
from fastapi import APIRouter

from llm.scorer import score_current_burnout
from llm.schemas import EmployeeMetrics, BurnoutScoreResult


router = APIRouter()


@router.post(
    "/api/v1/score/employee/current",
    response_model=BurnoutScoreResult,
)
def get_current_burnout_score(metrics: EmployeeMetrics) -> BurnoutScoreResult:
    return score_current_burnout(metrics)
```

### 2. Прогноз выгорания

Назначение:
вернуть прогноз на заданный горизонт и точки для графика в Streamlit.

Пример:

```python
from fastapi import APIRouter, Query

from llm.scorer import forecast_burnout
from llm.schemas import EmployeeMetrics, BurnoutForecastResult


router = APIRouter()


@router.post(
    "/api/v1/score/employee/forecast",
    response_model=BurnoutForecastResult,
)
def get_burnout_forecast(
    metrics: EmployeeMetrics,
    horizon_days: int = Query(..., ge=1, le=365),
) -> BurnoutForecastResult:
    return forecast_burnout(metrics, horizon_days)
```

Для MVP желательно ограничить набор допустимых горизонтов, например:

- `7`
- `14`
- `30`
- `60`

Это уменьшит нестабильность demo и упростит UX.

### 3. Рекомендации

Назначение:
вернуть рекомендации для менеджера при признаках перегрузки или риска выгорания.

Пример:

```python
from fastapi import APIRouter

from llm.scorer import generate_recommendations
from llm.schemas import EmployeeMetrics, RecommendationResult


router = APIRouter()


@router.post(
    "/api/v1/score/employee/recommendations",
    response_model=RecommendationResult,
)
def get_recommendations(metrics: EmployeeMetrics) -> RecommendationResult:
    return generate_recommendations(metrics)
```

## Если данные сначала читаются из SQLite

Если endpoint получает только `employee_id`, логика должна быть такой:

1. достать запись сотрудника из БД;
2. преобразовать запись в `EmployeeMetrics`;
3. передать `EmployeeMetrics` в функцию `llm.scorer`;
4. вернуть результат.

Пример:

```python
employee_row = repository.get_employee(employee_id)

metrics = EmployeeMetrics(
    employee_id=employee_row.employee_id,
    team_id=employee_row.team_id,
    overtime=employee_row.overtime,
    sick_leave=employee_row.sick_leave,
    vacation_gap=employee_row.vacation_gap,
    night_activity=employee_row.night_activity,
    meeting_load=employee_row.meeting_load,
)

result = score_current_burnout(metrics)
return result
```

## Как выглядят ответы

Функции `llm.scorer` возвращают не сырой JSON и не строку, а `Pydantic`-объекты.

Это значит, что FastAPI может сразу использовать их как `response_model`.

Пример:

```python
result = score_current_burnout(metrics)
return result
```

FastAPI сам сериализует объект в JSON.

## Как Streamlit должен использовать ответы

Streamlit получает обычный JSON от FastAPI и читает поля ответа.

Примеры:

- `risk_score`
- `risk_level`
- `key_factors`
- `forecast_points`
- `manager_actions`

FastAPI не должен вручную "разбивать" ответ LLM на отдельные JSON-поля, если `response_model` уже совпадает с контрактом.

## Разделение ответственности

### Ответственность `llm`

- AI-логика;
- prompt engineering;
- вызов OpenAI API;
- structured parsing;
- валидация ответа модели.

### Ответственность FastAPI

- HTTP routing;
- чтение входных данных;
- загрузка employee metrics из БД при необходимости;
- вызов нужной функции из `llm.scorer`;
- возврат результата клиенту.

## Краткая инструкция для интеграции

FastAPI-разработчику нужно сделать следующее:

1. импортировать функции из `llm.scorer`;
2. импортировать схемы из `llm.schemas`;
3. в роуте собрать `EmployeeMetrics`;
4. вызвать нужную функцию;
5. вернуть результат через `response_model`.

## Важное правило

Нельзя переносить LLM-логику в роуты.

Если потребуется изменить поведение AI:

- менять prompts;
- менять client;
- менять scorer;

нужно внутри модуля `llm`, а не в FastAPI endpoint'ах.
