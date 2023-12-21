FROM python:3.11.7-slim

COPY requirements.txt /ocrserver/requirements.txt

WORKDIR /ocrserver

RUN pip3 install -r requirements.txt

RUN pip3 install torch --index-url https://download.pytorch.org/whl/cpu

COPY /src /ocrserver

STOPSIGNAL SIGINT

CMD ["python3", "app.py"]
