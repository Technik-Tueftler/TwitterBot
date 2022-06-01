FROM python:3.10.2-buster

ENV WORKING_DIR /user/app
WORKDIR $WORKING_DIR

COPY requirements.txt ./TwitterBot/

RUN pip install -r ./TwitterBot/requirements.txt
RUN pip install mariadb SQLAlchemy
RUN pip install sqlalchemy-utils

COPY source/ ./TwitterBot/source/

CMD ["python", "-u", "./TwitterBot/source/message_handler.py"]