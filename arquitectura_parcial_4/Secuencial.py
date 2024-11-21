from multiprocessing import Process, Queue, cpu_count
import mysql.connector
import random
import string
import time
import psutil

# Configuración de conexión a la base de datos
DB_CONFIG = {
    "host": "127.0.0.1",    # Dirección IP del servidor de la base de datos (127.0.0.1 es local)
    "port": "3307",          # Puerto de conexión a la base de datos
    "user": "root",          # Usuario con permisos para acceder a la base de datos
    "password": "251121",    # Contraseña del usuario
    "database": "arquitectura",  # Nombre de la base de datos en la que se insertarán los datos
    "charset": "latin1"      # Conjunto de caracteres usado en la conexión (latin1 es compatible)
}

# Función para insertar datos en la base de datos usando el módulo multiprocessing
def insertar_datos_en_proceso(datos, resultados_queue):
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

        # Pone en la cola de resultados la cantidad de registros insertados
        resultados_queue.put(len(datos))  
    except mysql.connector.Error as err:
        # Maneja cualquier error de la base de datos
        print(f"Error: {err}")
        # Si ocurre un error, pone 0 en la cola (ningún registro fue insertado)
        resultados_queue.put(0)

# Función para generar datos aleatorios de clientes
def generar_datos_aleatorios(cantidad_registros):
    datos = []  # Lista donde se guardarán los datos generados
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

    # Obtener el número de núcleos disponibles en la CPU
    num_procesos = cpu_count()
    
    # Calcular cuántos registros le tocarán a cada proceso
    registros_por_proceso = total_registros // num_procesos

    # Generar los datos aleatorios para los registros
    print("Generando datos...")
    todos_los_datos = generar_datos_aleatorios(total_registros)

    # Dividir los datos generados en partes para cada proceso
    partes_datos = [todos_los_datos[i:i + registros_por_proceso] for i in range(0, total_registros, registros_por_proceso)]

    # Medir el tiempo de ejecución y la memoria antes de insertar los datos
    tiempo_inicio = time.time()
    memoria_inicial = psutil.virtual_memory().used

    # Crear una lista de procesos
    procesos = []
    # Crear una cola para almacenar los resultados de cada proceso
    resultados_queue = Queue()

    print(f"Insertando datos usando {num_procesos} procesos...")

    # Crear y lanzar un proceso para cada parte de datos
    for parte in partes_datos:
        proceso = Process(target=insertar_datos_en_proceso, args=(parte, resultados_queue))
        procesos.append(proceso)
        proceso.start()  # Inicia el proceso

    # Esperar a que todos los procesos terminen
    for proceso in procesos:
        proceso.join()  # Espera a que el proceso termine

    # Obtener los resultados de todos los procesos
    total_insertados = sum(resultados_queue.get() for _ in procesos)
    
    # Medir el tiempo de ejecución y el uso de memoria después de la inserción
    tiempo_final = time.time()
    memoria_final = psutil.virtual_memory().used

    # Calcular el tiempo total de ejecución
    tiempo_total = tiempo_final - tiempo_inicio
    
    # Calcular la memoria utilizada durante el proceso
    memoria_usada = (memoria_final - memoria_inicial) / (1024 * 1024)  # Convertir a MB

    # Mostrar los resultados
    print(f"Total de registros insertados: {total_insertados}")
    print(f"Tiempo de ejecución: {tiempo_total:.2f} segundos")
    print(f"Memoria utilizada: {memoria_usada:.2f} MB")

# Ejecutar el programa si este es el módulo principal
if __name__ == "__main__":
    main()
