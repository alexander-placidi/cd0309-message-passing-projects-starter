FROM python:3.13
LABEL maintainer="Alexander Placidi"

COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt

EXPOSE 5006

CMD [ "python", "app.py" ]