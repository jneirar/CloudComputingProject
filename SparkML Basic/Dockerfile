# Usa la imagen base de Apache Spark para Python
FROM apache/spark-py:latest

# Copia tu código de la aplicación al contenedor
COPY entrenamiento.py /entrenamiento.py

CMD ["ls"]
CMD ["spark-submit", "entrenamiento.py"]