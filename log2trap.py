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
import time
import json

def consultar_host_desde_api(ip, zabbixApiUser='Admin', zabbixApiPass='zabbix', zabbixApiURL='http://127.0.0.1/zabbix/'):
    #consulto la API para que me devuelva el host correspondiente a la ip obtenida
    zapi = ZabbixAPI(server=zabbixApiURL)
    zapi.session.verify = False #Deshabilita chequeo de certificado
    zapi.login(zabbixApiUser, zabbixApiPass)
    host = zapi.host.get(filter={"ip": ip}) #filtra por host que corresponden a la ip
    zapi.user.logout()
    if (len(host) > 0):
        if host[0]['status'] != '1': #controlo que el host no esté deshabilitado
            return host[0]['host']
    else:
        return None

def obtener_host_desde_cache(ip, datos_cache):
    # Verifica si el host está en la caché y si no ha expirado
    if ip in datos_cache and time.time() < datos_cache[ip]["expira"]:
        return datos_cache[ip]["host"]
    else:
        return None

def guardar_host_en_cache(ip, host):
    # Guarda el host en la caché con el tiempo de expiración
    rotation = 300
    datos_cache[ip] = {
        "host": host,
        "expira": time.time() + rotation
    }
    # Guarda los datos de caché en el archivo
    with open(str(os.path.dirname(__file__))+'/log2trap_host_cache.json', 'w') as archivo:
        json.dump(datos_cache, archivo)

def trap_send(host, message, zabbixServer, logType='syslog'):
    #envía los datos a zabbix por zabbixsender
    packet = [
        ZabbixMetric(host, logType, message),
        ]
    result = ZabbixSender(use_config=False, zabbix_server=zabbixServer).send(packet)


#traer el archivo de configuración
#donde está la info para conectarse a la api (usuario, pass, url)
#si encuentra el archivo de config con info personalizada, lo carga, sino usa
#los parámetros por default arriba fijados.
try:
    config = {}
    # open file
    file = open(str(os.path.dirname(__file__))+'/log2trap.conf').readlines()
    for line in file:
        line = line.strip('\n')
        if line:
                clave, valor = line.split('=', 1)
                config[clave.strip()] = valor.strip()
except Exception as e:
    print('--------->' + str(e))

#abro archivo temporal de cache
try:
    with open(str(os.path.dirname(__file__))+'/log2trap_host_cache.json', 'r') as archivo:
        datos_cache = json.load(archivo)
except: #si el archivo no existe, está vacío o tiene datos incorrectos, entra acá y lo empieza de cero más adelante.
    datos_cache = {}



while (True):
    host = []
    for line in sys.stdin:
        message = line #guardo el standart input en la var porque directamente en re no funciona.
        #message = "2017-12-19T09:26:26.314936+03:00 [10.0.40.2] syslog.info SysLogTest[4616]Test syslog message"
        try:
            ip = re.findall(r"[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}", message) #busco la ip en el mensaje
        except Exception as e:
            print('No se encontraron IPs de remitente en el mensaje, argumento no válido')

        if (len(ip) > 0): #si hay ip en el mensaje, continua con la búsqueda de su host
            #Caché de hosts
            ip = str(ip[0]) #elimina la lista
            host = obtener_host_desde_cache(ip, datos_cache)
            if not (host):
                #consulto a la api y guardo el cache
                host = consultar_host_desde_api(ip, config['user'], config['pass'], config['url'])
                if (host):
                    #siempre guardo lo que traigo de la api para actualizar el cache
                    guardar_host_en_cache(ip, host)
                    trap_send(host, message, config['server'])
            else:
                trap_send(host, message, config['server'])