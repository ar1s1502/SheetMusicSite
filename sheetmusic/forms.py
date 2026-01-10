from django.forms import ModelForm, Textarea, TextInput
from .models import Request, Feedback

class RequestForm(ModelForm):
    class Meta:
        model = Request
        exclude = ['responded', 'created_at',]
        labels = {
            'arrangement_name': 'Arrangement Name',
            'original_artist': 'Original Artist',
            'use_context': 'Arrangement Context',
            'additional_info': 'Additional Info',
        }
        widgets = {
            'name': TextInput(attrs={'class': 'form-control'}),
            'email': TextInput(attrs={'class':'form-control', 'placeholder': 'yourname@example.com'}),
            'arrangement_name': TextInput(attrs = {'class':'form-control', 'placeholder': 'Blackbird'}),
            'original_artist': TextInput(attrs = {'class':'form-control', 'placeholder': 'The Beatles'}),
            'use_context': Textarea(attrs = {'class':'form-control', 'placeholder': """What is the instrumentation? (SATB, SSA, Piano Trio, etc.)
Is your ensemble beginner/intermediate/advanced?
How do you want to use this arrangement? 
(Links to videos or sheet music of repetoire previously done by your group are very helpful)"""}),
            'additional_info': Textarea(attrs = {'class':'form-control', 'rows':2, 'placeholder': 'What else should I know for this project?'}),
        }

class FeedbackForm(ModelForm):
    class Meta:
        model = Feedback
        exclude = ['responded', 'created_at']
        labels = {
            'subject': 'Subject',
            'context': 'Context'
        }
        widgets = {
            'name': TextInput(attrs={'class': 'form-control'}),
            'email': TextInput(attrs={'class':'form-control', 'placeholder': 'yourname@example.com'}),
            'subject': TextInput(attrs={'class':'form-control', 'placeholder': 'eg. Issue with sheet music order'}),
            'context': Textarea(attrs = {'class':'form-control', })
        }
        