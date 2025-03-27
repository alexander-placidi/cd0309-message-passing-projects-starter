FROM python:3.13-alpine
LABEL maintainer="Alexander Placidi"

ENV SERVER_HOST="0.0.0.0"
ENV SERVER_PORT="30001"

WORKDIR .

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

EXPOSE 30001

COPY . .
CMD ["sh", "-c", "flask run --host $SERVER_HOST --port $SERVER_PORT"]