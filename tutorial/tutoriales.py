x = {
    0: {
        'nombre': 'Juan',
        'telefono': '123456789'
    },
    1: {
        'nombre': 'Pedro',
        'telefono': '987654321'
    }
}

def recorrido(dic:dict):
    for id, valor in dic.items():
        nombre = valor.get('nombre', '')
        telefono = valor.get('telefono', '')
        print(f"id= {id} {nombre} , {telefono}")

    print(f"nombres= {[nombre for  nombre in dic.keys()]}")
    lista = [
        {'nombre': dic[id]['nombre'], 'telefono': dic[id]['telefono']}
        for id in dic.keys()
    ]
recorrido(x)

# Importa las librerías necesarias
import pyodbc
import pandas as pd
import os

# Define la función principal
def convertir_access_a_json():
    # Paso 1: Configurar los nombres de los archivos
    nombre_db_access = os.path.join(os.getcwd(), 'Circuito1.accdb')
    #os.path.normpath('C:\\Nexo_PPEAM\\Circuito1.accdb')
    nombre_tabla_access = 'Circuito' 
    nombre_json_salida = 'datos_circuitos.json'
    try: 
        if not os.path.exists(nombre_db_access):
            raise FileNotFoundError(f"El archivo de base de datos Access no se encontró en '{nombre_db_access}'.")
            return
        ruta_bd = (f'DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={nombre_db_access};')

        conexion= pyodbc.connect(ruta_bd)
        query_sql=f"SELECT * FROM [{nombre_tabla_access}]"
        x=f"SELECT * FROM [{nombre_tabla_access}]"
        datos=pd.read_sql(query_sql, conexion)
        datos.to_json(nombre_json_salida, orient='records', indent=4)
        print(f"Datos exportados exitosamente a {nombre_json_salida}")
    except Exception as e:
        print(f"¡Oops! Ocurrió un error: {e}")
        print("Asegúrate de tener el controlador de Microsoft Access Database Engine instalado.")


# Llamar a la función principal solo si este archivo es ejecutado directamente
if __name__ == "__main__":
    convertir_access_a_json()