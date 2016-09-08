all:
	gcc -o gfsk_finder gfsk_finder.c
	mkfifo fifo
clean:
	rm gfsk_finder
	rm fifo

