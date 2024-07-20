FROM python:3.8-slim

WORKDIR /usr/src/app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 3000
EXPOSE 5000

CMD ["python", "main.py"]
