FROM --platform=linux/amd64  python:3.9

COPY . /app
RUN pip3 install -r /app/requirements.txt
WORKDIR /app
CMD python3 src/init_scripts.py && python3 src/endpoints.py