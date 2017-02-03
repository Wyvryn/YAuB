all:
	make env
	make deps
	make db

help:
	@echo "  env         create a development environment using virtualenv"
	@echo "  deps        install dependencies using pip"
	@echo "  db          Migrates the database"
	@echo "  clean       remove unwanted files like .pyc's"
	@echo "  lint        check style with flake8"
	@echo "  isort       sort imports with isort"

env:
	sudo easy_install pip && \
	pip install virtualenv && \
	virtualenv env

deps:
	( \
		. env/bin/activate && \
		pip install -r requirements/requirements.txt && \
		nodeenv -p --prebuilt && \
		npm install -g bower && \
		bower install --allow-root \
	)
	patch -p1 < patches/datetimepicker.patch

db:
	. env/bin/activate && \
	python manage.py db upgrade

clean:
	find . -name \*.pyc -delete

lint:
	flake8 --exclude=env,migrations,docs .

isort:
	isort --recursive YAuB/.
