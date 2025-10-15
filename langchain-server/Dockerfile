FROM python:3.12-slim

# UTF-8 환경 설정
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8
ENV PYTHONIOENCODING=utf-8

WORKDIR /app

RUN pip install poetry && poetry config virtualenvs.create false

COPY pyproject.toml ./
RUN poetry install --only main

COPY ./app ./app
COPY *.pdf ./
COPY *.json ./

CMD ["sh", "-c", "sleep 30 && poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"]
