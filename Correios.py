import httplib
import urllib
import time
from datetime import datetime
from HTMLParser import HTMLParser


class Correios(object):

    def tracking_continuo(self):
        """Faz a chamada da funcao tracking a cada 10 segundos, ate que seja interrompida pelo teclado."""
        self.correios = Correios()
        self.prosseguir = True
        while self.prosseguir:
            try:
                self.datas, self.infos = self.correios.tracking()
                for x in range(0, len(self.datas)):
                    status = str(self.datas[x]) + " " + self.infos[x] + "\n\n"
                    statusAnterior = ""
                    if statusAnterior != None:
                        if status == statusAnterior:
                            print "Nope."
                        else:
                            print status
                            statusAnterior = status
                    else:
                        statusAnterior = status
                    
                time.sleep(10)

            except KeyboardInterrupt:
                print "Tracking continuo finalizado"
                self.prosseguir = False


    def tracking(self):
        """Faz um request ao site dos correios com o codigo (de teste) do tracking.
        :returns: uma lista de datas e outra informacoes
         """
        try:
            conn = httplib.HTTPConnection("websro.correios.com.br")
            conn.request("POST", "/sro_bin/txect01$.Inexistente", urllib.urlencode({'P_COD_LIS': "ES750669959BR", 'P_LINGUA': "001", 'P_TIPO': "002"}))
            res = conn.getresponse()

        except:
            print "Ocorreu um erro de conexao"
            return "", ""

        else:
            print "Status:", res.status, res.reason
            dados = res.read()
            conn.close()

            # print Consertando codigo html mal feito...
            dados = dados.replace('LINK="000000"', 'LINK="000000" ')

            print "Iniciando parsing..."
            parser = CustomHTMLParser()
            parser.feed(dados)
            parser.close()
            self.datas = parser.datas
            self.infos = parser.infos
            
            print "... Concluido.\n"
            return self.datas, self.infos


class CustomHTMLParser(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.is_td = False
        self.is_relevante = False
#        self.is_info = False
        self.count = 0
        self.datas = []
        self.infos = []

    def handle_starttag(self, tag, attrs):
#        print "Localizada tag <%s> " % tag
        if tag == "td":
            self.is_td = True

    def handle_data(self, data):
        if self.is_td == True:
            try:
               dt = datetime.strptime(data, "%d/%m/%Y %H:%M")
               self.datas.append(dt)
               self.infos.append("")
               self.is_relevante = True
               
            except ValueError, TypeError:
                if self.is_relevante == True:
                    if "Entregue" in data:
                        self.infos[self.count] += "Sua encomenda consta como entregue."
                        self.count += 1
                        
                    elif "Saiu" in data:
                        self.infos[self.count] += "Sua encomenda saiu para entrega!"
                        self.count += 1
                        
                    elif "ausente" in data:
                        self.infos[self.count] += "Sua encomenda foi postada."
                        self.count += 1
                        
                    elif "Postado" in data:
                        self.infos[self.count] += "Sua encomenda foi postada."
                        self.count += 1

                    elif "Conferido" in data:
                        self.infos[self.count] += "Sua encomenda foi conferida."
                        
                    elif "Recebido" in data:
                        self.infos[self.count] += " - %s" % data
                        self.count += 1
                    
                    elif "Mal encaminhado" in data:
                        self.infos[self.count] += "Wheels!"
                        self.count += 1

                    elif "Encaminhado" in data:
                        self.infos[self.count] += "Sua encomenda foi encaminhada!"

                    elif "nsito para" in data:
                        self.infos[self.count] += " - %s" % data
                        self.count += 1

                    elif "Postado" in data:
                        self.infos[self.count] += "Sua encomenda foi postada!"
                        self.count += 1

                    else:
                        self.infos[self.count] += (data + " | ")

                
    def handle_endtag(self, tag):
#        print "Localizada tag </%s>" % tag
        if tag == "td":
            self.is_td = False
            


correios = Correios()
correios.tracking_continuo()
