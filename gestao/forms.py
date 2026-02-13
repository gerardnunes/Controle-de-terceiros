from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Local, Chamada, Presenca

class UsuarioRegistroForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'cpf', 'telefone', 'endereco', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].label = 'Nome'
        self.fields['first_name'].required = True

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'usuario'
        user.aprovado = False
        if commit:
            user.save()
        return user


    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.role = 'usuario'
        user.aprovado = False
        if commit:
            user.save()
        return user

class UsuarioForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'cpf', 'telefone', 'endereco', 'role', 'aprovado']
        # Para encarregado/gestor criar/editar usuários

class LocalForm(forms.ModelForm):
    class Meta:
        model = Local
        fields = ['nome', 'descricao']

class PresencaForm(forms.Form):
    # Formulário dinâmico para cada usuário em uma chamada
    pass

class ChamadaForm(forms.ModelForm):
    class Meta:
        model = Chamada
        fields = ['data']
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date'}),
        }

class RelatorioForm(forms.Form):
    data_inicio = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    data_fim = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    # Para gestor, pode adicionar filtro por encarregado/gerente