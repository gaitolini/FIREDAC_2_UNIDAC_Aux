import os
import re

# Configuração dos módulos a adicionar e remover
UNIDAC_MODULES = ["MemDS", "DBAccess", "Uni"]
FIREDAC_MODULES = [
    "FireDAC.Stan.Intf",
    "FireDAC.Stan.Option",
    "FireDAC.Stan.Param",
    "FireDAC.Stan.Error",
    "FireDAC.DatS",
    "FireDAC.Phys.Intf",
    "FireDAC.DApt.Intf",
    "FireDAC.Stan.Async",
    "FireDAC.DApt",
    "FireDAC.Comp.DataSet",
    "FireDAC.Comp.Client",
]

def process_pas_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # Juntar linhas em um único texto para facilitar a manipulação
    content = ''.join(lines)

    # Regular expressions para encontrar seções "uses"
    uses_pattern = re.compile(r'uses\s+(.*?);', re.DOTALL | re.IGNORECASE)

    # Localizar todas as seções uses
    uses_sections = uses_pattern.findall(content)
    if not uses_sections:
        return False  # Nenhuma seção uses encontrada

    # Dividir em interface e implementation (assume que o primeiro é interface)
    interface_uses = uses_sections[0]
    implementation_uses = uses_sections[1] if len(uses_sections) > 1 else ""

    # Função auxiliar para normalizar e deduplicar módulos (case-insensitive)
    def normalize_uses_section(uses_section):
        modules = [module.strip() for module in uses_section.split(',')]
        # Deduplicar ignorando maiúsculas/minúsculas
        unique_modules = {}
        for module in modules:
            key = module.lower()  # Usar o nome em minúsculas como chave
            if key not in unique_modules:
                unique_modules[key] = module  # Manter o formato original
        return ', '.join(unique_modules.values())

    # Adicionar UNIDAC se necessário
    if any(module in content for module in UNIDAC_MODULES):
        for module in UNIDAC_MODULES:
            if module.lower() not in interface_uses.lower():  # Checar case-insensitive
                interface_uses += f", {module}"

    # Remover módulos FIREDAC
    for module in FIREDAC_MODULES:
        interface_uses = re.sub(rf'\b{module}\b,?\s*', '', interface_uses, flags=re.IGNORECASE)
        implementation_uses = re.sub(rf'\b{module}\b,?\s*', '', implementation_uses, flags=re.IGNORECASE)

    # Normalizar e deduplicar seções
    interface_uses = normalize_uses_section(interface_uses)
    implementation_uses = normalize_uses_section(implementation_uses)

    # Garantir ";" no final de interface_uses
    if not interface_uses.endswith(';'):
        interface_uses += ';'

    # Substituir a seção "interface"
    content = re.sub(
        r'interface\s+uses\s+.*?;',
        f"interface\nuses\n{interface_uses};",
        content,
        count=1,
        flags=re.DOTALL | re.IGNORECASE
    )

    # Substituir a seção "implementation" (se existir)
    if implementation_uses:
        content = re.sub(
            r'implementation\s+uses\s+.*?;',
            f"implementation\nuses\n{implementation_uses};",
            content,
            count=1,
            flags=re.DOTALL | re.IGNORECASE
        )

    # Reescrever o arquivo
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)

    return True

def process_directory(path):
    for root, dirs, files in os.walk(path):
        # Ignorar o diretório .git
        if '.git' in dirs:
            dirs.remove('.git')  # Remove .git da lista de subdiretórios a explorar

        for file in files:
            if file.endswith('.pas'):
                file_path = os.path.join(root, file)
                print(f"Processando: {file_path}")
                try:
                    if process_pas_file(file_path):
                        print(f"Arquivo atualizado: {file_path}")
                    else:
                        print(f"Sem alterações necessárias: {file_path}")
                except Exception as e:
                    print(f"Erro ao processar {file_path}: {e}")

# Caminho do projeto
project_path = input("Informe o caminho do projeto: ").strip()

# Processar todos os arquivos .pas no diretório
process_directory(project_path)

print("Processamento concluído!")
