FROM debezium/connect:2.7.3.Final

USER root

RUN curl -L -o /tmp/kafka-connect-s3.zip "https://api.hub.confluent.io/api/plugins/confluentinc/kafka-connect-s3/versions/12.1.4/archive"

RUN mkdir -p /kafka/connect/kafka-connect-s3 \
    && unzip /tmp/kafka-connect-s3.zip -d /kafka/connect/kafka-connect-s3 \
    && rm /tmp/kafka-connect-s3.zip

USER 1001