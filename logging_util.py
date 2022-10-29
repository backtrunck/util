import logging
from logging.handlers import RotatingFileHandler

def set_loggers(log,level = logging.INFO,log_filename=''):
    '''
    Configura o log da aplicação. Um handler de arquivo e um para o terminal
    :param level: Nivel do log (DEBUG, INFO, CRITICAL, ERROR, etc)
    :param log_filename: (string) nome do arquivo onde os logs vão ser gravados. Caso não seja passado
    os logs vão ser mostrados somente na tela.
    :return: None
    '''
    log.setLevel(level)
    # se não tiver handlers
    if not log.handlers:
        if log_filename:
            fh = RotatingFileHandler(log_filename, maxBytes=2000000, backupCount=5)
            fh.setLevel(logging.INFO)
            format_fh = logging.Formatter('[ARQUIVO] "%(levelname)s";"%(asctime)s";"%(name)s";"%(funcName)s";"%(message)s"')
            fh.setFormatter(format_fh)
            log.addHandler(fh)

        ch = logging.StreamHandler()
        ch.setLevel(level)
        format_ch = logging.Formatter('[TERMINAL] %(levelname)s  %(asctime)s  %(name)s  %(funcName)s  %(message)s')
        ch.setFormatter(format_ch)
        log.addHandler(ch)
