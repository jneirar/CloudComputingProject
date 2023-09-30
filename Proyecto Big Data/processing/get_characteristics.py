# Librerías utilizadas
from pyspark import SparkConf, SparkContext
from pyspark.sql import SparkSession
from pyspark.ml.feature import VectorAssembler, MinMaxScaler
from pyspark.ml.classification import RandomForestClassifier
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
from pyspark.mllib.evaluation import MulticlassMetrics
import matplotlib.pyplot as plt
# Crear SparkContext y SparkSession
spark = SparkSession.builder \
    .appName("Classifier") \
    .master("yarn") \
    .config("spark.eventLog.enabled", "true") \
    .config("spark.eventLog.dir", "hdfs://node-master:9000/spark-logs") \
    .config("spark.executor.memory", "512m") \
    .config("spark.driver.memory", "512m") \
    .getOrCreate()

path_base = "hdfs://node-master:9000/user/azureuser/dataModel/"
folder_paths = [path_base + "Education",
                path_base + "Finance",
                path_base + "Games",
                path_base + "HealthFitness",
                path_base + "Music",
                path_base + "News",
                path_base + "Reading",
                path_base + "Shopping",
                path_base + "Travel"
                ]

# Leer los archivos Parquet y unirlos en un solo DataFrame
data = None
for folder_path in folder_paths:
    folder_data = spark.read.parquet(folder_path)
    if data is None:
        data = folder_data
    else:
        data = data.union(folder_data)

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

# Obtener el número de columnas
num_columns = 4

# Crear la figura y los ejes para los boxplots
fig, axs = plt.subplots(num_columns-1, 1, figsize=(8, num_columns*4))

# Configurar el título y etiquetas de los ejes
fig.suptitle("Boxplot por Columna", fontsize=16)
axs[-1].set_xlabel("Valores", fontsize=12)

# Recorrer cada columna y generar un boxplot por separado
for i in range(18,20):
    # Obtener el nombre de la columna actual
    column_name = selected_columns[i]

    # Obtener los datos de la columna como una lista
    column_data = selected_data.select(column_name).rdd.flatMap(lambda x: x).collect()

    # Dibujar el boxplot en el eje correspondiente
    axs[i-18].boxplot(column_data, vert=False, patch_artist=True)

    # Configurar el título y etiquetas del eje y
    axs[i-18].set_title(column_name, fontsize=14)
    axs[i-18].set_ylabel("")

# Ajustar el espacio entre subplots
plt.subplots_adjust(hspace=0.4)

# Guardar los boxplots como archivos PNG por cada columna
for i in range(18,20):
    # Obtener el nombre de la columna actual
    column_name = selected_columns[i]

    # Guardar el boxplot de la columna actual como un archivo PNG
    plt.savefig(f"{column_name}_boxplot.png")

# Cerrar SparkContext y SparkSession
spark.stop()
