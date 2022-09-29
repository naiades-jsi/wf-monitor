# BUILDING: docker build -t <container_name> .
# RUNNING: docker run <container_name>
# e.g. docker run -d --network="host" e3ailab/wf-monitor
FROM ubuntu:20.04
RUN apt-get update -y && \
    apt-get install -y python3-pip python3-dev
COPY ./requirements.txt /requirements.txt
WORKDIR /
RUN pip3 install -r requirements.txt
COPY . /

# e3ailab/wf-monitor
CMD ["python3", "scheduler.py"]
