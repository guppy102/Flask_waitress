import os
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, request, redirect, url_for, after_this_request
from flask_login import LoginManager, UserMixin, login_user,login_required,logout_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from werkzeug.utils import secure_filename 
from models import db, Article, Image, Content
from flask_migrate import Migrate
from datetime import timedelta
import secrets
from waitress import serve
import logging 
from logging.handlers import RotatingFileHandler
import time

secret_key = secrets.token_hex(64)  # 64バイトのランダムな16進数文字列



app = Flask(__name__)
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif'}
UPLOAD_FOLDER = 'uploads'  # アップロードディレクトリを './uploads' に変更
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = secret_key #セキュリティ、大事、secrets使おう
# アプリケーションの設定をconfig.pyから読み込む
app.config.from_object('config.Config')


#Log関係
# ロガーの設定
logger = logging.getLogger('waitress')
logger.setLevel(logging.INFO)

# ログファイルハンドラーの設定
handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=20)
formatter = logging.Formatter(
    '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
)
handler.setFormatter(formatter)
logger.addHandler(handler)

# リクエストごとの情報をログに記録する
@app.before_request
def log_request_info():
    ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    method = request.method
    logger.info(f"Request from {ip} with method {method}")

@app.after_request
def after_request(response):
    timestamp = time.strftime('[%Y-%b-%d %H:%M]')
    logger.info(f'{timestamp} {request.remote_addr} {request.method} {request.scheme} {response.status}')
    return response
#ログイン認証

# 認証用のユーザーモデルを作成
class User(UserMixin):
    def __init__(self, id):
        self.id = id
# ダミーユーザーを作成ずっと使いたいけどね

hashed_password = generate_password_hash('1234')
users = {'admin': {'password': hashed_password}}

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)
app.permanent_session_lifetime = timedelta(hours=1)
#↑設定、login使う、一時間指定
@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form['user_id']
        password = request.form['password']
        # ユーザーIDが存在し、かつパスワードのハッシュが一致するかチェック
        if user_id in users and check_password_hash(users[user_id]['password'], password):
            user = User(user_id)
            login_user(user)
            return redirect(url_for("list_articles"))
        else:
            return render_template('login.html')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return 'ログアウトしました'

# SQLAlchemyを初期化
db.init_app(app)
migrate = Migrate(app, db)

# ファイル指定
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/articles')
@login_required
def list_articles():
    # データベースから記事データを取得
    articles = Article.query.all()
    return render_template('article_list.html', articles=articles)

@app.route('/articles/create', methods=["GET","POST"])
@login_required
def create_articles():

    if request.method == "POST":
        # POSTリクエストの場合、フォームから入力されたデータを受け取ります
        title = request.form["title"]
        adress = request.form["adress"]
        description = request.form["description"]
        description1 = request.form["description1"]
        description2 = request.form["description2"]
        description3 = request.form["description3"]
        description4 = request.form["description4"]
        description5 = request.form["description5"]
        rentaltime = request.form["rentaltime"]  # フォームから"rentaltime"を受け取る
        bukkinngnorma = request.form["bukkinngnorma"]  # フォームから"bukkinngnorma"を受け取る
        janre = request.form["janre"]  # フォームから"janre"を受け取る
        
        booking_live = request.form["booking_live"]
        hall_rental_details = request.form["hall_rental_details"]
        one_drink_price = request.form["one_drink_price"]
        secondary_use = request.form["secondary_use"]
        streaming_live_available = request.form["streaming_live_available"]

        # Articleオブジェクトを作成し、フォームから受け取ったデータを設定
        article = Article(
            title=title,
            adress=adress,
            description=description,
            description1=description1,
            description2=description2,
            description3=description3,
            description4=description4,
            description5=description5,
            rentaltime=rentaltime,  # フォームから受け取った"rentaltime"を設定
            bukkinngnorma=bukkinngnorma,  # フォームから受け取った"bukkinngnorma"を設定
            janre=janre,  # フォームから受け取った"janre"を設定
            
            booking_live = booking_live,
            hall_rental_details = hall_rental_details,
            one_drink_price = one_drink_price,
            secondary_use = secondary_use,
            streaming_live_available = streaming_live_available,
        )
        db.session.add(article)

        # 画像のアップロードとデータベースへの保存
        for i in range(1, 11):
            field_name = f"picture{i}"
            if field_name in request.files:
                picture = request.files[field_name]
                if picture and allowed_file(picture.filename):
                    upload_path = os.path.join('./static/uploads', secure_filename(picture.filename))
                    picture.save(upload_path)

                    # 画像のファイルパスを該当するpictureカラムに設定
                    setattr(article, field_name, upload_path)

        # 一度だけコミットしてデータベースに保存
        db.session.commit()

        # 記事が正常に作成されたら記事一覧ページにリダイレクトします
        return redirect(url_for("list_articles"))

    # GETリクエストの場合、記事作成フォームを表示
    return render_template("create.html")



@app.route("/articles/update/<int:article_id>", methods=["GET", "POST"])
@login_required
def update_article(article_id):
    article = Article.query.get_or_404(article_id)

    if request.method == "POST":
        # フォームから新しい画像を取得し、適切なカラムに設定
        for i in range(1, 11):
            field_name = f"picture{i}"
            new_picture = request.files.get(field_name)

            if new_picture and allowed_file(new_picture.filename):
                # 新しい画像をアップロード
                upload_path = os.path.join('./static/uploads', secure_filename(new_picture.filename))
                new_picture.save(upload_path)

                # 既存の記事のカラムに新しい画像データを設定
                setattr(article, field_name, upload_path)

        # フォームから受け取った他のデータをもとに記事をアップデート
        article.title = request.form["title"]
        article.adress = request.form["adress"]
        article.description = request.form["description"]
        article.description1 = request.form["description1"]
        article.description2 = request.form["description2"]
        article.description3 = request.form["description3"]
        article.description4 = request.form["description4"]
        article.description5 = request.form["description5"]
        
        # 新しいフィールドに対応
        article.rentaltime = request.form["rentaltime"]
        article.bukkinngnorma = request.form["bukkinngnorma"]
        article.janre = request.form["janre"]
        
        article.booking_live = request.form["booking_live"]
        article.hall_rental_details = request.form["hall_rental_details"]
        article.one_drink_price = request.form["one_drink_price"]
        article.secondary_use = request.form["secondary_use"]
        article.streaming_live_available = request.form["streaming_live_available"]

        db.session.commit()  # 既存の記事と画像の更新を保存

        return redirect(url_for("list_articles"))

    return render_template("update_article.html", article=article)





@app.route('/articles/delete/<int:article_id>', methods=["GET", "POST"])
@login_required
def delete_article(article_id):
    article = Article.query.get_or_404(article_id)

    if request.method == "POST":
        # 記事に紐づく画像を削除
        for image in article.images:
            db.session.delete(image)

        # 記事に紐づくコンテンツを削除
        for content in article.contents:
            db.session.delete(content)

        # 記事をデータベースから削除
        db.session.delete(article)
        db.session.commit()
        return redirect(url_for("list_articles"))

    return render_template("delete_article.html", article=article)

@app.route('/display_image/<int:article_id>')
def display_image(article_id):
    article = Article.query.get(article_id)
    
    image_path = article.picture1  # picture1の画像ファイルパスを取得
    return render_template('image_display.html', image_path=image_path)

@app.route('/search/<int:article_id>')
def display(article_id):
    article = db.session.get(Article, article_id)
    return render_template("article.html",article=article)
    
@app.route('/search', methods=['GET', 'POST'])
def search_article():
    matching_articles = []  # 部分一致した記事のリストを格納する変数を用意
    if request.method == "POST":
        # キーワードがフォームから送信されたかを確認
        if "keyword" in request.form:
            keyword = request.form["keyword"]
            if keyword:
                keyword_list = keyword.split()

                for keyword in keyword_list:
                    # キーワードを含む記事を検索してリストに追加
                    query = db.session.query(Article).filter(or_(
                        Article.title.contains(keyword),
                        Article.adress.contains(keyword),
                        Article.description.contains(keyword),
                        Article.description1.contains(keyword),
                        Article.description2.contains(keyword),
                        Article.description3.contains(keyword),
                        Article.description4.contains(keyword),
                        Article.description5.contains(keyword),
                        Article.rentaltime.contains(keyword),  # 追加
                        Article.bukkinngnorma.contains(keyword),  # 追加
                        Article.janre.contains(keyword),  # 追加
                        
                        Article.hall_rental_details.contains(keyword),  # hall_rental_details
                        Article.booking_live.contains(keyword),  # booking_live
                        Article.one_drink_price.contains(keyword),  # one_drink_price
                        Article.secondary_use.contains(keyword),  # secondary_use
                        Article.streaming_live_available.contains(keyword)
                        
                    ))
                    articles = query.all()
                    matching_articles.extend(articles)

    # POSTリクエスト時または検索結果がある場合に結果を表示
    if request.method == "POST" or matching_articles:
        for article in matching_articles:
            print(article.id, article.title, article.description)
        return render_template("sarch.html", matching_articles=matching_articles)

    # GETリクエストでフォームを表示
    return render_template("sarch.html")

@app.route("/",methods=["GET","POST"])
def index():
    if request.method == "POST":
        return redirect(url_for('search_article'))
    return render_template("index.html")


@app.errorhandler(404)
def page_not_found(e):
    # 404.html テンプレートをレンダリングします。
    return render_template('404_Not.html'), 404


if __name__ == "__main__":
    #app.run('0.0.0.0', port=5000)
    
    #app.run('0.0.0.0',port=5000)
    serve(app, host='0.0.0.0', port=5000,threads=8)
    
    #本番
    #serve(app, host='0.0.0.0', port=80)
    #app.run(app, host='0.0.0.0', port=443, url_scheme='https', certfile='path_to_cert.pem', keyfile='path_to_key.pem')