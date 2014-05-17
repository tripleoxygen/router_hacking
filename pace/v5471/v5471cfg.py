#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# v5471cfg - Pace V5471 configuration diff file encoder and decoder
#
# The router.bin file is actually a 'tar' file scrambled by a quite
# simple algo based on bitwise operations.
#
# Inside the tar, there are 2 important files:
#
#  * router.diff -	A diff against the modem default configuration.
#					Lines starting with '-' means UNSET that parameter,
#					while "+" lines SETS it.
#
#  * router.magic - Simple verification/check for the router.diff file.
#					It contains the file size of router.diff in ASCII.
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

import sys

MAGIC_UNSCRAMBLE = 0x765432
MAGIC_SCRAMBLE = 0x7fffff

HEADER = bytearray([0xff, 0xff, 0xaa, 0xaa, 0xaa])

def decode(buf):
	reg = MAGIC_UNSCRAMBLE

	for i in range(len(buf)):
		xor = ((reg >> 5) ^ reg) & 0xff
		reg >>= 8
		reg += ((buf[i] & 0xff) << 15)
		buf[i] ^= xor

def encode(buf):
	reg = MAGIC_SCRAMBLE

	for i in range(len(buf)):
		xor = ((reg >> 5) ^ reg) & 0xff
		buf[i] ^= xor
		reg >>= 8
		reg += ((buf[i] & 0xff) << 15)		
	
def usage():
	print("Usage:")
	print()
	print("v5471cfg.py [mode] [input] [output]\n")
	print("mode\t-e\tEncode file")
	print("\t-d\tDecode file")
	print("input\t\tInput file name")
	print("output\t\tOutput file name")
	print()
	print("Example:")
	print("\tTo decode the file 'router.bin' to 'router.tar':")
	print("\tv5471cfg.py -d router.bin router.tar")
	print()
	print("\tTo encode the file 'router.tar' to 'router.new.bin':")
	print("\tv5471cfg.py -e router.tar router.new.bin")
	print()
	
def main(args):
	print()
	print("Pace V5471 Configuration diff file Encoder / Decoder")
	print("Copyright (C) 2014  Triple Oxygen <oxy@g3n.org>")
	print()
	
	if len(args) != 4:
		usage()
		sys.exit(-1)
	
	mode = args[1]
	
	if (mode == '-d' or mode == '-e'):
		try:
			i = open(args[2], 'rb')
			buf = bytearray(i.read())
			i.close()
			
			if (mode == '-e'):
				print("[+] Encoding data.")
				buf = HEADER[2:] + buf
				encode(buf)
				buf = HEADER[:2] + buf
				
			else:
				print("[+] Decoding data.")
				decode(buf)
				buf = buf[5:]
				
			o = open(args[3], 'wb')
			o.write(buf)
			o.close()
			
		except IOError as e:
			print("[!] Error: {0}.".format(e.strerror))
		else:
			print("[+] Done!")		
		
	else:
		print("[-] Unknown mode.")
	
	print()
		
if __name__ == '__main__':
	main(sys.argv)
