import os

from zipfile import ZipFile, ZIP_DEFLATED


class GerenciadorArquivos(object):
    @staticmethod
    def obter_arquivos(pasta, extensao, ano=''):
        """
        Obtem lista de arquivos de um pasta
        param: pasta: (string) pasta onde os arquivos vão ser procurados
        param: extensão: (string) extensão dos arquivos procurados
        param: ano: (string) ano do arquivo. Espera-se que o arquivo tenha o ano indicado em posição específica
        do nome.
        """
        if extensao[0] != '.':
            extensao = '.' + extensao

        if isinstance(ano,int):
            ano = str(ano)

        if ano:
            return [f for f in os.listdir(pasta)
                    if os.path.splitext(f)[1] == extensao and f[:4] == ano]
        else:
            return [f for f in os.listdir(pasta) if os.path.splitext(f)[1] == extensao]

    def zipar_arquivos(self, nome_arquivo_zipado, pasta, extensao, ano='', excluir=None, remover=True):
        """
        Compacta arquivos de um determinada pasta
        param: nome_arquivo_zipado: (string) arquivo para onde os arquivão vão ser zipados.
        param: pasta: (string) pasta onde os arquivos vão ser procurados
        param: extensão: (string) extensão dos arquivos procurados
        param: ano: (string) ano do arquivo. Espera-se que o arquivo tenha o ano indicado em posição específica
        do nome.
        param: excluir: (list) lista com os nomes dos arquivos q não devem ser zipados.
        param: remover: (boolean) se após zipados os arquivos originais vão ser removidos.
        """
        arquivos = self.obter_arquivos(pasta, extensao, ano)

        try:
            with ZipFile(os.path.join(pasta, nome_arquivo_zipado), 'w', compression=ZIP_DEFLATED) as zip_file:
                num_zipped = 0
                for arquivo in arquivos:
                    if arquivo not in excluir:
                        num_zipped += 1
                        zip_file.write(os.path.join(pasta, arquivo), os.path.basename(arquivo))
                    print(f'compactado {num_zipped:4d} de {len(arquivos):4d} arquivos', end='\r')
                print(f'Compactado: {num_zipped:4d} arquivos')
        except Exception as e:
            raise e
        else:
            if remover:
                print('\napagando arquivos...', end='')
                for arquivo in arquivos:
                    if arquivo not in excluir:
                        os.remove(os.path.join(pasta, arquivo))
                print('  Ok')
            print('')
            print('Processamento finalizado')
