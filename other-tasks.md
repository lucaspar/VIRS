# Tasks

### **Finish**

```bash
docker-compose down
```

### **Restart containers**

```bash
docker-compose down
docker-compose up
```

### **Wipe database**

```bash
docker-compose down
sudo mv .db/ .db.backup/
```

### **Running migrations**

```bash
# with containers running, open an interactive shell with:
docker-compose run web bash

./manage.py makemigrations
./manage.py migrate
```

### **Create Django superuser**

```bash
docker-compose run web bash
./manage.py createsuperuser
# login to admin dashboard at localhost:8000/admin
```

### **Rebuild**

If Docker files or image change

```bash
docker-compose down
sudo mv .db/ .db.backup/
docker-compose build
docker-compose up
```

### **Set permissions for local user**

```bash
pwd
# if at this project root, proceed with:
sudo chown $USER:$USER -R .
```



