# SpeedRecord-python-MQTT-Queue

### README.md

# Projet de Surveillance de Vitesse avec RabbitMQ et MySQL

Ce projet utilise RabbitMQ pour la messagerie et MySQL pour le stockage des données de vitesse. Il comprend également une API RESTful pour récupérer les données de la base MySQL et les envoyer au client sous forme de fichier JSON.

## Prérequis

- Docker
- Docker Compose

## Structure du Projet

```
.
├── Dockerfile
├── Dockerfile.api
├── api.py
├── main.py
├── docker-compose.yml
└── README.md
```

## Configuration

### Dockerfile

Le fichier `Dockerfile` est utilisé pour construire l'image Docker de l'application principale (`main.py`).

```Dockerfile
# Utiliser une image de base Python
FROM python:3.9-slim

# Définir des variables d'environnement
ENV PYTHONUNBUFFERED=1

# Installer les dépendances
RUN apt-get update && apt-get install -y \
    build-essential \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# Copier les fichiers de l'application dans le conteneur
COPY . /app
WORKDIR /app

# Installer les dépendances Python
RUN pip install --no-cache-dir pika mysql-connector-python

# Exposer le port sur lequel l'application va tourner
EXPOSE 5672 3306

# Commande pour démarrer l'application
CMD ["python", "main.py"]
```

### Dockerfile.api

Le fichier `Dockerfile.api` est utilisé pour construire l'image Docker de l'API (`api.py`).

```Dockerfile
# Utiliser une image de base Python
FROM python:3.9-slim

# Définir des variables d'environnement
ENV PYTHONUNBUFFERED=1

# Installer les dépendances
RUN apt-get update && apt-get install -y \
    build-essential \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# Copier les fichiers de l'application dans le conteneur
COPY . /app
WORKDIR /app

# Installer les dépendances Python
RUN pip install --no-cache-dir flask mysql-connector-python

# Exposer le port sur lequel l'application va tourner
EXPOSE 5000

# Commande pour démarrer l'application
CMD ["python", "api.py"]
```

### docker-compose.yml

Le fichier `docker-compose.yml` est utilisé pour configurer et démarrer les services RabbitMQ, MySQL, l'application principale et l'API.

```yaml
version: '3.8'

services:
  rabbitmq:
    image: "rabbitmq:3-management"
    ports:
      - "5672:5672"
      - "15672:15672"
    environment:
      RABBITMQ_DEFAULT_USER: guest
      RABBITMQ_DEFAULT_PASS: guest

  mysql:
    image: "mysql:5.7"
    ports:
      - "3306:3306"
    environment:
      MYSQL_ROOT_PASSWORD: root
      MYSQL_DATABASE: speed_data_db

  app:
    build:
      context: .
      dockerfile: Dockerfile
    depends_on:
      - rabbitmq
      - mysql
    links:
      - rabbitmq
      - mysql
    environment:
      - RABBITMQ_HOST=rabbitmq
      - MYSQL_HOST=mysql

  api:
    build:
      context: .
      dockerfile: Dockerfile.api
    depends_on:
      - mysql
    ports:
      - "5000:5000"
    environment:
      - MYSQL_HOST=mysql
```

## Exécution

### Construire les images Docker

```bash
docker-compose build
```

### Démarrer les conteneurs Docker

```bash
docker-compose up
```

### Tester l'API

Une fois que les conteneurs sont en cours d'exécution, vous pouvez tester l'API en accédant à l'URL suivante dans votre navigateur ou en utilisant un outil comme `curl` ou Postman :

```
http://localhost:5000/speed_data
```

Cela devrait retourner les données de la base MySQL sous forme de JSON.

## Logs

Pour vérifier les logs des conteneurs, utilisez la commande suivante :

```bash
docker-compose logs
```

## Auteur

- **Niko Stinko** - *Niko Stinko* - [Niko Stinko](https://github.com/NikoStinko)
- **Erythroz** - *Erythroz* - [Erythroz](https://github.com/erythroz)

## Licence

Ce projet est sous licence MIT
