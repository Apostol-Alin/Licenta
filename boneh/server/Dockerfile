FROM almalinux:9
WORKDIR /app
RUN dnf install -y python3 && \
    dnf install -y pip && \
    pip install flask && \
    pip install ecdsa && \
    pip install gunicorn && \
    pip install redis && \
    pip install sympy
COPY PedersenCommitmentScheme.py .
COPY TC.py .
COPY templates ./templates/
COPY static ./static/
COPY server.py .
CMD ["gunicorn", "-b", "0.0.0.0:5000", "-w", "2", "--timeout", "300", "server:app"]
# CMD ["python3", "server.py"]
