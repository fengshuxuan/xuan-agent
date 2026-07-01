FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN useradd -m -u 10001 sandbox
WORKDIR /workspace

RUN pip install pandas numpy matplotlib openpyxl python-docx pypdf pillow

USER sandbox
CMD ["python", "--version"]
