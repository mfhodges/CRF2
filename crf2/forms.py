from django import forms

class PennKey_Valid_Form(forms.Form):
    username = forms.CharField(label='pennkey', max_length=100)
