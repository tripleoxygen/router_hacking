#!/usr/bin/env python
#
# sendbin - send binary files over telnet, using echo -e escaped byte sequences.
# Copyright (C) 2012  Triple Oxygen <oxy@g3n.org>
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

import os, sys
import telnetlib

linesize = 64
progress = 0
cursor	 = ['\\', '-', '/','|']

if len(sys.argv) != 5:
	print "Usage: ./sendbin.py <host> <username> <password> <file>"
	sys.exit(-1)

username = sys.argv[2]
password = sys.argv[3]
tn = telnetlib.Telnet(sys.argv[1])

f = open(sys.argv[4], 'rb')
fname = os.path.basename(sys.argv[4])

tn.read_until("Login: ")
tn.write(username + "\n")
tn.read_until("Password: ")
tn.write(password + "\n")
tn.read_until(" > ")
tn.write("sh\n")
tn.read_until("# ")
tn.write("rm /var/{0}\n".format(fname))
tn.read_until("# ")

buf = f.read(linesize)

while len(buf) > 0:
	line = ''.join(["\\x" + x.encode('hex') for x in buf])
	tn.write("echo -n -e '{0}' >> /var/{1}\n".format(line, fname))
	tn.read_until("# ")
	buf = f.read(linesize)

	sys.stdout.write("\b{0}".format(cursor[progress % 4]))
	sys.stdout.flush()
	progress += 1

f.close()

tn.write("chmod +x /var/{0}\n".format(fname))
tn.read_until("# ")

tn.write("exit\n")
tn.read_until(" > ")
tn.write("exit\n")

tn.close()
print
