import pymysql
from config import DB_CONFIG

def get_db_connection():
    """Crea y retorna una conexión a la base de datos"""
    return pymysql.connect(
        host=DB_CONFIG['host'],
        port=DB_CONFIG['port'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        database=DB_CONFIG['database'],
        charset=DB_CONFIG['charset'],
        cursorclass=pymysql.cursors.DictCursor
    )

def execute_query(query, params=None, fetch=True):
    """Ejecuta una query y retorna los resultados"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params or ())
            if fetch:
                return cursor.fetchall()
            else:
                conn.commit()
                return cursor.lastrowid
    finally:
        conn.close()

def execute_single(query, params=None):
    """Ejecuta una query y retorna un solo resultado"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params or ())
            return cursor.fetchone()
    finally:
        conn.close()
