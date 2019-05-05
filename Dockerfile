FROM python:3.7.3-alpine
WORKDIR /usr/src/app

ENV AWS_DEFAULT_REGION="us-east-1"

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENTRYPOINT [ "python", "./sendmetrics.py" ]