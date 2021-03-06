from django.http import HttpResponse
from django.shortcuts import render
from seal.model import Practice, Delivery
from django.contrib.auth.decorators import login_required
from zipfile import ZipFile
from seal.utils import managepath
import os
from seal.model.student import Student
from seal.model.automatic_correction import AutomaticCorrection
from seal.model.correction import Correction
from seal.view import HTTP_401_UNAUTHORIZED_RESPONSE
import shutil

TYPEZIP = "application/zip"

@login_required
def listdelivery(request, idpractice):
    if(len(request.user.teacher_set.all()) > 0): # if an authenticated user "accidentally" access this section, he doesn't get an exception
        practice = Practice.objects.get(pk=idpractice)
        table_deliveries = []
        deliveries = Delivery.objects.filter(practice=practice).order_by('deliverDate')
        for delivery in deliveries:
            correction = Correction.objects.filter(delivery=delivery)
            table_deliveries.append({'delivery': delivery, 'correction':correction})
        return render(request, 'delivery/listdelivery.html', {'table_deliveries': table_deliveries , 'practice': practice,})
    else:
        return HTTP_401_UNAUTHORIZED_RESPONSE

@login_required
def download(request, iddelivery):
    if(len(request.user.teacher_set.all()) > 0): # if an authenticated user "accidentally" access this section, he doesn't get an exception
        delivery = Delivery.objects.get(pk=iddelivery)
        filename = delivery.file.name.split('/')[-1]
        response = HttpResponse(delivery.file, content_type=TYPEZIP)
        response['Content-Disposition'] = 'attachment; filename=%s' % filename
        return response
    else:
        return HTTP_401_UNAUTHORIZED_RESPONSE

def walk_directory(files_list, path, relative_path):
    tuples = []
    for walk_tuple in os.walk(path):
        tuples.append(walk_tuple)
    
    (path, directories, filenames) = tuples[0]
    for filename in filenames:
        if(relative_path is None):
            files_list.append(filename)
        else:
            files_list.append(os.path.join(relative_path, filename))
    for directory in directories:
        if(relative_path is None):
            walk_directory(files_list, os.path.join(path, directory), directory)
        else:
            walk_directory(files_list, os.path.join(path, directory), os.path.join(relative_path, directory))

@login_required
def browse(request, iddelivery, file_to_browse=None):
    if(len(request.user.teacher_set.all()) > 0): # if an authenticated user "accidentally" access this section, he doesn't get an exception
        delivery = Delivery.objects.get(pk=iddelivery);
        extraction_dir = os.path.join(managepath.get_instance().get_temporary_files_path(), str(delivery.pk))
        if (not os.path.exists(extraction_dir)):
            zipfile = ZipFile(delivery.file)
            zipfile.extractall(extraction_dir)
        
        files_list = []
        walk_directory(files_list, extraction_dir, None)
        
        if (file_to_browse is None):
            file_content = None
        else:
            file_path = os.path.join(extraction_dir, file_to_browse)
            with open(file_path, 'r') as content_file:
                file_content = content_file.read()
        return render(request, 'delivery/browsedelivery.html', 
                      {'delivery': delivery, 'files_list': files_list, 'file_content': file_content})
    else:
        return HTTP_401_UNAUTHORIZED_RESPONSE

@login_required
def explore(request, iddelivery):
    if(len(request.user.teacher_set.all()) > 0): # if an authenticated user "accidentally" access this section, he doesn't get an exception
        if(os.path.exists(os.path.join(managepath.get_instance().get_temporary_files_path(), str(iddelivery)))):
            shutil.rmtree(os.path.join(managepath.get_instance().get_temporary_files_path(), str(iddelivery)))
        return browse(request, iddelivery)
    else:
        return HTTP_401_UNAUTHORIZED_RESPONSE

@login_required
def detail(request, iddelivery):
    if(len(request.user.teacher_set.all()) > 0): # if an authenticated user "accidentally" access this section, he doesn't get an exception
        delivery = Delivery.objects.get(pk=iddelivery);
        correction = Correction.objects.filter(delivery=delivery)
        return render(request, 'delivery/deliverydetail.html', {'delivery': delivery, 'correction':correction})
    else:
        return HTTP_401_UNAUTHORIZED_RESPONSE

