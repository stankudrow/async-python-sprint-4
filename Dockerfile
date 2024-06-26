FROM python:3.11-alpine

# prevents pyc files from being copied to the container
ENV PYTHONDONTWRITEBYTECODE 1
# Ensures that python output is logged in the container's terminal
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY . .

# installing the project
RUN pip3 install . --no-cache-dir

CMD ["python3", "sprint4/main.py"]
