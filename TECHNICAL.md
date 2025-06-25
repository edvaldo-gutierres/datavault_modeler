# Documentação Técnica - Data Vault 2.0 Modeler

## Arquitetura do Sistema

### Visão Geral
O Data Vault 2.0 Modeler é uma aplicação web Django que implementa um modelador visual para estruturas Data Vault 2.0. A aplicação segue uma arquitetura MVC (Model-View-Controller) através do padrão MTV (Model-Template-View) do Django.

Para uma visualização detalhada da arquitetura, consulte o [Diagrama de Arquitetura](docs/diagrams.md#diagrama-de-arquitetura).


### Componentes Principais
1. **Models (modeler/models.py)**
   - Implementa as entidades principais do Data Vault
   - Utiliza o ORM do Django para persistência
   - Gerencia relacionamentos entre entidades

2. **Views (modeler/views.py)**
   - Implementa a lógica de negócio
   - Gerencia formulários e validações
   - Processa requisições e renderiza templates

3. **Templates (modeler/templates/)**
   - Interface do usuário em HTML
   - Utiliza Bootstrap para estilização
   - Implementa componentes reutilizáveis

4. **URLs (modeler/urls.py)**
   - Roteamento de requisições
   - Mapeamento de URLs para views

## Modelos de Dados

Para uma visualização completa do modelo de dados e seus relacionamentos, consulte o [Diagrama de Classes](docs/diagrams.md#diagrama-de-classes).

### Project
```python
class Project(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```
- Representa um projeto de modelagem Data Vault
- Contém nome, descrição e timestamps
- Serve como container para Hubs, Links e Satellites

### Hub
```python
class Hub(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    business_key = models.CharField(max_length=100)
    load_date = models.CharField(max_length=100)
    record_source = models.CharField(max_length=100)
```
- Representa entidades de negócio centrais
- Contém chave de negócio e metadados
- Relaciona-se com um Project específico

### Link
```python
class Link(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    hubs = models.ManyToManyField(Hub)
    load_date = models.CharField(max_length=100)
    record_source = models.CharField(max_length=100)
```
- Representa relacionamentos entre Hubs
- Implementa relacionamentos many-to-many
- Mantém metadados de carregamento

### Satellite
```python
class Satellite(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    parent_object = GenericForeignKey('content_type', 'object_id')
    attributes = models.JSONField(default=dict)
    load_date = models.CharField(max_length=100)
    record_source = models.CharField(max_length=100)
```
- Armazena atributos descritivos
- Usa GenericForeignKey para relacionar com Hub ou Link
- Atributos armazenados em JSONField

## Fluxos Principais

### 1. Criação de Projeto
1. Usuário acessa a página inicial
2. Clica em "Novo Projeto"
3. Preenche nome e descrição
4. Sistema cria novo projeto vazio

### 2. Modelagem de Data Vault
1. Usuário seleciona um projeto
2. Adiciona Hubs com chaves de negócio
3. Cria Links entre Hubs relacionados
4. Adiciona Satellites aos Hubs ou Links
5. Sistema valida e persiste cada operação

### 3. Geração de DDL
1. Usuário acessa visualização do projeto
2. Solicita geração de DDL
3. Sistema gera SQL com:
   - Definições de tabelas
   - Chaves primárias e estrangeiras
   - Campos de metadados
   - Encoding UTF-8

Para uma visualização detalhada do processo de geração de DDL, consulte o [Diagrama de Sequência - Geração de DDL](docs/diagrams.md#diagrama-de-sequência---geração-de-ddl).

### 4. Visualização do Modelo
1. Sistema gera diagrama usando Mermaid.js
2. Representa Hubs, Links e Satellites
3. Mostra relacionamentos entre entidades
4. Permite exportação como PNG

## Validações e Regras de Negócio

### Hubs
- Nome único no projeto
- Chave de negócio obrigatória
- Campos de metadados padrão

### Links
- Mínimo de 2 Hubs relacionados
- Nome único no projeto
- Validação de ciclos

### Satellites
- Deve ter um pai (Hub ou Link)
- Atributos em formato válido
- Nome único para o pai

## Segurança e Boas Práticas

### Proteção contra CSRF
- Tokens CSRF em formulários
- Middleware de segurança Django

### Validação de Dados
- Sanitização de inputs
- Validação de tipos
- Proteção contra SQL injection

### Integridade de Dados
- Cascading deletes configurados
- Transações em operações críticas
- Validações de modelo

## Tecnologias Utilizadas

### Backend
- Django 5.2.3
- Python 3.8+
- SQLite (desenvolvimento)

### Frontend
- Bootstrap (UI/UX)
- Mermaid.js (diagramas)
- JavaScript (interatividade)

### Ferramentas de Desenvolvimento
- pip (gerenciamento de pacotes)
- venv (ambientes virtuais)
- Git (controle de versão)

## Extensibilidade

### Pontos de Extensão
1. **Novos Tipos de Entidades**
   - Adicionar novos modelos
   - Implementar views correspondentes
   - Criar templates de interface

2. **Formatos de Exportação**
   - Implementar novos geradores
   - Adicionar opções de formato
   - Criar templates de saída

3. **Validações Customizadas**
   - Adicionar validadores de modelo
   - Implementar regras de negócio
   - Criar mensagens de erro

### Customização
1. **Temas e Estilos**
   - Sobrescrever templates
   - Customizar CSS
   - Adaptar componentes

2. **Regras de Negócio**
   - Adicionar validadores
   - Modificar fluxos
   - Customizar comportamentos

## Manutenção e Debugging

### Logs
- Utilizar logging do Django
- Registrar operações críticas
- Monitorar erros

### Testes
- Implementar testes unitários
- Adicionar testes de integração
- Criar testes end-to-end

### Monitoramento
- Verificar performance
- Monitorar uso de recursos
- Acompanhar erros

## Próximos Passos

### Melhorias Planejadas
1. Implementação de testes automatizados
2. Suporte a múltiplos bancos de dados
3. Interface de administração expandida
4. Sistema de versionamento de modelos
5. Exportação para outros formatos

### Otimizações
1. Cache de diagramas
2. Otimização de queries
3. Compressão de assets
4. Lazy loading de componentes

### Novas Funcionalidades
1. Importação de modelos existentes
2. Colaboração em tempo real
3. Histórico de alterações
4. Templates de projeto
5. Validações customizáveis 