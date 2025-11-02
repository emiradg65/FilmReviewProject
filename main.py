from flask import Flask, request, render_template, redirect, url_for, session, flash
from register import register_user
from login import login_user
from db import connect_db
import os

app = Flask(__name__)
app.secret_key = "film_review_secret_key"  # Oturum (session) verilerinin şifrelenmesi için gizli anahtar


# Kullanıcı Kayıt Sayfası

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Formdan gelen kullanıcı bilgilerini al
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        age = request.form["age"]
        country = request.form["country"]

        # Veritabanına kullanıcıyı kaydet
        register_user(username, email, password, age, country)
        flash("Registration successful!", "success")
        return redirect(url_for('login'))

    return render_template("register.html")


# Kullanıcı Giriş Sayfası

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        # Kullanıcı giriş bilgilerini kontrol et
        if login_user(email, password):
            session["user_email"] = email  # Kullanıcıyı oturuma al
            flash(" Logged in successfully.", "success")
            return redirect(url_for('dashboard'))
        else:
            flash(" Login failed! Incorrect email or password.", "danger")
            return redirect(url_for('login'))

    return render_template("login.html")


# Oturumu Sonlandır (Logout)

@app.route("/logout")
def logout():
    session.pop("user_email", None)  # Oturum bilgisini sil
    flash("✅ Logged out successfully.", "success")
    return redirect(url_for('dashboard'))


# Ana Sayfa - Tüm Filmleri Listele

@app.route("/dashboard")
def dashboard():
    db = connect_db()
    cursor = db.cursor()
    cursor.execute("SELECT id, title, year, imdb_rating, description FROM movies")
    movies = cursor.fetchall()
    cursor.close()
    db.close()

    return render_template("dashboard.html", movies=movies)


# Yeni Film Ekleme Sayfası

@app.route("/add_movie", methods=["GET", "POST"])
def add_movie():
    if "user_email" not in session:
        flash("⚠️ You must log in first.", "danger")
        return redirect(url_for('login'))

    if request.method == "POST":
        # Formdan gelen film bilgilerini al
        title = request.form["title"]
        year = request.form["year"]
        certificate = request.form["certificate"]
        runtime = request.form["runtime"]
        genre = request.form["genre"]
        imdb_rating = request.form["imdb_rating"]
        description = request.form["description"]
        meta_score = request.form["meta_score"]
        director = request.form["director"]
        star1 = request.form["star1"]
        star2 = request.form["star2"]
        star3 = request.form["star3"]
        star4 = request.form["star4"]
        no_of_votes = request.form["no_of_votes"]
        gross = request.form["gross"]

        # Veritabanına yeni film ekle
        db = connect_db()
        cursor = db.cursor()
        sql = """
        INSERT INTO movies 
        (title, year, certificate, runtime, genre, imdb_rating, description, meta_score, director, star1, star2, star3, star4, no_of_votes, gross) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (title, year, certificate, runtime, genre, imdb_rating, description,
                  meta_score, director, star1, star2, star3, star4, no_of_votes, gross)
        try:
            cursor.execute(sql, values)
            db.commit()
            flash(" Movie added successfully.", "success")
        except Exception as e:
            print(" Error while adding the movie:", e)
            flash(" An error occurred while adding the movie.", "danger")
        finally:
            cursor.close()
            db.close()

        return redirect(url_for('dashboard'))

    return render_template("add_movie.html")


# Film Detay Sayfası + Yorum Ekleme

@app.route("/movie/<int:movie_id>", methods=["GET", "POST"])
def movie_detail(movie_id):
    db = connect_db()
    cursor = db.cursor()

    # Yorum gönderildiyse işle
    if request.method == "POST":
        if "user_email" not in session:
            flash("⚠️ You must be logged in to comment.", "danger")
            return redirect(url_for('login'))

        comment = request.form["comment"]
        rating = request.form["rating"]
        user_email = session["user_email"]

        # Aynı kullanıcı aynı filme tekrar yorum yapamasın
        cursor.execute("SELECT * FROM reviews WHERE user_email = %s AND movie_id = %s", (user_email, movie_id))
        existing_review = cursor.fetchone()

        if existing_review:
            flash(" You have already reviewed this movie!", "danger")
            cursor.close()
            db.close()
            return redirect(url_for('movie_detail', movie_id=movie_id))

        # Yeni yorumu ekle
        sql = "INSERT INTO reviews (user_email, movie_id, comment, rating) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql, (user_email, movie_id, comment, rating))
        db.commit()
        flash(" Review added successfully.", "success")

    # Film bilgilerini al
    cursor.execute("SELECT * FROM movies WHERE id = %s", (movie_id,))
    movie = cursor.fetchone()

    # Filmin tüm yorumlarını al
    cursor.execute("SELECT user_email, comment, rating, created_at FROM reviews WHERE movie_id = %s ORDER BY created_at DESC", (movie_id,))
    reviews = cursor.fetchall()

    cursor.close()
    db.close()

    if movie:
        return render_template("movie_detail.html", movie=movie, reviews=reviews)
    else:
        flash(" Movie not found.", "danger")
        return redirect(url_for('dashboard'))


# İzleme Listesine Film Ekle

@app.route("/add_to_watchlist/<int:movie_id>")
def add_to_watchlist(movie_id):
    if "user_email" not in session:
        flash("You must log in first.", "danger")
        return redirect(url_for('login'))

    db = connect_db()
    cursor = db.cursor()
    user_email = session["user_email"]

    # Aynı film tekrar eklenemesin
    cursor.execute("SELECT * FROM watchlist WHERE user_email = %s AND movie_id = %s", (user_email, movie_id))
    if cursor.fetchone():
        flash(" This movie is already in your watchlist!", "info")
    else:
        cursor.execute("INSERT INTO watchlist (user_email, movie_id) VALUES (%s, %s)", (user_email, movie_id))
        db.commit()
        flash(" Movie added to your watchlist!", "success")

    cursor.close()
    db.close()

    return redirect(url_for('dashboard'))


# İzleme Listesinden Film Kaldır

@app.route("/remove_from_watchlist/<int:movie_id>")
def remove_from_watchlist(movie_id):
    if "user_email" not in session:
        flash(" You must log in first.", "danger")
        return redirect(url_for('login'))

    db = connect_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM watchlist WHERE user_email = %s AND movie_id = %s", (session["user_email"], movie_id))
    db.commit()
    cursor.close()
    db.close()

    flash(" Movie removed from watchlist!", "success")
    return redirect(url_for('watchlist'))


# Kullanıcının İzleme Listesi

@app.route("/watchlist")
def watchlist():
    if "user_email" not in session:
        flash(" You must log in first.", "danger")
        return redirect(url_for('login'))

    db = connect_db()
    cursor = db.cursor()

    cursor.execute("""
        SELECT movies.id, movies.title, movies.year, movies.imdb_rating
        FROM watchlist
        JOIN movies ON watchlist.movie_id = movies.id
        WHERE watchlist.user_email = %s
        ORDER BY watchlist.created_at DESC
    """, (session["user_email"],))
    watchlist_movies = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template("watchlist.html", watchlist_movies=watchlist_movies)


# Kullanıcının Yorumları

@app.route("/my_reviews")
def my_reviews():
    if "user_email" not in session:
        flash(" You must log in first.", "danger")
        return redirect(url_for('login'))

    db = connect_db()
    cursor = db.cursor()

    cursor.execute("""
        SELECT reviews.id, movies.title, reviews.comment, reviews.rating, reviews.created_at
        FROM reviews
        JOIN movies ON reviews.movie_id = movies.id
        WHERE reviews.user_email = %s
        ORDER BY reviews.created_at DESC
    """, (session["user_email"],))
    my_reviews = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template("my_reviews.html", my_reviews=my_reviews)


# Yorum Düzenleme

@app.route("/edit_review/<int:review_id>", methods=["GET", "POST"])
def edit_review(review_id):
    if "user_email" not in session:
        flash("You must log in first.", "danger")
        return redirect(url_for('login'))

    db = connect_db()
    cursor = db.cursor()

    if request.method == "POST":
        new_comment = request.form["comment"]
        new_rating = request.form["rating"]

        cursor.execute("""
            UPDATE reviews 
            SET comment = %s, rating = %s 
            WHERE id = %s AND user_email = %s
        """, (new_comment, new_rating, review_id, session["user_email"]))
        db.commit()
        cursor.close()
        db.close()

        flash(" Review updated successfully.", "success")
        return redirect(url_for('my_reviews'))

    cursor.execute("SELECT comment, rating FROM reviews WHERE id = %s AND user_email = %s", (review_id, session["user_email"]))
    review = cursor.fetchone()

    cursor.close()
    db.close()

    if review:
        return render_template("edit_review.html", review=review, review_id=review_id)
    else:
        flash(" Review not found.", "danger")
        return redirect(url_for('my_reviews'))


# Yorum Silme

@app.route("/delete_review/<int:review_id>")
def delete_review(review_id):
    if "user_email" not in session:
        flash(" You must log in first.", "danger")
        return redirect(url_for('login'))

    db = connect_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM reviews WHERE id = %s AND user_email = %s", (review_id, session["user_email"]))
    db.commit()
    cursor.close()
    db.close()

    flash(" Review deleted successfully.", "success")
    return redirect(url_for('my_reviews'))


# Profil Sayfası - Bilgileri Görüntüle / Güncelle

@app.route("/profile", methods=["GET", "POST"])
def profile():
    if "user_email" not in session:
        flash(" You must log in first.", "danger")
        return redirect(url_for('login'))

    db = connect_db()
    cursor = db.cursor()

    if request.method == "POST":
        new_age = request.form["age"]
        new_country = request.form["country"]
        new_password = request.form["password"]
        user_email = session["user_email"]

        # Şifre boş değilse şifre de güncellenir
        if new_password:
            sql = "UPDATE users SET age = %s, country = %s, password = %s WHERE email = %s"
            values = (new_age, new_country, new_password, user_email)
        else:
            sql = "UPDATE users SET age = %s, country = %s WHERE email = %s"
            values = (new_age, new_country, user_email)

        cursor.execute(sql, values)
        db.commit()

    cursor.execute("SELECT * FROM users WHERE email = %s", (session["user_email"],))
    user = cursor.fetchone()

    cursor.close()
    db.close()

    return render_template("profile.html", user=user)


# Film Arama Özelliği

@app.route("/search")
def search():
    query = request.args.get('query')

    db = connect_db()
    cursor = db.cursor()
    like_query = f"%{query}%"  # SQL'de LIKE ile eşleşme için

    cursor.execute("""
        SELECT id, title, year, imdb_rating, description
        FROM movies
        WHERE title LIKE %s
    """, (like_query,))
    search_results = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template("search_results.html", query=query, search_results=search_results)


# Flask Uygulamasını Başlat

if __name__ == "__main__":
    app.run(debug=True, port=5001) 
