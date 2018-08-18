from fabric.api import local, cd, env, run, get
from fabric.contrib import django
django.settings_module('base.settings')
from django.conf import settings
_ = settings.INSTALLED_APPS  # fabric bug: https://goo.gl/167WlO

env.hosts = ['webfaction']


def deploy():
    local('git push')
    with cd('~/susikiu'):
        run('git pull')
        run('pipenv install')
        run('bower install')
        run('pipenv run python manage.py collectstatic --noinput')
        run('pipenv run python manage.py migrate')
        run('supctl restart rq_susikiu')
        run('supctl restart susikiu')


def download_db():
    run('mysqldump -u {} --password={} {} > ~/tmp/susikiu.sql'.format(
        settings.DATABASES['default']['USER'],
        settings.DATABASES['default']['PASSWORD'],
        settings.DATABASES['default']['NAME']
    ))
    get('~/tmp/susikiu.sql', '/tmp')
    local('mysql -u {} --password={} {} < /tmp/susikiu.sql'.format(
        settings.DATABASES['default']['USER'],
        settings.DATABASES['default']['PASSWORD'],
        settings.DATABASES['default']['NAME']
    ))


def download_media():
    local('rsync -rtvu webfaction:~/webapps/susikiu_media/uploads/ uploads/')
