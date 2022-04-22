#Courtesy of Musho from druid discord

FROM python:3.9-slim-bullseye

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install dependencies:
COPY requirements.txt .
RUN pip install -r requirements.txt

# Run the application:
RUN apt update
RUN apt -y upgrade
COPY . .
EXPOSE 8080
CMD ["python", "main.py"]