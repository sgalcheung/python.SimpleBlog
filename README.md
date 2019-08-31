# SimpleBlog
本blog改编自[flask官方教程](https://flask.palletsprojects.com/en/1.1.x/tutorial/#tutorial)前端[首页](https://github.com/sgal008/web.html-and-css-visual-quickstart-guide/blob/master/chapter-12/finished-page.html)使用的是我的另一个repo[《HTML5与CSS3基础教程》](https://github.com/sgal008/web.html-and-css-visual-quickstart-guide)数据库使用的是sqlite3，模型设计采用了廖雪峰老师的[python实战项目](https://www.liaoxuefeng.com/wiki/1016959663602400/1018490658464544)blog分浏览文章的首页和个人管理中心，普通用户只能管理自己发布的文章，其中管理员可以同时管理普通用户发布的文章，但同是管理员之间不能操作对方发布的文章后台管理增加查看评论，删除评论功能，同上，普通用户自己操作自己的评论，管理员可以操作所有评论，但不包含其他管理员的评论后台管理增加查看注册用户信息功能，只允许管理员查看，删除用户会删除用户相关的文章和评论，请谨慎操作
#### 新技能
认识Flask框架，配置Flask安装环境，官方建议采用虚拟环境来开发和部署你的项目，Windows系统需要先安装python，通过cmd.exe安装
```bash
choco install python
```
如果没有安装[Chocolatey](https://chocolatey.org/install#installing-chocolatey)，先执行
```bash
@"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -InputFormat None -ExecutionPolicy Bypass -Command "iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))" && SET "PATH=%PATH%;%ALLUSERSPROFILE%\chocolatey\bin"
```
#### 创建一个环境
创建一个项目文件夹，其中包含一个venv文件
```
$ cd 你项目的存储位置
$ mkdir myproject
$ cd myproject
$ python3 -m venv venv
```
#### 激活创建的环境
在你开始你的项目之前，激活相应的环境，您的shell提示符将更改为显示激活环境的名称
```
$ . venv/bin/activate
> venv\Scripts\activate    # On Windows
```
#### 安装Flask
```
$ pip install Flask
```
#### 创建一个项目目录
```
$ mkdir flaskr
$ cd flaskr
```
#### 应用工厂
##### flaskr/_init_.py
```
flaskr/__init__.py
import os

from flask import Flask


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    return app
```
#### 运行应用程序
```
对于Linux和Mac
```
$ export FLASK_APP=flaskr
$ export FLASK_ENV=development
$ flask run
```
对于Windows cmd，请使用set而不是export：
```
> set FLASK_APP=flaskr
> set FLASK_ENV=development
> flask init-db           # 运行此项目需要初始化数据库
> flask run               # 出现异常，使用python -m flask run
```
项目结构目录最终类似于如下
```
/home/user/Projects/python.SimpleBlog
├── .vscode/              # 开发编辑器VS Code，与项目无关
|   ├── launch.json
|   ├── settings.json
├── flaskr/
│   ├── __init__.py
│   ├── db.py
│   ├── schema.sql
│   ├── auth.py
│   ├── blog.py
│   ├── templates/
│   │   ├── base.html
│   │   ├── auth/
│   │   │   ├── login.html
│   │   │   └── register.html
│   │   └── blog/
│   │       ├── create.html
│   │       ├── index.html
│   │       └── update.html
│   └── static/
│       └── style.css
├── tests/
│   ├── conftest.py
│   ├── data.sql
│   ├── test_factory.py
│   ├── test_db.py
│   ├── test_auth.py
│   └── test_blog.py
├── venv/
├── setup.py
└── MANIFEST.in
