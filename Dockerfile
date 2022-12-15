#
FROM python:3.9

#
WORKDIR /code

#
RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6  -y

RUN apt install net-tools
#
COPY ./requirements.txt /code/requirements.txt

#
RUN pip install --upgrade pip
RUN pip install --no-cache-dir --upgrade  -r /code/requirements.txt

#
COPY ./app /code/app

#
# CMD ["python3", "./app/main.py"]

EXPOSE 8080