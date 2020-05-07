# pull official base image
FROM node:13.12.0-alpine

# set working directory
WORKDIR /

# add /app/node_modules/.bin to $PATH
ENV PATH /node_modules/.bin:$PATH

# to fix this issue: https://github.com/facebook/create-react-app/issues/8688
ENV CI true

# add app
COPY /web-interface/ /

# start app
CMD ["npm", "start"]
