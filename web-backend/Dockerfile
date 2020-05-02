FROM ubuntu:16.04

RUN apt-get update -y && \
	apt-get install -y python-pip python-dev
COPY web-backend/requirements.txt /requirements.txt
WORKDIR /
RUN pip install -r requirements.txt
COPY web-backend/ /
ENTRYPOINT [ "python" ]
CMD ["index.py"]

#build:  docker build -t <name of image>
#run: docker run -it --rm -p 5050:5050 <name of image>
