from django.shortcuts import render, redirect, get_object_or_404
from .models import Hub, Link, Satellite
from .forms import HubForm, LinkForm, SatelliteForm, AttributeFormSet
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from django.http import HttpResponse
import re

# Create your views here.

def index(request):
    hubs = Hub.objects.all()
    links = Link.objects.all()
    satellites = Satellite.objects.all().select_related('content_type')
    return render(request, "modeler/index.html", {
        "hubs": hubs, 
        "links": links,
        "satellites": satellites
    })

def create_hub(request):
    if request.method == 'POST':
        form = HubForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = HubForm()
    return render(request, 'modeler/create_hub.html', {'form': form})

def update_hub(request, pk):
    hub = get_object_or_404(Hub, pk=pk)
    if request.method == 'POST':
        form = HubForm(request.POST, instance=hub)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = HubForm(instance=hub)
    return render(request, 'modeler/update_hub.html', {'form': form, 'hub': hub})

def delete_hub(request, pk):
    hub = get_object_or_404(Hub, pk=pk)
    if request.method == 'POST':
        hub.delete()
        return redirect('index')
    return render(request, 'modeler/hub_confirm_delete.html', {'hub': hub})

def create_link(request):
    if request.method == 'POST':
        form = LinkForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = LinkForm()
    
    if Hub.objects.count() < 2:
        # Você poderia usar o sistema de mensagens do Django para um aviso mais elegante
        return render(request, 'modeler/error_not_enough_hubs.html')

    return render(request, 'modeler/create_link.html', {'form': form})

def create_satellite(request):
    if request.method == 'POST':
        form = SatelliteForm(request.POST)
        formset = AttributeFormSet(request.POST, prefix='attributes')
        if form.is_valid() and formset.is_valid():
            satellite = form.save(commit=False)
            parent_str = form.cleaned_data['parent']
            content_type_id, object_id = parent_str.split('-')
            satellite.content_type = ContentType.objects.get_for_id(content_type_id)
            satellite.object_id = object_id
            # Monta a string de atributos
            attributes_list = []
            for f in formset.cleaned_data:
                if f and not f.get('DELETE', False):
                    name = f['name'].strip()
                    tipo = f['tipo'].strip()
                    attributes_list.append(f'{name}:{tipo}')
            satellite.attributes = ', '.join(attributes_list)
            satellite.save()
            messages.success(request, 'Satellite criado com sucesso!')
            return redirect('index')
    else:
        form = SatelliteForm()
        formset = AttributeFormSet(prefix='attributes')

    if not form.fields['parent'].choices:
         return render(request, 'modeler/error_no_parents.html')

    return render(request, 'modeler/create_satellite.html', {'form': form, 'formset': formset})

def update_satellite(request, pk):
    satellite = get_object_or_404(Satellite, pk=pk)
    if request.method == 'POST':
        print('POST recebido para update_satellite')
        form = SatelliteForm(request.POST, instance=satellite)
        formset = AttributeFormSet(request.POST, prefix='attributes')
        print('Form válido?', form.is_valid())
        print('Formset válido?', formset.is_valid())
        print('Erros do form:', form.errors)
        print('Erros do formset:', formset.errors)
        if form.is_valid() and formset.is_valid():
            satellite_instance = form.save(commit=False)
            parent_str = form.cleaned_data['parent']
            content_type_id, object_id = parent_str.split('-')
            satellite_instance.content_type = ContentType.objects.get_for_id(content_type_id)
            satellite_instance.object_id = object_id
            # Monta a string de atributos
            attributes_list = []
            for f in formset.cleaned_data:
                if f and not f.get('DELETE', False):
                    name = f['name'].strip()
                    tipo = f['tipo'].strip()
                    attributes_list.append(f'{name}:{tipo}')
            satellite_instance.attributes = ', '.join(attributes_list)
            satellite_instance.save()
            messages.success(request, 'Satellite atualizado com sucesso!')
            return redirect('index')
        else:
            print('Formulário ou formset inválido!')
            return render(request, 'modeler/update_satellite.html', {'form': form, 'formset': formset, 'satellite': satellite})
    else:
        # Define o valor inicial para o campo 'parent'
        initial_parent = f"{satellite.content_type.id}-{satellite.object_id}"
        form = SatelliteForm(instance=satellite, initial={'parent': initial_parent})
        # Preenche o formset com os atributos existentes
        attributes = []
        if satellite.attributes:
            for attr in satellite.attributes.split(','):
                attr = attr.strip()
                if ':' in attr:
                    name, tipo = [a.strip() for a in attr.split(':', 1)]
                else:
                    name, tipo = attr, 'string'
                attributes.append({'name': name, 'tipo': tipo})
        if attributes:
            formset = AttributeFormSet(initial=attributes, prefix='attributes')
        else:
            formset = AttributeFormSet(prefix='attributes')

    return render(request, 'modeler/update_satellite.html', {'form': form, 'formset': formset, 'satellite': satellite})

def delete_satellite(request, pk):
    satellite = get_object_or_404(Satellite, pk=pk)
    if request.method == 'POST':
        satellite.delete()
        return redirect('index')
    return render(request, 'modeler/satellite_confirm_delete.html', {'satellite': satellite})

def update_link(request, pk):
    link = get_object_or_404(Link, pk=pk)
    if request.method == 'POST':
        form = LinkForm(request.POST, instance=link)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = LinkForm(instance=link)
    return render(request, 'modeler/update_link.html', {'form': form, 'link': link})

def delete_link(request, pk):
    link = get_object_or_404(Link, pk=pk)
    if request.method == 'POST':
        link.delete()
        return redirect('index')
    return render(request, 'modeler/link_confirm_delete.html', {'link': link})

def visualize_model(request):
    try:
        hubs = Hub.objects.all()
        links = Link.objects.prefetch_related('hubs').all()
        satellites = Satellite.objects.select_related('content_type').all()

        hub_name_map = {h.id: h.name for h in hubs}
        link_name_map = {l.id: l.name for l in links}

        mermaid_lines = ['erDiagram']

        # Adiciona as entidades Hub, Link e Satellite
        for hub in hubs:
            mermaid_lines.append(f'    "{hub.name}" {{')
            safe_hub_name = hub.name.replace(' ', '_')
            mermaid_lines.append(f'        string HK_{safe_hub_name}')
            keys = [key.strip() for key in hub.business_keys.split(',') if key.strip()]
            for i, key in enumerate(keys):
                mermaid_lines.append(f'        string key_{i+1} "{key}"')
            mermaid_lines.append(f'        datetime load_date')
            mermaid_lines.append(f'        string record_source')
            mermaid_lines.append('    }')

        for link in links:
            mermaid_lines.append(f'    "{link.name}" {{')
            safe_link_name = link.name.replace(' ', '_')
            mermaid_lines.append(f'        string HK_{safe_link_name}')
            for hub in link.hubs.all():
                safe_hub_name = hub.name.replace(' ', '_')
                mermaid_lines.append(f'        string HK_{safe_hub_name}')
            mermaid_lines.append(f'        datetime load_date')
            mermaid_lines.append(f'        string record_source')
            mermaid_lines.append('    }')
        
        for satellite in satellites:
            mermaid_lines.append(f'    "{satellite.name}" {{')
            # FK para o pai
            parent_fk = None
            if satellite.content_type.model == 'hub':
                parent_name = hub_name_map.get(satellite.object_id)
                if parent_name:
                    safe_parent = re.sub(r'\W+', '_', parent_name)
                    parent_fk = f'        string HK_{safe_parent}'
            elif satellite.content_type.model == 'link':
                parent_name = link_name_map.get(satellite.object_id)
                if parent_name:
                    safe_parent = re.sub(r'\W+', '_', parent_name)
                    parent_fk = f'        string HK_{safe_parent}'
            if parent_fk:
                mermaid_lines.append(parent_fk)
            # Adiciona o HK_DIFF
            mermaid_lines.append(f'        string HK_DIFF')
            attributes = [attr.strip() for attr in satellite.attributes.split(',') if attr.strip()]
            for i, attr in enumerate(attributes):
                if ':' in attr:
                    name, tipo = [a.strip() for a in attr.split(':', 1)]
                else:
                    name, tipo = attr, 'string'
                safe_name = name.replace(' ', '_')
                mermaid_lines.append(f'        {tipo} {safe_name} "{name}"')
            mermaid_lines.append(f'        datetime load_date')
            mermaid_lines.append(f'        string record_source')
            mermaid_lines.append('    }')

        # Adiciona as relações
        for link in links:
            for hub in link.hubs.all():
                mermaid_lines.append(f'    "{hub.name}" ||--|{{ "{link.name}" : "connects"')

        for satellite in satellites:
            parent_name = None
            if satellite.content_type.model == 'hub':
                parent_name = hub_name_map.get(satellite.object_id)
            elif satellite.content_type.model == 'link':
                parent_name = link_name_map.get(satellite.object_id)
            
            if parent_name:
                mermaid_lines.append(f'    "{parent_name}" ||--o{{ "{satellite.name}" : "describes"')

        mermaid_data = "\n".join(mermaid_lines)
        error_message = None
    except Exception as e:
        mermaid_data = ''
        error_message = f"Ocorreu um erro ao gerar o diagrama: {e}"

    return render(request, 'modeler/visualize.html', {
        'mermaid_data': mermaid_data,
        'error_message': error_message
    })

def visualize_classdiagram(request):
    hubs = Hub.objects.all()
    links = Link.objects.prefetch_related('hubs').all()
    satellites = Satellite.objects.select_related('content_type').all()

    hub_name_map = {h.id: h.name for h in hubs}
    link_name_map = {l.id: l.name for l in links}

    mermaid_lines = ['classDiagram']
    classdefs = [
        'classDef hub fill:#cfe2ff,stroke:#084298,stroke-width:2px;',
        'classDef link fill:#fff3cd,stroke:#b45309,stroke-width:2px;',
        'classDef sat fill:#fff9db,stroke:#b6a100,stroke-width:2px;'
    ]
    # Hubs
    for hub in hubs:
        safe_name = re.sub(r'\W+', '_', hub.name)
        mermaid_lines.append(f'class {safe_name} {{')
        mermaid_lines.append(f'    +HK_{safe_name}')
        keys = [key.strip() for key in hub.business_keys.split(',') if key.strip()]
        for i, key in enumerate(keys):
            safe_key = re.sub(r'\W+', '_', key)
            mermaid_lines.append(f'    +key_{i+1}_{safe_key}')
        mermaid_lines.append(f'    +load_date')
        mermaid_lines.append(f'    +record_source')
        mermaid_lines.append('}')
        mermaid_lines.append(f'class {safe_name} hub;')
    # Links
    for link in links:
        safe_name = re.sub(r'\W+', '_', link.name)
        mermaid_lines.append(f'class {safe_name} {{')
        for hub in link.hubs.all():
            safe_hub = re.sub(r'\W+', '_', hub.name)
            mermaid_lines.append(f'    +HK_{safe_hub}')
        mermaid_lines.append(f'    +load_date')
        mermaid_lines.append(f'    +record_source')
        mermaid_lines.append('}')
        mermaid_lines.append(f'class {safe_name} link;')
    # Satellites
    for satellite in satellites:
        safe_name = re.sub(r'\W+', '_', satellite.name)
        mermaid_lines.append(f'class {safe_name} {{')
        # FK para o pai
        parent_fk = ''
        if satellite.content_type.model == 'hub':
            parent_name = hub_name_map.get(satellite.object_id)
            if parent_name:
                safe_parent = re.sub(r'\W+', '_', parent_name)
                parent_fk = f'HK_{safe_parent}'
        elif satellite.content_type.model == 'link':
            parent_name = link_name_map.get(satellite.object_id)
            if parent_name:
                safe_parent = re.sub(r'\W+', '_', parent_name)
                parent_fk = f'HK_{safe_parent}'
        if parent_fk:
            mermaid_lines.append(f'    +{parent_fk}')
        mermaid_lines.append(f'    +HK_DIFF')
        attributes = [attr.strip() for attr in satellite.attributes.split(',') if attr.strip()]
        for attr in attributes:
            if ':' in attr:
                name, tipo = [a.strip() for a in attr.split(':', 1)]
            else:
                name, tipo = attr, 'string'
            safe_attr = re.sub(r'\W+', '_', name)
            mermaid_lines.append(f'    +{safe_attr}')
        mermaid_lines.append(f'    +load_date')
        mermaid_lines.append(f'    +record_source')
        mermaid_lines.append('}')
        mermaid_lines.append(f'class {safe_name} sat;')
    # classDef antes das associações
    mermaid_lines += classdefs
    # Relações
    for link in links:
        safe_link = re.sub(r'\W+', '_', link.name)
        for hub in link.hubs.all():
            safe_hub = re.sub(r'\W+', '_', hub.name)
            mermaid_lines.append(f'{safe_hub} --> {safe_link}')
    for satellite in satellites:
        safe_sat = re.sub(r'\W+', '_', satellite.name)
        parent = None
        if satellite.content_type.model == 'hub':
            parent = hub_name_map.get(satellite.object_id)
        elif satellite.content_type.model == 'link':
            parent = link_name_map.get(satellite.object_id)
        if parent:
            safe_parent = re.sub(r'\W+', '_', parent)
            mermaid_lines.append(f'{safe_parent} --> {safe_sat}')
    mermaid_data = "\n".join(mermaid_lines)
    return render(request, 'modeler/visualize_classdiagram.html', {'mermaid_data': mermaid_data})
