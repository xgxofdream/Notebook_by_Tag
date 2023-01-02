from django import forms
from .models import Image
import datetime

import socket

def extract_ip():
    st = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        st.connect(('10.255.255.255', 1))
        IP = st.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        st.close()
    return IP



class ImageForm(forms.ModelForm):
    """Form for the image model"""

    class Meta:
        model = Image
        fields = (
            'image',
            'title',
            'capture_location',
            'created_time',

        )

    title = forms.CharField(initial='Not specified yet')
    capture_location = forms.GenericIPAddressField(initial=extract_ip())
    created_time = forms.DateTimeField(initial=datetime.datetime.utcnow())
    image = forms.FileField(widget=forms.FileInput(attrs={'accept': 'image/*', 'multiple':True}))