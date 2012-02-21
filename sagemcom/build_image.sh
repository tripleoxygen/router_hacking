#!/bin/bash

SAGEM_BUILD="./sagem_build"
MKSQUASHFS="/opt/bcm963xx_router/hostTools/mksquashfs"
SEC_CODE="SAGEM"

ROOTFS_DIR="$1"
KERNEL="$2"
OUTPUT="$3"

VERSION="0.1"

function usage() {
	echo "$0 <rootfs_dir> <kernel_file> <output_file>"
	echo "e.g. $0 ./rootfs kernel.lzma.cfe output/firmware.bin"
}

echo "sagemcom firmware image build $VERSION"

if [ $# -ne 3 ]; then
	usage
	exit 1
fi

if [ ! -d $ROOTFS_DIR ] || [ ! -e $KERNEL ]; then
	echo "one or more items not found"
	exit 1
fi

# simple sanity check...
if [ ! -e $ROOTFS_DIR/linuxrc ]; then
	echo "are you sure this rootfs directory is the right one?"
	exit 1
fi

if [ ! -d "tmp" ]; then
	mkdir -p tmp
else
	rm -rf tmp/*
fi

echo "building root filesystem..."

rm -rf tmp/rootfs.sqsh tmp/image
$MKSQUASHFS $ROOTFS_DIR tmp/rootfs.sqsh -all-root -be

echo "creating image..."
cat tmp/rootfs.sqsh $KERNEL > tmp/image

if [ ! -d `dirname $OUTPUT` ]; then
	mkdir -p `dirname $OUTPUT`
fi

if [ -e "tmp/image" ] && [ -e "tmp/rootfs.sqsh" ]; then

	echo "generating firmware tag..."
	$SAGEM_BUILD tmp/image tmp/rootfs.sqsh $KERNEL $SEC_CODE tmp/tag

	if [ $? -ne 0 ]
	then
		echo "sagem_build failed"
		exit 1
	fi

	cat tmp/tag tmp/image > $OUTPUT

	echo "done!"
	exit 0
fi

echo "failed to produce intermediate files"
exit 1
