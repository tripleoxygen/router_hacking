
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

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include <zlib.h>
#include <openssl/aes.h>

#include "sagem_build.h"

#define TAG_SIZE	256
#define TAG_SIZE_CRC	(256 - 20)
#define AES_BLOCK_SIZE	16
#define	NUM_DATA	3
#define CHUNK_SIZE	(64 * 1024)

#define VERSION		"0.1"
#define BANNER		"sagem_build v"VERSION"\n\n"

enum idx {
	IDX_IMAGE,
	IDX_ROOTFS,
	IDX_KERNEL,
};

inline static uint32_t swap(uint32_t n)
{
	uint32_t m;

	m  = (n & 0xff000000) >> 24;
	m |= (n & 0x00ff0000) >> 8;
	m |= (n & 0x0000ff00) << 8;
	m |= (n & 0x000000ff) << 24;

	return m;
}

static uint32_t get_aes_crc(uint32_t crc, const sagem_key *k)
{
	unsigned char buf[3][AES_BLOCK_SIZE];
	AES_KEY aes_key;

	memset(buf, '\0', 3 * AES_BLOCK_SIZE);
	memcpy(buf[0], k->sec_code, AES_BLOCK_SIZE);

	AES_set_encrypt_key(k->key, 128, &aes_key);
	AES_encrypt(buf[0], buf[1], &aes_key);

	*((uint32_t *)buf[2]) = swap(crc);

	AES_set_encrypt_key(buf[1], 128, &aes_key);
	AES_encrypt(buf[2], buf[0], &aes_key);

	/* flip the normal crc back before seeding it */
	return (uint32_t)((~crc32(~crc, buf[0], 16)) & 0xffffffffUL);
}

/* output is BCM-type (~crc) */
static int get_file_crc32(const char *f, uint32_t *crc, uint32_t *sz)
{
	size_t read;
	FILE *fp;
	unsigned char *buf;

	if(!crc || !f)
		return 1;

	*crc = crc32(0L, Z_NULL, 0);
	*sz = 0;

	if((fp = fopen(f, "rb")) == 0) {
		return 1;
	}

	buf = (unsigned char *)malloc(CHUNK_SIZE);

	while((read = fread(buf, 1, CHUNK_SIZE, fp)) > 0) {
		*crc = crc32(*crc, buf, read);
		*sz += read;
	}

	fclose(fp);
	free(buf);

	*crc = (~(*crc)) & 0xffffffffUL;

	return 0;
}

static void build_tag(PFILE_TAG tag, uint32_t crcs[NUM_DATA], uint32_t sizes[NUM_DATA])
{
	char tmp[16];

	memset(tag, '\0', sizeof(*tag));

	/* default values found inside original image */
	tag->tagVersion[0] = '6';
	strcpy(tag->signiture_1, "Broadcom Corporatio");
	strcpy(tag->signiture_2, "ver. 2.0");
	strcpy(tag->chipId, "6338");
	strcpy(tag->boardId, "F@ST1704");
	tag->bigEndian[0] = '1';
	tag->cfeAddress[0] = '0';
	tag->cfeLen[0] = '0';
	tag->psiLength[0] = '0';
	tag->iniLength[0] = '0';
	tag->backupLength[0] = '0';

	/* dynamic entries - sizes */
	snprintf(tmp, sizeof(tmp), "%u", sizes[IDX_IMAGE]);
	strcpy(tag->totalImageLen, tmp);
	snprintf(tmp, sizeof(tmp), "%u", sizes[IDX_ROOTFS]);
	strcpy(tag->rootfsLen, tmp);
	snprintf(tmp, sizeof(tmp), "%u", sizes[IDX_KERNEL]);
	strcpy(tag->kernelLen, tmp);

	/* addresses */
	snprintf(tmp, sizeof(tmp), "%u", rootfs_addr);
	strcpy(tag->rootfsAddress, tmp);
	snprintf(tmp, sizeof(tmp), "%u", rootfs_addr + sizes[IDX_ROOTFS]);
	strcpy(tag->kernelAddress, tmp);

	/* crcs */
	tag->crc_image  = swap(crcs[IDX_IMAGE]);
	tag->crc_rootfs = swap(crcs[IDX_ROOTFS]);
	tag->crc_kernel = swap(crcs[IDX_KERNEL]);
}

static int write_tag(PFILE_TAG tag, const char *f)
{
	size_t written;
	FILE *fp;

	if(!tag || !f)
		return 1;

	if((fp = fopen(f, "wb")) == 0) {
		return 1;
	}

	written = fwrite((const void *)tag, 1, sizeof(*tag), fp);

	fclose(fp);

	assert(written == sizeof(*tag));

	return 0;
}

static void usage(char *app)
{
	printf("Usage:\t%s <image> <rootfs> <kernel> <security_code> <output_tag>\n\n", app);
}

int main(int argc, char *argv[])
{
	FILE_TAG tag;
	uint32_t aes_crc, crc, i;
	const sagem_key *key_entry;
	uint32_t data_crc[NUM_DATA];
	uint32_t data_size[NUM_DATA];
	char *security_code;

	printf(BANNER);

	if(argc != 6) {
		usage(argv[0]);
		return 1;
	}

	key_entry = NULL;
	security_code = argv[4];

	while(sagem_keys[i].sec_code[0] != '\0') {
		if(!strcmp(sagem_keys[i].sec_code, security_code)) {
			key_entry = &sagem_keys[i];
			break;
		}
		i++;
	}

	if(!key_entry) {
		fprintf(stderr, "key not found for security code '%s'\n",
			security_code);
		return 1;
	}

	printf("found key for security code '%s'\n", security_code);

	for(i = 0; i < NUM_DATA; i++) {
		if(get_file_crc32(argv[i + 1], &data_crc[i], &data_size[i])) {
			fprintf(stderr, "failed getting crc32 of '%s'\n",
				argv[i + 1]);
			return 1;
		} else {
			printf("file '%s', sz=%u, crc=%08x\n",
				argv[i + 1], data_size[i], data_crc[i]);
		}
	}

	assert((data_size[IDX_ROOTFS] + data_size[IDX_KERNEL]) == data_size[IDX_IMAGE]);

	build_tag(&tag, &data_crc[0], &data_size[0]);

	crc = crc32(0, Z_NULL, 0);
	crc = ~crc32(crc, (const Bytef *)&tag, TAG_SIZE_CRC);

	aes_crc = get_aes_crc(crc, key_entry);
	tag.crc_header = swap(aes_crc);

	if(write_tag(&tag, argv[5])) {
		fprintf(stderr, "failed writing tag to '%s'\n",
			argv[5]);
		return 1;
	}

	printf("aes_crc = %08x\n", aes_crc);

	return 0;
}
