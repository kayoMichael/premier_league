FROM python:3.13-slim

WORKDIR /app

COPY setup.py .
COPY premier_league/ ./premier_league/
COPY README.md .

ENV SETUPTOOLS_SCM_PRETEND_VERSION=1.1.4
RUN pip install .[api]
RUN pip install .[pdf]

EXPOSE 5000

CMD ["python", "-c", "from premier_league import run_server; run_server(host='0.0.0.0')"]
