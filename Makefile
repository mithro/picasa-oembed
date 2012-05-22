
build:
	python index.py > static/index.html

upload: build
	../google_appengine/appcfg.py --oauth2 update .

serve: build
	../google_appengine/dev_appserver.py -a 0.0.0.0 .
