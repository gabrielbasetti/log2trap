<div align="center" id="top"> 
  <img src="./.github/app.gif" alt="Log2trap" />

  &#xa0;

  <!-- <a href="https://log2trap.netlify.app">Demo</a> -->
</div>

<h1 align="center">Log2trap</h1>

<p align="center">
  <img alt="Github top language" src="https://img.shields.io/github/languages/top/gabrielbasetti/log2trap?color=56BEB8">

  <img alt="Github language count" src="https://img.shields.io/github/languages/count/gabrielbasetti/log2trap?color=56BEB8">

  <img alt="Repository size" src="https://img.shields.io/github/repo-size/gabrielbasetti/log2trap?color=56BEB8">

  <img alt="License" src="https://img.shields.io/github/license/gabrielbasetti/log2trap?color=56BEB8">

  <!-- <img alt="Github issues" src="https://img.shields.io/github/issues/gabrielbasetti/log2trap?color=56BEB8" /> -->

  <!-- <img alt="Github forks" src="https://img.shields.io/github/forks/gabrielbasetti/log2trap?color=56BEB8" /> -->

  <!-- <img alt="Github stars" src="https://img.shields.io/github/stars/gabrielbasetti/log2trap?color=56BEB8" /> -->
</p>

<!-- Status -->

<!-- <h4 align="center"> 
	🚧  Log2trap 🚀 Under construction...  🚧
</h4> 

<hr> -->

<p align="center">
  <a href="#dart-about">About</a> &#xa0; | &#xa0; 
  <a href="#sparkles-features">Features</a> &#xa0; | &#xa0;
  <a href="#rocket-technologies">Technologies</a> &#xa0; | &#xa0;
  <a href="#white_check_mark-requirements">Requirements</a> &#xa0; | &#xa0;
  <a href="#checkered_flag-starting">Starting</a> &#xa0; | &#xa0;
  <a href="#memo-license">License</a> &#xa0; | &#xa0;
  <a href="https://github.com/gabrielbasetti" target="_blank">Author</a>
</p>

<br>

## :dart: About ##

log2trap is a script that sends logs received from network equipment (routers, switches, etc) to zabbix, using rsyslog and zabbix trapper.<br>
This allows you to generate alerts in zabbix from log messages (login correct/incorrect, hardware error and whatever you can think of).<br>

The original project from which I took the initiative corresponds to:<br>
https://github.com/v-zhuravlev/zabbix-syslog<br>
To whom I thank all the previous work that has been done.<br>
I also thank adubkov for the development of the library for zabbix_sender (*)<br>
https://github.com/adubkov/py-zabbix

## :sparkles: Basic behavior ##

1. Device generates a log and sends it to a remote rsyslog server.
2. Rsyslog receives it and runs a script (log2trap).
3. log2trap extracts the ip of the device that sent the log.
4. log2trap searches the zabbix db through its API for a host that has that ip.
5. log2trap then sends the log to the zabbix and its corresponding host.
6. Zabbix processes it.

## :rocket: Technologies ##

The following tools were used in this project:

- [Python](https://python.org/)
- [Zabbix](https://zabbix.com)
- [Rsyslog](https://rsyslog.com)

## :white_check_mark: Requirements ##

Before starting, you need to have Zabbix Server 6.4 previously installed and running and Python3 compiler installed.<br>
pyzabbix and py-zabbix repos are not the same. Python pip install the two repos in the same folder "pyzabbix", what causes problems.<br>
Don't install py-zabbix as for some reason it doesn't work with Zabbix Server 6.4

## :checkered_flag: Starting ##

```bash
# In /home/your-username/ Clone this project
$ git clone https://github.com/gabrielbasetti/log2trap

# Install requirements
$ cd log2trap
$ pip3 install -r requirements.txt

# Change file permissions
$ chown syslog:syslog log2trap.conf log2trap.py sender.py logger.py
$ chmod +x log2trap

# Setup log2trap.conf with your zabbix's API values
$ nano log2trap.conf

# Create new file in rsyslog conf directory
$ nano /etc/rsyslog.d/zabbix_rsyslog.conf

# Copy-paste this settings into zabbix_rsyslog.conf. ***Check the path of the binary***
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
        action(type="omprog" binary="/home/your-username/log2trap/log2trap.py" template="network-fmt")
        stop
}


# Restart services
$ systemctl restart rsyslog zabbix-server

```

## :memo: License ##

This project is under license from GNU General Public License v3.0. For more details, see the [LICENSE](LICENSE) file.


Made with :heart: by <a href="https://github.com/gabrielbasetti" target="_blank">Gabriel Basetti</a>

&#xa0;

<a href="#top">Back to top</a>
