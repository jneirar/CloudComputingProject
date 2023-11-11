from pyspark.sql import SparkSession
from pyspark.ml.feature import VectorAssembler, MinMaxScaler
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
from pyspark.mllib.evaluation import MulticlassMetrics
from pyspark.sql.functions import col
import time
import numpy as np
import matplotlib.pyplot as plt
from pyspark.ml.classification import DecisionTreeClassifier

tiempo_programa = time.time()

spark = SparkSession.builder \
    .appName("Classifier") \
    .getOrCreate()

percentage = '01'
path_base = "/mnt/data" + percentage + "/"
folder_paths = [path_base + "Education",
                path_base + "Finance",
                path_base + "Games",
                path_base + "HealthFitness",
                path_base + "LifeService",
                path_base + "Music",
                path_base + "News",
                path_base + "Reading",
                path_base + "Shopping",
                path_base + "Social",
                path_base + "Tools",
                path_base + "Travel",
                path_base + "Video"
                ]

# Leer los archivos Parquet y unirlos en un solo DataFrame
data = None
for folder_path in folder_paths:
    folder_data = spark.read.parquet(folder_path)
    if data is None:
        data = folder_data
    else:
        data = data.union(folder_data)

data = data.withColumn("CLASS", col("CLASS").cast("double"))

# Seleccionar columnas de interés
selected_columns = ['CLASS', 'LEN_SRC_IP', 'LEN_DEST_IP', 'Source_IP1', 'Source_IP2', 'Source_IP3', 'Source_IP4', 'Destination_IP1', 'Destination_IP2', 'Destination_IP3', 'Destination_IP4', 'TCP_SPORT', 'TCP_DPORT', 'LEN_RAW', 'Send_Year', 'Send_Month', 'Send_Day', 'Send_Hour', 'Send_Minute', 'Send_Second']
selected_data = data.select(selected_columns)

# Definir columnas de características y objetivo
feature_columns = data.columns[1:]
target_column = data.columns[0]

# Imprimir el número de filas, columnas y clases
print("Número de filas:", data.count())
print("Número de columnas:", len(data.columns))
print("Número de clases:", data.select(target_column).distinct().count())

# Crear ensamblador de características
assembler = VectorAssembler(inputCols=feature_columns, outputCol='features')
data = assembler.transform(data)

# Crear objeto MinMaxScaler
scaler = MinMaxScaler(inputCol='features', outputCol='scaledFeatures')

# Calcular estadísticas resumen y normalizar características
scaler_model = scaler.fit(data)
data = scaler_model.transform(data)

# Dividir los datos en conjuntos de entrenamiento y prueba
train_data, test_data = data.randomSplit([0.8, 0.2], seed=42)

# Entrenar el modelo
dt = DecisionTreeClassifier(labelCol=target_column, featuresCol='features', seed=42)
start_time =time.time()
model = dt.fit(train_data)
total_time = time.time() - start_time
predictions = model.transform(test_data)

# Calcular métricas de evaluación
evaluator_accuracy = MulticlassClassificationEvaluator(labelCol=target_column, predictionCol="prediction", metricName="accuracy")
evaluator_precision = MulticlassClassificationEvaluator(labelCol=target_column, predictionCol="prediction", metricName="weightedPrecision")
evaluator_recall = MulticlassClassificationEvaluator(labelCol=target_column, predictionCol="prediction", metricName="weightedRecall")
evaluator_f1 = MulticlassClassificationEvaluator(labelCol=target_column, predictionCol="prediction", metricName="f1")

accuracy = evaluator_accuracy.evaluate(predictions)
precision = evaluator_precision.evaluate(predictions)
recall = evaluator_recall.evaluate(predictions)
f1 = evaluator_f1.evaluate(predictions)

# Calcular matriz de confusión
predictionAndLabels = predictions.select("prediction", target_column).rdd
metrics = MulticlassMetrics(predictionAndLabels)
confusion_matrix = metrics.confusionMatrix()

tiempo_programa_final = time.time() - tiempo_programa

print("-----------Resultados para el modelo decision-tree con 60% de datos----------- ")

print("Accuracy:", accuracy)
print("Precision:", precision)
print("Recall:", recall)
print("F1 Score:", f1)
print("Duración de entrenamiento: ", total_time,"seg")
print("Duración total del programa: ", tiempo_programa_final,"seg")

confusion_matrix_np = confusion_matrix.toArray()

# Crear una figura y un eje
fig, ax = plt.subplots()

# Plotear la matriz de confusión como una imagen
im = ax.imshow(confusion_matrix_np, cmap='Blues')

# Configurar etiquetas de ejes
ax.set_xlabel('Predicted')
ax.set_ylabel('Actual')

# Crear una barra de color
cbar = ax.figure.colorbar(im, ax=ax)

# Configurar los valores de la matriz como etiquetas en cada celda
for i in range(confusion_matrix_np.shape[0]):
    for j in range(confusion_matrix_np.shape[1]):
        ax.text(j, i, '{:.2f}'.format(confusion_matrix_np[i, j]), ha='center', va='center', color='white', fontsize=0)

ax.set_xticks(np.arange(confusion_matrix_np.shape[1]))
ax.set_yticks(np.arange(confusion_matrix_np.shape[0]))

plt.setp(ax.get_xticklabels(), rotation = 45, ha= "right", rotation_mode = "anchor")
# Guardar la figura como un archivo PNG
im.set_clim(vmin=0, vmax=confusion_matrix_np.max() * 0.8)

output_directory = path_base + "output_images/"
filename = output_directory + "confusion_matrix_dt_" + percentage + "%.png"

# Asegúrate de que el directorio exista o créalo
import os
if not os.path.exists(output_directory):
    os.makedirs(output_directory)

# Guarda la figura en la ruta especificada
plt.savefig(filename, dpi=300)

# Cerrar SparkContext y SparkSession
spark.stop()