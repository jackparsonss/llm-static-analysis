.PHONY: data experiment

build:
	python3 -mvenv .
	. bin/activate && pip3 install -r requirements.txt

data:
	. bin/activate && python3 src/data.py

experiment:
	. bin/activate && python3 src/main.py
