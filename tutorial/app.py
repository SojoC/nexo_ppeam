import sys
sys.path.append('./backend')
from backend.services.contact_service import crear_contacto
try:
    from backend.config.firebase_config import db_firestore
except Exception:
    db_firestore = None
from backend.services.contact_service_firestore import obtener_contacto
from backend.services.contact_service_firestore import buscar_contacto_por_id  
from backend.services.contact_service_firestore import buscar_por_limite_contacto 
from backend.services.contact_service_firestore import actualizar_contacto
from backend.services.contact_service_firestore import eliminar_contacto    

if __name__ == "__main__":
    # Ejemplo de uso de crear_contacto

    contacto = {
        "Circuito": "Monagas 3",
        "Congregacion": "Sarrapial",
        "Direccion_de_habitacion": "La Muralla",
        "Id": 505,
        "Nombre": "Cesar Viña",
        "Telefono": "04249672742",
        "Fecha_de_nacimiento": "1990-01-01",
        "Fecha_de_bautismo": "2010-01-01"
    }

    doc_id = crear_contacto(**contacto)
    print(f"ID del nuevo contacto: {doc_id}")

    # Buscar el contacto recién creado por su Id
    print("\nBuscando contacto por Id=505...")
    if db_firestore is None:
        print("db_firestore not configured; skipping Firestore example")
    else:
        coleccion = db_firestore.collection('Congregacion')
        query = coleccion.where('id', '==', 505).stream()
        encontrado = False
        for doc in query:
            print(f"ID Firestore: {doc.id} => {doc.to_dict()}")
            encontrado = True
        if not encontrado:
            print("No se encontró el contacto con Id=505.")




print("\nBuscando contacto por campo 'Telefono' con valor 041443441294...")
contacto = buscar_contacto_por_id('Telefono', '04143441294')
print(contacto)
print("\nBuscando los 25 primeros contactos...")
#los 25 primeros
contactos = buscar_por_limite_contacto(25)
print(contactos)

eliminar_contacto("02RBD8eqi70o8IDEsxvB")
