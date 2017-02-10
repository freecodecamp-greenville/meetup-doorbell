FROM python:3.6
MAINTAINER Daniel Jones <tortxof@gmail.com>

RUN groupadd -r docker && useradd -r -g docker docker

RUN wget https://github.com/Yelp/dumb-init/releases/download/v1.2.0/dumb-init_1.2.0_amd64.deb && \
    dpkg -i dumb-init_1.2.0_amd64.deb && \
    rm dumb-init_1.2.0_amd64.deb

COPY requirements.txt /app/
WORKDIR /app
RUN pip install -r requirements.txt
COPY . /app/

USER docker

EXPOSE 5000

ENTRYPOINT ["dumb-init"]
CMD ["python3", "app.py"]
