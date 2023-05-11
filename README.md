# Tapio-case
[![CI](https://github.com/bnothomb/tapio-case/actions/workflows/ci.yml/badge.svg)](https://github.com/bnothomb/tapio-case/actions/workflows/ci.yml)


## Setup
```
python3 -m venv env
source env/bin/activate
pip install -r tapioview/requirements.txt

# Setup pre-commit linting
pre-commit install
```


## Run
```
python manage.py runserver
```

## Test
```
pre-commit run --all-files

python manage.py test

coverage run --source='.' manage.py test
coverage report
```