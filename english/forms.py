from django import forms
from .models import Image, Video
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
            'image_name',
            'created_time',
            'capture_location',
            'description',

        )

    description = forms.Textarea()
    capture_location = forms.GenericIPAddressField(initial=extract_ip())
    created_time = forms.DateTimeField(initial=datetime.datetime.now())
    image_name = forms.FileField(widget=forms.FileInput(attrs={'accept': 'image/*', 'multiple':True}))

class VideoForm(forms.ModelForm):
    """Form for the video model"""
    class Meta:
        model = Video
        fields = (
            'video_name',
            'created_time',
            'capture_location',
            'description',

        )

    description = forms.Textarea()
    capture_location = forms.GenericIPAddressField(initial=extract_ip())
    created_time = forms.DateTimeField(initial=datetime.datetime.now())
    video_name = forms.FileField(widget=forms.FileInput(attrs={'accept': 'video/*', 'multiple':True}))
