#-------------------------------------------------------------------------------
# Name:        ProgressMeter.py
# Purpose:
#
# Author:      luiscar
#
# Created:     02/03/2018
# Copyright:   (c) luiscar 2018
# Licence:     <your licence>
#-------------------------------------------------------------------------------

class ProgressMeter(dict):
    
    def __init__(self,item_atual=0,valor_maximo=0,valor_maximo_visual=50):
        #super.__init__()
        self.item_atual = item_atual
        self["value"] = item_atual
        self["maximum"] = valor_maximo
        self["maximum_visual"] = valor_maximo_visual
        #self.__valor_maximo = valor_maximo
        #self.valor_maximo_visual = valor_maximo_visual
        self.progress_bar = None
    
    def stop(self):
        #TODO
        pass
    
    def config(self,mode=""):
        #TODO
        pass
    
    def start(self,valor=0):
        #TODO
        pass
    
    def update_progress(self,item_atual):
        if item_atual == 0:
            return
        modulo = self["maximum"] / self["maximum_visual"]
        #calcula qt deve ser mostrado
        qt_visual = int(item_atual/modulo)
        self["value"] = item_atual

        if self.progress_bar == None:
            self.print_terminal(qt_visual)
        else:
            #progrees_bar is tkinter.ttk.progressbar
            self.progress_bar["value"]  = self["maximum"]

    def set_valor_max(self,valor_maximo):
        """Atualiza o valor maximo do Medidor """
        self["maximum"] = valor_maximo
        #atualiza valor maximo do progress bar
        if self.progress_bar != None:
            self.progress_bar["maximum"] = valor_maximo

    def print_terminal(self,qt_visual):
        #inicializa hashes, o '+ 1' é para ajustar o arredondamento e conse-
        #guir fechar barra de hashes
        hashes = '#' * (qt_visual + 1)
        if len(hashes) > self["maximum_visual"]:
            hashes = "#" * (self["maximum_visual"] + 1)

        # impressÃ£o da barra de hashes
        print('[', end='')
        #Todo, ver uma forma de gerar o formato de maneira dinÃ¢mica ({}) qdo max mudar alterar
        #o espaÃ§amento do formato
        formato = '{:50}'.format(hashes)
        print(formato, end='')
        print(']', end='')

        #fim da impressÃ£o de hashes
        #volta o cursor 50 vezes, para que na proxima impressÃ£o, dÃª a impressa de que a barra de hash
        #estÃ¡ aumentando
        #TODO: quando se colocar o formato dinÃ¢mica colocar "range(qt_total_visual)"
        for i in range(50):
            print('\r', end='')
        #se for o ultimo item a ser impresso (100%), quebra a linha no final da barra.
        if self["value"] >= self["maximum"]:
            print('')

def main():
    import time 
    
    p = ProgressMeter(item_atual=0,valor_maximo=50,valor_maximo_visual=50)
    
    for i in range(50):
        time.sleep(0.2)
        p.update_progress(i) 
    

if __name__ == '__main__':
    main()
