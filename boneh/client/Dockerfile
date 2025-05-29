FROM almalinux:9
WORKDIR /app
RUN dnf install -y python3 && \
    dnf install -y pip && \
    pip install requests && \
    pip install ecdsa && \
    pip install sympy
COPY . .
CMD ["python3", "client.py"]
