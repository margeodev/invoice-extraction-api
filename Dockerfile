# Dockerfile

# Etapa 1: Definir a imagem base
# Usamos uma imagem oficial do Python. A versão "slim" é mais leve.
FROM python:3.11-slim

# Etapa 2: Instalar as dependências do sistema operacional (O MAIS IMPORTANTE)
# Este comando instala o Tesseract OCR e o pacote de idioma português.
# É o equivalente ao que estávamos tentando fazer com os outros arquivos.
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-por \
    && rm -rf /var/lib/apt/lists/*

# Etapa 3: Configurar o ambiente de trabalho
# Define o diretório padrão dentro do contêiner para /app
WORKDIR /app

# Etapa 4: Instalar as dependências do Python
# Copia primeiro o requirements.txt para aproveitar o cache do Docker
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Etapa 5: Copiar o código da sua aplicação para o contêiner
COPY . .

# Etapa 6: Comando para iniciar a aplicação
# O Railway definirá a variável de ambiente $PORT automaticamente.
# O Gunicorn irá iniciar o servidor web ouvindo em todas as interfaces de rede na porta fornecida.
CMD ["gunicorn", "--bind", "0.0.0.0:$PORT", "app:app"]
