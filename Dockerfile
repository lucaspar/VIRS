FROM python:3
ENV PYTHONUNBUFFERED 1

# Get latest updates
RUN apt-get update && apt-get upgrade -y

# Create less privileged user
RUN groupadd -r app && \
    useradd -r -g app -d /home/app -s /sbin/nologin -c "Docker image user" app

# Create working directory
ENV APP_DIR=/virs/
RUN install -g app -o app -d ${APP_DIR}
WORKDIR $APP_DIR

# Install project requirements
ADD requirements.txt $APP_DIR
RUN pip install -r requirements.txt
ADD . $APP_DIR

# Set permissions
RUN find ${APP_DIR} -type d -exec chmod g+s {} \;
RUN chmod -R g+w ${APP_DIR}

# Select user
USER app
