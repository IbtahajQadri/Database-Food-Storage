FROM python:latest
WORKDIR /app
COPY *.py ./
CMD [ "echo", "Docker image built. No app to run yet."]