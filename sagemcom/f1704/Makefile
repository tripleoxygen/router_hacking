
TARGET=sagem_build

CC=gcc
CFLAGS=-c -Wall -I.

all: $(TARGET)

$(TARGET): sagem_build.o
	$(CC) -lz -lssl -o $@ $<

%.o: %.c sagem_build.h
	$(CC) $(CFLAGS) -c -o $@ $< 

clean:
	rm -rf *.o *~ $(TARGET)
