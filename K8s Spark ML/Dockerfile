FROM apache/spark-py:latest

USER root

RUN pip install --no-cache-dir numpy pandas matplotlib

COPY training_dt.py /training_dt.py
COPY data100 /data100

RUN chmod +x /training_dt.py

CMD ["spark-submit", "/training_dt.py"]
