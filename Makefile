.PHONY: build fetch data experiment clean

build:
	python3 -mvenv .
	. bin/activate && pip3 install -r requirements.txt

fetch:
	. bin/activate && python3 src/data_downloader.py

data:
	. bin/activate && python3 src/data.py

experiment:
	. bin/activate && python3 src/main.py

clean:
	rm -rf *_output
