FROM python:3.13
LABEL maintainer="Alexander Placidi"

ENV SERVER_HOST "0.0.0.0"
ENV SERVER_PORT "5000"

COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt

EXPOSE 30001

CMD ["flask", "run", "--host", ${SERVER_HOST}, "--port", ${SERVER_PORT}]