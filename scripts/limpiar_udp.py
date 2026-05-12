import os
import sys

# Asegurar que se puede importar desde api/db_config
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, os.path.join(PROJECT_ROOT, "api"))

from db_config import get_connection

def vaciar_registros_udp():
    print("Conectando a Supabase para eliminar registros UDP...")
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        # Primero contamos cuántos hay
        cur.execute("SELECT COUNT(*) FROM datos_warehouse WHERE origen = 'UDP'")
        cantidad = cur.fetchone()[0]
        
        if cantidad == 0:
            print("No hay registros UDP para borrar.")
            return

        # Eliminamos solo los registros de origen UDP
        cur.execute("DELETE FROM datos_warehouse WHERE origen = 'UDP'")
        conn.commit()
        
        print(f"¡Éxito! Se han eliminado {cantidad} registros de telemetría (UDP) de Supabase.")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error al limpiar la base de datos: {e}")

if __name__ == "__main__":
    confirmacion = input("¿Estás seguro de que quieres borrar TODOS los registros UDP de la base de datos? (s/n): ")
    if confirmacion.lower() == 's':
        vaciar_registros_udp()
    else:
        print("Operación cancelada.")
