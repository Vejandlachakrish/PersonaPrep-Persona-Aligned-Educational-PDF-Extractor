
#extractor.py
# FROM --platform=linux/amd64 python:3.10-slim

# WORKDIR /app

# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

# COPY extractor.py .

# CMD ["python", "extractor.py"]

#persona_matcher.py

FROM python:3.9-slim
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt
CMD ["python", "persona_extractor.py"]
