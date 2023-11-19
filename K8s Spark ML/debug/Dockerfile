FROM apache/spark-py:latest

USER root

RUN pip install --no-cache-dir numpy pandas matplotlib

COPY list_directories.py /list_directories.py
COPY data01 /data01

RUN chmod +x /list_directories.py

CMD ["spark-submit", "/list_directories.py"]
