# Python 3.11 base image
FROM python:3.11-slim

# System dependencies va LibreOffice o'rnatish
RUN apt-get update && apt-get install -y \
    libreoffice \
    libreoffice-writer \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Working directory
WORKDIR /app

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application code
COPY . .

# Generated files directory
RUN mkdir -p generated_files

# Environment variables (Railway'da qo'shiladi)
ENV PYTHONUNBUFFERED=1

# Botni ishga tushirish
CMD ["python", "main.py"]

