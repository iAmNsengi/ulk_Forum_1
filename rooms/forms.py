from django import forms
from froala_editor.widgets import FroalaEditor
from .models import Message

class MessageForm(forms.Form):
    post = forms.CharField(widget=FroalaEditor(attrs = {'theme':'dark','id':'chatMessageInput'}))

    class Meta:
        model = Message
        fields = ('content',)