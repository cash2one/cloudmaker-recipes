#Wordpress Cloudmaker Recipe#
This recipe sets up a Wordpress site on Digital Ocean IaaS with nightly backups
to an Amazon S3 Bucket.

The installation is idempotent so in case of failure it can simply be run
again.  Deploying this recipe does the following.
* provisions a virtual server on Digital Ocean
* create name records on Digital Ocean name servers
* installs mysql-server with a configurable root password
* installs apache, php5 and other needed packages
* installs the cloudmaker python package
* installs the aws-cli python package and configures it
* downloads the lates wordpress from https://wordpress.org/latest.zip and
unpacks it in the apache root directory
* creates a mysql database with configurable name, username and password
* creates the necessary configuration to connect wordpress to the mysql database
* installs backup and restore scripts at "/root/backup.py" and "/root/restore.py"
which creats an archive containing the wordpress web content and the mysql
database and copies it to an amazon s3 bucket
* installs a cron job to run the backup script each night
* runs the restore script to restore a previously saved wordpress site (if any)

# Prerequisites #
* A Digital Ocean account and a Digital Ocean API Access Key ( see https://www.digitalocean.com/community/tutorials/how-to-use-the-digitalocean-api-v2 for more information)
* Cloudmaker uses ssh keys to access the servers on Digital Ocean. See step one
and two of https://www.digitalocean.com/community/tutorials/how-to-set-up-ssh-keys--2
for instructions on creating the key. You will need the public half of the key
typicall stored at ~/.ssh/id_rsa.pub.
* An AWS s3 bucket which will contain the backups.
* Amazon credentials ("aws access key" and "aws secret access key") that have
access to the s3 bucket

#Quick Start#
1. Install cloudmaker: `pip install cloudmaker`
1. Download the wordpress recipe `git clone https://github.com/wrmay/cloudmaker-recipes`
1. Copy the "wordpress" directory to a directory named after your wordpress
site (e.g. "mysite")
1. Edit "mysite/server.json" and provide all of the requested credentials. You
can also change the "size" parameter to "1gb" or "2gb" to install a larger server
but it is not recommended that you change the "image" parameter.
1. Run `cloudmaker deploy mysite` where "mysite" is the absolute or relative
path to the directory containing your recipe.

Thats It!

To undeploy, run `cloudmaker undeploy mysite`

#Sample Recipe Configuration File#
```json
{
    "digitalocean" : {
        "security" : {
            "digital_ocean_api_key" : "***"
            ,"public_ssh_key" : "ssh-rsa *** user@mysite.com"
        }, "provision": {
            "name" : "myserver"
            , "region" : "nyc3"
            , "size" : "512mb"
            , "image" :  "debian-7-0-x64"
            , "backups" : false
            , "dnsRecords" :["mysite.com","www.mysite.com"]
        }
    }, "mysql" : {
        "root_password":"ch0r1z0"
    }, "wordpress": {
        "db_name": "wordpress"
        , "db_user" : "wordpress"
        , "db_password" : "***"
    }, "aws" : {
        "aws_access_key_id":"***"
        ,"aws_secret_access_key" : "***"
        , "default.region" : "us-east-1"
    } , "backup" :{
        "s3_bucket" : "s3://mysite-backups"
    }
}
```
