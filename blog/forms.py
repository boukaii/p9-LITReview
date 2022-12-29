from django import forms
from . import models


class LoginForm(forms.Form):
    username = forms.CharField(max_length=63, label='Nom d’utilisateur')
    password = forms.CharField(max_length=63, widget=forms.PasswordInput, label='Mot de passe')


class TicketForm(forms.ModelForm):
    class Meta:
        model = models.Ticket
        fields = ['titre', 'description', 'image']


class ReviewForm(forms.ModelForm):
    choice_value = [('1', '- 1'), ('2', '- 2'), ('3', '- 3'), ('4', '- 4'), ('5', '- 5')]
    rating = forms.ChoiceField(label='Note', widget=forms.RadioSelect, choices=choice_value)
    edit_review = forms.BooleanField(widget=forms.HiddenInput, initial=True)

    class Meta:
        model = models.Review
        fields = ['headline', 'rating', 'body', ]
