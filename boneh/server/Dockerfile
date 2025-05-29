FROM almalinux:9
WORKDIR /app
RUN dnf install -y python3 && \
    dnf install -y pip && \
    dnf install -y mod_ssl && \
    pip install flask && \
    pip install ecdsa && \
    pip install gunicorn && \
    pip install redis && \
    pip install sympy

COPY . .

RUN cat certs/server.crt >> /etc/pki/tls/certs/ca-bundle.crt

CMD ["gunicorn","--certfile", "certs/server.crt", "--keyfile", "certs/server.key", "-b", "0.0.0.0:443", "-w", "4", "--timeout", "300", "server:app"]
