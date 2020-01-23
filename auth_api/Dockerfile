FROM python:3.7-slim

ARG ENV
ARG FLASK_PATH

COPY . ${FLASK_PATH}

WORKDIR ${FLASK_PATH}

RUN pip install -r requirements/${ENV}.txt

CMD ["python", "app.py"]