FROM python:3.11.7-slim

COPY requirements.txt /ocrserver/requirements.txt

WORKDIR /ocrserver

RUN pip3 install -r requirements.txt

RUN pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

COPY /src /ocrserver

CMD ["python3", "app.py"]
