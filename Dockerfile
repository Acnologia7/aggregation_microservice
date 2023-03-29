FROM python:3.10.6

ENV PYTHONUNBUFFERED 1
ENV APP_HOME=/app
ENV TZ="Europe/Prague"
ENV TESTING_MODE=1
WORKDIR ${APP_HOME}
EXPOSE 5000


COPY app app
COPY make_db.py make_db.py
COPY run.py run.py
COPY tests tests
COPY .env ./
COPY requirements.txt ./

RUN pip install -r requirements.txt 

#FOR TESTING
ENTRYPOINT [ "tail", "-f", "/dev/null" ]

#FOR APP RUNNING 
#ENTRYPOINT ["flask", "run", "--host=0.0.0.0"]

