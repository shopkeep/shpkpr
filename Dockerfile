FROM python:3.6.15-slim-bullseye

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

# install the application locally
COPY . /usr/src/app
RUN pip install --no-cache-dir 'pytest-runner==5.3.2' && \
    pip install --no-cache-dir .

CMD ["shpkpr"]
