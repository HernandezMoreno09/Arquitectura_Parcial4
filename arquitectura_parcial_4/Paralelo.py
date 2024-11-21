import mysql.connector
import random
import string
import time
import psutil

# Configuración de la conexión a la base de datos
DB_CONFIG = {
    "host": "127.0.0.1",    # Dirección IP del servidor de la base de datos (127.0.0.1 es local)
    "port": "3307",          # Puerto de conexión a la base de datos
    "user": "root",          # Usuario con permisos para acceder a la base de datos
    "password": "251121",    # Contraseña del usuario
    "database": "arquitectura",  # Nombre de la base de datos en la que se insertarán los datos
    "charset": "latin1"      # Conjunto de caracteres usado en la conexión (latin1 es compatible)
}

# Función para insertar múltiples registros en la base de datos
def insertar_datos_en_lote(datos):
    try:
        # Establece la conexión a la base de datos
        conexion = mysql.connector.connect(**DB_CONFIG)
        cursor = conexion.cursor()

        # Consulta SQL para insertar los datos
        consulta = "INSERT INTO clientes (nombre, telefono, correo, direccion) VALUES (%s, %s, %s, %s)"
        
        # Ejecuta la consulta para insertar múltiples registros a la vez
        cursor.executemany(consulta, datos)
        
        # Realiza la confirmación de la transacción
        conexion.commit()
        
        # Cierra el cursor y la conexión a la base de datos
        cursor.close()
        conexion.close()
    except mysql.connector.Error as err:
        # Si ocurre un error en la base de datos, imprime el error
        print(f"Error: {err}")

# Función para generar datos aleatorios de clientes
def generar_datos_aleatorios(cantidad_registros):
    datos = []  # Lista donde se guardarán los registros generados
    for _ in range(cantidad_registros):
        # Generar un nombre aleatorio de 10 caracteres
        nombre = ''.join(random.choices(string.ascii_letters, k=10))
        
        # Generar un teléfono aleatorio de 10 dígitos
        telefono = ''.join(random.choices(string.digits, k=10))
        
        # Crear un correo electrónico a partir del nombre generado
        correo = f"{nombre.lower()}@example.com"
        
        # Generar una dirección aleatoria de 20 caracteres alfanuméricos
        direccion = ''.join(random.choices(string.ascii_letters + string.digits, k=20))
        
        # Añadir el registro como una tupla a la lista de datos
        datos.append((nombre, telefono, correo, direccion))
    
    return datos  # Devuelve la lista con todos los registros generados

# Función principal
def main():
    total_registros = 10000  # Número total de registros a insertar

    # Generar los datos aleatorios
    print("Generando datos...")
    todos_los_datos = generar_datos_aleatorios(total_registros)

    # Medir el tiempo de ejecución y el uso de memoria antes de insertar los datos
    tiempo_inicio = time.time()
    memoria_inicial = psutil.virtual_memory().used

    print("Insertando datos en lotes...")

    # Insertar los datos en lotes (por ejemplo, cada 1000 registros)
    batch_size = 1000  # Tamaño del lote (número de registros por inserción)
    for i in range(0, total_registros, batch_size):
        lote = todos_los_datos[i:i+batch_size]  # Extrae un lote de registros
        insertar_datos_en_lote(lote)  # Llama a la función para insertar el lote

    # Medir el tiempo y la memoria después de insertar los datos
    tiempo_final = time.time()
    memoria_final = psutil.virtual_memory().used

    # Calcular el tiempo total de ejecución
    tiempo_total = tiempo_final - tiempo_inicio
    
    # Calcular la memoria utilizada durante el proceso
    memoria_usada = (memoria_final - memoria_inicial) / (1024 * 1024)  # Convertir a MB

    # Mostrar los resultados
    print(f"Total de registros insertados: {total_registros}")
    print(f"Tiempo de ejecución: {tiempo_total:.2f} segundos")
    print(f"Memoria utilizada: {memoria_usada:.2f} MB")

# Ejecutar el programa si este es el módulo principal
if __name__ == "__main__":
    main()
