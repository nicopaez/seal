from behave import *
from parse import *
from selenium import webdriver
from django.core.files import File
import shutil

# The next few steps are required to load the configuration and include the application model for the behavioural tests.
import os, sys
from django.contrib.auth import login
from seal.utils.managepath import Managepath
managepath = Managepath()

sys.path.append(managepath.get_web_path())         # Required to use the app model
sys.path.append(managepath.get_daemon_path())
sys.path.append(managepath.get_model_path()) # Fixes 'No module named model'
os.environ['DJANGO_SETTINGS_MODULE'] = 'seal.settings'

practicePath = managepath.get_practice_path()
deliveryPath = managepath.get_delivery_path()
scriptPath = managepath.get_script_path()

# Now we can load our model
from seal.model import Course, Student, Practice, Delivery, Teacher, Correction, Suscription
from django.contrib.auth.models import User

def before_all(context):
    Suscription.objects.all().delete()
    Correction.objects.all().delete()
    Delivery.objects.all().delete()
    Practice.objects.all().delete()
    Course.objects.all().delete()
    Student.objects.all().delete() # Given Students are authenticated users, can't delete them without deleting the users
    Teacher.objects.all().delete()
    User.objects.exclude(username='seal').delete()
    
def after_all(context):
    Suscription.objects.all().delete()
    Correction.objects.all().delete()
    Delivery.objects.all().delete()
    Practice.objects.all().delete()
    Course.objects.all().delete()
    Student.objects.all().delete() # Given Students are authenticated users, can't delete them without deleting the users
    Teacher.objects.all().delete()
    User.objects.exclude(username='seal').delete()
    if os.path.isdir(practicePath):
        shutil.rmtree(practicePath)
    if os.path.isdir(deliveryPath):
        shutil.rmtree(deliveryPath)
    if os.path.isdir(scriptPath):
        shutil.rmtree(scriptPath)
        
def before_feature(context, feature):
    context.browser = webdriver.Firefox()
    context.browser.get('http://localhost:8000/')

def after_feature(context, feature):
    Suscription.objects.all().delete()
    Correction.objects.all().delete()
    Delivery.objects.all().delete()
    Practice.objects.all().delete()
    Course.objects.all().delete()
    Student.objects.all().delete() # Given Students are authenticated users, can't delete them without deleting the users
    Teacher.objects.all().delete()
    User.objects.exclude(username='seal').delete()
    context.browser.close()

def before_scenario(context, scenario):
    context.browser.get('http://localhost:8000/')
