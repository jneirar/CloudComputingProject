# Proyecto de Big Data

## Integrantes
- Chahua, Luis
- Neira, Jorge

## Descripción

El proyecto consiste en utilizar herramientas de Big Data y Machine Learning para clasificar la información obtenida de los paquetes de red capturados en la base de datos [ZTE_TAD](https://www.kaggle.com/datasets/camellia2013/zte-tad-dataset) de Kaggle.

## Clúster de Hadoop

Para la implementación del clúster de Hadoop se crearon 2 máquinas virtuales básicas de Linux en Azure y se siguió el siguiente [tutorial](https://www.linode.com/docs/guides/how-to-install-and-set-up-hadoop-cluster/) para la instalación de Hadoop, configuración de Yarn y de Spark.

Los archivos configurados tanto para Hadoop, Yarn y Spark se encuentran en la carpeta [config](config).

## Procesamiento de la base de datos

Luego de descargar los datos de la base de datos debemos obtener la información de los paquetes de red. Para ello se utilizó la herramienta scapy. En Linux se puede instalar con el comando:

```bash
sudo apt-get install python3-scapy
```

Para Windows, debemos instalar la herramienta npcap en el siguiente [link](https://npcap.com/#download). Luego, usamos el script [get_data_from_packets.py](processing/get_data_from_packets.py) para obtener la información de los paquetes de red y generar los archivos parquet para cada archivo pcap de la base de datos. La estructura de las carpetas es la siguiente:

- Data
    - pcap
        - Education
        - Finance
        - Games
        - Health Fitness
        - Life Service
        - Music
        - News
        - Reading
        - Shopping
        - Social
        - Tools
        - Travel
        - Video
    - parquet
- get_data_from_packets.py

El script debe ejecutarse desde la carpeta Data y creará las carpetas de las clases y sus archivos parquet correspondientes en la carpeta parquet. Para crear la información de 80%, 60%, 40% y 20% debemos configurar la variable *porcentaje* del script. Además, si deseamos obtener más información de los paquetes, debemos descomentar las líneas y comentar las líneas que seleccionan solo las características que se utilizarán para el entrenamiento de los modelos.

## Subir archivos al HDFS

Para subir la información al cluster, debemos asegurarnos que esté corriendo. Para ello el comando jps nos confirmará los procesos que están corriendo en cada nodo. En caso no estén corriendo, debemos ejecutar el comando start-all.sh para iniciarlos. Si tenemos 2 nodos, un ejemplo de la salida del comando jps en el nodo master sería:

```bash
1860 DataNode
3301 ResourceManager
3830 Jps
1691 NameNode
3467 NodeManager
2109 SecondaryNameNode
```

y en el nodo worker:

```bash
2321 NodeManager
1796 DataNode
2444 Jps
```

Si el clúster de Hadoop no cuenta con suficientes recursos, debemos tener cuidado al subir la data. Con el comando
    
```bash
hdfs dfsadmin -report
```

podemos ver el espacio disponible en el clúster de HDFS. Para subir la información, enviamos primero la data desde nuestro computador local al nodo master con el comando:

```bash
scp -r Data/ <usuario>@<ip>:/ruta/destino
```

y luego, desde el nodo master, enviamos la información al HDFS con el comando:

```bash
hdfs dfs -put /ruta/destino/Data /ruta/destino
```
## Ejecución de scripts de PySpark

Para ejecutar los scripts de PySpark, debemos enviar el archivo al nodo master y ejecutar el comando:

```bash
spark-submit --master yarn --num-executors 2 --executor-cores 2 --deploy-mode client  file.py
```

Para las máquinas virtuales que se crearon en Azure, podemos utilizar un máximo de 2 *executors* y 2 *cores* por *executor*.

## Características

Para obtener información de las características, usamos el script [get_characteristics.py](processing/get_characteristics.py). Este script carga los archivos parquet del clúster de HDFS y obtiene información sobre las características de la base de datos y genera gráficos de boxplot para cada característica.

## Entrenamiento de modelos

### Random Forest

Para el entrenamiento del modelo de Random Forest, usamos el script [random_forest.py](models/random_forest.py). Este script carga los archivos parquet del clúster de HDFS y entrena el modelo de Random Forest. Luego, se evalúa el modelo con la data de test e imprime las métricas de accuracy, precision, recall y f1 score, además del tiempo de entrenamiento y el tiempo total del programa. También se genera la matriz de confusión del modelo en una imagen.

### Decision Tree

El entrenamiento es similar al de Random Forest, pero con el script [decision_tree.py](models/decision_tree.py).

### Multilayer Perceptron

El entrenamiento es similar al de Random Forest, pero con el script [multilayer_perceptron.py](models/multilayer_perceptron.py).

## Referencias

- [Base de datos](https://www.kaggle.com/datasets/camellia2013/zte-tad-dataset)
- [Configuración Hadoop y Yarn](https://www.linode.com/docs/guides/how-to-install-and-set-up-hadoop-cluster/)
- [Configuración Spark](https://www.linode.com/docs/guides/install-configure-run-spark-on-top-of-hadoop-yarn-cluster/)
- [SparkML](https://spark.apache.org/docs/latest/ml-guide.html)
