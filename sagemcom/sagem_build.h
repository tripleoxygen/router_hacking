
/*
 *  sagem_build - Creates a valid tag for building a Sagemcom fw image
 *  Copyright (C) 2012  Triple Oxygen <oxy@g3n.org>
 *
 *  This program is free software; you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation; either version 2 of the License, or
 *  (at your option) any later version.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License along
 *  with this program; if not, write to the Free Software Foundation, Inc.,
 *  51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
 * 
 */

#ifndef _SAGEM_BUILD_H_
#define _SAGEM_BUILD_H_

#include <stdint.h>

const uint32_t rootfs_addr = 0xbfc10100; /* 3217096960 */

typedef struct _sagem_key {
	char sec_code[16];
	unsigned char key[16];
} sagem_key;

const sagem_key sagem_keys[] = {
	{
	.sec_code = "STC",
	.key = "\x5d\x3e\x15\x42\x28\xae\xd2\xa6\xab\xf7\x15\x62\x09\x1d\x4f\x3c",
	},
	{
	.sec_code = "SONAECOM",
	.key = "\x2b\x7e\x15\x16\x37\xae\xc2\xa6\xb7\xf7\xa3\x44\x09\xcf\x4f\x3c",
	},
	{
	.sec_code = "SAGEM",
	.key = "\x2b\x7e\x15\x16\x28\xae\xd2\xa6\xab\xf7\x15\x88\x09\xcf\x4f\x3c",
	},
	{
	.sec_code = "",
	.key = "",
	},
};

/* taken from GPLed code: shared/opensource/include/bcm963xx/bcmTag.h */
typedef struct _FILE_TAG
{
	char tagVersion[4]; // tag version. Will be 2 here.
	char signiture_1[20]; // text line for company info
	char signiture_2[14]; // additional info (can be version number)
	char chipId[6]; // chip id
	char boardId[16]; // board id
	char bigEndian[2]; // if = 1 - big, = 0 - little endia of the host
	char totalImageLen[10]; // the sum of all the following length
	char cfeAddress[12]; // if non zero, cfe starting address
	char cfeLen[10]; // if non zero, cfe size in clear ASCII text.
	char rootfsAddress[12]; // if non zero, filesystem starting address
	char rootfsLen[10]; // if non zero, filesystem size in clear ASCII text.
	char kernelAddress[12]; // if non zero, kernel starting address
	char kernelLen[10]; // if non zero, kernel size in clear ASCII text.
	char imageSequence[4]; // incrments everytime an image is flashed
	char psiLength[10]; //save psi length
	char iniLength[10]; // save INI length
	char backupLength[10]; //save backup length
	char reserved[44]; // reserved for later use
	uint32_t crc_image;
	uint32_t crc_rootfs;
	uint32_t crc_kernel;
	char imageValidationToken[8]; // image validation token - can be crc, md5, sha; for
					// now will be 4 unsigned char crc
	uint32_t crc_header;
	char tagValidationToken[16]; // validation token for tag(from signiture_1 to end of
					// imageValidationToken)
} FILE_TAG, *PFILE_TAG;

#endif /* _SAGEM_BUILD_H_ */
