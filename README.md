# log2trap
Simple script to send rsyslog remote msgs to zabbix's trapper

Intro:
log2trap es un script que envía logs recibidos desde equipos de red (routers, switchs, etc) a zabbix, utilizando rsyslog y zabbix trapper.
Esto permite generar alertas en zabbix a partir de mensajes de log (login correcto/incorrecto, hardware error y todo lo que se te ocurra)

El proyecto original del que tomé la iniciativa corresponde a: 
https://github.com/v-zhuravlev/zabbix-syslog
A quién agradezco por todo el trabajo previo que ha realizado.
También agradezco a adubkov por el desarrollo de la librería para zabbix_sender (\*)
https://github.com/adubkov/py-zabbix

El funcionamiento básico es el siguiente: 
1. Dispositivo genera un log y lo envía a un servidor rsyslog remoto.
2. Rsyslog lo recibe y ejecuta un script (log2trap).
3. log2trap extrae la ip del dispositivo que envió el log.
4. log2trap busca en la db de zabbix a través de su API un host que tenga esa ip.
5. log2trap entonces envía el log al zabbix y a su correspondiente host.
6. Zabbix lo procesa.

Requisitos previos
Tener instalado Zabbix Server 6.4
Tener instalado python3

Instalación

En /home/username/ clonar el repositorio:
$ git clone https://github.com/gabrielbasetti/log2trap.git
$ cd log2trap
$ pip3 install -r requirements.txt
Setear permisos de archivos
$ chown syslog:syslog log2trap.conf log2trap.py sender.py logger.py
$ chmod +x log2trap.py
Configurar log2trap.conf con los valores de tu zabbix API
Crear archivo de configuración de rsyslog
$ nano /etc/rsyslog.d/zabbix_rsyslog.conf
Copy-Paste: 
# provides UDP syslog reception
$ModLoad imudp
$UDPServerRun 514

#enables omrpog module
$ModLoad omprog

$template RFC3164fmt,"<%PRI%>%TIMESTAMP% %HOSTNAME% %syslogtag%%msg%"
$template network-fmt,"%TIMESTAMP:::date-rfc3339% [%fromhost-ip%] %pri-text% %syslogtag%%msg%\n"

#exclude unwanted messages(examples):
:msg, contains, "Child connection from" stop
:msg, contains, "exit after auth (ubnt): Disconnect received" stop
:msg, contains, "password auth succeeded for 'ubnt' from" stop
:msg, contains, "exit before auth: Exited normally" stop
if $fromhost-ip != '127.0.0.1' then {
        action(type="omprog" binary="/etc/zabbix/scripts/zabbix_syslog_lkp_host.pl" template="network-fmt")
        stop
}




(\*) pyzabbix y py-zabbix no son lo mismo, pip instala los dos bajo el mismo directorio "pyzabbix" lo que genera problemas.
 No instales py-zabbix ya que por alguna razón no funciona en Zabbix 6.4.
