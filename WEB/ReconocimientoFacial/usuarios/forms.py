from django import forms
from .models import Persona

class PersonaForm(forms.ModelForm):
    class Meta:
        model = Persona
        # fields = ['nombres', 'apellidos', 'documento', 'foto', 'contacto', 'cargo']
        fields = '__all__' # usar todos los campos deñ formulario
