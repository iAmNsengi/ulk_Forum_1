from django import forms
from froala_editor.widgets import FroalaEditor
from .models import Post

class PostForm(forms.Form):
    post = forms.CharField(widget=FroalaEditor(theme='dark'))

    class Meta:
        model = Post
        fields = ('post',)