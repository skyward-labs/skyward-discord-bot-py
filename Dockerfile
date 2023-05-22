FROM python:3.11.3

WORKDIR /app

RUN apt-get update && apt-get install -y build-essential libssl-dev ca-certificates libasound2 wget

COPY requirements.txt requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "src/__init__.py"]
