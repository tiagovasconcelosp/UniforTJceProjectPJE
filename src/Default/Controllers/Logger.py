import os
import json
import time
import socket
import asyncio
import aiohttp
import pandas as pd
from pathlib import Path
from urllib import request
from datetime import datetime
from getmac import get_mac_address


class Logger():

    SUCESSO = "Realizado"

    def __init__(self, url=None, token=None) -> None:
        # Irá armazenar a url enviada se ela não for None, caso contrário irá usar a defautl
        if url is not None:
            self.url = url
        else:
            self.url = "https://bpmex.tjce.jus.br/services/log"
        # Irá armazenar o token enviado se ele não for None, caso contrário irá usar o defautl
        if token is not None:
            self.token = token
        else:
            self.token = "eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJDbG92aXMifQ.W8triArmhdS2rbgUJeHHUnW-yWfF0l3kTCPoCgJ1yGIvhP0yzwNtwQYLQ6xTsWIJd303eh6IzFZujnn1MFvv0Q"

        self.gerar_diretorio_executados()

    def get_ip(self):
        try:
            url = request.urlopen('http://ip-api.com/json').read()
            jsn = json.loads(url.decode('UTF-8'))
            IP = str(jsn['query'])
        except:
            hostname = socket.gethostname()
            IP = socket.gethostbyname(hostname)
        return IP

    def set_macro_dados(self, nome_rpa, aplicacao, versao, navegador, usuario, codigoRpa=None):
        self.nome_rpa = nome_rpa
        self.aplicacao = aplicacao
        self.codigoRpa = codigoRpa
        self.aplicacao_versao = versao
        self.aplicacao_ip = self.get_ip()
        self.aplicacao_mac_address = str(get_mac_address())
        self.navegador = navegador
        self.usuario_loggado_aplicacao = usuario

    def set_dados_processo(self, num_processo, passo_executado, erro, mensagem):
        self.num_processo = num_processo
        self.passo_executado = passo_executado
        self.erro = erro
        self.mensagem = mensagem

    def montar_dados_requisicao(self):
        data_hora = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        data = {"nomeRpa": self.nome_rpa,
                "dataDeOcorrencia" : data_hora,#"2023-09-27T12:54:32",
                "erro" : self.erro,
                "nomePassoExecutado": self.passo_executado,
                "aplicacao": self.aplicacao,
                "numeroProcessoJudicial": self.num_processo, 
                "aplicacaoVersao": self.aplicacao_versao, 
                "aplicacaoIp": self.aplicacao_ip, 
                "aplicacaoMacAddress": self.aplicacao_mac_address, 
                "navegador": self.navegador, 
                "usuarioLoggadoAplicacao": self.usuario_loggado_aplicacao,
                "mensagem": self.mensagem
                }
        if self.codigoRpa is not None:
            data["codigoRpa"] = self.codigoRpa
        return data

    async def post_with_bearer_token(self, data):
        try:
            if "Teste" not in self.aplicacao:
                headers = {
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json"
                }
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(self.url, json=data, headers=headers) as response:
                        return await response.text()
        except Exception as e:
            print(repr(e))

    async def enviar_requisicao(self):
        data = self.montar_dados_requisicao()
        content = await self.post_with_bearer_token(data)
        print(content)

    def realizar_requisicao(self, num_processo, passo_executado, mensagem, erro=False):
        self.set_dados_processo(num_processo, passo_executado, erro, mensagem)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.enviar_requisicao())

    def gerar_diretorio_executados(self):
        desktop = Path.home() / "Desktop"
        if not Path.exists(desktop):                 
            desktop = Path.home() / "OneDrive - tjce.jus.br" / "Área de Trabalho"
        if not Path.exists(desktop):                 
            desktop = Path.home() / "OneDrive - tjce.jus.br" / "Desktop"
        if not Path.exists(desktop):                 
            desktop = Path.home() / "OneDrive" / "Área de Trabalho"             
        if not Path.exists(desktop):                 
            desktop = Path.home() / "OneDrive" / "Desktop"
        self.path_executados = os.path.join(desktop, "executados")
        if not os.path.isdir(self.path_executados):
            os.mkdir(self.path_executados)

    def substitui_sinais_proibidos(self, nome):
        nome_tratado = nome
        for sinal in ['/', '\\', '*', '?', '"', '<', '>', '|', ':']:
            nome_tratado = nome_tratado.replace(sinal, " ")
            nome_tratado = nome_tratado.replace("  ", " ")
        return nome_tratado

    def gerar_diretorio_executados_automacao(self):
        nome_rpa_tratado = self.substitui_sinais_proibidos(self.nome_rpa)
        self.path_executados = os.path.join(self.path_executados, nome_rpa_tratado)
        if not os.path.isdir(self.path_executados):
            os.mkdir(self.path_executados)

    def criar_arquivo_executados(self, etapas):
        self.gerar_diretorio_executados_automacao()
        data_arq = time.localtime() 
        self.nome_arquivo = os.path.join(self.path_executados, "processos_executados_"
                        +str(data_arq.tm_mday) +"-"+str(data_arq.tm_mon)+"-"+str(data_arq.tm_year)
                        +"_" +str(data_arq.tm_hour)+"-"+str(data_arq.tm_min)+".xlsx")
        self.etapas = ["Processo", "Data"] + etapas
        self.lista_processos = pd.DataFrame(columns=self.etapas)
        self.lista_processos.to_excel(self.nome_arquivo, index=False)

    def adicionar_processo(self, processo):
        if processo not in self.lista_processos["Processo"].unique():
            dados = {"Processo": processo, "Data": datetime.now()}
            for etapa in self.etapas[2:]:
                dados[etapa] = 'Não'
            novo = pd.DataFrame([dados])
            self.lista_processos = pd.concat([self.lista_processos, novo])
            self.lista_processos.to_excel(self.nome_arquivo, index=False)
            self.realizar_requisicao(num_processo=processo, 
                                    passo_executado="Inicio",
                                    mensagem=self.SUCESSO)
        else:
            for etapa in self.etapas[2:]:
                if "Não" not in self.lista_processos.loc[self.lista_processos["Processo"]==processo, etapa].values:
                    self.atualizar_etapa_processo(processo, etapa, "Não")

    def atualizar_etapa_processo(self, processo, etapa, atualizacao):
        if etapa in self.etapas:
            self.lista_processos.loc[self.lista_processos["Processo"]==processo, etapa] = atualizacao
            self.lista_processos.to_excel(self.nome_arquivo, index=False)
            if etapa == self.etapas[-1]:
                self.realizar_requisicao(num_processo=processo, 
                                         passo_executado="Fim", 
                                         mensagem=self.SUCESSO)

    def retorna_nome_arquivo(self):
        if " " in self.nome_arquivo:
            barra = "\\"
            if "/" in self.nome_arquivo:
                barra = "/"
            parcial = self.nome_arquivo.split(barra)
            for parte in parcial:
                if " " in parte:
                    parte2 = '"'+parte+'"'
                    self.nome_arquivo = self.nome_arquivo.replace(parte, parte2)
        return self.nome_arquivo
        

    def enviar_erro(self, num_processo, passo_executado, mensagem):
        self.realizar_requisicao(num_processo, passo_executado, mensagem, erro=True)

# ['Processo', 'Data', 'Encaminhar PAC', 
# 'Destinatário', 'Endereço', 'Conteúdo Carta',
# 'Assinatura', 'Enviar com AR e Aguardando Correios']
    
