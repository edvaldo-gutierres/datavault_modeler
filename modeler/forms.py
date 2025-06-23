from django import forms
from .models import Hub, Link, Satellite, Project
from django.contrib.contenttypes.models import ContentType

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class HubForm(forms.ModelForm):
    class Meta:
        model = Hub
        fields = ['project', 'name', 'business_key', 'load_date', 'record_source']
        widgets = {
            'project': forms.HiddenInput(),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'business_key': forms.TextInput(attrs={'class': 'form-control'}),
            'load_date': forms.TextInput(attrs={'class': 'form-control'}),
            'record_source': forms.TextInput(attrs={'class': 'form-control'})
        }

class LinkForm(forms.ModelForm):
    class Meta:
        model = Link
        fields = ['project', 'name', 'hubs', 'load_date', 'record_source']
        widgets = {
            'project': forms.HiddenInput(),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'hubs': forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
            'load_date': forms.TextInput(attrs={'class': 'form-control'}),
            'record_source': forms.TextInput(attrs={'class': 'form-control'})
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'initial' in kwargs and 'project' in kwargs['initial']:
            project = kwargs['initial']['project']
            self.fields['hubs'].queryset = Hub.objects.filter(project=project)

class AttributeForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nome do atributo'
        })
    )
    tipo = forms.ChoiceField(
        choices=[
            ('string', 'String'),
            ('integer', 'Integer'),
            ('decimal', 'Decimal'),
            ('datetime', 'DateTime'),
            ('boolean', 'Boolean')
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )

class SatelliteForm(forms.ModelForm):
    parent = forms.ChoiceField(
        choices=[],
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Hub ou Link Pai'
    )

    class Meta:
        model = Satellite
        fields = ['project', 'name', 'load_date', 'record_source']
        widgets = {
            'project': forms.HiddenInput(),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'load_date': forms.TextInput(attrs={'class': 'form-control'}),
            'record_source': forms.TextInput(attrs={'class': 'form-control'})
        }
        labels = {
            'load_date': 'Data de Carga',
            'record_source': 'Fonte do Registro'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'initial' in kwargs and 'project' in kwargs['initial']:
            project = kwargs['initial']['project']
            # Busca Hubs do projeto
            hub_ct = ContentType.objects.get_for_model(Hub)
            hubs = Hub.objects.filter(project=project)
            hub_choices = [(f"{hub_ct.id}-{hub.id}", f"Hub: {hub.name}") for hub in hubs]
            
            # Busca Links do projeto
            link_ct = ContentType.objects.get_for_model(Link)
            links = Link.objects.filter(project=project)
            link_choices = [(f"{link_ct.id}-{link.id}", f"Link: {link.name}") for link in links]
            
            # Combina as escolhas
            self.fields['parent'].choices = [('', '-- Selecione --')] + hub_choices + link_choices 