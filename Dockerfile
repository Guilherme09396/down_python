FROM python:3.11-slim

WORKDIR /app

# instalar dependências do sistema
RUN apt-get update && apt-get install -y ffmpeg curl

# copiar arquivos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# instalar yt-dlp
RUN pip install -U yt-dlp

COPY . .

# porta dinâmica (IMPORTANTE)
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-3000}"]