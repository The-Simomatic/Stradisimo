FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PORT=8080

CMD ["sh", "-c", "echo MESOP_PATH=$(which mesop) && mesop --help && ls -la && mesop run app.py --port=$PORT"]

