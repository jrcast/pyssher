FROM python:3.7.3-slim-stretch


RUN apt-get -y update \
    && apt-get -y upgrade \
    && apt-get clean all

RUN mkdir -p /pyssher/build /pyssher/keys
COPY ./ /pyssher/build/

RUN cd /pyssher/build \
    && python3 setup.py sdist \
    && cd dist \
    && pip install -U $(ls)  \
    && rm -r /pyssher/build


ENTRYPOINT ["pyssher"]
