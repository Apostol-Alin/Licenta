FROM almalinux:9
WORKDIR /app
COPY server.py .
RUN dnf install -y python3 && \
    dnf install -y pip && \
    pip install flask
CMD ["python3", "server.py"]
