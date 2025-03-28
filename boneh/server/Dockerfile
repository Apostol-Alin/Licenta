FROM almalinux:9
WORKDIR /app
RUN dnf install -y python3 && \
    dnf install -y pip && \
    pip install flask && \
    pip install ecdsa && \
    pip install sympy
COPY PedersenCommitmentScheme.py .
COPY TC.py .
COPY server.py .
CMD ["python3", "server.py"]
