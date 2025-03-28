FROM almalinux:9
WORKDIR /app
RUN dnf install -y python3 && \
    dnf install -y pip && \
    pip install requests && \
    pip install ecdsa && \
    pip install sympy
COPY PedersenCommitmentScheme.py .
COPY TC.py .
COPY client.py .
CMD ["python3", "client.py"]
