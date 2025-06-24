FROM eclipse-mosquitto:latest

WORKDIR /mosquitto
RUN mkdir -p /mosquitto/config
RUN mkdir -p /mosquitto/data
RUN mkdir -p /mosquitto/log

RUN echo persistence true > /mosquitto/config/mosquitto.conf && \
    echo persistence_location /mosquitto/data/ >> /mosquitto/config/mosquitto.conf && \
    echo log_dest file /mosquitto/log/mosquitto.log >> /mosquitto/config/mosquitto.conf && \
    echo allow_anonymous true >> /mosquitto/config/mosquitto.conf && \
    echo listener 9001 >> /mosquitto/config/mosquitto.conf && \
    echo protocol websockets >> /mosquitto/config/mosquitto.conf && \
    echo listener 1883 >> /mosquitto/config/mosquitto.conf && \
    echo protocol mqtt >> /mosquitto/config/mosquitto.conf