"""
Created on 19/10/2012

@author: anibal

Fabric file. This file imports the necessary modules and sets up the enviroment
to be able to perform all the tasks intended for fabric.
"""
from __future__ import with_statement
from fabric.api import local, settings
from fabric.context_managers import lcd
from subprocess import Popen
import time


import ConfigParser, os
import sys
from fileinput import close
config = ConfigParser.ConfigParser()
config.readfp(open('web/conf/local.cfg'))
sys.path.append(config.get("Path", "path.project.web"))      # Required to use the app model
sys.path.append(config.get("Path", "path.project.daemon"))
sys.path.append(config.get("Path", "path.behave.model")) # Fixes 'No module named model'


os.environ['DJANGO_SETTINGS_MODULE'] = 'seal.settings'
project_base_path = os.path.realpath(os.path.dirname(__file__))
os.environ['PROJECT_PATH'] = project_base_path + "/"

class FabricContext:
    """
    Context class to transfer information from one call to another.
    """
    server_process = None


def set_pythonpath():
    import os
    project_base_path = os.path.realpath(os.path.dirname(__file__))
    os.environ["PYTHONPATH"] = project_base_path + "/web/" + ":" + project_base_path + "/daemon/" + ":" + project_base_path + "/web/seal/"
    print "PYTHONPATH set to : \"" + os.environ["PYTHONPATH"] + "\""


def launch_server(context):
    """
    Launches the test instance of the application server in a separate process
    to run the feature tests.
    """
    print("[fabric] launching server instance for feature tests.")
    set_pythonpath()
    context.server_process = Popen(["python", "web/seal/manage.py", "runserver", "--noreload"])
    print("[fabric] server online... pid: " + str(context.server_process.pid))

def kill_server(context):
    """
    Terminates the tests instance of the application server. It is supposed to
    be called after running the feature tests.
    """
    print("[fabric] killing server...")
    context.server_process.terminate()
    print("[fabric] server killed...")

def get_mysql_bash():
    """
    Builds the string that should be used to call a command over the database.
    It is used to include the username and password to access the service. This
    command would allow you to connect to de database, if you want to invoke a
    given sql command, use get_mysql_bash_cmd.
    """
    user = config.get("Database", "user")
    passwd = config.get("Database", "pass")
    local_cmd = "mysql -u " + user
    if (passwd != ""):
        local_cmd += " -p'" + passwd + "'"
    return local_cmd

def get_mysql_bash_cmd(sql_sentence = "SHOW TABLES;", database = None):
    """
    Builds the string that should be used to call a command over the database
    with a given sql command. It uses the configuration given in the local.conf
    file.
    """
    user = config.get("Database", "user")
    passwd = config.get("Database", "pass")
    local_cmd = "mysql -e '" + sql_sentence + "' -u " + user
    if (database is not None and database != ""):
        local_cmd += " -D " + database + " "
    if (passwd != ""):
        local_cmd += " -p'" + passwd + "' "
    return local_cmd

def create_super_user():
    """
    After the database is flushed and syncronized, it is necessary to create a
    user to access the admin site. Teachers can be created from the admin site
    and Students register themselves.
    """
    set_pythonpath()
    from django.contrib.auth.models import User
    try:
        admin_user = User.objects.get_by_natural_key('seal')
        print "Super user already exists: " + str(admin_user)
    except:
        u = User.objects.create(
            username='seal',
            first_name='Seal',
            last_name='Administrator',
            email='seal@gmail.com',
            is_superuser=True,
            is_staff=True,
            is_active=True
        )
        u.set_password('seal')
        u.save()
        print "User account created"

def prepare_db(context = None):
    """
    Resets the database applying the latests changes made in the app model.
    """
    print("[fabric] preparing database.")
    if(config.get("Enviroment", "location") == "travis"):
        print("Travis location detected. Seting up database layout...")
        cmd = get_mysql_bash_cmd(sql_sentence = "create database seal;")
        local(cmd)
        cmd = get_mysql_bash()
        local(cmd + " < build_files/ci_dbuser.sql")
        print("Layout set.")
    else:
        print("Environment detected. No need to create either database user nor schema.")
        print("Sincronizing DB...")
        cmd = get_mysql_bash_cmd(sql_sentence = "SHOW TABLES;", database = "seal")
        output = local(cmd + " -N ", capture=True)
        if (output != ""):
            mysql_cmd = "SET foreign_key_checks = 0; "
            mysql_cmd += "DROP TABLE IF EXISTS " + ",".join(output.splitlines()) +" CASCADE; "
            mysql_cmd += "SET foreign_key_checks = 1;"
            cmd = get_mysql_bash_cmd(sql_sentence = mysql_cmd, database = "seal")
            local(cmd)
    with lcd("web"):
        local("python seal/manage.py syncdb --noinput")
    create_super_user()
    print("syncdb complete")

def run_tests(context = None):
    """Runs the application tests for the Django app"""
    print("[fabric] invoking tests.")
    with lcd("web"):
        local("python seal/manage.py test")

def run_features_tests(context = None):
    """
    Runs the feature tests. Launches the server before running the tests, and
    kills it after
    """
    launch_server(context)
    print("[fabric] invoking feature testing.")
    with lcd("web/feature_test"):
        local("behave")
    kill_server(context)

def prepare_deploy(context = None):
    """Syncronizes the database and runs all the tests"""
    prepare_db(context)
    test()
    if (config.get("Enviroment", "location") == "dev"):
        run_features_tests(context)

def invoke_test_deploy(context = None):
    """Calls a url in the test server to update the test instance"""
    if(config.get("Enviroment", "location") == "travis"):
        print("[fabric] tests run successfully... deploying to test instance.")
        local("wget http://ixion-tech.com.ar/seal/requestUpdate.php")
        local("cat requestUpdate.php")


def run_coverage_analysis(context = None):
    """Invokes the test coverage analysis and generates the reports"""
    set_pythonpath()
    with lcd("web"):
        local("coverage run seal/manage.py test model")
        if(config.get("Enviroment", "location") == "travis"):
            local("coverage report")
        else:
            local("coverage html")

def pylint():
    """Runs the pylint analysis and saves the report to be available"""
    print "launching pylint static analysis..."
    set_pythonpath()
    with settings(warn_only=True):
        result = local("pylint web/seal daemon/auto_correction --rcfile=pylintrc > pylint_report/pylint.html")
    print "pylint static analysis complete... exit status: " + str(result.return_code)
    print "you can access the report result pylint_report/pylint.html"

def run():
    """Main command for the fabric run"""
    ctxt = FabricContext()
    prepare_deploy(ctxt)
    # This line is called to rise the flag in the test server to activate the update and deploy of the changes
    # invoke_test_deploy(ctxt)
    run_coverage_analysis()

def start():
    print("[fabric] launching server instance.")
    set_pythonpath()
    server_process = Popen(["nohup", "python", "web/seal/manage.py", "runserver", "--noreload"], stdout = open(os.devnull, 'w+', 0), env=os.environ)
    local("echo " + str(server_process.pid) + " > /tmp/seal_server.pid")
    print("[fabric] server online... pid: " + str(server_process.pid))


def start_ip(ip):
    print("[fabric] launching server instance.")
    set_pythonpath()
    server_process = Popen(["nohup", "python", "web/seal/manage.py", "runserver", str(ip) + ":8000", "--noreload"], stdout = open(os.devnull, 'w+', 0), env=os.environ)
    local("echo " + str(server_process.pid) + " > /tmp/seal_server.pid")
    print("[fabric] server online... pid: " + str(server_process.pid))

def stop():
    file = open("/tmp/seal_server.pid")
    line = file.readline()
    local("kill -2 " + line)
    file.close()
    os.remove("/tmp/seal_server.pid")

def start_daemon_DEPRECATED():
    print "[fabric] launching daemon..."
    set_pythonpath()
    daemon_process = Popen(["nohup", "python", "daemon/auto_correction/daemon_control.py"], stdout = open("/tmp/daemon.out", 'w+', 0), env=os.environ)
    local("echo " + str(daemon_process.pid) + " > /tmp/seal_daemon.pid")
    print("[fabric] daemon active... pid: " + str(daemon_process.pid))

def stop_daemon_DEPRECATED():
    print "[fabric] stopping daemon..."
    file = open("/tmp/seal_daemon.pid")
    line = file.readline()
    local("kill -2 " + line)
    file.close()
    os.remove("/tmp/seal_daemon.pid")
    print("[fabric] daemon killed - pid: " + line)


def start_daemon():
    set_pythonpath()
    with lcd("daemon/auto_correction"):
        local("python daemon_control.py start")

def stop_daemon():
    set_pythonpath()
    with lcd("daemon/auto_correction"):
        local("python daemon_control.py stop")


def test(app_name=''):
    set_pythonpath()
    with lcd("web/seal"):
        local("python manage.py test " + app_name)

def behave():
    set_pythonpath()
    with lcd("web/feature_test"):
        local("behave")

def feature(arg):
    """It runs all behave features which contains te arg value"""
    set_pythonpath()
    with lcd("web/feature_test"):
        local("behave -i " + arg)
