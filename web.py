import pickle,os,random,datetime,time,logging,requests,configparser
import itertools
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.proxy import Proxy,ProxyType
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException,NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


# def wait_visible(drive, qt_seconds, locator, target):
#     '''Verifica se o elemento vai ficar visivel, caso passe uma quantidade de segundos(qt_seconds) retorna False'''
#     try:
#         WebDriverWait(drive, qt_seconds).until(
#             EC.visibility_of_element_located((locator, target)))
#         return False #ok, achou o elemento
#     except TimeoutException:
#         return True
#
# def wait_clickable(driver, qt_seconds, locator, target):
#     '''Verifica se o elemento vai ficar visivel, caso passe uma quantidade de segundos(qt_seconds) retorna False'''
#     WebDriverWait(driver, qt_seconds).until(EC.element_to_be_clickable((locator, target)))

class CyclePool(object):
    '''Poço cíclico. Guarda objetos e vai devolvendo de forma cíclica (sem fim)'''
    def __init__(self,pool):
        self._pool = pool
        self.shuffle()

    def get_next(self):
        return self._cycle_pool.__next__()

    def shuffle(self):
        '''Embaralha os itens e guarda no poço'''
        random.shuffle(self._pool)
        self._cycle_pool = itertools.cycle(self._pool)

    def remove_item(self,item):
        if len(self._pool) == 1:
            raise Exception('Cycle Pool Esvaziado')
        if item in self._pool: #verifica se o item tá na lista
            index = self._pool.index(item) #pega o índice do item
            if index > 0 or len(self._pool) <=1:
                index -=1 #pega o indice anterior
            else:
                index = len(self._pool) - 2 #se o indice do item era zero, pega o último índice
            self._pool.remove(item)            #remove o item
            self._cycle_pool = itertools.cycle(self._pool) #atualiza a lista cíclica
            while self._pool[index] != self.get_next():  #coloca a lista no próximo item, aquele após o item retirado
                pass

    def __str__(self):
        return str(self._pool)

    def __len__(self):
        return self._pool.__len__()

class SiteScraper(object):

    def __init__(self,scrap_file_config,enviroment='desenvolvimento',log_level=logging.INFO,name_scrapper='SiteScrapper',
                 proxy_pool=['51.158.119.88:8811'],scrap_method=''):
        '''
            parametros:
                scrap_file_config (sting): path/Nome do arquivo de configuração.
                host(string): endereço ip onde vai estar o servidor selenium. #rodar o jar do selenium deve estar ativo
                user_server(boolean): informa se vai usar o servidor selenium ou não.
                change_proxy_selenium(boolean): informa se vai ser alterado o proxy a cada PROXY_LIMIT_REQUEST requisições
                log_file(boolean): informa se o log vão ser gravados em arquivo, caso contrário serão mostrados na tela.
                log_level: informa o nivel do log (INFO,DEBUG,ERROR...)
                name_scrapper(string): Nome do objeto scrapper. vai ser utilizado nos logs para rastreamento
                proxy_pool(list): list com os endereços do proxys a serem usados
                user_agent(string): O tipo do browser que o será verá durante a conexão
        '''
        self.enviroment = enviroment
        self.scrap_file_config = scrap_file_config
        self.read_config()
        if scrap_method != '':
            self.SCRAP_METHOD = scrap_method
        self.make_folders()
        self.http_session = None
        self.CSRFToken = None
        self._request_number_selenium = 0  # informa qdo mudar o proxy, juntamento com PriceSite.PROXY_LIMIT_REQUEST
        self._request_data_number = 0 #rastreia a quantidade de requisições feitas por request_data, para troca do proxy
        self.make_user_agent_pool()
        self.USER_AGENT = self.user_agent_pool.__next__()

        if self.LOG_FILE:
            nome_arq_log = self.LOG_FOLDER + '/' + datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '.log'
            formatacao_log = '%(asctime)s;%(levelname)s;%(funcName)s;%(message)s'
            logging.basicConfig(filename=nome_arq_log,
                                level=log_level,
                                filemode='w',
                                format=formatacao_log,
                                datefmt='%Y-%m-%d-%H:%M:%S')
        else:
            formatacao_log = '%(asctime)s %(levelname)s %(funcName)s %(message)s'
            logging.basicConfig(level=log_level,
                                format=formatacao_log,
                                datefmt='%Y-%m-%d-%H:%M:%S')

        self.log = logging.getLogger(name_scrapper)
        self.log.info(f'Iniciado {name_scrapper}')

        if proxy_pool:
            self.make_proxy_pool()
        else:
            self.current_proxy = None
            self.proxy_pool = None


        if self.SCRAP_METHOD == 'SELENIUM':
            caps = DesiredCapabilities.FIREFOX.copy()
            caps['general.useragent.override'] = self.USER_AGENT
            if self.USE_SERVER:
                #conecta via servidor (rodar o jar antes)
                caps = DesiredCapabilities.FIREFOX.copy()
                caps['general.useragent.override'] = self.USER_AGENT
                caps['browserName'] = 'firefox'
                self.driver = webdriver.Remote(command_executor=f'http://{self.HOST_SERVER }:4444/wd/hub',
                                               desired_capabilities=caps)
                self.log.info(f'Abriu um novo webdrive conectado em "http://{self.HOST_SERVER }:4444/wd/hub"')
            else:
                self.driver = webdriver.Firefox(desired_capabilities=caps)
                self.log.info(f'Abriu um novo webdrive local')

            self.log.info(f'Ajustando um proxy pro selenium...')
            new_proxy = self.set_new_proxy_selenium()
            if new_proxy:
                self.log.info(f'Novo proxy selenium em: {new_proxy}')
            else:
                self.log.info(f'Selenium sem Proxy')

        else:
            self.set_new_proxy_request()

    def make_folders(self):
        ''' Cria as pasta necessário para a classe'''
        if not os.path.exists(self.TMP_FOLDER):
            os.mkdir(self.TMP_FOLDER)
        if not os.path.exists(self.LOG_FOLDER):
            os.mkdir(self.LOG_FOLDER)
        if not os.path.exists(self.EXTRACT_FOLDER):
            os.mkdir(self.EXTRACT_FOLDER)

    def make_proxy_pool(self):
        with open(f'{self.INPUT_FOLDER}/{self.PROXIES_FILE}','r') as f:
            proxies = f.read().split('\n')[:-1]
            proxy_pool = []
            for proxy in proxies:
                proxy_pool.append('http://' + proxy.strip())
            self.proxy_pool= CyclePool(proxy_pool)
            self.log.info(f'proxy_pool iniciado com {len(self.proxy_pool)} proxies')

    def make_user_agent_pool(self):
        with open(f'{self.INPUT_FOLDER}/{self.USER_AGENTS_FILE}','r') as f:
            self.user_agent_pool = itertools.cycle(f.read().split('\n')[:-1])

    def increment_request_number_selenium(self):
        self.log.info(f'Requisição de dados Selenium-> {self._request_number_selenium + 1}')
        self._request_number_selenium += 1

    def increment_request_data_number(self):
        self.log.info(f'Requisição de dados-> {self._request_data_number + 1}' )
        self._request_data_number += 1

    def is_time_to_change_proxy_request(self):
        '''
            Troca o proxy caso 'proxy_pool' seja preenchido e a quantidade de requisições para o site
             for maior ou igual a 'PROXY_LIMIT_REQUEST'.
        '''

        if not self.current_proxy:
            return None
        if self._request_data_number >= self.PROXY_LIMIT_REQUEST:
            self._request_data_number = 0
            self.set_new_proxy_request()
            self.log.info(f'Obtido novo request proxy {self.current_proxy}')

    def is_time_to_change_proxy_selenium(self):
        '''
            Troca o proxy caso 'change_proxy_selenium' for True e a quantidade de requisições para o site 'self._request'
             for maior ou igual a 'PROXY_LIMIT_REQUEST'.
        '''

        if not self.current_proxy:
            return None
        if self._request_number_selenium >= self.PROXY_LIMIT_REQUEST:
            self.log.info(f'Alterando o proxy do selenium...')
            self._request_number_selenium = 1
            self.set_new_proxy_selenium()


    def pause(self, fraction=1):
        self.log.info(f'Aguardando {self.PAUSE / fraction} segundos ...')
        time.sleep(self.PAUSE / fraction)

    def read_config(self):
        self.file_config = configparser.ConfigParser()
        #self.file_config.read('scraper.cfg')
        if not os.path.exists(self.scrap_file_config):
            raise Exception(f'Não foi encontrado o arquivo de configuração {self.scrap_file_config}.')

        self.file_config.read(self.scrap_file_config)
        self.EXTRACT_FOLDER = self.file_config[self.enviroment]['EXTRACT_FOLDER']
        self.HOST_SERVER = self.file_config[self.enviroment]['HOST_SERVER']
        self.INPUT_FOLDER = self.file_config[self.enviroment]['INPUT_FOLDER']
        self.USER_AGENTS_FILE = self.file_config[self.enviroment]['USER_AGENTS_FILE']
        self.LOG_FILE = int(self.file_config[self.enviroment]['LOG_FILE'])
        self.LOG_FOLDER = self.file_config[self.enviroment]['LOG_FOLDER']
        self.PAUSE = int(self.file_config[self.enviroment]['PAUSE'])
        self.PAUSE_PESQUISAR = int(self.file_config[self.enviroment]['PAUSE_PESQUISAR'])
        self.PROXY_LIMIT_REQUEST = int(self.file_config[self.enviroment]['PROXY_LIMIT_REQUEST'])
        self.PROXY_TIMEOUT = int(self.file_config[self.enviroment]['PROXY_TIMEOUT'])
        self.PROXIES_FILE = self.file_config[self.enviroment]['PROXIES_FILE']
        self.TMP_FOLDER = self.file_config[self.enviroment]['TMP_FOLDER']
        self.USE_SERVER = int(self.file_config[self.enviroment]['USE_SERVER'])
        self.USER_AGENT = self.file_config[self.enviroment]['USER_AGENT']
        self.USER_AGENTS_FILE = self.file_config[self.enviroment]['USER_AGENTS_FILE']
        self.SCRAP_METHOD = self.file_config[self.enviroment]['SCRAP_METHOD']


    @property
    def request_number_selenium(self):
        return self._request_number_selenium

    @property
    def request_data_number(self):
        '''Informa o numero da requisição atual'''
        return self._request_data_number


    def save_file(self,content,file_name='',page_source=False):
        '''
            Salva num arquivo o conteudo passado em 'content'
            parametros:
                content(string): conteúdo a ser salvo no arquivo
                file_name(string): nome do arquivo
                page_source(boolean): indica se esta salvando um arquivo normal ou o conteudo da página. O nome
                    do arquivo começará com 'page se for a página ou 'file' nos outros casos.
            return:
                file_name(string): o nome do arquivo
        '''

        type_file,ext = ('page_','.html') if page_source else ('file_','.txt')
        if file_name == '':
            file_name = self.LOG_FOLDER + '/' + type_file + datetime.datetime.now().strftime('%Y%m%d%H%M%S_%f') + ext
        with open(file_name,'w') as f:
            f.write(content)
        return file_name

    def save_page_source(self,file_name=''):
        '''
            Salva a página atual
            return:
                file_name(string): o nome do arquivo
        '''
        return self.save_file(self.driver.page_source,file_name=file_name,page_source=True)

    def set_new_proxy_request(self,host_port=None):
        '''
            Muda o proxy do ṕara o resquest_data.
            parâmetros:
                host_port(tuple of string): Endereço ip e número da porta do proxy, (ip_number,port_number).
                Se não for passado valor, pega, sequencialmente um proxy do pool de proxy (circularmente)
            returns:
                None

                '''
        if host_port:
            host = host_port[0]
            port = host_port[1]
        else:
            if self.proxy_pool: #se tiver proxy_pool
                myProxy = self.proxy_pool.get_next()
                self.log.info(f'proxy_pool com {len(self.proxy_pool)} proxies')
                if not myProxy:
                    pass
                self.current_proxy = myProxy
                self._request_data_number = 0
            else: #senão tiver devolve o proxy atual
                return self.current_proxy
        return self.current_proxy

    def set_new_proxy_selenium(self, host_port=None):
        '''
            Muda o proxy do browser. Altera o endereço para about:config. lembrar, após a mudança do proxy retornar
            para o endereço anterior
            parâmetros:
                host_port(tuple of string): Endereço ip e número da porta do proxy, (ip_number,port_number). Se não for
                   passado valor, pega, aleatóriamente um proxy do pool de PROXY_LIST
            returns:
                None

        '''
        if host_port:
            host = host_port[0]
            port = host_port[1]
        else:
            if self.proxy_pool:
                myProxy = self.proxy_pool.get_next()
                self.current_proxy = myProxy
                self._request_data_number = 0
                host,port = myProxy[7:].split(':') #[6:] para retirar o http://
                #host, port = myProxy.split(':')
            else:
                return self.proxy_pool

        self.driver.get("about:config")
        time.sleep(3)
        bt = self.driver.find_element_by_id('warningButton')
        bt.click()
        time.sleep(3)
        java_script = f'var prefs = Components.classes["@mozilla.org/preferences-service;1"].' + \
                      'getService(Components.interfaces.nsIPrefBranch);' + \
                      'prefs.setIntPref("network.proxy.type", 1);' + \
                      f'prefs.setCharPref("network.proxy.http", "{host}");' + \
                      f'prefs.setIntPref("network.proxy.http_port", "{port}");' + \
                      f'prefs.setCharPref("network.proxy.ssl", "{host}");' + \
                      f'prefs.setIntPref("network.proxy.ssl_port", "{port}");' + \
                      f'prefs.setCharPref("network.proxy.ftp", "{host}");' + \
                      f'prefs.setIntPref("network.proxy.ftp_port", "{port}");' + \
                      f'prefs.setCharPref("network.proxy.socks", "{host}");' + \
                      f'prefs.setIntPref("network.proxy.socks_port", "{port}");'

        self.driver.execute_script(java_script)
        time.sleep(3)
        return host + ':' + port

    def set_new_user_agent(self,old_agent=''):
        new_user_agent = old_agent
        while new_user_agent == old_agent:  #pega um user_agent diferente
            new_user_agent = self.USER_AGENT_LIST[random.randint(0,len(self.USER_AGENT_LIST)- 1)]
