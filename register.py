from db import connect_db #veritabanına bağlanmak için import ettik

def register_user(username, email, password, age, country):
    # veritabanı bağlantısını başlattık
    db = connect_db()
    cursor = db.cursor()

    # kullanıcıyı veritabanına eklemek için sql sorgusu
    sql = "INSERT INTO users (username, email, password, age, country) VALUES (%s, %s, %s, %s, %s)"
    values = (username, email, password, age, country)

    try:
        # sql sorgusunu çalıştır ve veriyi veritabanına kaydet
        cursor.execute(sql, values)
        db.commit()
        print(" Registration successful!")
    except Exception as e:
        
        print(" Error:", e)
    finally:
       
        cursor.close()
        db.close()


