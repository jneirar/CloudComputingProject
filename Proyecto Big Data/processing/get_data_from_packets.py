import binascii
from datetime import datetime
import ipaddress
import os
import pandas as pd
from scapy.all import rdpcap

ruta_principal = 'Proyecto Big Data'

classes = []

ruta_pcap = os.path.join(ruta_principal, 'pcap')
ruta_parquet = os.path.join(ruta_principal, 'parquet')

# Crear la carpeta parquet si no existe
if not os.path.exists(ruta_parquet):
    os.makedirs(ruta_parquet)

# Obtener las clases
for carpeta_clase in os.listdir(ruta_pcap):
    classes.append(carpeta_clase)

# Crear una carpeta para cada clase y generar los archivos parquet
i_class = 0
for clase in classes:
    class_pacp_path = os.path.join(ruta_pcap, clase)
    class_parquet_path = os.path.join(ruta_parquet, clase)

    if not os.path.exists(class_parquet_path):
        os.makedirs(class_parquet_path)

    i_file = 0
    for file in os.listdir(class_pacp_path):
        filename, file_extension = os.path.splitext(file)
        pcap_file = os.path.join(class_pacp_path, file)

        # Leer el archivo pcap
        packets = rdpcap(pcap_file)
        # Crear una lista para almacenar los datos de los paquetes
        packet_data = []
        # Crear diccionarios para almacenar los paquetes filtrados
        tcp_packets = {}
        a = []

        # Extraer un subconjunto de paquetes TCP
        total_packets = len(packets)
        porcentaje = 1.0
        limit_packets = int(porcentaje * total_packets)
        
        for it, packet in enumerate(packets):
            if it > limit_packets:
                break
            # Crear un diccionario para almacenar las características
            packet_info = {}
            packet_info['CLASS'] = i_class

            if 'IP' in packet:
                source_ip = packet['IP'].src
                dest_ip = packet['IP'].dst
                packet_info['LEN_SRC_IP'] = len(source_ip)
                packet_info['LEN_DEST_IP'] = len(dest_ip)

                # Parsear las direcciones IP utilizando la biblioteca ipaddress
                try:
                    source_ip = ipaddress.ip_address(source_ip)
                except ValueError:
                    source_ip = None

                try:
                    dest_ip = ipaddress.ip_address(dest_ip)
                except ValueError:
                    dest_ip = None

                if source_ip:
                    packet_info['Source_IP1'] = source_ip.packed[0]
                    packet_info['Source_IP2'] = source_ip.packed[1]
                    packet_info['Source_IP3'] = source_ip.packed[2]
                    packet_info['Source_IP4'] = source_ip.packed[3]
                else:
                    packet_info['Source_IP1'] = None
                    packet_info['Source_IP2'] = None
                    packet_info['Source_IP3'] = None
                    packet_info['Source_IP4'] = None

                if dest_ip:
                    packet_info['Destination_IP1'] = dest_ip.packed[0]
                    packet_info['Destination_IP2'] = dest_ip.packed[1]
                    packet_info['Destination_IP3'] = dest_ip.packed[2]
                    packet_info['Destination_IP4'] = dest_ip.packed[3]
                else:
                    packet_info['Destination_IP1'] = None
                    packet_info['Destination_IP2'] = None
                    packet_info['Destination_IP3'] = None
                    packet_info['Destination_IP4'] = None

            # Características de flujo
            if 'TCP' in packet:
                packet_info["TCP_SPORT"] = packet['TCP'].sport
                packet_info["TCP_DPORT"] = packet['TCP'].dport
            if 'Raw' in packet:
                payload = packet['Raw'].load
                hex_payload = binascii.hexlify(payload).decode('utf-8')
                packet_info["LEN_RAW"] = len(hex_payload)

            if 'IP' in packet and 'TCP' in packet:
                send_time = datetime.fromtimestamp(int(packet.time))
                packet_info['Send_Year'] = send_time.year
                packet_info['Send_Month'] = send_time.month
                packet_info['Send_Day'] = send_time.day
                packet_info['Send_Hour'] = send_time.hour
                packet_info['Send_Minute'] = send_time.minute
                packet_info['Send_Second'] = send_time.second
                packet_info["VERSION"] = packet['IP'].version
                packet_info['IHL'] = packet['IP'].ihl
            '''
            # Características no utilizadas en el modelo
            if 'Ether' in packet:
                dst_address = packet['Ether'].dst
                dst_numbers = dst_address.split(':')
                src_address = packet['Ether'].src
                src_numbers = src_address.split(':')
                for i, num in enumerate(dst_numbers):
                    packet_info[f'DST_{i+1}'] = int(num, 16)
                for i, num in enumerate(src_numbers):
                    packet_info[f'SRC_{i+1}'] = int(num, 16)

                packet_info['TYPE'] = packet['Ether'].type
                packet_info['LEN'] = packet['IP'].len
                packet_info['ID'] = packet['IP'].id
                packet_info['FLAGS'] = packet['IP'].flags
                packet_info['FRAG'] = packet['IP'].frag
                packet_info['TTL'] = packet['IP'].ttl
                packet_info['PROTO'] = packet['IP'].proto
                packet_info['CHKSUM'] = packet['IP'].chksum
                packet_info['SEQ'] = packet['TCP'].seq
                packet_info['ACK'] = packet['TCP'].ack
                packet_info['DATAOFS'] = packet['TCP'].dataofs
                packet_info['RESERVED'] = packet['TCP'].reserved
                packet_info['FLAGS'] = packet['TCP'].flags
                packet_info['WINDOW'] = packet['TCP'].window
                packet_info['CHKSUM_'] = packet['TCP'].chksum
                packet_info['URGPTR'] = packet['TCP'].urgptr
                packet_info["MESSAGE_RAW"] = packet['Raw'].load
                packet_info["TIME_TCP"] = datetime.fromtimestamp(int(packet.time))
                packet_info["NAME"] = packet.name
                '''
            packet_data.append(packet_info)

        # Crear un DataFrame de pandas a partir de la lista de datos
        df = pd.DataFrame(packet_data)
        #df['FLAGS'] = df['FLAGS'].astype('string')

        # Selecciona las columnas que se utilizarán para el entrenamiento
        # Ignorar si se desea utilizar todas las características
        selected_columns = ['CLASS', 'LEN_SRC_IP', 'LEN_DEST_IP', 'Source_IP1', 'Source_IP2', 'Source_IP3', 'Source_IP4', 'Destination_IP1', 'Destination_IP2', 'Destination_IP3', 'Destination_IP4', 'TCP_SPORT', 'TCP_DPORT', 'LEN_RAW', 'Send_Year', 'Send_Month', 'Send_Day', 'Send_Hour', 'Send_Minute', 'Send_Second']
        df = df[selected_columns]

        # Guardar el DataFrame en un archivo parquet
        out_parquet = os.path.join(class_parquet_path, str(i_class) + '_' + str(i_file) + '.parquet')
        df.to_parquet(out_parquet, engine='pyarrow', index=False)
        i_file = i_file + 1
    i_class = i_class + 1