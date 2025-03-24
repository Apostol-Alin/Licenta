FROM almalinux:9
WORKDIR /app
COPY ./client.py .
RUN dnf install -y python3 && \
    dnf install -y pip && \
    pip install requests
CMD ["python3", "client.py"]
