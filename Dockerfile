FROM python:3.11-slim

COPY requirements.txt /ocrserver/requirements.txt

WORKDIR /ocrserver

RUN pip3 install -r requirements.txt --no-cache-dir && pip3 install torch --index-url https://download.pytorch.org/whl/cpu --no-cache-dir

COPY /src /ocrserver

STOPSIGNAL SIGINT

ENTRYPOINT ["/bin/bash", "-c", "python3", "app.py"]
