from django import forms
from .models import Hub, Link, Satellite
from django.contrib.contenttypes.models import ContentType
from django.forms import formset_factory

class HubForm(forms.ModelForm):
    class Meta:
        model = Hub
        fields = ['name', 'description', 'business_keys']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'business_keys': forms.TextInput(attrs={'class': 'form-control'}),
        }

class LinkForm(forms.ModelForm):
    class Meta:
        model = Link
        fields = ['name', 'hubs', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'hubs': forms.CheckboxSelectMultiple,
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class SatelliteForm(forms.ModelForm):
    parent = forms.ChoiceField(label="Parent (Hub or Link)")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Popula o campo 'parent' com todos os Hubs e Links existentes
        hubs = Hub.objects.all()
        links = Link.objects.all()
        hub_content_type = ContentType.objects.get_for_model(Hub)
        link_content_type = ContentType.objects.get_for_model(Link)

        self.fields['parent'].choices = [
            (f"{hub_content_type.id}-{hub.id}", f"Hub: {hub.name}") for hub in hubs
        ] + [
            (f"{link_content_type.id}-{link.id}", f"Link: {link.name}") for link in links
        ]
        self.fields['parent'].widget.attrs.update({'class': 'form-select'})
        self.fields['attributes'].required = False

    class Meta:
        model = Satellite
        fields = ['name', 'attributes']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'attributes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class AttributeForm(forms.Form):
    name = forms.CharField(
        label='Nome do atributo', 
        max_length=100, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        error_messages={'required': 'O nome do atributo é obrigatório.'}
    )
    tipo = forms.ChoiceField(
        label='Tipo',
        choices=[('string', 'String'), ('int', 'Inteiro'), ('float', 'Decimal'), ('date', 'Data'), ('bool', 'Booleano')],
        widget=forms.Select(attrs={'class': 'form-select'})
    )

AttributeFormSet = formset_factory(AttributeForm, extra=1, can_delete=True) 