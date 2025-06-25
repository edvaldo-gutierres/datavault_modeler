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

def create_hub(request, project_pk):
    """Cria um novo Hub."""
    project = get_object_or_404(Project, pk=project_pk)
    
    if request.method == 'POST':
        form = HubForm(request.POST)
        if form.is_valid():
            hub = form.save()
            return redirect('project_detail', pk=project.pk)
    else:
        form = HubForm(initial={'project': project.pk})
    
    return render(request, 'modeler/create_hub.html', {
        'form': form,
        'project': project
    })

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

def create_link(request, project_pk):
    """Cria um novo Link."""
    project = get_object_or_404(Project, pk=project_pk)
    
    if request.method == 'POST':
        form = LinkForm(request.POST)
        if form.is_valid():
            link = form.save()
            return redirect('project_detail', pk=project.pk)
    else:
        form = LinkForm(initial={'project': project.pk})
    
    if Hub.objects.filter(project=project).count() < 2:
        return render(request, 'modeler/error_not_enough_hubs.html', {'project': project})

    return render(request, 'modeler/create_link.html', {
        'form': form,
        'project': project
    })

def create_satellite(request, project_pk):
    """Cria um novo Satellite."""
    project = get_object_or_404(Project, pk=project_pk)
    
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
        return render(request, 'modeler/error_no_parents.html', {'project': project})

    return render(request, 'modeler/create_satellite.html', {
        'form': form,
        'formset': formset,
        'project': project
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

def visualize_legacy(request):
    """Função de compatibilidade para redirecionar a URL antiga para a nova."""
    project_id = request.GET.get('project')
    if project_id:
        return redirect('visualize', pk=project_id)
    return redirect('project_list')

def visualize(request, pk):
    """Visualiza o modelo Data Vault usando Mermaid."""
    project = get_object_or_404(Project, pk=pk)
    hubs = Hub.objects.filter(project=project)
    links = Link.objects.filter(project=project).prefetch_related('hubs')
    satellites = Satellite.objects.filter(project=project).select_related('content_type')
    
    # Cria dicionários para mapear IDs para nomes
    hub_name_map = {str(hub.id): hub.name for hub in hubs}
    link_name_map = {str(link.id): link.name for link in links}
    
    mermaid_lines = []
    mermaid_lines.append('erDiagram')
    
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
        
        # Adiciona os relacionamentos do Link com os Hubs
        for hub in link.hubs.all():
            safe_hub = re.sub(r'\W+', '_', hub.name)
            mermaid_lines.append(f'    L_{safe_name} }}|--|| H_{safe_hub} : "references"')
    
    # Adiciona as entidades Satellite
    for satellite in satellites:
        safe_name = re.sub(r'\W+', '_', satellite.name)
        mermaid_lines.append(f'    S_{safe_name}:::satelliteStyle {{')
        
        # Adiciona a chave do pai (Hub ou Link)
        parent_name = None
        if satellite.content_type.model == 'hub':
            parent = Hub.objects.get(id=satellite.object_id)
            parent_name = parent.name
            safe_parent = re.sub(r'\W+', '_', parent_name)
            mermaid_lines.append(f'        string HK_{safe_parent}')
        elif satellite.content_type.model == 'link':
            parent = Link.objects.get(id=satellite.object_id)
            parent_name = parent.name
            safe_parent = re.sub(r'\W+', '_', parent_name)
            mermaid_lines.append(f'        string HK_{safe_parent}')
        
        # Adiciona o HK_DIFF e campos default
        mermaid_lines.append(f'        string HK_DIFF')
        mermaid_lines.append(f'        datetime valid_from')
        mermaid_lines.append(f'        datetime valid_to')
        mermaid_lines.append(f'        boolean is_current')
        
        # Adiciona os atributos específicos
        for name, tipo in satellite.attributes.items():
            safe_attr = re.sub(r'\W+', '_', name)
            mermaid_lines.append(f'        {tipo} {safe_attr} "{name}"')
        
        # Adiciona os campos de auditoria
        mermaid_lines.append(f'        datetime load_date')
        mermaid_lines.append(f'        string record_source')
        mermaid_lines.append('    }')
        
        # Adiciona o relacionamento do Satellite com seu pai
        if parent_name:
            safe_parent = re.sub(r'\W+', '_', parent_name)
            prefix = 'H_' if satellite.content_type.model == 'hub' else 'L_'
            mermaid_lines.append(f'    S_{safe_name} }}|--|| {prefix}{safe_parent} : "describes"')
    
    mermaid_data = "\n".join(mermaid_lines)
    error_message = None
    
    return render(request, 'modeler/visualize.html', {
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

def view_ddl(request, pk):
    """Visualiza o DDL SQL na página."""
    project = get_object_or_404(Project, pk=pk)
    hubs = Hub.objects.filter(project=project)
    links = Link.objects.filter(project=project)
    satellites = Satellite.objects.filter(project=project)
    
    # Mapeamento de tipos Python para SQL
    type_mapping = {
        'string': 'VARCHAR(255)',
        'integer': 'INTEGER',
        'float': 'DECIMAL(18,2)',
        'boolean': 'BOOLEAN',
        'datetime': 'TIMESTAMP',
        'date': 'DATE'
    }
    
    ddl_lines = []
    ddl_lines.append(f'-- DDL gerado automaticamente para o projeto: {project.name}')
    ddl_lines.append('\n-- Criação dos Hubs')
    
    # Gera DDL para Hubs
    for hub in hubs:
        safe_name = re.sub(r'\W+', '_', hub.name)
        ddl_lines.append(f'\nCREATE TABLE H_{safe_name} (')
        ddl_lines.append(f'    HK_{safe_name} VARCHAR(32) PRIMARY KEY,')
        ddl_lines.append(f'    {hub.business_key} VARCHAR(255) NOT NULL,')
        ddl_lines.append('    load_date TIMESTAMP NOT NULL,')
        ddl_lines.append('    record_source VARCHAR(255) NOT NULL')
        ddl_lines.append(');')
    
    # Gera DDL para Links
    ddl_lines.append('\n-- Criação dos Links')
    for link in links:
        safe_name = re.sub(r'\W+', '_', link.name)
        ddl_lines.append(f'\nCREATE TABLE L_{safe_name} (')
        ddl_lines.append(f'    HK_{safe_name} VARCHAR(32) PRIMARY KEY,')
        
        # Adiciona as chaves dos Hubs relacionados
        for hub in link.hubs.all():
            safe_hub = re.sub(r'\W+', '_', hub.name)
            ddl_lines.append(f'    HK_{safe_hub} VARCHAR(32) NOT NULL,')
            ddl_lines.append(f'    FOREIGN KEY (HK_{safe_hub}) REFERENCES H_{safe_hub}(HK_{safe_hub}),')
        
        ddl_lines.append('    load_date TIMESTAMP NOT NULL,')
        ddl_lines.append('    record_source VARCHAR(255) NOT NULL')
        ddl_lines.append(');')
    
    # Gera DDL para Satellites
    ddl_lines.append('\n-- Criação dos Satellites')
    for satellite in satellites:
        safe_name = re.sub(r'\W+', '_', satellite.name)
        ddl_lines.append(f'\nCREATE TABLE S_{safe_name} (')
        
        # Adiciona a chave do pai (Hub ou Link)
        parent_fk = None
        if satellite.content_type.model == 'hub':
            parent_name = Hub.objects.get(id=satellite.object_id).name
            safe_parent = re.sub(r'\W+', '_', parent_name)
            ddl_lines.append(f'    HK_{safe_parent} VARCHAR(32) NOT NULL,')
            ddl_lines.append(f'    FOREIGN KEY (HK_{safe_parent}) REFERENCES H_{safe_parent}(HK_{safe_parent}),')
        elif satellite.content_type.model == 'link':
            parent_name = Link.objects.get(id=satellite.object_id).name
            safe_parent = re.sub(r'\W+', '_', parent_name)
            ddl_lines.append(f'    HK_{safe_parent} VARCHAR(32) NOT NULL,')
            ddl_lines.append(f'    FOREIGN KEY (HK_{safe_parent}) REFERENCES L_{safe_parent}(HK_{safe_parent}),')
        
        # Adiciona o HK_DIFF e campos default
        ddl_lines.append('    HK_DIFF VARCHAR(32) NOT NULL,')
        ddl_lines.append('    valid_from TIMESTAMP NOT NULL,')
        ddl_lines.append('    valid_to TIMESTAMP,')
        ddl_lines.append('    is_current BOOLEAN NOT NULL,')
        
        # Adiciona os atributos específicos
        for name, tipo in satellite.attributes.items():
            safe_attr = re.sub(r'\W+', '_', name)
            sql_type = type_mapping.get(tipo.lower(), 'VARCHAR(255)')
            ddl_lines.append(f'    {safe_attr} {sql_type},')
        
        # Adiciona os campos de auditoria
        ddl_lines.append('    load_date TIMESTAMP NOT NULL,')
        ddl_lines.append('    record_source VARCHAR(255) NOT NULL,')
        ddl_lines.append('    PRIMARY KEY (HK_DIFF)')
        ddl_lines.append(');')
    
    return render(request, 'modeler/view_ddl.html', {
        'project': project,
        'ddl_content': '\n'.join(ddl_lines)
    })

def generate_ddl(request, pk):
    """Gera o DDL SQL para download."""
    project = get_object_or_404(Project, pk=pk)
    hubs = Hub.objects.filter(project=project)
    links = Link.objects.filter(project=project)
    satellites = Satellite.objects.filter(project=project)
    
    # Mapeamento de tipos Python para SQL
    type_mapping = {
        'string': 'VARCHAR(255)',
        'integer': 'INTEGER',
        'float': 'DECIMAL(18,2)',
        'boolean': 'BOOLEAN',
        'datetime': 'TIMESTAMP',
        'date': 'DATE'
    }
    
    ddl_lines = []
    ddl_lines.append(f'-- DDL gerado automaticamente para o projeto: {project.name}')
    ddl_lines.append('\n-- Criação dos Hubs')
    
    # Gera DDL para Hubs
    for hub in hubs:
        safe_name = re.sub(r'\W+', '_', hub.name)
        ddl_lines.append(f'\nCREATE TABLE H_{safe_name} (')
        ddl_lines.append(f'    HK_{safe_name} VARCHAR(32) PRIMARY KEY,')
        ddl_lines.append(f'    {hub.business_key} VARCHAR(255) NOT NULL,')
        ddl_lines.append('    load_date TIMESTAMP NOT NULL,')
        ddl_lines.append('    record_source VARCHAR(255) NOT NULL')
        ddl_lines.append(');')
    
    # Gera DDL para Links
    ddl_lines.append('\n-- Criação dos Links')
    for link in links:
        safe_name = re.sub(r'\W+', '_', link.name)
        ddl_lines.append(f'\nCREATE TABLE L_{safe_name} (')
        ddl_lines.append(f'    HK_{safe_name} VARCHAR(32) PRIMARY KEY,')
        
        # Adiciona as chaves dos Hubs relacionados
        for hub in link.hubs.all():
            safe_hub = re.sub(r'\W+', '_', hub.name)
            ddl_lines.append(f'    HK_{safe_hub} VARCHAR(32) NOT NULL,')
            ddl_lines.append(f'    FOREIGN KEY (HK_{safe_hub}) REFERENCES H_{safe_hub}(HK_{safe_hub}),')
        
        ddl_lines.append('    load_date TIMESTAMP NOT NULL,')
        ddl_lines.append('    record_source VARCHAR(255) NOT NULL')
        ddl_lines.append(');')
    
    # Gera DDL para Satellites
    ddl_lines.append('\n-- Criação dos Satellites')
    for satellite in satellites:
        safe_name = re.sub(r'\W+', '_', satellite.name)
        ddl_lines.append(f'\nCREATE TABLE S_{safe_name} (')
        
        # Adiciona a chave do pai (Hub ou Link)
        parent_fk = None
        if satellite.content_type.model == 'hub':
            parent_name = Hub.objects.get(id=satellite.object_id).name
            safe_parent = re.sub(r'\W+', '_', parent_name)
            ddl_lines.append(f'    HK_{safe_parent} VARCHAR(32) NOT NULL,')
            ddl_lines.append(f'    FOREIGN KEY (HK_{safe_parent}) REFERENCES H_{safe_parent}(HK_{safe_parent}),')
        elif satellite.content_type.model == 'link':
            parent_name = Link.objects.get(id=satellite.object_id).name
            safe_parent = re.sub(r'\W+', '_', parent_name)
            ddl_lines.append(f'    HK_{safe_parent} VARCHAR(32) NOT NULL,')
            ddl_lines.append(f'    FOREIGN KEY (HK_{safe_parent}) REFERENCES L_{safe_parent}(HK_{safe_parent}),')
        
        # Adiciona o HK_DIFF e campos default
        ddl_lines.append('    HK_DIFF VARCHAR(32) NOT NULL,')
        ddl_lines.append('    valid_from TIMESTAMP NOT NULL,')
        ddl_lines.append('    valid_to TIMESTAMP,')
        ddl_lines.append('    is_current BOOLEAN NOT NULL,')
        
        # Adiciona os atributos específicos
        for name, tipo in satellite.attributes.items():
            safe_attr = re.sub(r'\W+', '_', name)
            sql_type = type_mapping.get(tipo.lower(), 'VARCHAR(255)')
            ddl_lines.append(f'    {safe_attr} {sql_type},')
        
        # Adiciona os campos de auditoria
        ddl_lines.append('    load_date TIMESTAMP NOT NULL,')
        ddl_lines.append('    record_source VARCHAR(255) NOT NULL,')
        ddl_lines.append('    PRIMARY KEY (HK_DIFF)')
        ddl_lines.append(');')
    
    # Retorna o DDL como texto com encoding UTF-8
    response = HttpResponse('\n'.join(ddl_lines), content_type='text/plain; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="{project.name}_ddl.sql"'
    return response
