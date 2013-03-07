from django.http import HttpResponseRedirect
from django.shortcuts import render
from seal.model import Delivery
from django.template.context import RequestContext
from seal.forms.correction import CorrectionForm
from seal.model import Correction
from django.contrib.auth.decorators import login_required
from seal.model.mail import Mail
from seal.model.teacher import Teacher
from seal.model.innings import Innings

PATHREDIRECTINDEX = "/teacher/correction/edit/%s/%s"
#PATHOK = "/teacher/delivery/list/%s"
SUBJECTEMAIL = "You have a correction to see on SEAL"
BODYEMAIL = "You have a correction to see in delivery: %s from practice: %s. Coment: %s. Grade: %s"

@login_required
def index(request, iddelivery, previus):  
    delivery = Delivery.objects.get(pk=iddelivery)
    correction = Correction.objects.filter(delivery=delivery)
    corrector = ""
    if len(correction) != 0:
        return HttpResponseRedirect(PATHREDIRECTINDEX % (str(correction[0].pk),str(previus)))
    else:
        if (request.method == 'POST'):
            correction = Correction(delivery=delivery)
            teacher = Teacher.objects.get(user=request.user)
            correction.corrector = teacher
            corrector = correction.corrector
            form = CorrectionForm(request.POST, instance=correction)
            if (form.is_valid()):
                form.save()
                mail = Mail()
                mail.save_mail(SUBJECTEMAIL, BODYEMAIL % (str(correction.delivery.pk), correction.delivery.practice.uid, form.data['publicComent'], form.data['grade']), correction.delivery.student.user.email)
                if (previus == str(1)):
                    PATHOK = "/"
                elif (previus == str(3)):
                    PATHOK = "/teacher/delivery/list/%s" % (str(correction.delivery.practice.pk))
                elif (previus == str(4)):
                    inning = correction.delivery.student.innings.filter(course=correction.delivery.practice.course)[0]
                    PATHOK = "/teacher/students/listdeliveries/%s/%s/" % (str(correction.delivery.student.pk), inning.pk)
                return HttpResponseRedirect(PATHOK)

        else:
            form = CorrectionForm()
        return render(request, 'correction/index.html', {'form': form, 'delivery': delivery, 'corrector': corrector}, context_instance=RequestContext(request))

@login_required
def editcorrection(request, idcorrection,previus):
    correction = Correction.objects.get(pk=idcorrection)
    if (request.method == 'POST'):
        teacher = Teacher.objects.get(user=request.user)
        correction.corrector = teacher
        form = CorrectionForm(request.POST, instance=correction)
        if (form.is_valid()):
            form_edit = form.save(commit=False)
            form_edit.save()
            mail = Mail()
            mail.save_mail(SUBJECTEMAIL, BODYEMAIL % (str(correction.delivery.pk), correction.delivery.practice.uid, form.data['publicComent'], form.data['grade']), correction.delivery.student.user.email)
            if (previus == str(1)):
                PATHOK = "/"
            elif (previus == str(3)):
                PATHOK = "/teacher/delivery/list/%s" % (str(correction.delivery.practice.pk))
            elif (previus == str(4)):
                inning = correction.delivery.student.innings.filter(course=correction.delivery.practice.course)[0]
                PATHOK = "/teacher/students/listdeliveries/%s/%s/" % (str(correction.delivery.student.pk), inning.pk)
            return HttpResponseRedirect(PATHOK)

    else:    
        form = CorrectionForm(instance=correction)
    return render(request, 'correction/index.html',
                  {'form': form, 'delivery': correction.delivery, 'corrector': correction.corrector},
                  context_instance=RequestContext(request))
