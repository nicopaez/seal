from django.http import HttpResponseRedirect
from django.shortcuts import render
from seal.model import Delivery
from django.template.context import RequestContext
from seal.forms.correction import CorrectionForm
from seal.model import Correction

def index(request, iddelivery):  
    delivery = Delivery.objects.get(pk=iddelivery)
    correction = Correction.objects.filter(delivery=delivery)
    if len(correction) != 0: 
        pathredirect = "/correction/edit/" + str(correction[0].pk)
        return HttpResponseRedirect(pathredirect)
    else:
        if (request.method == 'POST'):
            correction = Correction(delivery=delivery)
            form = CorrectionForm(request.POST, instance=correction)
            if (form.is_valid()):
                form.save()
                pathok = "/delivery/listdelivery/" + str(delivery.practice.pk)
                return HttpResponseRedirect(pathok)
        else:
            form = CorrectionForm()
        return render(request, 'correction/index.html', {'form': form, 'delivery': delivery}, context_instance=RequestContext(request))

def editcorrection(request, idcorrection):
    correction = Correction.objects.get(pk=idcorrection)
    if (request.method == 'POST'):
        form = CorrectionForm(request.POST, instance=correction)
        if (form.is_valid()):
            formEdit = form.save(commit=False)
            formEdit.save()
            pathok = "/delivery/listdelivery/" + str(correction.delivery.practice.pk)
            return HttpResponseRedirect(pathok)
    else:    
        form = CorrectionForm(instance=correction)
    return render(request, 'correction/index.html', {'form': form, 'delivery': correction.delivery}, context_instance=RequestContext(request))

def consultcorrection(request, iddelivery):
    delivery = Delivery.objects.get(pk=iddelivery)
    correction = Correction.objects.filter(delivery=delivery)
    return render(request, 'correction/consult.html', {'correction': correction, 'delivery': delivery})