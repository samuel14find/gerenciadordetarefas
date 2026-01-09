from django import forms

class FormularioComentario(forms.Form):
  nome = forms.CharField()
  comentario = forms.CharField(
     widget=forms.Textarea( attrs={"rows": "6", "cols": "50"}))