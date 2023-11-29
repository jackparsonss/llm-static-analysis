.PHONY: build fetch data experiment clean codeql-mac codeql-linux codeql-windows

build:
	python3 -mvenv .
	. bin/activate && pip3 install -r requirements.txt

codeql-mac:
	. bin/activate && python3 src/scripts/codeql_installer.py --os=osx

codeql-linux:
	. bin/activate && python3 src/scripts/codeql_installer.py --os=linux

codeql-windows:
	. bin/activate && python3 src/scripts/codeql_installer.py --os=win

fetch:
	. bin/activate && python3 src/scripts/data_downloader.py

data:
	. bin/activate && python3 src/data.py

experiment:
	. bin/activate && python3 src/main.py --test_llm gpt-3.5 --rank_llm gpt-3.5

clean:
	rm -rf *_output
