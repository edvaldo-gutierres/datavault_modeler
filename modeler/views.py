from django.shortcuts import render, redirect, get_object_or_404
from .models import Hub, Link, Satellite, Project
from .forms import HubForm, LinkForm, SatelliteForm, AttributeForm
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from django.http import HttpResponse
import re
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.forms import formset_factory

# Formset para criação (com um campo extra)
AttributeFormSet = formset_factory(AttributeForm, extra=1)
# Formset para edição (sem campos extras)
AttributeEditFormSet = formset_factory(AttributeForm, extra=0)

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
    project_id = request.GET.get('project')
    if not project_id:
        return redirect('project_list')
    
    project = get_object_or_404(Project, pk=project_id)
    
    if request.method == 'POST':
        form = HubForm(request.POST)
        if form.is_valid():
            hub = form.save()
            return redirect('project_detail', pk=project.pk)
    else:
        form = HubForm(initial={'project': project.pk})
    
    return render(request, 'modeler/create_hub.html', {'form': form})

def update_hub(request, pk):
    hub = get_object_or_404(Hub, pk=pk)
    if request.method == 'POST':
        form = HubForm(request.POST, instance=hub)
        if form.is_valid():
            hub = form.save()
            messages.success(request, 'Hub atualizado com sucesso!')
            return redirect('project_detail', pk=hub.project.pk)
        else:
            messages.error(request, 'Por favor, corrija os erros no formulário.')
    else:
        form = HubForm(instance=hub)
    return render(request, 'modeler/update_hub.html', {'form': form, 'hub': hub})

def delete_hub(request, pk):
    hub = get_object_or_404(Hub, pk=pk)
    project_id = hub.project.pk
    
    # Verifica se há Links ou Satellites dependentes
    links = hub.links.all()
    satellites = Satellite.objects.filter(
        content_type=ContentType.objects.get_for_model(Hub),
        object_id=hub.id
    )
    
    if request.method == 'POST':
        if 'confirm' in request.POST:
            # Deleta o hub e suas dependências
            hub.delete()
            messages.success(request, 'Hub e seus objetos dependentes foram deletados com sucesso!')
            return redirect('project_detail', pk=project_id)
    
    context = {
        'hub': hub,
        'links': links,
        'satellites': satellites,
    }
    return render(request, 'modeler/hub_confirm_delete.html', context)

def create_link(request):
    project_id = request.GET.get('project')
    if not project_id:
        return redirect('project_list')
    
    project = get_object_or_404(Project, pk=project_id)
    
    if request.method == 'POST':
        form = LinkForm(request.POST)
        if form.is_valid():
            link = form.save()
            return redirect('project_detail', pk=project.pk)
    else:
        form = LinkForm(initial={'project': project.pk})
    
    if Hub.objects.filter(project=project).count() < 2:
        return render(request, 'modeler/error_not_enough_hubs.html')

    return render(request, 'modeler/create_link.html', {'form': form})

def create_satellite(request):
    project_id = request.GET.get('project')
    if not project_id:
        return redirect('project_list')
    
    project = get_object_or_404(Project, pk=project_id)
    
    if request.method == 'POST':
        form = SatelliteForm(request.POST, initial={'project': project.pk})
        formset = AttributeFormSet(request.POST, prefix='attributes')
        if form.is_valid() and formset.is_valid():
            satellite = form.save(commit=False)
            satellite.project = project
            parent_str = form.cleaned_data['parent']
            content_type_id, object_id = parent_str.split('-')
            satellite.content_type = ContentType.objects.get_for_id(int(content_type_id))
            satellite.object_id = object_id
            
            # Converte o formset em um dicionário de atributos
            attributes_dict = {}
            for f in formset.cleaned_data:
                if f and not f.get('DELETE', False):
                    name = f['name'].strip()
                    tipo = f['tipo'].strip()
                    attributes_dict[name] = tipo
            
            satellite.attributes = attributes_dict
            satellite.save()
            messages.success(request, 'Satellite criado com sucesso!')
            return redirect('project_detail', pk=project.pk)
        else:
            if form.errors:
                messages.error(request, 'Por favor, corrija os erros no formulário.')
            if formset.errors:
                messages.error(request, 'Por favor, corrija os erros nos atributos.')
    else:
        form = SatelliteForm(initial={'project': project.pk})
        formset = AttributeFormSet(prefix='attributes')

    if not form.fields['parent'].choices:
        return render(request, 'modeler/error_no_parents.html')

    return render(request, 'modeler/create_satellite.html', {
        'form': form, 
        'formset': formset
    })

def update_satellite(request, pk):
    satellite = get_object_or_404(Satellite, pk=pk)
    if request.method == 'POST':
        form = SatelliteForm(request.POST, instance=satellite, initial={'project': satellite.project})
        formset = AttributeEditFormSet(request.POST, prefix='attributes')
        if form.is_valid() and formset.is_valid():
            satellite_instance = form.save(commit=False)
            parent_str = form.cleaned_data['parent']
            content_type_id, object_id = parent_str.split('-')
            satellite_instance.content_type = ContentType.objects.get_for_id(int(content_type_id))
            satellite_instance.object_id = object_id
            
            # Converte o formset em um dicionário de atributos
            attributes_dict = {}
            for f in formset.cleaned_data:
                if f and not f.get('DELETE', False):
                    name = f['name'].strip()
                    tipo = f['tipo'].strip()
                    attributes_dict[name] = tipo
            
            satellite_instance.attributes = attributes_dict
            satellite_instance.save()
            messages.success(request, 'Satellite atualizado com sucesso!')
            return redirect('project_detail', pk=satellite.project.pk)
        else:
            if form.errors:
                messages.error(request, 'Por favor, corrija os erros no formulário.')
            if formset.errors:
                messages.error(request, 'Por favor, corrija os erros nos atributos.')
    else:
        # Obtém o content_type e object_id do parent atual
        if satellite.content_type and satellite.object_id:
            initial_parent = f"{satellite.content_type.id}-{satellite.object_id}"
        else:
            messages.error(request, 'Este Satellite não tem um Hub ou Link pai definido.')
            return redirect('project_detail', pk=satellite.project.pk)
        
        form = SatelliteForm(instance=satellite, initial={'parent': initial_parent, 'project': satellite.project})
        
        # Inicializa o formset com os atributos existentes
        initial_attributes = [
            {'name': name, 'tipo': tipo}
            for name, tipo in satellite.attributes.items()
        ] if satellite.attributes else []
        
        formset = AttributeEditFormSet(
            prefix='attributes',
            initial=initial_attributes
        )

    return render(request, 'modeler/update_satellite.html', {
        'form': form,
        'formset': formset,
        'satellite': satellite
    })

def delete_satellite(request, pk):
    satellite = get_object_or_404(Satellite, pk=pk)
    project_id = satellite.project.pk
    
    if request.method == 'POST':
        if 'confirm' in request.POST:
            satellite.delete()
            messages.success(request, 'Satellite deletado com sucesso!')
            return redirect('project_detail', pk=project_id)
    
    return render(request, 'modeler/satellite_confirm_delete.html', {'satellite': satellite})

def update_link(request, pk):
    link = get_object_or_404(Link, pk=pk)
    if request.method == 'POST':
        form = LinkForm(request.POST, instance=link, initial={'project': link.project})
        if form.is_valid():
            link = form.save()
            messages.success(request, 'Link atualizado com sucesso!')
            return redirect('project_detail', pk=link.project.pk)
        else:
            messages.error(request, 'Por favor, corrija os erros no formulário.')
    else:
        form = LinkForm(instance=link, initial={'project': link.project})
    return render(request, 'modeler/update_link.html', {'form': form, 'link': link})

def delete_link(request, pk):
    link = get_object_or_404(Link, pk=pk)
    project_id = link.project.pk
    
    # Verifica se há Satellites dependentes
    satellites = Satellite.objects.filter(
        content_type=ContentType.objects.get_for_model(Link),
        object_id=link.id
    )
    
    if request.method == 'POST':
        if 'confirm' in request.POST:
            # Deleta o link e seus satellites
            link.delete()
            messages.success(request, 'Link e seus satellites foram deletados com sucesso!')
            return redirect('project_detail', pk=project_id)
    
    context = {
        'link': link,
        'satellites': satellites,
    }
    return render(request, 'modeler/link_confirm_delete.html', context)

def visualize(request):
    try:
        project_id = request.GET.get('project')
        if not project_id:
            return redirect('project_list')
        
        project = get_object_or_404(Project, pk=project_id)
        hubs = Hub.objects.filter(project=project)
        links = Link.objects.filter(project=project).prefetch_related('hubs')
        satellites = Satellite.objects.filter(project=project).select_related('content_type')

        hub_name_map = {h.id: h.name for h in hubs}
        link_name_map = {l.id: l.name for l in links}

        mermaid_lines = ['erDiagram']
        
        # Adiciona as definições de estilo
        mermaid_lines.extend([
            '%% Style Definitions',
            'classDef hubStyle fill:#1a1a1a,stroke:#60a5fa,stroke-width:2px,color:#60a5fa',
            'classDef linkStyle fill:#1a1a1a,stroke:#fb923c,stroke-width:2px,color:#fb923c',
            'classDef satelliteStyle fill:#1a1a1a,stroke:#facc15,stroke-width:2px,color:#facc15'
        ])

        # Adiciona as entidades Hub
        for hub in hubs:
            safe_name = re.sub(r'\W+', '_', hub.name)
            mermaid_lines.append(f'    H_{safe_name}:::hubStyle {{')
            mermaid_lines.append(f'        string HK_{safe_name}')
            mermaid_lines.append(f'        string {hub.business_key}')
            mermaid_lines.append(f'        datetime load_date')
            mermaid_lines.append(f'        string record_source')
            mermaid_lines.append('    }')

        # Adiciona as entidades Link
        for link in links:
            safe_name = re.sub(r'\W+', '_', link.name)
            mermaid_lines.append(f'    L_{safe_name}:::linkStyle {{')
            mermaid_lines.append(f'        string HK_{safe_name}')
            for hub in link.hubs.all():
                safe_hub = re.sub(r'\W+', '_', hub.name)
                mermaid_lines.append(f'        string HK_{safe_hub}')
            mermaid_lines.append(f'        datetime load_date')
            mermaid_lines.append(f'        string record_source')
            mermaid_lines.append('    }')
        
        # Adiciona as entidades Satellite
        for satellite in satellites:
            safe_name = re.sub(r'\W+', '_', satellite.name)
            mermaid_lines.append(f'    S_{safe_name}:::satelliteStyle {{')
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
            
            # Adiciona o HK_DIFF e campos default
            mermaid_lines.append(f'        string HK_DIFF')
            mermaid_lines.append(f'        datetime valid_from')
            mermaid_lines.append(f'        datetime valid_to')
            mermaid_lines.append(f'        boolean is_current')
            
            # Adiciona os atributos específicos
            for name, tipo in satellite.attributes.items():
                safe_name = name.replace(' ', '_')
                mermaid_lines.append(f'        {tipo} {safe_name} "{name}"')
            
            # Adiciona os campos de auditoria
            mermaid_lines.append(f'        datetime load_date')
            mermaid_lines.append(f'        string record_source')
            mermaid_lines.append('    }')

        # Adiciona as relações
        for link in links:
            safe_link = re.sub(r'\W+', '_', link.name)
            for hub in link.hubs.all():
                safe_hub = re.sub(r'\W+', '_', hub.name)
                mermaid_lines.append(f'    H_{safe_hub} ||--|{{ L_{safe_link} : "connects"')

        for satellite in satellites:
            safe_sat = re.sub(r'\W+', '_', satellite.name)
            parent = None
            if satellite.content_type.model == 'hub':
                parent = hub_name_map.get(satellite.object_id)
            elif satellite.content_type.model == 'link':
                parent = link_name_map.get(satellite.object_id)
            if parent:
                safe_parent = re.sub(r'\W+', '_', parent)
                if satellite.content_type.model == 'hub':
                    mermaid_lines.append(f'    H_{safe_parent} ||--o{{ S_{safe_sat} : "describes"')
                else:
                    mermaid_lines.append(f'    L_{safe_parent} ||--o{{ S_{safe_sat} : "describes"')

        mermaid_data = "\n".join(mermaid_lines)
        error_message = None
    except Exception as e:
        mermaid_data = ''
        error_message = f"Ocorreu um erro ao gerar o diagrama: {e}"
        project = None

    return render(request, 'modeler/visualize.html', {
        'mermaid_data': mermaid_data,
        'error_message': error_message,
        'project': project
    })

def visualize_classdiagram(request):
    try:
        project_id = request.GET.get('project')
        if not project_id:
            return redirect('project_list')
        
        project = get_object_or_404(Project, pk=project_id)
        hubs = Hub.objects.filter(project=project)
        links = Link.objects.filter(project=project).prefetch_related('hubs')
        satellites = Satellite.objects.filter(project=project).select_related('content_type')

        hub_name_map = {h.id: h.name for h in hubs}
        link_name_map = {l.id: l.name for l in links}

        mermaid_lines = ['classDiagram']
        
        # Adiciona as definições de estilo
        mermaid_lines.extend([
            '%% Style Definitions',
            'classDef hubStyle fill:#1a1a1a,stroke:#60a5fa,stroke-width:2px,color:#60a5fa',
            'classDef linkStyle fill:#1a1a1a,stroke:#fb923c,stroke-width:2px,color:#fb923c',
            'classDef satelliteStyle fill:#1a1a1a,stroke:#facc15,stroke-width:2px,color:#facc15'
        ])

        # Hubs
        for hub in hubs:
            safe_name = re.sub(r'\W+', '_', hub.name)
            mermaid_lines.append(f'class H_{safe_name} {{')
            mermaid_lines.append(f'    +HK_{safe_name}')
            mermaid_lines.append(f'    +{hub.business_key}')
            mermaid_lines.append(f'    +load_date')
            mermaid_lines.append(f'    +record_source')
            mermaid_lines.append('}')
            mermaid_lines.append(f'class H_{safe_name} hubStyle')

        # Links
        for link in links:
            safe_name = re.sub(r'\W+', '_', link.name)
            mermaid_lines.append(f'class L_{safe_name} {{')
            mermaid_lines.append(f'    +HK_{safe_name}')
            for hub in link.hubs.all():
                safe_hub = re.sub(r'\W+', '_', hub.name)
                mermaid_lines.append(f'    +HK_{safe_hub}')
            mermaid_lines.append(f'    +load_date')
            mermaid_lines.append(f'    +record_source')
            mermaid_lines.append('}')
            mermaid_lines.append(f'class L_{safe_name} linkStyle')

        # Satellites
        for satellite in satellites:
            safe_name = re.sub(r'\W+', '_', satellite.name)
            mermaid_lines.append(f'class S_{safe_name} {{')
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
            
            # Adiciona o HK_DIFF e campos default
            mermaid_lines.append(f'    +HK_DIFF')
            mermaid_lines.append(f'    +valid_from')
            mermaid_lines.append(f'    +valid_to')
            mermaid_lines.append(f'    +is_current')
            
            # Adiciona os atributos específicos
            for name, tipo in satellite.attributes.items():
                safe_attr = re.sub(r'\W+', '_', name)
                mermaid_lines.append(f'    +{safe_attr}')
            
            # Adiciona os campos de auditoria
            mermaid_lines.append(f'    +load_date')
            mermaid_lines.append(f'    +record_source')
            mermaid_lines.append('}')
            mermaid_lines.append(f'class S_{safe_name} satelliteStyle')

        # Relações
        for link in links:
            safe_link = re.sub(r'\W+', '_', link.name)
            for hub in link.hubs.all():
                safe_hub = re.sub(r'\W+', '_', hub.name)
                mermaid_lines.append(f'H_{safe_hub} --> L_{safe_link}')

        for satellite in satellites:
            safe_sat = re.sub(r'\W+', '_', satellite.name)
            parent = None
            if satellite.content_type.model == 'hub':
                parent = hub_name_map.get(satellite.object_id)
            elif satellite.content_type.model == 'link':
                parent = link_name_map.get(satellite.object_id)
            if parent:
                safe_parent = re.sub(r'\W+', '_', parent)
                if satellite.content_type.model == 'hub':
                    mermaid_lines.append(f'H_{safe_parent} --> S_{safe_sat}')
                else:
                    mermaid_lines.append(f'L_{safe_parent} --> S_{safe_sat}')

        mermaid_data = "\n".join(mermaid_lines)
        error_message = None
    except Exception as e:
        mermaid_data = ''
        error_message = f"Ocorreu um erro ao gerar o diagrama: {e}"
        project = None

    return render(request, 'modeler/visualize_classdiagram.html', {
        'mermaid_data': mermaid_data,
        'error_message': error_message,
        'project': project
    })

class ProjectListView(ListView):
    model = Project
    template_name = 'modeler/project_list.html'
    context_object_name = 'projects'

class ProjectCreateView(CreateView):
    model = Project
    template_name = 'modeler/project_form.html'
    fields = ['name', 'description']
    success_url = reverse_lazy('project_list')

class ProjectUpdateView(UpdateView):
    model = Project
    template_name = 'modeler/project_form.html'
    fields = ['name', 'description']
    success_url = reverse_lazy('project_list')

class ProjectDeleteView(DeleteView):
    model = Project
    template_name = 'modeler/project_confirm_delete.html'
    success_url = reverse_lazy('project_list')

def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    context = {
        'project': project,
        'hubs': project.hubs.all(),
        'links': project.links.all(),
        'satellites': project.satellites.all()
    }
    return render(request, 'modeler/project_detail.html', context)
