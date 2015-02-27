from django.forms import ModelForm, IntegerField
from .models import ResponseCapability


class ResponseCapabilityForm(ModelForm):

    class Meta:
        model = ResponseCapability
        exclude = ['firestation']