FROM ubuntu:latest

RUN apt-get update -y && \
	apt-get install -y python3 python3-pip python3-dev
WORKDIR /
COPY /web-backend/ /
RUN pip3 install -r requirements.txt

CMD ["sleep", "10000"]
#CMD ["python3", "index.py"]

