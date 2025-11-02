from db import connect_db  # Veritabanı bağlantı fonksiyonunu içe aktar

# bu fonksiyon ile kullanıcının giriş yapmasını kontrol ediyoruz email ve password bilgisi ile
def login_user(email, password):
    db = connect_db()           
    cursor = db.cursor()        # Cursor oluştur, SQL sorgusu çalıştırmak için kullanılır
    
    #sql sorgumuz
    sql = "SELECT * FROM users WHERE email = %s AND password = %s"  
    values = (email, password)  

    try:
        cursor.execute(sql, values)   # sql sorgusunu çalıştır
        user = cursor.fetchone()      
        if user:
            print("Login successful! Welcome,", user[1])  
            return True
        else:
            print("Invalid email or password!")          
            return False
    except Exception as e:
        print("Error:", e)  
        return False
    finally:
        cursor.close()   
        db.close()      
