import os
from flask import Flask, Blueprint, request, render_template, flash, redirect, url_for
#Flask 객체 인스턴스 생성
main = Blueprint( 'main', __name__, url_prefix='/')
app = Flask(__name__)

@app.route('/', methods= ['GET']) # 접속하는 url
def index():
    from utils import mysql
    print("here")
    res =  mysql.mysql_sample_query()
    #print(res)
    return render_template('index.html', data =res )

if __name__=="__main__":
    app.run(debug=True, host = '0.0.0.0', port = 80)

