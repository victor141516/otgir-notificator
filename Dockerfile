FROM python:3-alpine

WORKDIR /app
RUN pip install requests beautifulsoup4
VOLUME [ "/app/config.py" ]
COPY . /app
CMD [ "python", "main.py" ]