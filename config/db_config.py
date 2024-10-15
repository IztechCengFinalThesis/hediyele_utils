# config/db_config.py
import psycopg2

def get_db_connection():
    conn = psycopg2.connect(
        host="hediyele-hediyele.h.aivencloud.com", 
        database="defaultdb",
        user="avnadmin",
        password="AVNS_uB3eS5nBg9hbv93vLAa"
    )
    return conn
