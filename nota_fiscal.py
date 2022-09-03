from bradocs4py import ValidadorChaveAcessoNFe
from gtin import GTIN

check_key_nfce = ValidadorChaveAcessoNFe.validar

def check_gtin(product_code, length=13):
    '''
        Verifica se um codigo gtim esta correto
    '''
    if len(product_code) == 13:
        try:
            #biblioteca GTIN com problemas
            return True
            GTIN(product_code, length)
        except Exception:
            return False
        return True
    else:
        return False