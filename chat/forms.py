from django import forms

class ChatForm(forms.Form):
    text = forms.CharField(label="Message", widget=forms.TextInput(attrs={
        "placeholder": "Type a message…",
        "class": "w-full"
    }))
