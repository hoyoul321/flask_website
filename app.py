
from flask import Flask, render_template

#Flask 객체 인스턴스 생성
app = Flask(__name__)

@app.route('/') # 접속하는 url
def index():
    from utils import mysql
    res =  mysql.mysql_sample_query()
    print(res)
    return render_template('index.html', data =res )

if __name__=="__main__":
    app.run(debug=True)

