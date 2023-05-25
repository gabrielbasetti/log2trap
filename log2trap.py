#!/usr/bin/python3
# -*- coding: utf-8 -*-
#rsyslog to zabbix trapper connector
#Cuando es llamado por el action de la conf del rsyslog, busca el host
#de la ip del log recibido y le manda los datos vía zabbix-sender

#instalar paquete pyzabbix, NO py-zabbix!!!!!

from pyzabbix import ZabbixAPI
from sender import ZabbixMetric, ZabbixSender
import sys
import re
import os

zabbixApiUser = 'Admin'
zabbixApiPass = 'zabbix'
zabbixApiServer = '127.0.0.1' #cambiar a 127.0.0.1 en producción
zabbixApiURL = 'http://127.0.0.1/zabbix/' #lo trae del archivo conf
config = {}

#traer el archivo de configuración
#donde está la info para conectarse a la api (usuario, pass, url)
#si encuentra el archivo de config con info personalizada, lo carga, sino usa
#los parámetros por default arriba fijados.
try:
    # open file
    file = open(str(os.path.dirname(__file__))+'/log2trap.conf').readlines()
    for line in file:
        line = line.strip('\n')
        if line:
                clave, valor = line.split('=', 1)
                config[clave.strip()] = valor.strip()
    zabbixApiUser = config['user']
    zabbixApiPass = config['pass']
    zabbixApiServer = config ['server']
    zabbixApiURL = config['url']    
    
except Exception as e:
    print('--------->' + str(e))

while (True):
    host = []
    for line in sys.stdin:
        message = line #guardo el standart input en la var porque directamente en re no funciona.
        #tempText = "2017-12-19T09:26:26.314936+03:00 [10.0.62.2] syslog.info SysLogTest[4616]Test syslog message"
        try:
            ip = re.findall(r"[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}", message) #busco la ip en el mensaje
        except Exception as e:
            print('No se encontraron IPs de remitente en el mensaje, argumento no válido')

        #consulto la API para que me devuelva el host correspondiente a la ip obtenida        
        if (len(ip) > 0): #si no hay ip en el mensaje, entonces que no consulte la api
            zapi = ZabbixAPI(server=zabbixApiURL)
            zapi.session.verify = False #Deshabilita chequeo de certificado
            zapi.login(zabbixApiUser, zabbixApiPass)
            host = zapi.host.get(filter={"ip": ip[0]}) #filtra por host que corresponden a la ip y por status
            zapi.user.logout()

        #envío los datos con zabbix_sender al trapper específico
        if (len(host) > 0): #controlo que haya un host asociado a la ip
            if host[0]['status'] != '1': #controlo que el host no esté deshabilitado
                print(host[0]['host'])
                packet = [
                  ZabbixMetric(host[0]['host'], 'syslog', message),
                ]
                #envía los datos al trapper
                result = ZabbixSender(use_config=False, zabbix_server=zabbixApiServer).send(packet)