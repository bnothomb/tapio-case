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

## API documentation
```
python tapioview/manage.py runserver
# Available at http://127.0.0.1:8000/api/schema/swagger-ui/
```

## Run
```
python tapioview/manage.py runserver
# Run on http://127.0.0.1:8000/
# Test user : admin/admin
```

## Run in docker
```
# Warning ! No data persistence for the moment !
docker build tapioview/ -t docker-tapioview
docker run -d --publish 5000:8000 docker-tapioview
# Run on http://127.0.0.1:5000/
```


## Test
```
ruff --format=github .

python tapioview/manage.py test

coverage run --source='.' tapioview/manage.py test
coverage report
```