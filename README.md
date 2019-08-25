# SimpleBlog
使用flask写一个简单的blog

[本blog改编自flask官方教程](https://flask.palletsprojects.com/en/1.1.x/tutorial/#tutorial)

前端[首页](https://github.com/sgal008/web.html-and-css-visual-quickstart-guide/blob/master/chapter-12/finished-page.html)使用的是[《HTML5与CSS3基础教程》](https://github.com/sgal008/web.html-and-css-visual-quickstart-guide)

数据库使用的是sqlite3，模型设计采用了廖雪峰老师的[python实战项目](https://www.liaoxuefeng.com/wiki/1016959663602400/1018490658464544)

blog分浏览文章的首页和个人管理中心，普通用户只能管理自己发布的文章，其中管理员可以同时管理普通用户发布的文章，但同是管理员之间不能操作对方发布的文章

后台管理增加查看评论，删除评论功能，同上，普通用户自己操作自己的评论，管理员可以操作所有评论，但不包含其他管理员的评论

后台管理增加查看注册用户信息功能，只允许管理员查看，删除用户涉及到用户相关的文章和评论
