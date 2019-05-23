#docker build -t serverssh -f ./testServer.Dockerfile .
#docker run -d  -p 10000:22   serverssh


FROM ubuntu

ENV TERM xterm

RUN apt-get -y update \
    && apt-get -y install openssh-server \
    && mkdir -p /var/run/sshd \
    && mkdir /root/.ssh && chmod 700 /root/.ssh \
    && touch /root/.ssh/authorized_keys \
    && apt-get clean all


RUN ssh-keygen -t rsa -C "thisisnotanemail@gmail.com" -N "" -f /root/.ssh/id_rsa \
    && cat /root/.ssh/id_rsa.pub >> /root/.ssh/authorized_keys \
    && cat /root/.ssh/id_rsa


ENTRYPOINT ["/usr/sbin/sshd", "-D"]
