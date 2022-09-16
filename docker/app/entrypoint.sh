#!/bin/sh

if [ "$DB_ENGINE" = "django.db.backends.postgresql" ]
then
    echo "Waiting for PostgreSQL..."

    while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

python manage.py flush --no-input
python manage.py migrate

$ python manage.py dumpdata \
  --exclude admin.logentry --exclude sessions.session \
  --format json --output fixtures/init.json --indent 4

exec "$@"
