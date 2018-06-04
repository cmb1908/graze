.PHONY: all package upload image run

all: package upload image

package:
	python3 setup.py sdist bdist_wheel

upload:
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*

image:
	docker build -t graze .

bash:
	docker run -v `pwd`:/usr/src/app/dev --privileged -it graze bash

run:
	docker run --privileged -p 4000:80 -d -it graze

scrape:
	scrape 'https://www.apps08.osr.nsw.gov.au/erevenue/ucm/ucm_list.php'

