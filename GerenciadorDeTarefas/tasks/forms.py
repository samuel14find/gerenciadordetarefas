from django import forms
from django.forms import inlineformset_factory
from .models import Tarefa, Etapa, CategoriaDeTarefa

class TarefaForm(forms.ModelForm):
    class Meta:
        model = Tarefa
        fields = ['titulo', 'descricao', 'categoria', 'data_inicio', 'data_conclusao', 'status', 'is_foco_atual']
        widgets = {
            'data_inicio': forms.DateInput(attrs={'type': 'date'}),
            'data_conclusao': forms.DateInput(attrs={'type': 'date'}),
            'descricao': forms.Textarea(attrs={'rows': 3}),
        }

# FormSet para gerenciar as etapas (Checklist) junto com a tarefa
EtapaFormSet = inlineformset_factory(
    Tarefa, 
    Etapa, 
    fields=('descricao', 'concluida'),
    extra=1,            # Exibe 1 campo extra vazio
    can_delete=True     # Permite deletar etapas
)

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = CategoriaDeTarefa
        fields = ['nome', 'cor']
        widgets = {
            'cor': forms.TextInput(attrs={'type': 'color'}),
        }

class CSVUploadForm(forms.Form):
    arquivo_csv = forms.FileField(label='Selecione o arquivo CSV')
