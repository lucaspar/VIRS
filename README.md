VIRS
===
**_Visualization and Information Retrieval System_**

Construído com o Web Framework Django. Pronto para rodar com Docker.

### Execução

#### 1. Terminal 1 - executar containers
```bash
docker-compose up
```

#### 2. Terminal 2 - executar shell interativo

```bash
docker-compose run web bash

# executar migrações
./manage.py makemigrations
./manage.py migrate
```

#### 3. Acessar página em localhost:8000

### Outros procedimentos

##### Reiniciar containers

```bash
docker-compose down
docker-compose up
```

##### Database wipe

```bash
docker-compose down
mv postgres-data postgres-data.backup
# neste ponto é necessário re-executar as migrações
# para executar o projeto novamente
```

##### Executar migrações

```bash
# com os containers rodando, executar:
docker-compose run web bash
./manage.py makemigrations
./manage.py migrate
```

##### Finalizar

```bash
docker-compose down
```

##### Criar django superuser

```bash
docker-compose run web bash
./manage.py createsuperuser
# logar como admin em localhost:8000/admin
```

##### Redefinir permissões para usuário local

```bash
pwd
# confirme 3x que está na raiz do projeto
sudo chown $USER:$USER -R .
```
