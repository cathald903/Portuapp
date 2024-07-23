ARG PYTHON_VERSION=3.11
FROM python:${PYTHON_VERSION}-slim as base
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    pip install -r requirements.txt

COPY . .

EXPOSE 8000
ENV PYTHONPATH=/app
ENV FLASK_APP='app/csvs/rest_app.py'
ENV VERB_FILE='app/csvs/Verbs.csv'
ENV VOCAB_FILE='app/csvs/Vocab.csv'
ENV ANSWER_FILE='app/csvs/Answers.csv'
ENV USERSUB_FILE='app/csvs/UserSubscriptions.csv'
ENV ENVIRONMENT='Test'