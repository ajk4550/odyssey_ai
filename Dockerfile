FROM python:3.11-slim

WORKDIR /code

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x entrypoint.sh

ENV PYTHONPATH=/code/app

EXPOSE 8000

ENTRYPOINT ["sh", "entrypoint.sh"]
