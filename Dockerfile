FROM python:3.13-slim

WORKDIR /app

# install pipenv
RUN pip install --no-cache-dir pipenv

# copy dependency files first (better caching)
COPY Pipfile Pipfile.lock ./

# install dependencies into system python (no virtualenv inside container)
RUN pipenv install --system --deploy

# copy entire project
COPY . .

# run FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]