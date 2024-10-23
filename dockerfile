FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt setup.py ./

RUN pip install --no-cache-dir -r requirements.txt

COPY app/ app/
COPY premier_league/ premier_league/
COPY app.py .

RUN pip install -e .

ENV FLASK_APP=app.py
ENV FLASK_ENV=production

EXPOSE 3000

CMD ["gunicorn", "--bind", "0.0.0.0:3000", "--chdir", "/app", "app:app"]
