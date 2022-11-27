FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9
WORKDIR /app

COPY ./app .
COPY ./requirements.txt ./requirements.txt

RUN pip install --no-cache-dir --upgrade -r requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]



