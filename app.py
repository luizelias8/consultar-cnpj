import os
import sys
import re
import requests
import csv

# Define o diretório do app verificando se o script está rodando em uma versão "congelada".
diretorio_app = os.path.dirname(sys.executable if hasattr(sys, 'frozen') else __file__)

# Cria o caminho completo para o arquivo cnpjs.txt no diretório do aplicativo.
caminho_arquivo = os.path.join(diretorio_app, 'cnpjs.txt')

# Cria o caminho completo para o arquivo saida.csv no diretório do aplicativo.
caminho_arquivo_saida = os.path.join(diretorio_app, 'saida.csv')

# Verifica se o arquivo cnpjs.txt existe
if not os.path.isfile(caminho_arquivo):
    print(f'Arquivo "{os.path.basename(caminho_arquivo)}" não encontrado. Encerrando o script.')
    exit()

# Verifica se o arquivo saida.csv existe e o exclui
if os.path.isfile(caminho_arquivo_saida):
    os.remove(caminho_arquivo_saida)
    print(f'Arquivo "{os.path.basename(caminho_arquivo_saida)}" excluído com sucesso.')

def formatar_cnpj(cnpj):
    # Aplica a máscara de CNPJ
    return f'{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}'

def limpar_cnpj(cnpj):
    """
    Remove caracteres nao numericos do CNPJ.
    """
    return re.sub(r'\D', '', cnpj)

def ler_cnpjs(arquivo):
    try:
        with open(arquivo, 'r') as arquivo:
            # Lê o arquivo e remove linhas em branco e espaços em branco extras
            cnpjs = [linha.strip() for linha in arquivo.read().splitlines() if linha.strip()]
        # Remove CNPJs duplicados
        # return list(set(cnpjs))
        return cnpjs
    except FileNotFoundError:
        print(f'Arquivo {arquivo} nao encontrado.')
        return []

def consultar_cnpj(cnpj):
    cnpj_limpo = limpar_cnpj(cnpj) # Limpa o CNPJ para remover caracteres não numéricos
    url = f'https://brasilapi.com.br/api/cnpj/v1/{cnpj_limpo}' # URL da API com o CNPJ limpo

    try:
        # Faz a solicitação GET para a API
        resposta = requests.get(url)
        if resposta.status_code == 200:
            # Imprime sucesso para o CNPJ
            # print(f'OK: {cnpj_limpo}')
            print(f'OK: {cnpj}')
            # Retorna a resposta em formato JSON
            return resposta.json()
        else:
            print(f'Erro ao consultar o CNPJ: {resposta.status_code}') # Imprime código de erro
            return None
    except requests.exceptions.RequestException as e:
        print(f'Erro de conexao: {e}') # Imprime erro de conexão
        return None

def salvar_dados(dados, caminho_arquivo):
    """
    Salva os dados do CNPJ em um arquivo CSV, adicionando ao final se o arquivo já existir.
    """
    if dados and 'cnpj' in dados:
        # Captura os dados específicos
        razao_social = dados.get('razao_social', '')
        cnpj = dados.get('cnpj', '')
        natureza_juridica = dados.get('natureza_juridica', '')
        data_inicio_atividade = dados.get('data_inicio_atividade', '')

        # Ajusta opcao_pelo_simples para "sim" ou "não"
        opcao_pelo_simples = dados.get('opcao_pelo_simples', '')
        opcao_pelo_simples = 'X' if opcao_pelo_simples else ''

        data_opcao_pelo_simples = dados.get('data_opcao_pelo_simples', '')
        data_exclusao_do_simples = dados.get('data_exclusao_do_simples', '')

        # Formata o CNPJ antes de salvar
        cnpj_formatado = formatar_cnpj(cnpj)

        arquivo_existe = os.path.isfile(caminho_arquivo)
        with open(caminho_arquivo, mode='a' if arquivo_existe else 'w', newline='', encoding='latin1') as arquivo:
            # Cria um escritor de CSV
            escritor = csv.writer(arquivo, delimiter=';')

            if not arquivo_existe:
                # Escreve os cabeçalhos na primeira linha
                escritor.writerow([
                    'razao_social',
                    'cnpj',
                    'natureza_juridica',
                    'data_inicio_atividade',
                    'opcao_pelo_simples',
                    'data_opcao_pelo_simples',
                    'data_exclusao_do_simples'
                ])

            # Escreve os valores na segunda linha
            escritor.writerow([
                razao_social,
                cnpj_formatado, # Usa o CNPJ formatado
                natureza_juridica,
                data_inicio_atividade,
                opcao_pelo_simples,
                data_opcao_pelo_simples,
                data_exclusao_do_simples
            ])

        print(f"Dados de CNPJ {cnpj_formatado} salvos com sucesso em '{os.path.basename(caminho_arquivo)}'.")
    else:
        print('Nenhum dado disponível para salvar.')

cnpjs = ler_cnpjs(caminho_arquivo)

if not cnpjs:
    print('Nenhum CNPJ encontrado para consultar.')
    exit()

for cnpj in cnpjs:
    dados = consultar_cnpj(cnpj)
    if dados:
        salvar_dados(dados, caminho_arquivo_saida)
    else:
        print(f"Não foi possível obter informações para o CNPJ {cnpj}.")