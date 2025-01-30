FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt requirements.txt
COPY app.py app.py
COPY mtg_cards.db mtg_cards.db
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 5000
CMD ["python", "app.py"]
