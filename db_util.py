import getpass
import os

from subprocess import PIPE, CalledProcessError, run as run_program


def login_mysql(database, host='localhost'):
    """
    Utiliza o mysqlclient para simular um login no banco de dados_testes utilizando a biblioteca subprocess. Pode ser utilizado
    para validar um usuário e senha do mysql antes da execução de scrits no bd.
    param: database: (string) nome do banco de dados_testes no mysql.
    param: host: (string) endereço ip do banco de dados_testes.
    Return: (tuple(string,string) se a senha, usuário e database forem válidos retorna uma tupla com o usurio e senha.
    Caso não seja válido retorna uma tupla com (None, None).
    """

    print(f'Login Mysql- DB: {database} Host: {host}!')
    usr = input('Usr: ')

    pwd = getpass.getpass(f'Senha: ')

    if not usr:
        print('Usuário ou senha inválido!')
        return False

    os.environ['MYSQL_PWD'] = pwd
    mysql_client_command = f'mysql -u {usr} -h {host}'

    try:
        run_program(mysql_client_command.split(),
                    input=f'use {database}'.encode('utf-8'),
                    check=True,
                    stderr=PIPE)

    except CalledProcessError as e:
        print(e.stderr.decode("utf-8"))
        return None, None

    except Exception as e:
        print(f'Erro ao conectar com Mysql')
        return None, None

    finally:
        os.environ['MYSQL_PWD'] = ''

    print('logado com sucesso')
    return usr, pwd
