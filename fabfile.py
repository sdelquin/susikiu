from fabric.api import cd, env, get, local, run
from fabric.contrib import django

django.settings_module('base.settings')
from django.conf import settings
_ = settings.INSTALLED_APPS  # fabric bug: https://goo.gl/167WlO

env.hosts = ['cloud']


def deploy():
    local('git push')
    with cd('~/susikiu'):
        run('git pull')
        run('pipenv install')
        run('bower install')
        run('pipenv run python manage.py collectstatic --noinput')
        run('pipenv run python manage.py migrate')
        run('supervisorctl restart rq_susikiu')
        run('supervisorctl restart susikiu')


def download_db():
    db_user = settings.DATABASES['default']['USER']
    db_password = settings.DATABASES['default']['PASSWORD']
    db_name = settings.DATABASES['default']['NAME']

    run('pg_dump --clean --dbname='
        f'postgresql://{db_user}:{db_password}@localhost/{db_name} > '
        '/tmp/susikiu.sql')

    get('/tmp/susikiu.sql', '/tmp')

    local('psql '
          f'--dbname=postgresql://{db_user}:{db_password}@localhost/{db_name} '
          '< /tmp/susikiu.sql')


def download_media():
    local('rsync -rtvu cloud:~/susikiu/media/ media/')
