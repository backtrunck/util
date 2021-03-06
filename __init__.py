import re, os, string, locale, datetime, sys, traceback
from gtin import GTIN
from bradocs4py import ValidadorChaveAcessoNFe
from unicodedata import normalize

check_key_nfce = ValidadorChaveAcessoNFe.validar

descritores_moeda = {   "Real":\
                            {  'simbolo_monetario':"$", \
                                'simbolo_moeda':('R', 'r'), \
                                'separador_milhar':'.', \
                                'separador_decimal':','\
                            }}


def check_gtin(product_code, length=13):
    '''
        Verifica se um codigo gtim esta correto
    '''
    if len(product_code) == 13:
        try:
            GTIN(product_code, length)
        except Exception:
            return False
        return True
    else:
        return False

def remover_acentos(txt):
   return normalize('NFKD', txt).encode('ASCII', 'ignore').decode('ASCII')
    
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
            
            day , month, year = date_str.split('/')
        else:
            day , month, year = date_str.split('-')
    else:    
        
        if '/' in date_str:
            
            month, day, year = date_str.split('/')
        else:
            month, day, year = date_str.split('-')
    return (year, month, day, )        
            
def string_to_date(date_str, format = 2):
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
    
    year,  month,  day = string_to_tupledate(date_str, format)
     
    return datetime.date(int(year), int(month), int(day))
    
def is_valid_date(date_str, format = 2):
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
        year , month,  day = string_to_tupledate(date_str, format)
    
        datetime.datetime(int(year), int(month),  int(day))
        
    except ValueError:
        return False
        
    return True
            
def formata_nome_proprio (nome, tamanho_minimo = 4):
    '''Formata cada palavra do nome, com tamanho maior que tamanho_minimo para que fique com a primeira letra Maiuscula. '''
    nome_proprio = []
    for indice, palavra in enumerate(nome.title().split()):
        if len(palavra) < tamanho_minimo:
            palavra = palavra.lower()
        nome_proprio.append(palavra)
    return " ".join(nome_proprio)
    
def formata_nome_empresa(nome, tamanho_minimo = 3):
    '''Padroniza no nome da empresa o "Ltda. - ME'''
    padrao_ltda = r'((L|l)(T|t)(D|d)(A|a)(\.?))((\s*-?\s*(M|m)(E|e)\s*)?)\s*$'
    tipo_empresarial = ''
    nome_aux = formata_nome_proprio(nome, tamanho_minimo)
    achado = re.search(padrao_ltda, nome_aux)
    
    if achado:   
        
        if achado.groups(1)[0]:
            #print(achado.groups(1)[0])
            tipo_empresarial += 'Ltda.'
        if achado.groups(7)[6]:
            #print(achado.groups(7)[6])
            if tipo_empresarial:
                tipo_empresarial = 'Ltda - Me'
            else:
                tipo_empresarial =  '- Me'
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


def formatar_moeda(valor, localizacao = 'pt_BR.utf8', separador_milhar = True, simbolo_moeda = None):
    locale.setlocale(locale.LC_ALL, localizacao)
    valor = locale.currency(valor, grouping = separador_milhar, symbol = simbolo_moeda)
    return valor

def desformatar_moeda(valor_str,localizacao = 'pt_BR.utf8'):
    locale.setlocale(locale.LC_ALL, localizacao)
    return locale.delocalize(valor_str)

def formatar_data(date_time, format = '%A %d de %B de %Y, %H:%M:%S', local = 'pt_BR.utf8'):
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
    #verifica se é um numero negativo
    if valor_monetario.find('-') != -1:
        #achou um sinal de menos, retira-o e ajusta o valor do multiplicador para no final 
        #negativar o numero
        valor_monetario = valor_monetario.replace('-', '')
        multiplicador = -1.0
    else:
        multiplicador = 1.0
        
    if eh_valor_monetario(valor_monetario, descritor_moeda):
        
        for chave, simbolo in [(v, u) for v, u in descritores_moeda[descritor_moeda].items() if v != 'separador_decimal']:
            if chave != 'simbolo_moeda':
                valor_monetario = valor_monetario.replace(simbolo,'')
            elif chave == 'simbolo_moeda':
                for simb_moeda in simbolo:
                    valor_monetario = valor_monetario.replace(simb_moeda,'')
        
        if descritores_moeda[descritor_moeda]['separador_decimal'] != '.':
            return float(valor_monetario.replace(descritores_moeda[descritor_moeda]['separador_decimal'], '.')) \
                    * multiplicador
            
        return float(valor_monetario) * multiplicador       

    
def eh_valor_monetario(valor_moeda="",descritor_moeda="Real"):

    padrao = '^\\s*-?\\s*((' + '|'.join((descritores_moeda[descritor_moeda])['simbolo_moeda']) + ')\\' 
    padrao += descritores_moeda[descritor_moeda]['simbolo_monetario'] 
    padrao += ')?\\s*(((\\d?\\d?\\d' 
    #+ descritores_moeda[descritor_moeda]['separador_milhar'] 
    padrao +=  ')(\\.\\d\\d\\d)*)|(\\d)+)(' +  descritores_moeda[descritor_moeda]['separador_decimal'] 
    padrao +='\\d*)?$'      
    #padrao = '^\s*((R|r)\$)?\s*(((\d?\d?\d)(\.\d\d\d)*)|(\d)+)(,\d*)?$'
    if valor_moeda.strip() :
        if re.match(padrao,valor_moeda):
            return 1
        else:
            return 0
    else:
        return 0


def obter_nome_arquivo_e_extensao(nome_arquivo):
    ''' Obtem o nome do arquivo e da extensão do arquivo passado como parâmetro
    Parâmetro: (str) nome_arquivo: O caminho ou arquivo que se quer obter o nome sem extensao e a extensão
    Saída: (tupla): Uma tupla: na primeira posicao, o nome sem extensao e na segunda posição, a extensão'''
    nome_base = os.path.basename(nome_arquivo)
    partes_nome_arquivo = nome_base.split('.')
    if len(partes_nome_arquivo) > 1:                            #Verifica se passou um nome de arquivo sem extensão
        nome_sem_extensao = '.'.join(partes_nome_arquivo[:-1])
        extensao = partes_nome_arquivo[-1]
        return (nome_sem_extensao, extensao)
    else:
        return(partes_nome_arquivo, '')                         #Retorna string nula como extensão, caso o arquivo não tenha extensão

 
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

    
def retirar_pontuacao(texto):
    texto_sem_pontuacao = ''
    for caracter in texto:
        if caracter not in string.punctuation:
            texto_sem_pontuacao +=  caracter
    return texto_sem_pontuacao

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
    #print(desformatar_moeda('10.000,53'))
    #converte_monetario_float('123.23')
    try:
        a = 1/0
    except Exception as e:
        obj_traceback = sys.exc_info()[2]
        print(traceback_to_string(e, obj_traceback))
        raise e 
