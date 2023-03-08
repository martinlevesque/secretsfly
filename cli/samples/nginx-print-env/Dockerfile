FROM alpine:latest

RUN apk add --no-cache curl
RUN apk add --no-cache python3
#RUN curl https://raw.githubusercontent.com/martinlevesque/secretsfly/main/cli/cli.py -o /usr/local/bin/secretsfly \
#    && chmod +x /usr/local/bin/secretsfly
COPY cli.py /usr/local/bin/secretsfly
RUN chmod +x /usr/local/bin/secretsfly

CMD ["python3", "/usr/local/bin/secretsfly", "--", "env"]