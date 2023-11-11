from pyspark import SparkContext, SparkConf
import os
import time

print("----------------------------------------")
print("START SPARK APLICATION")
print("----------------------------------------")

# Crear la configuración de Spark
conf = SparkConf().setAppName('DirectoryLister')
sc = SparkContext(conf=conf)

# Define el path al directorio para revisar
directory_path = '/mnt/data01'

def list_dirs_and_count_files(path):
    # Lista de subdirectorios
    dirs = [d.path for d in os.scandir(path) if d.is_dir()]

    # Lista de tuplas de subdirectorio y conteo de archivos
    dir_file_counts = []
    for sub_dir in dirs:
        # Utiliza Spark para contar los archivos
        files = [f.path for f in os.scandir(sub_dir) if f.is_file()]
        rdd = sc.parallelize(files)
        count = rdd.count()
        dir_file_counts.append((sub_dir, count))
    
    return dir_file_counts

print("----------------------------------------")
print("CALL TO FUNC")
print("----------------------------------------")

# Llamar a la función y obtener la lista de directorios y conteos de archivos
directories_and_counts = list_dirs_and_count_files(directory_path)

print("----------------------------------------")
print("PRINT:")
print("----------------------------------------")

# Imprimir los resultados
for directory, count in directories_and_counts:
    print(f"{directory} has {count} files")

# Detener el contexto de Spark
sc.stop()

print("----------------------------------------")
print("STOP SPARK APLICATION")
print("----------------------------------------")

while True:
    print("Script en ejecución... Ctrl+C para detener.")
    time.sleep(60)  