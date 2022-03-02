FROM python:3.8
WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN apt-get update && \
    apt-get install gettext libgettextpo-dev -y && \
    pip install -r requirements.txt
COPY . /app
# RUN python manage.py migrate
RUN python manage.py collectstatic --noinput
RUN python manage.py compilemessages
CMD uwsgi --module=astroedu_wagtail.wsgi --http=0.0.0.0:80
