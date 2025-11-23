FROM python:3.11.4-slim

RUN apt-get update && apt-get install -y libpq-dev gcc
RUN pip install poetry

WORKDIR /application

RUN mkdir /application/data

COPY poetry.lock poetry.lock
COPY pyproject.toml pyproject.toml
RUN poetry install --no-root

RUN apt-get autoremove -y gcc

COPY . .
RUN poetry install

CMD ["poetry", "run", "python", "src/bookly/__init__.py"]