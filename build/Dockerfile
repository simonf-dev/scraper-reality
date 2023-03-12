FROM --platform=linux/amd64  python:3.9

COPY . /build
RUN pip3 install -r /build/requirements.in
WORKDIR /app
CMD python3 src/init_scripts.py && python3 src/endpoints.py