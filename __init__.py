import datetime
import locale
import math
import os
import re
import string
import sys
import traceback

from unicodedata import normalize

# pega uma dos seguintes padrões de sequencias 'municipal' ou 'mun' ou 'mun.' ou 'munic.' ou 'munic'
PDR_ESFERA_MUN = '(?i:municipal)|(?i:mun)|(?i:mun\.)|(?i:munic\.)|(?i:munic)'
# pega uma dos seguintes padrões de sequencias 'estadual' ou 'est' ou 'est.'
PDR_ESFERA_EST = '(?i:estadual)|(?i:est)|(?i:est\.)'
# pega uma dos seguintes padrões de sequencias 'federal' ou 'fed' ou 'fed.' ou 'nacional' ou 'nac.'
PDR_ESFERA_NAC = '(?i:federal)|(?i:fed)|(?i:fed\.)|(?i:nacional)|(?i:nac\.)'
# junção dos padrões MUN, EST e NAC
PDR_ESFERA_LEGAL = '(' + PDR_ESFERA_MUN + '|' + PDR_ESFERA_EST + '|' + PDR_ESFERA_NAC + ')'
# pega o padrão do número do normativo. Ex: 15.278.
PDR_NUM_NORMATIVO = '((\d{1,3}\.)*\d{1,3})'
PDR_ANO_NORMATIVO = '(/\d{2,4})'
# pega o padrão para tipos de normaitos: leis , decretos portaria
PDR_TIPO_NORMATIVO = '((?i:lei)|(?i:decreto)|(?i:portaria)|(?i:intrução normativa)|(?i:in))'

PDR_NORMATIVO = re.compile(
    f'{PDR_TIPO_NORMATIVO}\s+({PDR_ESFERA_LEGAL}\s+)?((nº|n\.|num|num\.)\s+)?{PDR_NUM_NORMATIVO}{PDR_NUM_NORMATIVO}?')

descritores_moeda = {"Real": \
                         {'simbolo_monetario': "$", \
                          'simbolo_moeda': ('R', 'r'), \
                          'separador_milhar': '.', \
                          'separador_decimal': ',' \
                          }}


class ErrorTotaisInconsistentes(Exception):
    pass


def definir_largura_colunas_xlsx(planilha,tamanhos):
    pos_A = ord('A')
    for i in range(tamanhos):
        planilha.column_dimensions[chr(pos_A + i)].width = tamanhos(i)

def normal_round(n, decimals=0):
    # https://stackoverflow.com/questions/33019698/how-to-properly-round-up-half-float-numbers
    expoN = n * 10 ** decimals
    if abs(expoN) - abs(math.floor(expoN)) < 0.5:
        return math.floor(expoN) / 10 ** decimals
    return math.ceil(expoN) / 10 ** decimals


def remover_acentos(txt):
    return normalize('NFKD', txt).encode('ASCII', 'ignore').decode('ASCII')


def remove_accent_characters(old):
    """
    https://stackoverflow.com/questions/517923/what-is-the-best-way-to-remove-accents-normalize-in-a-python-unicode-string
    Removes common accent characters, lower form.
    Uses: regex.
    """
    # new = old.lower()

    new = re.sub(r'[ÀÁÂÃ]', 'A', old)
    new = re.sub(r'[àáâã]', 'a', new)
    new = re.sub(r'[ÈÉÊẼ]', 'E', new)
    new = re.sub(r'[èéêẽ]', 'e', new)
    new = re.sub(r'[ÌÍÎĨ]', 'I', new)
    new = re.sub(r'[ìíîĩ]', 'i', new)
    new = re.sub(r'[ÒÓÔÕ]', 'O', new)
    new = re.sub(r'[òóôõ]', 'o', new)
    new = re.sub(r'[ÚÚÛŨ]', 'U', new)
    new = re.sub(r'[ùúûũ]', 'u', new)
    new = re.sub(r'[Ç]', 'C', new)
    new = re.sub(r'[ç]', 'c', new)
    return new


def string_to_tupledate(date_str, formato=2):
    '''
        Verifica se um determinado valor passado é uma data válida
        parametros:
            date_str (string): uma string que contém uma data
            formato (int): um inteiro que irá informar a disposição do dia/mes/ano na 
                            data. Exemplo:
                            1 - Espera-se uma data no formato Ano/mes/dia
                            2 - Espera-se uma data no formato dia/mes/Ano
                            3 - Espera-se uma data no formato mes/dia/Ano,
                            o caracter separador pode ser '/', exemplo: 13/02/2010 ou
                            '-', exemplo 13-02-2010
            retorno:
                (tupla): com o ano, mês e dia.
    '''

    if formato == 1:

        if '/' in date_str:

            year, month, day = date_str.split('/')
        else:
            year, month, day = date_str.split('-')
    elif formato == 2:

        if '/' in date_str:

            day, month, year = date_str.split('/')
        else:
            day, month, year = date_str.split('-')
    else:

        if '/' in date_str:

            month, day, year = date_str.split('/')
        else:
            month, day, year = date_str.split('-')
    return (year, month, day,)


def somar_dicionarios(dict_acumulado, novo_dict):
    """
    Soma dois dicionarios. acumulando a soma no primeiro dicionario passado. Caso o primeiro dicionario seja vazio.
    Copia o segundo no primeiro.
    """
    # se o dicionário que vai acumular valores for vazio. Atualiza suas chaves com o novo dicionario
    if dict_acumulado:
        for key in dict_acumulado:
            dict_acumulado[key] += novo_dict[key]
    else:
        dict_acumulado.update(novo_dict)


def string_to_date(date_str, format=2):
    ''' 
        Converte uma string passada num determinado formato em uma data
        parametros:
            date_str (string): uma string que contém uma data a ser validada
            format (int): um inteiro que irá informar a disposição do dia/mes/ano na 
                            data. Exemplo:
                            1 - Espera-se uma data no formato Ano/mes/dia
                            2 - Espera-se uma data no formato dia/mes/Ano
                            3 - Espera-se uma data no formato mes/dia/Ano,
                            o caracter separador pode ser '/', exemplo: 13/02/2010 ou
                            '-', exemplo 13-02-2010
    '''

    year, month, day = string_to_tupledate(date_str, format)

    return datetime.date(int(year), int(month), int(day))


def is_valid_date(date_str, format=2):
    ''' 
        Verifica se um determinado valor passado é uma data válida
        parametros:
            date_str (string): uma string que contém uma data a ser validada
            format (int): um inteiro que irá informar a disposição do dia/mes/ano na 
                            data. Exemplo:
                            1 - Espera-se uma data no formato Ano/mes/dia
                            2 - Espera-se uma data no formato dia/mes/Ano
                            3 - Espera-se uma data no formato mes/dia/Ano,
                            o caracter separador pode ser '/', exemplo: 13/02/2010 ou
                            '-', exemplo 13-02-2010
    '''
    try:
        year, month, day = string_to_tupledate(date_str, format)

        datetime.datetime(int(year), int(month), int(day))

    except ValueError:
        return False

    return True


def formata_nome_proprio(nome, tamanho_minimo=4):
    '''Formata cada palavra do nome, com tamanho maior que tamanho_minimo para que fique com a primeira letra Maiuscula. '''
    nome_proprio = []
    for indice, palavra in enumerate(nome.title().split()):
        if len(palavra) < tamanho_minimo:
            palavra = palavra.lower()
        nome_proprio.append(palavra)
    return " ".join(nome_proprio)


def formata_nome_empresa(nome, tamanho_minimo=3):
    '''Padroniza no nome da empresa o "Ltda. - ME'''
    padrao_ltda = r'((L|l)(T|t)(D|d)(A|a)(\.?))((\s*-?\s*(M|m)(E|e)\s*)?)\s*$'
    tipo_empresarial = ''
    nome_aux = formata_nome_proprio(nome, tamanho_minimo)
    achado = re.search(padrao_ltda, nome_aux)

    if achado:

        if achado.groups(1)[0]:
            # print(achado.groups(1)[0])
            tipo_empresarial += 'Ltda.'
        if achado.groups(7)[6]:
            # print(achado.groups(7)[6])
            if tipo_empresarial:
                tipo_empresarial = 'Ltda - Me'
            else:
                tipo_empresarial = '- Me'
        nome_aux = re.sub(padrao_ltda, tipo_empresarial, nome_aux)

    return nome_aux


def formatar_numero(number, precision=0, group_sep='.', decimal_sep=','):
    number = ('%.*f' % (max(0, precision), number)).split('.')

    integer_part = number[0]
    if integer_part[0] == '-':
        sign = integer_part[0]
        integer_part = integer_part[1:]
    else:
        sign = ''

    if len(number) == 2:
        decimal_part = decimal_sep + number[1]
    else:
        decimal_part = ''

    integer_part = list(integer_part)
    c = len(integer_part)

    while c > 3:
        c -= 3
        integer_part.insert(c, group_sep)

    return sign + ''.join(integer_part) + decimal_part


def formatar_moeda(valor, localizacao='pt_BR.utf8', separador_milhar=True, simbolo_moeda=None):
    locale.setlocale(locale.LC_ALL, localizacao)
    valor = locale.currency(valor, grouping=separador_milhar, symbol=simbolo_moeda)
    return valor


def desformatar_moeda(valor_str, localizacao='pt_BR.utf8'):
    locale.setlocale(locale.LC_ALL, localizacao)
    return locale.delocalize(valor_str)


def desformatar_moeda_cifra(valor_str, localizacao='pt_BR.utf8'):
    valor = desformatar_moeda(valor_str, localizacao=localizacao)
    valor = valor.replace('R$', '').strip()
    if valor.find('-') != -1:
        valor = valor.replace('-', '')
        valor = '-' + valor.strip()
    return valor


def formatar_data(date_time, format='%A %d de %B de %Y, %H:%M:%S', local='pt_BR.utf8'):
    '''
        Formata um data passada em data_str, num formato passado em format,
        utilizando a localização (definições regionais) passada em local
        parametros:
        date_time (objeto): objeto do tipo datetime
        format(string): formatação para o objeto datetime, ver na documentação do datetime
     local(string): contém o locale da região, ver na documentação do objeto locale
    '''

    locale.setlocale(locale.LC_TIME, local)
    return date_time.strftime(format)


def converte_monetario_float(valor_monetario, descritor_moeda="Real"):
    """ Converte um valor monetario, no formato indicado no parametro 'descritor_moeda', para um valor float"""
    try:
        return float(valor_monetario)
    except ValueError:
        pass
    except TypeError:
        pass
    # verifica se é um numero negativo
    if valor_monetario.find('-') != -1:
        # achou um sinal de menos, retira-o e ajusta o valor do multiplicador para no final
        # negativar o numero
        valor_monetario = valor_monetario.replace('-', '')
        multiplicador = -1.0
    else:
        multiplicador = 1.0

    if eh_valor_monetario(valor_monetario, descritor_moeda):

        for chave, simbolo in [(v, u) for v, u in descritores_moeda[descritor_moeda].items() if
                               v != 'separador_decimal']:
            if chave != 'simbolo_moeda':
                valor_monetario = valor_monetario.replace(simbolo, '')
            elif chave == 'simbolo_moeda':
                for simb_moeda in simbolo:
                    valor_monetario = valor_monetario.replace(simb_moeda, '')

        if descritores_moeda[descritor_moeda]['separador_decimal'] != '.':
            return float(valor_monetario.replace(descritores_moeda[descritor_moeda]['separador_decimal'], '.')) \
                * multiplicador

        return float(valor_monetario) * multiplicador
    else:
        # se não for valor monetário retorna zero
        return 0.0


def eh_valor_monetario(valor_moeda="", descritor_moeda="Real"):
    padrao = '^\\s*-?\\s*((' + '|'.join((descritores_moeda[descritor_moeda])['simbolo_moeda']) + ')\\'
    padrao += descritores_moeda[descritor_moeda]['simbolo_monetario']
    padrao += ')?\\s*(((\\d?\\d?\\d'
    # + descritores_moeda[descritor_moeda]['separador_milhar']
    padrao += ')(\\.\\d\\d\\d)*)|(\\d)+)(' + descritores_moeda[descritor_moeda]['separador_decimal']
    padrao += '\\d*)?$'
    # padrao = '^\s*((R|r)\$)?\s*(((\d?\d?\d)(\.\d\d\d)*)|(\d)+)(,\d*)?$'
    if valor_moeda.strip():
        if re.match(padrao, valor_moeda):
            return 1
        else:
            return 0
    else:
        return 0


def obter_informacoes_erro(e):
    '''
    Obtem informacoes sobre um exceção disparada tipo, descricao,arquivo e número da linha
    '''
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    return f' Erro: "{exc_obj}", Tipo: {exc_type}, Arquivo: {fname}, linha: {exc_tb.tb_lineno}, name: {exc_tb.tb_frame.f_code.co_name}'


def obter_nome_arquivo_e_extensao(nome_arquivo):
    ''' Obtem o nome do arquivo e da extensão do arquivo passado como parâmetro
    Parâmetro: (str) nome_arquivo: O caminho ou arquivo que se quer obter o nome sem extensao e a extensão
    Saída: (tupla): Uma tupla: na primeira posicao, o nome sem extensao e na segunda posição, a extensão'''
    nome_base = os.path.basename(nome_arquivo)
    partes_nome_arquivo = nome_base.split('.')
    if len(partes_nome_arquivo) > 1:  # Verifica se passou um nome de arquivo sem extensão
        nome_sem_extensao = '.'.join(partes_nome_arquivo[:-1])
        extensao = partes_nome_arquivo[-1]
        return nome_sem_extensao, extensao
    else:
        return partes_nome_arquivo, ''  # Retorna string nula como extensão, caso o arquivo não tenha extensão


def print_same_line(msg):
    print('\r' + ' ' * len(msg), end='')
    print('\r' + msg, end='')

def obter_arquivos(caminho, extensao):
    ''' Executa um list dir numa pasta passada obtendo somente arquivo com determinada extensões passada numa tupla
   Parametros (string:caminho): caminho para uma pasta onde vão ser procurados os arquivos
              (tuple: extensão): uma tupla de string, contendo as extensões de arquivos desejada
    Retorno (list) - uma lista com os arquivos que coincidiram com as extensões passadas'''
    arquivos = []
    extensao_aux = []
    if os.path.exists(caminho):

        for ext in extensao:
            extensao_aux.append(ext.upper())

        for arq in os.listdir(caminho):
            if obter_nome_arquivo_e_extensao(arq)[1].upper() in extensao_aux:
                arquivo = os.path.join(caminho, arq)
                if os.path.isfile(arquivo):
                    arquivos.append(arquivo)
    return arquivos


def retirar_pontuacao(texto, retirar_carateres=None):
    """
    Retira caracteres de pontuação de texto exceto os em retirar_caracter (string)
    """
    pontuacao = string.punctuation
    texto_sem_pontuacao = ''
    if retirar_carateres:
        for caracter in retirar_carateres:
            pontuacao = pontuacao.replace(caracter, '')
    for caracter in texto:
        if caracter not in pontuacao:
            texto_sem_pontuacao += caracter
    return texto_sem_pontuacao


def substituir_caracteres(texto, caracteres_a_remover, caracter_substituto=' '):
    """
    substitui, na variável texto, todos os caracteres contidos em caracteres_a_remover pelo caracter_substituto
    Param:
    texto: string: texto q vai ser trabalhado
    caracteres_a_remover: string: Esta variavel conterá os caracteres que devem ser substituidos em texto
    caracter_substituto: string: Esta variável conterá o caracter que vai substituir os caracteres_a_remover de texto
    return: (string): retorna o texto com os caracteres substituidos
    """

    for c in caracteres_a_remover:
        if texto.find(c) != -1:
            texto = texto.replace(c, caracter_substituto)
    return texto


def traceback_to_list(obj_exception, obj_traceback=None):
    if not obj_traceback:
        obj_traceback = obj_exception.__traceback__
    lines = []
    for line in [line.rstrip('\n') for line in \
                 traceback.format_exception(obj_exception.__class__, obj_exception, obj_traceback)]:
        lines.extend(line.splitlines())
    return lines


def traceback_to_string(obj_exception, obj_traceback=None):
    list_lines = traceback_to_list(obj_exception, obj_traceback)
    return ' '.join(list_lines)


if __name__ == "__main__":
    # print(desformatar_moeda('10.000,53'))
    # converte_monetario_float('123.23')
    try:
        a = 1 / 0
    except Exception as e:
        obj_traceback = sys.exc_info()[2]
        print(traceback_to_string(e, obj_traceback))
        raise e
