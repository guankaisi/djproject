# 中国人民大学工位管理系统

##  工位管理系统安装及部署说明

首先准备一个Ubuntu服务器，本次实验中选择的是华为弹性云服务器1vCPUs | 2GiB | t6.medium.2

Ubuntu 20.04 server 64bit

 

### **将项目下载到服务器**

```bash
cd home

git clone https://github.com/guankaisi/djproject
```

最终在/home文件夹下得到djproject文件夹

 

**配置虚拟环境**

~~~bash
**

```
virtualenv venv --python=python3.8
```

# 进入环境

source /home/venv/bin/activate

# 推出环境 

deactivate
~~~

 

 **数据库构建和链接**

首先安装mysql

```bash
sudo apt update

sudo apt install mysql-server
```

接下来mysql账户创建以及登录操作，登录mysql后，创建数据库一个数据库名为assign

接下来在djproject/mysite/settings.py文件中更改，数据库为自己的用户以及密码

```PytPyt
DATABASES = {

  'default': {

​    'ENGINE': 'django.db.backends.mysql',

​    'NAME': 'assign',

​    'USER': 'r2',

​    'PASSWORD': '1234',

​    'HOST': '127.0.0.1',

​    'PORT': '3306',

  }

}
```

 

**需要安装的软件**

1)使用pip3安装django3.1.3、pymysql和requests

```bash
pip3 install Django=3.1.3

pip3 install pymysql

pip3 install requests
```

如果服务器上没有pip3，可用apt-get install python-pip3命令安装

2)安装Apache2,在服务器上输入以下命令:

```bash
apt-get install apache2

apt-get install apache2-dev
```

3)安装mod_wsgi,在服务器上输入命令：

```
apt-get install libapache2-mod-wsgi-py3
```

上面的命令会在安装完成后自动启用mod_wsgi,但这一版本中的mod_wsgi.so文件版本较低，可能导致运行时错误，建议按照以下方法重新编译mod_wsgi.so

```
wget https://github.com/GrahamDumpleton/mod_wsgi/archive/4.7.1.tar.gz

tar xvfz 4.7.1.tar.gz
```

打开解压后得到的文件夹执行：

./configure --with-python=/usr/bin/python3.8 --with-python=后的地址为服务器上python可执行文件的地址 可用whereis python查询

```
make

make install
```

安装完成后可使用a2enmod wsgi检查mod_wsgi是否可用

参考链接https://modwsgi.readthedocs.io/en/develop/user-guides/quick-installation-guide.html



**Django****管理员账户生成与测试**

运行代码

```
python manager.py createsuperuser
```

创建管理员账户

```
 python manager.py tunserver 8080
```

在URL栏输入，localhost:8080/admin即可登录测试

 

**数据库内容表格以及触发器创建**

进入mysql

```
using assign
```

之后运行tables.sql,和triggers.sql文件（就在djproject文件夹下）

**Apache2设置部署**

需要对Apache2进行一些设置才能使系统在服务器上顺利运行。

1）在/etc/apache2/sites-available下添加一个文件djproject.conf,文件内容如下图(下图中的/home需要替换成venv和djproject两个文件夹的实际地址)：

```python
<VirtualHost  :80>
	WSGIDaemonProcess djproject python-home=/home/venv python-path=/home/djproject
    WSGIProcessGroup djproject
    WSGIScriptAlias / /home/djproject/mysite/wsgi.py
    <Directory home/djproject/mysite>
    <Files wsgi.py>
    	Require all granted
	</Files>
	</Directory>
    Alias /static/ /home/djproject/static root
    <Directory /home/djproject/static root>
    	Require all granted
    </Directory>
<VirtualHost>
```

​                               

2）输入命令

```
a2ensite djproject.conf
```

3)使用ls命令查看/etc/apache2/sites-enable 下的文件，对除djproject.conf文件之外全部.conf文件使用a2dissite命令（如果是第一次使用Apache2，则只有一个默认的000-default.conf）

```
a2dissite 000-default.conf
```

4)以上命令完成后，输入命令

```
apache2ctl restart
```

重启Apache2，就可以在浏览器上访问系统了

 

附件：已经本项目demo已经部署到服务器上，链接为

http://123.249.69.230/assign/admin/index/

服务器到期时间为2023/04/04
