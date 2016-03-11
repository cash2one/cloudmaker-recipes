#!/usr/bin/python

import json
import logging
import os
import os.path
import shutil
import stat
import subprocess
import sys
import urllib2

from cloudmaker.linux import *
from cloudmaker.mysql import *
from cloudmaker.template import *

logging.basicConfig(level='INFO')

with open('/tmp/setup/server.json') as configFile:
    config = json.load(configFile)
    logging.info('loaded configuration from /tmp/setup/server.json')


passw = config['mysql']['root_password']
debconfSetSelections('mysql-server', 'mysql-server/root_password', 'password', passw)
debconfSetSelections('mysql-server', 'mysql-server/root_password_again', 'password', passw)
aptInstall('mysql-server')
aptInstall('apache2')
aptInstall('php5')
aptInstall('php-pear')
aptInstall('php5-mysql')
aptInstall('php5-curl')
subprocess.check_call(['pip','install','Jinja2'])

wpdb = config['wordpress']['db_name']
wpuser=config['wordpress']['db_user']
wppass=config['wordpress']['db_password']

createDB('root',passw,wpdb)
createLocalUserWithAllPrivilegesOnDB('root',passw,wpuser, wppass,wpdb)

#download wordpress and move it into place
if os.path.exists('/tmp/latest.zip'):
    os.remove('/tmp/latest.zip')
    
    
subprocess.check_call(['wget', 'https://wordpress.org/latest.zip'], cwd='/tmp')
subprocess.check_call(['unzip','/tmp/latest.zip','-d','/var'])
subprocess.check_call(['rm', '-rf', '/var/www'])
subprocess.check_call(['mv','/var/wordpress','/var/www'])

#obtain random salt setting from the wordpress service
f = urllib2.urlopen('https://api.wordpress.org/secret-key/1.1/salt') 
saltSettings = f.read()

#render the wp-config template
templateArgs = dict()
templateArgs['WORDPRESS_DB_NAME'] = wpdb
templateArgs['WORDPRESS_DB_USER'] = wpuser
templateArgs['WORDPRESS_DB_PASSWORD'] = wppass
templateArgs['WORD_PRESS_SECRET_STUFF'] = saltSettings

renderTemplate('/tmp/setup','wp-config.php.template','/var/www/wp-config.php', templateArgs)

logging.info('installed wordpress')

#install and configure AWS CLI for backups
subprocess.check_call(['pip','install','awscli'])
subprocess.check_call(['aws', 'configure','set','aws_access_key_id',config['aws']['aws_access_key_id']])
subprocess.check_call(['aws', 'configure','set','aws_secret_access_key',config['aws']['aws_secret_access_key']])
subprocess.check_call(['aws', 'configure','set','default.region',config['aws']['default.region']])
logging.info('installed and configured aws cli')

#copy the backup restore scripts
templateArgs['BACKUP_S3_BUCKET'] = config['backup']['s3_bucket']
templateArgs['MYSQL_ROOT_PASSWORD'] = config['mysql']['root_password']
renderTemplate('/tmp/setup','backup.py.template','/root/backup.py',templateArgs)
renderTemplate('/tmp/setup','restore.py.template','/root/restore.py',templateArgs)
os.chmod('/root/backup.py', 700)
os.chmod('/root/restore.py', 700)
logging.info('copied backup and restore scripts')

subprocess.check_call(['crontab', '/tmp/setup/crontab.txt'])
logging.info('installed cron jobs')

#run the restore script
subprocess.check_call(['/root/restore.py'])
