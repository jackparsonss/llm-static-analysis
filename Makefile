.PHONY: build fetch data experiment clean

build:
	python3 -mvenv .
	. bin/activate && pip3 install -r requirements.txt

fetch:
	. bin/activate && python3 src/data_downloader.py

data:
	. bin/activate && python3 src/data.py

experiment:
	. bin/activate && python3 src/main.py --test_llm gpt-3.5 --rank_llm gpt-3.5

clean:
	rm -rf *_output
