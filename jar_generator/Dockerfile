FROM node:alpine3.16 AS nodejs-env
RUN apk add git \
  && git clone https://github.com/CodinGame/SummerChallenge2024Olymbits.git --depth 1 \
  && mv SummerChallenge2024Olymbits CodinGameChallenge \
  && cd CodinGameChallenge/src/main/resources/view \
  && yarn install \
  && yarn run tsc \
  && rm -rf node_modules


FROM maven:3.6.3-openjdk-17-slim as maven-env
COPY --from=nodejs-env /CodinGameChallenge /CodinGameChallenge
RUN cd /CodinGameChallenge \
  && mv src/test/java/Main.java src/main/java/Main.java \
  && mvn assembly:assembly -DdescriptorId=jar-with-dependencies \
  && mv ./target/*.jar ./ \
  && mvn clean

