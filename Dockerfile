FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
ENV DISPLAY=:1

RUN apt update && apt install -y \
    xfce4 \
    xfce4-goodies \
    tigervnc-standalone-server \
    novnc \
    websockify \
    dbus-x11 \
    xterm \
    python3 \
    python3-pip \
    nano \
    curl \
    wget \
    git \
    && apt clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . /app

EXPOSE 6080
EXPOSE 5901

CMD bash -c '\
mkdir -p /root/.vnc && \
echo "1234" | vncpasswd -f > /root/.vnc/passwd && \
chmod 600 /root/.vnc/passwd && \
printf "#!/bin/bash\n\
unset SESSION_MANAGER\n\
unset DBUS_SESSION_BUS_ADDRESS\n\
exec dbus-launch --exit-with-session startxfce4\n" > /root/.vnc/xstartup && \
chmod +x /root/.vnc/xstartup && \
vncserver :1 -geometry 1920x1080 -depth 24 && \
websockify --web=/usr/share/novnc/ 6080 localhost:5901 \
'
