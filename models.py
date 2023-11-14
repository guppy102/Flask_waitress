from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

class Article(db.Model):
    __tablename__ = 'article'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.Text)
    adress = db.Column(db.Text)
    description = db.Column(db.Text)
    description1 = db.Column(db.Text)
    description2 = db.Column(db.Text)
    description3 = db.Column(db.Text)
    description4 = db.Column(db.Text)
    description5 = db.Column(db.Text)
    
    #追加部分2023/11/07
    rentaltime = db.Column(db.Text)
    bukkinngnorma = db.Column(db.Text)
    janre = db.Column(db.Text) #得意なジャンル
    #追加2023/11/15
    booking_live = db.Column(db.Text)  # ブッキングライブ
    hall_rental_details = db.Column(db.Text)  # ホールレンタルの詳細
    one_drink_price = db.Column(db.Text)              # ONEDRINKの価格               
    secondary_use = db.Column(db.Text) # 二次利用可能かどうか
    streaming_live_available = db.Column(db.Text) # ストリーミングライブの有無
    
    picture1 = db.Column(db.String(255))
    picture2 = db.Column(db.String(255))
    picture3 = db.Column(db.String(255))
    picture4 = db.Column(db.String(255))
    picture5 = db.Column(db.String(255))
    picture6 = db.Column(db.String(255))
    picture7 = db.Column(db.String(255))
    picture8 = db.Column(db.String(255))
    picture9 = db.Column(db.String(255))
    picture10 = db.Column(db.String(255))
    
    
    
    images = db.relationship('Image', backref='article', lazy=True)
    contents = db.relationship('Content', backref='article', lazy=True)

class Image(db.Model):#つかわない
    __tablename__ = 'image'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    path = db.Column(db.String(255))
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'))

class Content(db.Model):#使わない
    __tablename__ = 'content'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    text = db.Column(db.Text)
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'))