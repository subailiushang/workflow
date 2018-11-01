from django.shortcuts import render, redirect, HttpResponse
from django.http import JsonResponse
from .models import Project, DailyReports, MyUser
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from datetime import datetime, date
from django.db.models import Sum
import logging
import zmail

logger = logging.getLogger("default")


def login(request):
    """
    用户登陆验证，并将此登陆用户名，加入到session会话中保存
    :param request:
    :return:
    """
    if request.method == 'GET':
        return render(request, 'login.html')
    elif request.method == 'POST':
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)
        # authenticate验证用户名和密码
        print(username, password)
        user = auth.authenticate(request, username=username, password=password)
        print(user)
        if user is not None:
            auth.login(request, user)
            # 将登陆用户名加入到session会话中
            request.session['username'] = username
            return redirect('dailyReports')
        else:
            return HttpResponse("用户名或密码输入错误")


def register(request):
    if request.method == 'GET':
        return render(request, 'register.html')
    elif request.method == 'POST':
        email = request.POST.get('email', None)
        password = request.POST.get('password', None)
        check_email_password = zmail.server(username=email, password=password, smtp_host='smtp.pachiratech.com',
                                            smtp_port=25,
                                            smtp_ssl=False)
        if check_email_password.smtp_able():
            logger.info("密码验证通过")
            # 创建系统用户使用create_user 和 create_superuser
            MyUser.objects.create_user(username=email, password=password, email=email, emailpasswd=password)
            return redirect('login')
        else:
            logger.error("密码验证失败")
            return render(request, 'register.html', {'error': "邮箱密码输入错误"})


@login_required()
def logout(request):
    """
    用户退出，自动清理session会话
    :param request:
    :return:
    """
    auth.logout(request)
    return redirect('login')


@login_required()
def base(request):
    return render(request, 'base.html')


@login_required()
def dailyReports(request):
    # 获取今天日期
    today = datetime.now().date()
    if request.method == 'GET':
        username = request.session.get('username', None)
        names = Project.objects.all().values('name')

        # 获取当前登陆用户的日报内容-->web table显示该用户所有日期日报
        reports = DailyReports.objects.filter(creator=username).values()
        # 获取当前时间当前用户的日报内容--> 用于构造当日该用户日报内容
        todayReports = DailyReports.objects.filter(date=datetime.now(), creator=username).values()
        print(todayReports)
        # 构造日报内容
        sumReports = ''
        for todayReport in todayReports:
            sumReports = sumReports + "项目名称：" + todayReport['project'] + "\n耗费工时：" + str(
                todayReport['working_time']) + "\n主要工作内容：" + todayReport['content'] + "\n" + "\n"

        # 获取所有的user用于发送邮件
        users = MyUser.objects.values('username', 'email')

        return render(request, 'dailyReports.html',
                      context={'names': names, 'reports': reports, 'sumReports': sumReports, 'username': username,
                               'today': today, 'todayReports': todayReports, 'users': users})
    elif request.method == 'POST':
        name = request.POST.get('name', None)
        working_time = request.POST.get('working_time', None)
        content = request.POST.get('content', None)
        week = datetime.now().weekday()
        username = request.session.get('username', None)
        if name is not None:
            if DailyReports.objects.filter(project=name, date=today):
                return HttpResponse("<h2>今日已经添加此项目,请返回修改后重新提交<h2>")
            else:
                DailyReports.objects.create(project=name, working_time=working_time, content=content, week=week,
                                            creator=username)
                return redirect('dailyReports')
        else:
            sumReports = request.POST.get('sumReports', None)
            # getlist方法获取下拉多选框的值,获取邮件接收用户
            receivers = request.POST.getlist('email', None)
            # 发送邮件接口

            sender = MyUser.objects.get(username=username).email
            passwd = MyUser.objects.get(username=username).emailpasswd
            subject = username + ":" + str(today) + "日报"

            # 定义邮件发送功能
            # 1.邮件内容:主题+内容
            mail_content = {
                'subject': subject,
                'content': sumReports,
            }
            logger.info("邮件发送人:" + sender)
            logger.info("密码:" + passwd)
            logger.info("邮件接收人:" + str(receivers))
            server = zmail.server(username=sender, password=passwd, smtp_host='smtp.pachiratech.com', smtp_port=25,
                                  smtp_ssl=False)
            if server.smtp_able():
                logger.info('邮件连接正常')
                server.send_mail(receivers, mail=mail_content)
            else:
                logger.info("邮件连接异常")
            return redirect('dailyReports')


@login_required()
def del_dailyReports(request):
    # 获取删除的id号对于的日报记录
    report_id = request.GET.get('id')
    DailyReports.objects.filter(id=report_id).delete()
    return JsonResponse(data={'status': '1'})


@login_required()
def projects(request):
    if request.method == 'GET':
        username = request.session.get('username')
        details = Project.objects.all().values()
        return render(request, 'projects.html', context={'details': details, 'username': username})
    elif request.method == 'POST':
        # 获取id用于判断为新建项目还是修改项目，因为新建项目不存在id号的
        pid = request.POST.get('id', None)
        name = request.POST.get('name', None)
        stage = request.POST.get('stage', None)
        city = request.POST.get('city', None)
        sales = request.POST.get('sales', None)
        manager = request.POST.get('manager', None)
        operator = request.POST.get('operator', None)
        developer = request.POST.get('developer', None)
        business = request.POST.get('business', None)
        agent = request.POST.get('agent', None)
        license = request.POST.get('license', None)
        maintaince = request.POST.get('maintaince', None)
        product = request.POST.get('product', None)

        # 根据是否有id判断当前页面是新建项目，还是修改项目，新建项目id=None，修改项目存在id值
        if pid is None:
            try:
                Project.objects.get(name=name)
                return HttpResponse("当前项目已经存在，返回重新添加")
            except Project.DoesNotExist:
                Project.objects.create(name=name, stage=stage, city=city, sales=sales, manager=manager,
                                       operator=operator,
                                       developer=developer, business=business, agent=agent, license=license,
                                       maintaince=maintaince, product=product)
                return redirect('projects')
        else:
            Project.objects.filter(id=pid).update(name=name, stage=stage, city=city, sales=sales, manager=manager,
                                                  operator=operator, developer=developer, business=business,
                                                  agent=agent, license=license, maintaince=maintaince, product=product)
            return redirect('projects')


@login_required()
def dashboard(request):
    if request.method == 'GET':
        username = request.session.get('username', None)
        cur_date_first = datetime(date.today().year, date.today().month, 1).date()
        # cur_date_last = (datetime(date.today().year, date.today().month + 1, 1) - timedelta(1)).date()  本月最后一天
        cur_date_last = datetime(date.today().year, date.today().month + 1, 1).date()

        # 本月范围内按照项目分组,统计每个项目花费时长
        monthlyReportsByProject = DailyReports.objects.filter(date__range=[cur_date_first, cur_date_last]).values(
            'project').annotate(total_time=Sum('working_time'))
        logger.info(monthlyReportsByProject)

        # 本月范围内按照个人分组,统计每个项目花费时长
        monthlyReportsByCreator = DailyReports.objects.filter(date__range=[cur_date_first, cur_date_last]).values(
            'creator').annotate(total_time=Sum('working_time'))
        logger.info(monthlyReportsByCreator)
        return render(request, 'dashboard.html', {'monthlyReportsByProject': monthlyReportsByProject,
                                                  'monthlyReportsByCreator': monthlyReportsByCreator,
                                                  'username': username})
