# pull official base image
FROM node:13.12.0-alpine

# set working directory
WORKDIR /

# add /app/node_modules/.bin to $PATH
ENV PATH /node_modules/.bin:$PATH

# add app
COPY /web-interface/ /
# start app
CMD ["sleep", "9999999"]
