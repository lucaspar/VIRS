VIRS
===
**_Visualization and Information Retrieval System_**

Construído com o Web Framework Django. Pronto para rodar com Docker.

### Execução

**1. Terminal 1 - executar serviço**
```bash
docker-compose up
```

**2. Terminal 2 - executar shell interativo**
```bash
docker-compose run web bash

# executar migrações
./manage.py makemigrations
./manage.py migrate
```

**3. Acessar página em localhost:8000**
