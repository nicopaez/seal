from django.forms import ModelForm
from seal.model.course import Course

class CourseForm(ModelForm):
    class Meta:
        model = Course
    