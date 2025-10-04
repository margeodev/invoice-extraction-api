# Dockerfile (versão corrigida)

# Etapa 1: Definir a imagem base
FROM python:3.11-slim

# Etapa 2: Instalar as dependências do sistema operacional
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-por \
    && rm -rf /var/lib/apt/lists/*

# Etapa 3: Configurar o ambiente de trabalho
WORKDIR /app

# Etapa 4: Instalar as dependências do Python
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Etapa 5: Copiar o código da sua aplicação para o contêiner
COPY . .

# Etapa 6: Comando para iniciar a aplicação (CORRIGIDO)
# Esta forma garante que a variável de ambiente $PORT seja substituída pelo seu valor.
CMD gunicorn --bind 0.0.0.0:$PORT app:app
