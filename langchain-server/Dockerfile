FROM python:3.12-slim

WORKDIR /app

RUN pip install poetry && poetry config virtualenvs.create false

COPY pyproject.toml ./
RUN poetry install --only main

COPY ./app ./app
COPY *.pdf ./
COPY *.json ./

CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
