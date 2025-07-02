# Data Vault 2.0 Modeler

Este é um aplicativo web Django projetado para modelar e visualizar estruturas de Data Vault 2.0. Ele permite que os usuários criem e gerenciem Hubs, Links e Satellites e, em seguida, visualizem o modelo resultante como um Diagrama de Entidade-Relacionamento (ERD).

## 📄 Licença

Este projeto está licenciado sob uma **Licença Educacional** que permite apenas uso para fins de estudo e aprendizado. **Uso comercial é estritamente proibido**. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## Funcionalidades

- **Criar Hubs:** Defina as entidades de negócio centrais com suas chaves de negócio.
- **Criar Links:** Estabeleça relacionamentos entre os Hubs.
- **Criar Satellites:** Adicione atributos descritivos e contextuais aos Hubs e Links.
- **Visualização do Modelo:** Gere e exiba um diagrama ER do modelo Data Vault completo, mostrando as entidades e seus relacionamentos.
- **Interface CRUD:** Funcionalidades completas de Criar, Ler, Atualizar e Deletar para todas as entidades do modelo.

## Setup do Projeto

Siga estas instruções para configurar e executar o ambiente de desenvolvimento localmente.

### Pré-requisitos

- Python 3.8 ou superior
- `pip` e `venv`

### Instruções de Instalação

1.  **Clone o repositório:**
    ```bash
    git clone <URL_DO_REPOSITORIO>
    cd datavault_app
    ```

2.  **Configure as variáveis de ambiente:**
    ```bash
    cp env.example .env
    # Edite o arquivo .env com suas configurações
    # IMPORTANTE: Gere uma nova SECRET_KEY para produção
    ```

3.  **Crie e ative um ambiente virtual:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

4.  **Instale as dependências:**
    O arquivo `requirements.txt` contém todos os pacotes Python necessários.
    ```bash
    pip install -r requirements.txt
    ```

5.  **Aplique as migrações do banco de dados:**
    Isso criará o esquema do banco de dados com base nos modelos definidos.
    ```bash
    python manage.py migrate
    ```

6.  **Inicie o servidor de desenvolvimento:**
    ```bash
    python manage.py runserver
    ```

    A aplicação estará disponível em `http://127.0.0.1:8000/`.

    Para parar o servidor, pressione `CTRL+C` no terminal onde ele está sendo executado.

## Como Usar

1.  **Navegue até a página inicial:** Acesse `http://127.0.0.1:8000/` para ver a lista de Hubs, Links e Satellites existentes.
2.  **Crie Entidades:** Use os botões "Create Hub", "Create Link" ou "Create Satellite" para adicionar novas entidades ao seu modelo. Preencha os formulários com as informações necessárias.
3.  **Visualize o Modelo:** Clique no link "Visualize" na barra de navegação para ver o diagrama ER do seu modelo Data Vault. O diagrama é gerado dinamicamente com base nas entidades que você criou.

## Exportando o Diagrama como Imagem

Após criar e visualizar seu modelo, você pode exportar o diagrama como PNG:

1. Acesse a página de visualização do modelo (Visualize).
2. Clique no botão **"Exportar como PNG"** logo abaixo do diagrama.
3. O diagrama será baixado como uma imagem PNG, pronta para ser usada em apresentações ou documentação.

O diagrama é renderizado automaticamente usando o Mermaid.js, que já está incluído no projeto.

## 🔒 Segurança

### ⚠️ **IMPORTANTE PARA PRODUÇÃO:**

1. **Gere uma nova SECRET_KEY:**
   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

2. **Configure para produção:**
   ```bash
   # Para desenvolvimento
   cp env.example .env
   
   # Para produção
   cp env.production.example .env
   # Edite o .env com suas configurações reais
   ```

3. **Verifique a segurança:**
   ```bash
   python manage.py check --deploy
   ```

4. **Configure DEBUG=False em produção**

5. **Use HTTPS em produção**

6. **Configure ALLOWED_HOSTS adequadamente**

7. **Nunca commite arquivos .env com dados reais**

### 🛡️ **Configurações de Segurança:**
- O projeto usa variáveis de ambiente para configurações sensíveis
- Arquivos `.env` estão no `.gitignore`
- Use o arquivo `env.example` para desenvolvimento
- Use o arquivo `env.production.example` para produção
- Todas as configurações de segurança são controladas por variáveis de ambiente 