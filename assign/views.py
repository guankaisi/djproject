from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.db import connection
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.views import generic
from django.utils import timezone

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import views as auth_views, authenticate, login
from django.http import JsonResponse

import json, time, re, requests, logging

from .forms import NameForm, RegisterForm, LoginForm, SearchForm#test for nameform
colors = (
    'Aqua','Aquamarine', 'Lavender', 'LightCyan', 'Brown', 'BurlyWood', 'SeaShell', 'Azure', 'Beige',
    'Bisque', 'DodgerBlue', 'FloralWhite', 'HoneyDew', 'DarkOrange','DarkSalmon','DarkSeaGreen','Snow',
    'DarkTurquoise','Navy'
)
logger = logging.getLogger(__name__)


#注册视图，考虑要不要检查前端发过来的数据有效性，如果无效应该怎么处理
def register(request):
    print("test register")
    if request.method == 'GET':
        print("tets GET")
    else:
        #form = RegisterForm(request.POST)
        print("test POST")
        username = request.POST.get('account')
        password = request.POST.get('password')
        try:
            print("test register valid")
            user = User.objects.create_user(username=username, password=password)
            user.save()
            #form.success = True
            response = HttpResponse(json.dumps({"status": 1}))
            #return HttpResponseRedirect(reverse('assign:login'))
            return response
        except:
            print("test register invalid")
            #form = RegisterForm()
            #form.duplicate = True
            #msg = "用户名或密码错误"
            #return render(request, 'accounts/register.html', {'form': form, 'msg': msg})
            response = HttpResponse(json.dumps({"status": 0}))
            return response
    
    return render(request, 'accounts/register.html')
'''
        if form.is_valid():
            print(form.cleaned_data['username'])
            try:
                print("test register valid")
                user = User.objects.create_user(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
                user.save()
                form.success = True
                return HttpResponseRedirect(reverse('assign:login'))
            except:
                print("test register invalid")
                form = RegisterForm()
                #form.duplicate = True
                msg = "用户名或密码错误"
                return render(request, 'accounts/register.html', {'form': form, 'msg': msg})
'''
    

# 人大验证登陆
def loggin(request):
    loginServer = "http://cas.ruc.edu.cn/cas/login"
    myurl = "http://180.76.163.103/assign/accounts/cas"
    print("test")
    return redirect(loginServer+'?service='+myurl,code=302)

def _login(request):
    next = ""
    status = 0
    if request.method == 'GET':
        #当提交方式为GET时有两种情况：1.用户直接访问登录界面 2.用户先进入其它url后被重定向
        #此处需要加一个判断next是否为本网站中已有url的部分
        try:
            next = request.GET['next']
            print(type(next))
        except:
            next = ""
            print('error next')
    else:
        #form = LoginForm(request.POST)
        try:
            account = request.POST.get('account')
            password = request.POST.get('password')
        except:
            account = ""
            password = ""

        print("test post") 
        user = authenticate(username=account, password=password)
        if user is not None: #用户存在，按照用户类型（老师/管理员）跳转到相应页面
            login(request, user)
            if user.is_staff:
                next = reverse('assign:admin_index')
            else:
                next = reverse('assign:teacher_index')
            print("login success")
            print(next)
            
            response = HttpResponse(json.dumps({
                "status": 1,
                "next": next             
            }))
            return response
            
        else: #用户不存在
            #form.error = True
            #print(form.error)
            status = 0
            response = HttpResponse(json.dumps({
                "status": status,             
            }))
            return response
            
    return render(request, 'accounts/login.html')


def cas(request):
    print("cas test")
    ticket = request.GET["ticket"]
    print(ticket)
    myurl ="http://180.76.163.103/assign/accounts/cas" 
    validateServer = "http://cas.ruc.edu.cn/cas/serviceValidate"
    validateurl = validateServer+"?ticket="+ticket+'&service='+myurl
    content = requests.get(validateurl).text

    # 使用正则表达式得到ruc.cas返回的学号和名字
    sch = re.search(r'uid.*value="(.*)"', content, re.M|re.I)
    uid = sch.group(1) 
    # sch = re.search(r'name="sn".*value="(.*)"', content, re.M|re.I)
    # uname = sch.group(1)

    # 和现有数据库内账户匹配
    try:
        user = User.objects.get(username=uid)
        login(request, user)
        print("user exitsts")
        if user.is_staff:
            next = reverse('assign:admin_index')
        else:
            next = reverse('assign:teacher_index')
        return redirect(next)
    except:
        print("user not exists")
        # request.session.flush()
        return HttpResponse(content="sorry no permission")


@login_required()
def logout(request):
    #return HttpResponse('test')
    request.session.flush()
    return redirect(reverse('assign:login'))
    # return auth_views.logout_then_login(request)


def get_name(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = NameForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # redirect to a new URL:
            return HttpResponseRedirect(reverse('assign:teacher'))
    # if a GET (or any other method) we'll create a blank form
    else:
        form = NameForm()

    return render(request, 'assign/test.html', {'form': form})


#老师登陆时看到的工位布局图
#需要先查房间，按照房间id排序，得到一个二维list，每个元素都为[id,_row,line]
#根据房间号去合并Chair和Student，得到二维数组，第二维方向上每个元素为一个学生使用工位记录
@login_required()
def teacher_index(request):
    tid = request.user.username
    username = request.user.first_name
    print(tid)
    print(username)
    with connection.cursor() as cursor:
        #得到房间信息
        cursor.execute("select id,_row,line from Room order by id asc")
        list_lab_info = list(cursor.fetchall())
        print(list_lab_info)
        #得到每个房间的工位信息
        list_seat_info = []
        for e in list_lab_info:
            cursor.execute("select C._row,C.line,C.id,C.ctype,C.taken,S.name,S.id,S.stype,S.tid,T.gname from Chair C left join Student S on C.id=S.cid left join Teacher T on S.tid = T.id where C.rid=%s;",[e[0]])
            list_seat_info.append(list(cursor.fetchall()))
        #得到每个老师和对应名字的字典
        cursor.execute("select id,name from Teacher order by id asc")
        dict_tname = dict(cursor.fetchall())
        #得到老师id和对于颜色的字典（检查老师和颜色的数量）
        cursor.execute("select id from Teacher order by id asc")
        temp = cursor.fetchall()
        ids = []
        for t in range(len(temp)):
            ids.append(temp[t][0])
        dict_color = dict(zip(ids,colors))

        # 得到当前老师的学生信息，按学号排序（注：入学年份不可被json）
        cursor.execute("select S.name,S.id,S.stype,C.rid,C.id from Student S,Chair C where S.tid=%s and C.id=S.cid order by S.id",[tid])
        list_student_info = cursor.fetchall()
        attrs = ['姓名','学号','身份','入学年份','所在房间','工位编号']
        #list_student_info = [['张敏', '20201010', '研一', '何军', '1', '1111111'],
        #     ['张敏', '20201010', '研一', '何军', '1', '1111111']]
        
        # 得到每个实验室内老师的编号，通过某个实验室中学生得到当前实验室中老师有哪些
        # 注意某些学生没有被分配座位，不应该算在内
        list_lab_teacher = []
        for lab in list_lab_info:
            temp = [lab[0]]
            cursor.execute("select tid from Student where cid like %s and cid is not null", [str(lab[0])+'%'])
            for e in cursor.fetchall():
                if e[0] not in temp:
                    temp.append(e[0])
            list_lab_teacher.append(temp)
        
        # 得到包含有该导师学生的实验室数组
        list_index= []
        for i in range(len(list_lab_info)):
            if tid in list_lab_teacher[i]:
                list_index.append(i)
        
    return render(request, 'assign/teacher_index.html', context={
        'tid': json.dumps(tid), 
        'username': json.dumps(username),
        'list_lab_info': json.dumps(list_lab_info),
        'list_seat_info': json.dumps(list_seat_info),
        'dict_tname': json.dumps(dict_tname),
        'dict_color': json.dumps(dict_color),
        'list_student_info': json.dumps(list_student_info),
        'list_lab_teacher': json.dumps(list_lab_teacher),
        'list_index': json.dumps(list_index)
        })


# 录入视图
@login_required()
def teacher_enroll(request):
    # 前台记录的各个字段意义
    attrs = ['学号','姓名','身份','入学年份','所在房间','工位编号']
    tid = request.user.username
    username = request.user.first_name

    if request.method == "GET":
        with connection.cursor() as cursor:
            # 首先得到某个老师的学生列表
            # 要允许某些学生并没有被分配座位
            sql = "select S.id,S.name,S.stype,date_format(S.enroll_date,'%Y.%m.%d'),C.rid,S.cid from Student S left join Chair C on S.cid=C.id where S.tid=\'" + str(tid) + "\'"
            cursor.execute(sql)
            list_student_info = list(cursor.fetchall())
            print("enroll")
            print(str(tid))
            print(list_student_info)
    else:
        # 前台会返回所有记录，包括存在的和不存在的，逐个把前台返回的数据插入数据库，如果插入失败就跳过
        # 要先把该导师的所有学生记录删除（写一个触发器，使得删除某个学生记录后原有位置无人使用）

        # 得到前台的数据
        sno = request.POST.getlist('sno')
        sname = request.POST.getlist('sname')
        stype = request.POST.getlist('stype')
        sdate = request.POST.getlist('sdate')

        # 保留下每个老生对应的工位，在往数据库中插入数据时先检查是否为老生
        # 老生的工位使用原有位置，新生的工位置为NULL
        with connection.cursor() as cursor:
            try:
                cursor.execute("select id,cid from Student where tid=%s", [tid])
                old_student = dict(cursor.fetchall())
                cursor.execute("delete from Student where tid=%s", [tid])
                for i in range(len(sno)):
                    try:
                        if sno[i] in old_student:
                            cursor.execute("insert into Student values(%s,%s,%s,%s,%s,%s)", [sno[i],sname[i],stype[i],sdate[i],old_student[sno[i]],tid])
                        else:
                            cursor.execute("insert into Student values(%s,%s,%s,%s,null,%s)", [sno[i],sname[i],stype[i],sdate[i],tid])
                    except:
                        continue
                now = time.strftime('%Y-%m-%d',time.localtime(time.time()))
                cursor.execute("update Teacher set last_date=%s where id=%s", [now,tid])

                response = HttpResponse(json.dumps({
                    "status": 1
                }))
            except:
                response = HttpResponse(json.dumps({
                    "status": 0
                }))

        return response
        

    return render(request, 'assign/teacher_enroll.html', {
        'attrs': json.dumps(attrs),
        'username': json.dumps(username),
        'list_student_info': json.dumps(list_student_info)
    })


# 管理员视图
@login_required()
def admin_index(request):
    with connection.cursor() as cursor:
        #得到房间信息
        cursor.execute("select id,_row,line from Room order by id asc")
        list_lab_info = list(cursor.fetchall())
        #得到每个房间的工位信息
        list_seat_info = []
        for e in list_lab_info:
            cursor.execute("select C._row,C.line,C.id,C.ctype,C.taken,S.name,S.id,S.stype,S.tid,T.gname from Chair C left join Student S on C.id=S.cid left join Teacher T on S.tid = T.id where C.rid=%s;",[e[0]])
            list_seat_info.append(list(cursor.fetchall()))
        #得到每个老师和对应颜色的字典
        cursor.execute("select id,name from Teacher order by id asc")
        dict_tname = dict(cursor.fetchall())
        #得到老师id和对于颜色的字典（检查老师和颜色的数量）
        cursor.execute("select id from Teacher order by id asc")
        temp = cursor.fetchall()
        ids = []
        for t in range(len(temp)):
            ids.append(temp[t][0])
        dict_color = dict(zip(ids,colors))

        # 得到每个实验室内老师的编号，通过某个实验室中学生得到当前实验室中老师有哪些
        list_lab_teacher = []
        for lab in list_lab_info:
            temp = [lab[0]]
            cursor.execute("select tid from Student where cid like %s", [str(lab[0])+'%'])
            for e in cursor.fetchall():
                if e[0] not in temp:
                    temp.append(e[0])
            list_lab_teacher.append(temp) 
        
        # 得到未分配座位学生名单
        cursor.execute("select S.name,S.id,S.stype,S.enroll_date,T.name from Student S,Teacher T where S.cid=NULL and S.tid=T.id order by T.id")
        list_student_info = list(cursor.fetchall())
        # 定义界面中每栏的意义
        attrs = ['姓名','学号','身份','入学年份','导师姓名']
    return render(request, 'assign/admin_index.html', {
        'username': json.dumps(request.user.first_name),
        'list_lab_info': json.dumps(list_lab_info),
        'list_seat_info': json.dumps(list_seat_info),
        'list_student_info': json.dumps(list_student_info),
        'list_lab_teacher': json.dumps(list_lab_teacher),
        'dict_color': json.dumps(dict_color),
        'dict_tname': json.dumps(dict_tname)        
    })


# 账户管理界面
@login_required()
def admin_account(request):
    if request.method == "GET":
        with connection.cursor() as cursor:
            cursor.execute("select username,first_name,is_staff from auth_user")
            account_info = cursor.fetchall()
            
            cursor.execute("select name,date_format(last_date,'%Y.%m.%d') from Teacher")
            enroll_info = cursor.fetchall()

        return render(request, 'assign/admin_account.html', {
            'username': json.dumps(request.user.first_name),
            'account_info': json.dumps(account_info),
            'enroll_info': json.dumps(enroll_info)
        })        
    else:
        with connection.cursor() as cursor:
            _type = request.POST['status']
            print(_type)
            if _type == '0': # 添加账户，同时添加一个老师记录
                try:
                    account_info = request.POST.getlist('account_info')
                    for e in account_info:
                        if len(e) == 0:
                            break
                    if account_info[3] != account_info[4]: # 两次密码不一致
                        status = 0
                    else:
                        if account_info[2] == '0': # 教授
                            user = User.objects.create_user(username=account_info[0], password=account_info[3])
                            if user is not None:
                                user.first_name = account_info[1]
                                user.save()
                                status = 1
                                with connection.cursor() as cursor: # 添加老师
                                    cursor.execute("insert into Teacher(id,name,Title) values(%s,%s,%s)", [user.username,user.first_name,"教授"])
                            else:
                                status = 0
                        elif account_info[2] == '1': # 副教授
                            user = User.objects.create_user(username=account_info[0], password=account_info[3])
                            if user is not None:
                                user.first_name = account_info[1]
                                user.save()
                                status = 1
                                with connection.cursor() as cursor: # 添加老师
                                    cursor.execute("insert into Teacher(id,name,Title) values(%s,%s,%s)", [user.username,user.first_name,"副教授"])
                            else:
                                status = 0

                        elif account_info[2] == '2': #讲师
                            user = User.objects.create_user(username=account_info[0], password=account_info[3])
                            if user is not None:
                                user.first_name = account_info[1]
                                user.save()
                                status = 1
                                with connection.cursor() as cursor: # 添加老师
                                    cursor.execute("insert into Teacher(id,name,Title) values(%s,%s,%s)", [user.username,user.first_name,"讲师"])
                            else:
                                status = 0

                        else: # 管理员
                            user = User.objects.create_superuser(username=account_info[0], password=account_info[3])
                            if user is not None:
                                user.first_name = account_info[1]
                                user.save()
                                status = 1
                            else:
                                status = 0
                except:
                    status = 0
            else: # 删除账户，同时删除导师记录
                try:
                    delete_info = request.POST.getlist('delete_info')
                    for ac in delete_info:
                        ac = ac.split(',')
                        user = User.objects.get(username=ac[0])
                        if user is not None:
                            user.delete()
                            with connection.cursor() as cursor:
                                cursor.execute("delete from Teacher where id=%s", [ac[0]])
                            status = 1
                        else:
                            status = 0
                except:
                    status = 0
            
            response = HttpResponse(json.dumps({
                "status": status
            }))
        return response
import datetime
@login_required()
def admin_graduate(request):
    if request.method == "GET":
        with connection.cursor() as cursor:
            cursor.execute("select id,name,stype,left(id,4) year from Student where length(id) = 10")
            student_info = cursor.fetchall()
            graduatelist = []
            curYear = datetime.datetime.today().year
            for student in student_info:
                id,name,stype,year = student
                if stype=="直博" and int(year)+5<=curYear:
                    graduatelist.append(student)
                if stype=="普通博士" and int(year)+3<=curYear:
                    graduatelist.append(student)
                if stype=="学硕" and int(year)+3<=curYear:
                    graduatelist.append(student)
                if stype=="非全日制工硕" and int(year)+2<=curYear:
                    graduatelist.append(student)
                if stype=="全日制工硕" and int(year)+2<=curYear:
                    graduatelist.append(student)
        return render(request, 'assign/admin_graduate.html', {
            'username': json.dumps(request.user.first_name),
            'graduate_info': json.dumps(tuple(graduatelist))
        })        
    else:
        _type = request.POST['status']
        try:
            delete_info = request.POST.getlist('delete_info')
            for stu in delete_info:
                with connection.cursor() as cursor:
                    cursor.execute("delete from Student where id=%s",[stu])
            status = 1   
        except:
            status = 0

        response = HttpResponse(json.dumps({
            "status": status,
        }))
        return response
#座位排布
@login_required()
def admin_seat(request):
    if request.method == "GET":
        with connection.cursor() as cursor:
            # 得到未分配座位学生名单
            cursor.execute("select S.id,S.name,S.stype,T.name from Student S,Teacher T where S.cid is NULL and S.tid=T.id order by T.id")
            list_student_info = list(cursor.fetchall())
            #得到房间信息
            cursor.execute("select id,_row,line from Room order by id asc")
            list_lab_info = list(cursor.fetchall())
            #得到每个房间的工位信息
            list_seat_info = []
            for e in list_lab_info:
                cursor.execute("select C._row,C.line,C.id,C.ctype,C.taken,S.name,S.id,S.stype,S.tid,T.gname from Chair C left join Student S on C.id=S.cid left join Teacher T on S.tid = T.id where C.rid=%s;",[e[0]])
                list_seat_info.append(list(cursor.fetchall()))
            #得到每个老师和对应名字的字典
            cursor.execute("select id,name from Teacher order by id asc")
            dict_tname = dict(cursor.fetchall())
        return render(request, 'assign/admin_seat.html',{
            'username': json.dumps(request.user.first_name),
            "list_student_info": json.dumps(list_student_info),
            "list_lab_info": json.dumps(list_lab_info),
            "list_seat_info": json.dumps(list_seat_info),
            "dict_tname": json.dumps(dict_tname)
        })
    else:
        new_list_student_info = ""
        actype = request.POST['actype']
        if actype == "8" or actype == "9" or actype == "10" or actype == "11" or actype == "13":
            try:
                status = 1
                with connection.cursor() as cursor:
                    if actype == "8":
                        cursor.execute("select S.id,S.name,S.stype,T.name from Student S,Teacher T where S.cid is NULL and S.tid=T.id order by S.id")
                        new_list_student_info = list(cursor.fetchall())
                    elif actype == "9":
                        cursor.execute("select S.id,S.name,S.stype,T.name from Student S,Teacher T where S.cid is NULL and S.tid=T.id order by S.name")
                        new_list_student_info = list(cursor.fetchall())
                    elif actype == "10":
                        cursor.execute("select S.id,S.name,S.stype,T.name from Student S,Teacher T where S.cid is NULL and S.tid=T.id order by T.name")
                        new_list_student_info = list(cursor.fetchall())
                    elif actype == "11":
                        cursor.execute("select S.id,S.name,S.stype,T.name from Student S,Teacher T where S.cid is NULL and S.tid=T.id order by S.stype")
                        new_list_student_info = list(cursor.fetchall())
                    elif actype == "13":
                        cursor.execute("select S.id,S.name,S.stype,T.name from Student S,Teacher T where S.cid is NULL and S.tid=T.id order by S.id")
                        new_list_student_info = list(cursor.fetchall())
            except:
                status = 0
            response = HttpResponse(json.dumps({
                "status": status,
                "new_list_student_info":new_list_student_info
            }))
        elif actype == "12":
            try: 
                stype = request.POST['stype']
                key = request.POST['key']
            except:
                stype = 0
                key = ""
            try:
                status = 1
                with connection.cursor() as cursor:
                    if stype == '1':
                        cursor.execute("select S.id,S.name,S.stype,T.name from Student S,Teacher T where S.cid is NULL and S.tid=T.id and S.id=%s order by T.id",[key])
                        new_list_student_info = list(cursor.fetchall())
                    elif stype == "2":
                        cursor.execute("select S.id,S.name,S.stype,T.name from Student S,Teacher T where S.cid is NULL and S.tid=T.id and S.name=%s order by T.id",[key])
                        new_list_student_info = list(cursor.fetchall())
                    elif stype == "3":
                        cursor.execute("select S.id,S.name,S.stype,T.name from Student S,Teacher T where S.cid is NULL and S.tid=T.id and T.name=%s order by T.id",[key])
                        new_list_student_info = list(cursor.fetchall())
                    elif stype == "4":
                        cursor.execute("select S.id,S.name,S.stype,T.name from Student S,Teacher T where S.cid is NULL and S.tid=T.id and S.stype=%s order by T.id",[key])
                        new_list_student_info = list(cursor.fetchall())
            except:
                status = 0
            response = HttpResponse(json.dumps({
                "status": status,
                "new_list_student_info":new_list_student_info,
            }))
        else:
            info = request.POST.getlist('info')
            _row = info[1]
            line = info[2]
            if len(_row) == 1:
                _row = '0'+_row
            if len(line) == 1:
                line = '0' + line
            cid = info[0] + _row + line
            try:
                turn = False
                with connection.cursor() as cursor:
                    if actype == '0': # 创建一个工位
                        cursor.execute("insert into Chair values(%s,%s,%s,%s,%s,%s)",[cid,info[0],info[1],info[2],info[3],'0'])
                    elif actype == '1': # 删除工位
                        cursor.execute("delete from Chair where id = %s", [cid])
                    elif actype == '2': # 把某个工位分配给某个学生
                        cursor.execute("update Student set cid = %s where id = %s", [cid,info[3]])
                    elif actype == '3': # 学生不再使用某个工位
                        cursor.execute("update Student set cid=NULL where id = %s", [info[3]])
                    elif actype == '4': # 交换
                        # cursor.execute("update Student set cid=NULL where id = %s", [info[3]])
                        cursor.execute("update Student set cid=%s where id = %s", [cid,info[4]])
                    elif actype == '5': # 验证实验室行列修改是否合法
                        cursor.execute("select * from Chair where taken='1' and rid=%s and (_row>=%s or line>=%s)", [info[0],info[1],info[2]])
                        temp = cursor.fetchall()
                        cursor.execute("select * from Room where id=%s",[info[0]])
                        room = cursor.fetchall()
                        if len(room) != 0 and (room[0][1] != int(info[1]) or room[0][2] != int(info[2])): # 进行房间行列修改
                            if len(temp) != 0:
                                turn = True
                            else:
                                cursor.execute("update Room set _row=%s,line=%s where id=%s", [info[1],info[2],info[0]])
                    elif actype == '6': # 添加房间
                        cursor.execute("insert into Room values(%s,%s,%s)",[info[0],info[1],info[2]])
                    elif actype == '7': # 删除房间
                        cursor.execute("delete from Room where id=%s", [info[0]])
                status = 1
                if turn:
                    status = 0
            except:
                status = 0

            response = HttpResponse(json.dumps({
                "status": status
            }))
        return response


            
    




# 查询视图，返回查询界面
@login_required()
def search(request):
    user = request.user
    if user.is_staff:
        url = 'assign/admin_search.html'
    else:
        url = 'assign/teacher_search.html'
    return render(request, url, {
        'username': json.dumps(user.first_name)
    })


# 返回查询结果
@login_required()
def query(request):
    try: 
        stype = request.GET['stype']
        key = request.GET['key']
        #print("test get")
    except:
        stype = 0
        key = ""
    print(stype)
    print(key)

    # 以下数据要返回给前台
    list_seat_info = []
    list_lab_info = []
    search_col = int()
    search_key = str()
    status = 0
    with connection.cursor() as cursor:
        if stype == '1': #学生学号，先找到该学生所在实验室，然后把该实验室中的工位取出
            print("test")
            cursor.execute("select C.rid from Student S,Chair C where S.id=%s and S.cid=C.id", [key])
            try: # 不存在结果
                rid = cursor.fetchone()[0]
                # 得到房间
                cursor.execute("select id,_row,line from Room where id =%s",[rid])
                list_lab_info.append(cursor.fetchone())
                # 得到该房间的工位
                cursor.execute("select C._row,C.line,C.id,C.ctype,C.taken,S.name,S.id,S.stype,S.tid,T.gname from Chair C left join Student S on C.id=S.cid left join Teacher T on S.tid = T.id where C.rid=%s;",[rid])
                list_seat_info.append(cursor.fetchall())
            except TypeError:
                status = 1
            # col
            search_col = 6
            search_key = key
        elif stype == '2': # 学生姓名，先找到该学生所在实验室，然后把该实验室中的工位取出     
            cursor.execute("select C.rid from Student S,Chair C where S.name=%s and S.cid=C.id", [key])
            try: # 不存在结果
                rid = cursor.fetchone()[0]
                # 得到房间
                cursor.execute("select id,_row,line from Room where id =%s",[rid])
                list_lab_info.append(cursor.fetchone())
                # 得到该房间的工位
                cursor.execute("select C._row,C.line,C.id,C.ctype,C.taken,S.name,S.id,S.stype,S.tid,T.gname from Chair C left join Student S on C.id=S.cid left join Teacher T on S.tid = T.id where C.rid=%s;",[rid])
                list_seat_info.append(cursor.fetchall())
            except TypeError:
                status = 1
            # col
            search_col = 5
            search_key = key
        elif stype == '3': # 导师编号，先得到导师学生所在实验室，再得到实验室的工位信息
            cursor.execute("select R.id,R._row,R.line from Teacher T, Student S, Chair C, Room R where T.id=%s and S.tid=T.id and S.cid = C.id and C.rid=R.id order by R.id", [key])
            temp = cursor.fetchall()
            print(temp)
            try:
                temp[0]
                for t in temp:
                    if t not in list_lab_info:
                        list_lab_info.append(t)
                # 得到该房间的工位
                for lab in list_lab_info:
                    cursor.execute("select C._row,C.line,C.id,C.ctype,C.taken,S.name,S.id,S.stype,S.tid,T.gname from Chair C left join Student S on C.id=S.cid left join Teacher T on S.tid = T.id where C.rid=%s;",[lab[0]])
                    list_seat_info.append(cursor.fetchall())
            except TypeError:
                status = 1
            # col
            search_col = 8
            search_key = key
        elif stype == '4': # 课题组，先查询课题组中的老师，然后查询学生，根据学生得到，但是会遇到实验室重复的情况
            #print(key)
            appr_labs = dict()
            cursor.execute("select id from Teacher where gname=%s order by id", [key])
            try:
                tids = cursor.fetchall()
                tids[0]
                # 得到需要显示的实验室
                for tid in tids:
                    cursor.execute("select R.id,R._row,R.line from Teacher T, Student S, Chair C, Room R where T.id=%s and S.tid=T.id and S.cid = C.id and C.rid=R.id order by R.id", [tid])
                    temp = cursor.fetchall()
                    for r in temp:
                        if r[0] not in appr_labs:
                            list_lab_info.append(r)
                            appr_labs[r[0]] = True
                list_lab_info.sort(key=lambda x:x[0],reverse=False) # 实验室按照编号升序排列
                # 得到房间的工位
                for lab in list_lab_info:
                    cursor.execute("select C._row,C.line,C.id,C.ctype,C.taken,S.name,S.id,S.stype,S.tid,T.gname from Chair C left join Student S on C.id=S.cid left join Teacher T on S.tid = T.id where C.rid=%s;",[lab[0]])
                    list_seat_info.append(cursor.fetchall())
            except IndexError:
                status = 1
            # col
            search_col = 9
            search_key = key
        elif stype == '5': # 查询空闲工位
            # 得到有空闲工位的实验室
            cursor.execute("select R.id,R._row,R.line from Room R where exists(select * from Chair C where R.id=C.rid and C.taken='0')")
            try:
                temp = cursor.fetchall()
                temp[0]
                list_lab_info = list(temp) 
                # 得到工位
                for lab in list_lab_info:
                    cursor.execute("select C._row,C.line,C.id,C.ctype,C.taken,S.name,S.id,S.stype,S.tid,T.gname from Chair C left join Student S on C.id=S.cid left join Teacher T on S.tid = T.id where C.rid=%s;",[lab[0]])
                    list_seat_info.append(cursor.fetchall())
            except TypeError:
                status = 1
            # col
            search_col = 4
            search_key = '0'
            
    response = HttpResponse(json.dumps({"status":status, 
                                        "list_lab_info":list_lab_info,
                                        "list_seat_info":list_seat_info,
                                        "search_col":search_col,
                                        "search_key":search_key}))

    return response

# 个人资料视图
@login_required()
def person_info(request):
    user = request.user

    if request.method == "POST":
        _type = request.POST['_type']
        if _type == '0':
            rid = request.POST['roomid']
            with connection.cursor() as cursor:
                try:
                    cursor.execute("select* from Room where id=%s",[rid])
                    temp = cursor.fetchall()
                    if len(temp) == 0: # 房间不存在
                        raise EnvironmentError
                    cursor.execute("update Teacher set rid=%s where id=%s", [rid,user.username])
                    status = 1
                except:
                    status = 0
        elif _type == '1':
            password_old = request.POST['password1']
            password_new1 = request.POST['password2']
            password_new2 = request.POST['password3']
            user = authenticate(username=user.username, password=password_old)
            if user is not None and password_new1==password_new2: # 原密码正确并且两次输入的密码相同
                try:
                    user.set_password(password_new1)
                    user.save()
                    status = 1
                except:
                    status = 0
            else:
                status = 0
        else:
            gname = request.POST['gname']
            with connection.cursor() as cursor:
                try:
                    cursor.execute("update Teacher set gname=%s where id=%s", [gname, user.username])
                    status = 1
                except:
                    status = 0

        response = HttpResponse(json.dumps({
            "status": status
        })) 
        return response       
        
    if user.is_staff:
        url = 'assign/admin_info.html'
        roomid = 0
        gname = ""
    else:
        url = 'assign/teacher_info.html'
        with connection.cursor() as cursor:
            cursor.execute("select rid,gname from Teacher where id=%s", [user.username])
            temp = cursor.fetchall()
            roomid = temp[0][0]
            gname = temp[0][1]

    return render(request, url, {
        'tid': json.dumps(user.username),
        'username': json.dumps(user.first_name),
        'roomid': json.dumps(roomid),
        'gname': json.dumps(gname)
    })        


# 自动分配工位视图
@login_required()
def auto_assign(request):
    # 先得到未被分配工位的学生名单（按照“直博 > 普通博士 > 学硕 > 全日制工硕 > 非全日制工硕”的顺序，
    #                           优先级越高，排在越前面）
    # 编号 期望分配的实验室
    print("test auto")
    try:
        with connection.cursor() as cursor:
            cursor.execute("select S.id,T.rid from Student S,Teacher T where S.cid is null and S.tid=T.id order by S.stype,S.id")
            cand = cursor.fetchall() # 是否要判断cand为空？
            untaken = dict() # 每个实验室的id为key，value为该实验室中空闲工位的id list（按照固定、临时的排序），
            cursor.execute("select id from Room order by id asc")
            labs = cursor.fetchall()
            for e in labs:
                cursor.execute("select id from Chair where rid=%s and taken='0' and ctype<>'2' order by ctype",[e[0]])
                eids = cursor.fetchall() # 得到每个实验室内空闲工位的编号
                temp = []
                for eid in eids:
                    temp.append(eid[0])
                untaken[e[0]] = temp
            print(untaken)

            for c in cand: # 先尝试把学生分配到导师所在的实验室，如果该实验室内没有空位，需要检查邻近的实验室
                if c[1] in untaken and len(untaken[c[1]]) != 0: # 学生期望实验室有空闲工位
                    # if len(untaken[c[1]]) != 0: # 对应实验室有空位
                    cursor.execute("update Student set cid=%s where id=%s", [untaken[c[1]][0], c[0]])
                    untaken[c[1]].pop(0)
                else: # 得到邻近实验室
                    cursor.execute("select id from Room R where id<>%s order by abs(id-%s)", [c[1],c[1]])
                    temp = cursor.fetchall()
                    print(temp)
                    for lab in temp: # 分配到邻近实验室  lab为(417,)的形式       
                        if len(untaken[lab[0]]) != 0:
                            print("test")
                            nei = lab[0]
                            cursor.execute("update Student set cid=%s where id=%s", [untaken[nei][0], c[0]])
                            untaken[nei].pop(0)
                            break
        status = 1
    except:
        status = 0

    response = HttpResponse(json.dumps({
        "status": status
    }))
    return response
        

'''
###### 分割线 以下是计费功能处 写好注释 #####
'''
# 实现计费功能，有两个函数，一个是管理员计费页面显式所有老师费用，一个是老师计费页面，显式自己的收费明细

# 测试视图函数
@login_required()
def test(request):
    test_name = "测试成功"
    view_list = ['测试1','测试2','测试3']
    return render(request,'assign/test.html',{"name":test_name,'view_list':view_list})


# 管理员计费函数
@login_required()
def admin_fee(request):
    if request.method == "GET":# 获取数据加载到网页页面上
        with connection.cursor() as cursor:
            sql = "select tname,Title,free_Postgraduate,free_Doctor,occupy_Postgraduate, occupy_Doctor,occupy_Other,unit_Price, Total_Price, pay from Fee"
            cursor.execute(sql)
            fee_info = cursor.fetchall()
            # print("WHat???")
            # print(json.dumps(fee_info))
        # print(request.user.first_name)
        # print("Here")
        # print(request.user.username)
        return render(request, 'assign/admin_fee.html', {
            'username': json.dumps(request.user.username),
            'fee_info': json.dumps(fee_info)
        })
    else:# 返回数据加载到数据库中
        # print("Yes????")
        with connection.cursor() as cursor:
            fee_info = request.POST.getlist('fee_info')
            print("Here")
            print(fee_info)
            print(type(fee_info))
            cursor.execute("update Fee set free_Postgraduate=%s,free_Doctor=%s,unit_Price=%s,Total_Price=%s,pay=%s where tname=%s",[fee_info[2],fee_info[3],fee_info[7],fee_info[8],fee_info[9],fee_info[0]])
            response = HttpResponse(json.dumps({
                "status":1
            }))
        return response




# 教师计费函数
@login_required()
def teacher_fee(request):
    teachername = request.user.first_name
    if request.method == "GET":
        tid = request.user.username
        with connection.cursor() as cursor:
            sql = "select tname,Title,free_Postgraduate,free_Doctor,occupy_Postgraduate, occupy_Doctor,occupy_Other,unit_Price,Total_Price, pay from Fee where Fee.tid = %s;"
            cursor.execute(sql, [tid])
            fee_info = cursor.fetchall()
        return render(request, 'assign/teacher_fee.html', {
            'teachername': json.dumps(teachername),
            'fee_info': json.dumps(fee_info)
        })   
    # test_name = "测试成功"
    # view_list = ['测试1','测试2','测试3']
    # return render(request,'assign/test.html',{"name":test_name,'view_list':view_list})



'''
##### 分割线  以下是 2,3,4功能代码处 请写好注释 ######
'''
@login_required()
def admin_info2(request):
    if request.method == "GET":
        with connection.cursor() as cursor:
            sql = "select Student.id,Student.name,stype,Teacher.name,enroll_date,Chair.rid,cid from Student Left join Chair on Student.cid=Chair.id,Teacher where Student.tid = Teacher.id"
            cursor.execute(sql)
            list_student_info = cursor.fetchall()
            info_lists = []
            for info in list_student_info:
                list_info = list(info)
                list_info[4] = str(list_info[4])
                info_lists.append(list_info)
        return render(request, 'assign/admin_student_info.html', {
                'username': json.dumps(request.user.username),
                'list_student_info':json.dumps(info_lists)
            })
    if request.method == "POST":
        sno = request.POST.getlist('sno')
        sname = request.POST.getlist('sname')
        stype = request.POST.getlist('stype')
        steacher = request.POST.getlist('steacher')
        sdate = request.POST.getlist('sdate')

        # 保留下每个老生对应的工位，在往数据库中插入数据时先检查是否为老生
        # 老生的工位使用原有位置，新生的工位置为NULL
        with connection.cursor() as cursor:
            try:
                cursor.execute("select id,cid from Student")
                old_student = dict(cursor.fetchall())
                print(old_student)
                cursor.execute("delete from Student")
                cursor.execute("select name,id from Teacher")
                teacher_dict = dict(cursor.fetchall())
                print(teacher_dict)
                for i in range(len(sno)):
                    print(sno)
                    try:
                        if sno[i] in old_student:
                            cursor.execute("insert into Student values(%s,%s,%s,%s,%s,%s)", [sno[i],sname[i],stype[i],sdate[i],old_student[sno[i]],teacher_dict[steacher[i]]])
                        else:
                            cursor.execute("insert into Student values(%s,%s,%s,%s,null,%s)", [sno[i],sname[i],stype[i],sdate[i],teacher_dict[steacher[i]]])
                    except:
                        continue

                response = HttpResponse(json.dumps({
                    "status": 1
                }))
            except:
                response = HttpResponse(json.dumps({
                    "status": 0
                }))
        return response

### 辅助函数先把像传输的数据映射到一个网页上 assign/admin/info/json,再用 axios.get提取数据
# 这里面的一些问题：print(rows)之后返现Student.name 不见了，sql语句中明明select了
def dictfetchall(cursor):
    "将游标返回的结果保存到一个字典对象中"
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]

@login_required()
def admin_info_JSON(request):
    if request.method == "GET":
        with connection.cursor() as cursor:
            # list_student_info = cursor.fetchall()
            sql = "select Student.id,Student.name as sname,stype,Teacher.name as tname,enroll_date,Chair.rid,cid from Student Left join Chair on Student.cid=Chair.id,Teacher where Student.tid = Teacher.id"
            cursor.execute(sql)
            rows = dictfetchall(cursor)
            rows_new = []
            for item in rows:
                new = {}
                new['stuNo'] = item['id']
                new['teacher'] = item['tname']
                new['identity'] = item['stype']
                new['name'] = item['sname']
                new['roomNo'] = item['rid']
                if new['roomNo'] == None:
                    new['roomNo'] = ""
                new['workNo'] = item['cid']
                if new['workNo'] == None:
                    new['workNo'] = ""
                new['date'] = item['enroll_date']
                rows_new.append(new)
            print(rows_new)
        return JsonResponse(rows_new, safe=False, json_dumps_params={'ensure_ascii': False})



@login_required()
@csrf_exempt
def admin_info(request):
    if request.method == "GET":
        return render(request, 'assign/admin_student_new.html', {
                'username': json.dumps(request.user.username),
            })
    if request.method == "POST":
        sno = request.POST.getlist('sno')
        sname = request.POST.getlist('sname')
        stype = request.POST.getlist('stype')
        steacher = request.POST.getlist('steacher')
        sdate = request.POST.getlist('sdate')

        # 保留下每个老生对应的工位，在往数据库中插入数据时先检查是否为老生
        # 老生的工位使用原有位置，新生的工位置为NULL
        with connection.cursor() as cursor:
            try:
                cursor.execute("select id,cid from Student")
                old_student = dict(cursor.fetchall())
                print(old_student)
                cursor.execute("delete from Student")
                cursor.execute("select name,id from Teacher")
                teacher_dict = dict(cursor.fetchall())
                print(teacher_dict)
                for i in range(len(sno)):
                    print(sno)
                    try:
                        if sno[i] in old_student:
                            cursor.execute("insert into Student values(%s,%s,%s,%s,%s,%s)", [sno[i],sname[i],stype[i],sdate[i],old_student[sno[i]],teacher_dict[steacher[i]]])
                        else:
                            cursor.execute("insert into Student values(%s,%s,%s,%s,null,%s)", [sno[i],sname[i],stype[i],sdate[i],teacher_dict[steacher[i]]])
                    except:
                        continue

                response = HttpResponse(json.dumps({
                    "status": 1
                }))
            except:
                response = HttpResponse(json.dumps({
                    "status": 0
                }))
        return response








