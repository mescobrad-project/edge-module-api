FROM python:3.7-slim

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY src/requirements.txt /usr/src/app/

RUN apt-get update && apt-get install -y git dcm2niix unzip gzip wget libgomp1

RUN pip3 install --no-cache-dir -r requirements.txt

COPY ./src /usr/src/app

EXPOSE 8080

ENTRYPOINT ["python3"]

CMD ["-m", "mescobrad_edge"]
