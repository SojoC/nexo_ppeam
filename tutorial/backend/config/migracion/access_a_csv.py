import pyodbc
import pandas as pd 


import pyodbc
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import os

# --- PARÁMETROS DE CONFIGURACIÓN ---

# Reemplaza 'path/to/your/serviceAccountKey.json' con la ruta a tu archivo JSON de credenciales de Firebase
ruta_credenciales_firebase = 'C:\\Nexo_PPEAM\\base-de-datos-02-8b402-firebase-adminsdk-nvtge-ef258cb69b.json'

# Reemplaza 'path/to/your/database.accdb' con la ruta a tu base de datos de Access
ruta_base_datos_access = 'C:\\Nexo_PPEAM\\Circuito1.accdb'

# Reemplaza 'NombreDeLaTabla' con el nombre de la tabla de Access que quieres leer
nombre_tabla_access = 'Circuito'

# Reemplaza 'nombre_coleccion_firebase' con el nombre de la colección en Firestore donde guardarás los datos
nombre_coleccion_firebase = 'Congregacion'

# --- INICIALIZACIÓN DE FIREBASE ---

try:
    if not firebase_admin._apps:
        cred = credentials.Certificate(ruta_credenciales_firebase)
        firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("Conexión a Firebase exitosa.")
except FileNotFoundError:
    print(f"Error: El archivo de credenciales de Firebase no se encontró en '{ruta_credenciales_firebase}'.")
    exit()
except Exception as e:
    print(f"Error al inicializar Firebase: {e}")
    exit()

# --- CONEXIÓN Y LECTURA DE DATOS DE ACCESS ---

try:
    # La cadena de conexión a Access. Odbc Driver 12 es común para archivos .accdb
    cadena_conexion_access = (
        r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
        rf'DBQ={ruta_base_datos_access};'
    )

    
    
    conn = pyodbc.connect(cadena_conexion_access)
    cursor = conn.cursor()
    
    print(f"Conexión a la base de datos de Access exitosa.")
    
    # Selecciona todos los registros de la tabla
    cursor.execute(f'SELECT * FROM [{nombre_tabla_access}]')
    
    # Obtiene los nombres de las columnas
    columnas = [column[0] for column in cursor.description]
    
    filas = cursor.fetchall()
    
    print(f"Se han leído {len(filas)} registros de la tabla '{nombre_tabla_access}'.")
    
    conn.close()

except pyodbc.Error as ex:
    sqlstate = ex.args[0]
    print(f"Error de conexión a Access: {sqlstate}. Asegúrate de que el 'Microsoft Access Database Engine' esté instalado y la ruta sea correcta.")
    exit()

# --- SUBIDA DE DATOS A FIRESTORE ---

if filas:
    contador_subidos = 0
    for fila in filas:
        try:
            # Crea un diccionario con los datos de la fila
            # Utiliza un generador para crear el diccionario de forma eficiente
            datos = {columnas[i]: valor for i, valor in enumerate(fila)}
            
            # Convierte los valores datetime.date y datetime.datetime a un formato compatible
            for key, value in datos.items():
                if isinstance(value, (pyodbc.Date, pyodbc.Time, pyodbc.Timestamp)):
                    datos[key] = str(value)

            # Sube el diccionario como un nuevo documento en la colección de Firestore
            # Firestore generará automáticamente un ID único para cada documento
            db.collection(nombre_coleccion_firebase).add(datos)
            contador_subidos += 1
            
        except Exception as e:
            print(f"Error al subir el documento: {e}. Datos de la fila: {fila}")
            continue

    print("-" * 50)
    print(f"Proceso completado. Se subieron {contador_subidos} documentos a la colección '{nombre_coleccion_firebase}' en Firestore.")
else:
    print("No se encontraron registros en la tabla de Access para subir.")