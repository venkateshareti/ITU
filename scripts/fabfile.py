import datetime
import os
import time

from fabric.api import *


def start_service(apache_service):
    sudo("systemctl start httpd")


def stop_service(apache_service):
    try:
        sudo("systemctl stop httpd")
    except Exception as e:
        print("Exception: %s" % e)
        print ("Continuing..")


def deploy(install_config="yes", apache_service="httpd", ssl_only="no"):
    #stop_service(apache_service)
    run("rm -rf /opt/ITU_ENV1")
    run("mkdir /opt/ITU_ENV1", capture=False)
    # Create virtualenv
    run("virtualenv /opt/ituvenv")
    with cd("/opt/ITU_ENV1"):
        run("cp -r /opt/latest_code/ITU .")
    with prefix("source /opt/ituvenv/bin/activate"):
        with cd("/opt/ITU_ENV1/ITU"):
            run("echo source activated")
            run("pip install -r requirements.txt")
            run("DONE.......")


    # Wait for a while
    time.sleep(2)
    #start_service(apache_service)
    # run("rm /tmp/myplex_service.tar.gz")
    # local("rm -r %s" % local_tmp_dir)

