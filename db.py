import mysql.connector  # MySQL ile bağlantı kurmak için gerekli kütüphane

# Veritabanına bağlanmak için fonksiyon
def connect_db():
    return mysql.connector.connect(
        host="localhost",      
        user="root",           
        password="",            
        database="film_db"      
    )
