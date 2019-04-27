import time
import requests
import re
import os
import threading
import smtplib
from email.mime.text import MIMEText
import pymysql


content = '领取结果:'
status = 0
resp = []
custom_url = ''

# 读取配置文件
with open('./配置文件.ini','r',encoding='utf-8') as f:
    config = f.readlines()
config_dict = {}

for conf in config[1:]:
    conf = conf.split('=')
    config_dict[conf[0].strip()] = conf[1].strip()

# 若自定义领取链接不为空,读取领取链接
if config_dict['自定义链接'] != '[]':
    custom_url = config_dict['自定义链接'].strip('[').strip(']')

# 读取数据库优惠券信息
user = config_dict['数据库账号'].strip()
passwd = config_dict['数据库密码'].strip()
db = config_dict['数据库名称'].strip()
connect = pymysql.connect(
    host='localhost',
    user=user,
    passwd=passwd,
    db=db,
    charset='utf8'
)
try:
    cursor = connect.cursor()
    # 读取优惠券信息
    cursor.execute("select * from jd_help")
    conf_data = cursor.fetchall()
    # 读取抢券接口信息
    cursor.execute("select port from re_port")
    re_port = cursor.fetchall()
except Exception as e:
    print(e)
finally:
    connect.close()


# 读取cookie信息
def get_ck():
    cookie = {}
    ck = []
    for root, dirs, files in os.walk('./ck'):
        for file in files:
            phone = file.split('.')[0]
            with open('./ck/'+file, 'r') as f:
                for i in f.readlines():
                    mobile = i.split('----')[0]
                    oo = mobile.split(';')
                    for ooo in oo:
                        oooo = ooo.strip().split('=')
                        cookie[oooo[0]] = oooo[1]
                    ck.append((phone, cookie))
                    cookie = {}
    return ck


# 获取京东时间
def get_time():
    res = requests.get(
        url='https://a.jd.com//ajax/queryServerData.html',
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.80 Safari/537.36'})
    data_server = res.json()
    return data_server['serverTime']


# 延续整点时间
def time_pos():
    t = time.localtime(int(get_time() / 1000))
    if 0 <= t.tm_hour < 10:
        preset_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())).split(' ')[0]+' 10:00:00'
    elif 10 <= t.tm_hour < 12:
        preset_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())).split(' ')[0] + ' 12:00:00'
    elif 12 <= t.tm_hour < 14:
        preset_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())).split(' ')[0] + ' 14:00:00'
    elif 14 <= t.tm_hour < 16:
        preset_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())).split(' ')[0] + ' 16:00:00'
    elif 16 <= t.tm_hour < 18:
        preset_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())).split(' ')[0] + ' 18:00:00'
    elif 18 <= t.tm_hour < 20:
        preset_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())).split(' ')[0] + ' 20:00:00'
    elif 20 <= t.tm_hour < 22:
        preset_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())).split(' ')[0] + ' 22:00:00'
    else:
        new_year = t[0]
        new_month = t[1]
        new_day = t[2] + 1
        if t.tm_mon == 4 or t.tm_mon == 6 or t.tm_mon == 9 or t.tm_mon == 11:
            if t.tm_mday == 30:
                new_month = t[1] + 1
                new_day = '01'
        elif t.tm_mon == 12:
            if t.tm_mday == 31:
                new_year = t[0] + 1
                new_month = 1
                new_day = '01'
        elif t.tm_mon == 2:
            this_year = int(t.tm_year)
            if this_year % 400 == 0 or this_year % 4 == 0 and this_year % 100 != 0:
                if t.tm_mday == 29:
                    new_month = t[1] + 1
                    new_day = '01'
            else:
                if t.tm_mday == 28:
                    new_month = t[1] + 1
                    new_day = '01'
        else:
            if t.tm_mday == 31:
                new_month = t[1] + 1
                new_day = '01'
        preset_time = str(new_year) + '-' + str(new_month) + '-' + str(new_day) + ' 00:00:00'

    return preset_time


# 主抢券代码
def begin_get(role, key, quan_detail, phone_jiekou, begin_time, cookienum, j, oo, diff):

    cookies = get_ck()
    header = {'accept': '*/*',
              'referer': 'https://wq.jd.com/activeapi/obtainjdshopfreecouponv2',
              'Content-Type': 'application/x-www-form-urlencoded',
              'accept-language': 'zh-cn',
              'User-Agent': 'Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.1)'}
    oo = int(oo)
    # 设置开抢提前时间
    s = int((begin_time - oo - diff)/100)/10
    time.sleep(s)
    now = int(time.time() * 1000)
    swith = 0
    # 设置抢券循环次数
    for x in range(4):
        if swith == 1:
            break
        for url in phone_jiekou:
            if custom_url == '':
                re_url = url.format(role, now, key)
            else:
                re_url = custom_url
            try:
                jd_login = requests.get(re_url, headers=header, cookies=cookies[cookienum][1], allow_redirects=False)
                jds = jd_login.content.decode('utf-8')
            except Exception as er:
                print('第{}次抢卷异常'.format(x), er)
                continue
            # 判断抢券结果
            try:
                if len(jds) > 300:
                    jds = '出了点小问题'
                else:
                    jds = re.search('[\u4e00-\u9fa5]+.*[\u4e00-\u9fa5]+', jds, re.S).group()
            except Exception as er:
                print('抢卷异常', er)
                jds = '出了点小问题'
            resp.append(cookies[cookienum][0]+':'+jds)

            if re.search('早点来|结束|成功|重复', jds, re.S):
                swith = 1
                break
        if x == 0:
            phone_jiekou = phone_jiekou[1:]


# 多线程抢券类
class myThread (threading.Thread):
    def __init__(self, role, key, quan_detail, phone_jiekou, begintime, num, j, oo, diff):
        threading.Thread.__init__(self)
        self.begintime = begintime
        self.num = num
        self.role = role
        self.key = key
        self.quan_detail = quan_detail
        self.phone_jiekou = phone_jiekou
        self.oo = oo
        self.j = j
        self.diff = diff

    def run(self):
        """
        每个线程代表一个账户
        :return:
        """
        print("任务{}：".format(self.num), self.num)
        begin_get(self.role, self.key, self.quan_detail, self.phone_jiekou, self.begintime, self.num, self.j, self.oo, self.diff)
        print("退出线程：", self.num)


# 发送邮件配置
def send_mail():
    mail_host = config_dict['邮箱发送主机']
    mail_user = config_dict['邮箱发送账号']
    mail_pass = config_dict['邮箱发送密码']
    sender = config_dict['邮箱发送地址']
    receivers = [config_dict['邮箱接收地址']]
    # print(mail_host,mail_user,mail_pass,sender,receivers)
    title = '领券反馈'
    if status == 1:
        message = MIMEText(content, 'plain', 'utf-8')  # 内容, 格式, 编码
        message['From'] = "{}".format(sender)
        message['To'] = ",".join(receivers)
        message['Subject'] = title
        try:
            smtpObj = smtplib.SMTP_SSL(mail_host, 465)  # 启用SSL发信, 端口一般是465
            smtpObj.login(mail_user, mail_pass)  # 登录验证
            smtpObj.sendmail(sender, receivers, message.as_string())  # 发送
            print("已发反馈邮件")
        except smtplib.SMTPException as e:
            print(e)


def run():
    j = 0
    while True:
        # pc_jiekou=['http://coupon.jd.com/ilink/couponSendFront/send_index.action?key={2}da&roleId={0}&to=jd.com','https://passport.jd.com/loginservice.aspx?callback=jQuery{0}&method=Login&_={1}','https://coupon.jd.com/ilink/couponActiveFront/front_index.action?key={2}&roleId={0}&to=jd.com',]
        # 抢券接口信息
        phone_jiekou = [x[0] for x in re_port]
        # 获取要抢券京东账号cookie
        cookies = get_ck()
        # 读取要抢优惠券信息
        for p in conf_data:
            endtime = p[6].split('----')[1]
            print(p[0], p[1], endtime, p[2], p[5].split('=')[1])
        # 当配置文件中自定义抢券链接为空时,使用固定接口抢券
        if custom_url == '':
            if j == 0:
                j = input('请输入要抢券编号:')
            youhuiquan = conf_data[int(j)-1]
            key = youhuiquan[3].strip()
            role = youhuiquan[4].strip()
            header = {
                'accept': '*/*',
                'referer': 'https://wq.jd.com/activeapi/obtainjdshopfreecouponv2',
                'Content-Type': 'application/x-www-form-urlencoded',
                'accept-language': 'zh-cn',
                'User-Agent': 'Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.1)'}
            now = get_time()
            jiekou = phone_jiekou[1]
            urll = jiekou.format(role, now, key)
            # 尝试抢券获取下次开抢的准确时间
            jd_l = requests.get(urll, headers=header, cookies=cookies[0][1])
            try:
                time_mec = re.search('(\d+):', jd_l.content.decode('utf-8'), re.S).group(1)
                yushe_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())).split(' ')[0] + ' {}:00:00'.format(time_mec)
                print('下场精确时间点', yushe_time)
                print('已开始抢券名称: ', conf_data[int(j) - 1][1], '定时时间:', yushe_time)
            except:
                print('此活动已过期')
                # 当准确获取开抢时间抛出异常时,自动延续下场整点时间
                yushe_time = time_pos()
                print('下场预设时间:', yushe_time)
            # yushe_time='2019-2-19 9:40:20'
        else:
            youhuiquan = conf_data[int(j) - 1]
            key = youhuiquan[3].strip()
            role = youhuiquan[4].strip()
            yushe_time = time_pos()
            print('当前自定义领券模式开启中', '定时时间:' + yushe_time)

        # 转换时间格式,并最终获取开抢unix时间戳
        timeArray = time.strptime(yushe_time, "%Y-%m-%d %H:%M:%S")
        unix = time.mktime(timeArray)
        unix = int(unix*1000)
        # 读取配置中自定义的提前开抢时间 单位为ms
        diff = int(config_dict['等待时间'])
        thread_list = []
        oo = get_time()
        # 根据cookie数量开启多线程,建议四五个账号cookie最佳
        for i in range(len(cookies)):
            t = myThread(role, key, conf_data, phone_jiekou, unix, i, j, oo, diff)
            unix = unix+8
            thread_list.append(t)
        print('-------------------------------------------------')
        for t in thread_list:
            t.setDaemon(True)
            t.start()
        print('-------------------------------------------------')
        for t in thread_list:
            t.join()
        # check_all()
        global resp, content, status
        # 当最终领取结果中有账号领取成功时,保留当前账号的信息并添加到要发送邮箱内容文本中
        for res in resp:
            if re.search('领取成功', res, re.S):
                ck = res.split(':')[0]
                status = 1
                content = content + ck + youhuiquan[1] + '   '
            print(res)

        resp = []
        send_mail()
        status = 0
        content = ''
        print('-' * 40)


if __name__ == '__main__':
    # 开启主函数
    run()
    send_mail()
