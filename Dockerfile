FROM alpine:3.17

RUN apk add --no-cache python3-dev \
    && python3 -m ensurepip \
    && pip3 install --upgrade pip

WORKDIR /opt/magda

# Upgrade and install Python packages
COPY ./requirements.txt /opt/magda/requirements.txt
RUN pip3 --no-cache-dir install -r /opt/magda/requirements.txt

# Make necessary folders in the container including code, tests, bin etc.
RUN mkdir app bin tests

# Copy in needed folders into the image
COPY alembic.ini ./
COPY vars.env ./
COPY app ./app
COPY bin ./bin
COPY tests ./tests
