import pymysql
import requests
import re
import time


# 读取配置文件
with open('./配置文件.ini', 'r', encoding='utf-8') as f:
    config = f.readlines()
config_dict = {}

for conf in config[1:]:
    conf = conf.split('=')
    config_dict[conf[0].strip()] = conf[1].strip()

# 读取数据库配置信息
user = config_dict['数据库账号'].strip()
passwd = config_dict['数据库密码'].strip()
db = config_dict['数据库名称'].strip()
connect = pymysql.connect(
    host='localhost',
    user=user,
    passwd=passwd,
    db=db,
    charset='utf8')
# 捕获异常信息
try:
    cursor = connect.cursor()
    cursor.execute("truncate table jd_help")
    connect.commit()

    coupon = []
    with open('coupon.txt', 'r') as f:
        coupons = f.readlines()
    for k, cou in enumerate(coupons):
        coupon = 'http://coupon.m.jd.com/coupons/show.action?{}&to=m.jd.com'.format(cou.strip())
        res = requests.get(
            url=coupon,
            headers={'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1'}
        )
        ur_yuan = res.content.decode('utf-8')
        limitStr = re.search('limitStr":"(.*?)"', ur_yuan, re.S).group(1)
        discount = re.search('discount":"(.*?)"', ur_yuan, re.S).group(1)
        quota = re.search('quota":"(.*?)"', ur_yuan, re.S).group(1)
        batchid = re.search('batchId":"(.*?)"', ur_yuan, re.S).group(1)
        batchcount = re.search('batchCount":(\d+),', ur_yuan, re.S).group(1)
        des = limitStr+quota+'-'+discount
        key = cou.split('&')[0].split('=')[1].strip()
        role = cou.split('&')[1].split('=')[1].strip()
        begintime = re.search('constraintBeginTime":"(.*?)"', ur_yuan, re.S).group(1)
        begintime = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(int(begintime[:-3])))
        endtime = re.search('constraintEndTime":"(.*?)"', ur_yuan, re.S).group(1)
        endtime = int(endtime[:-3])
        now = int(time.time())
        if now < endtime:
            print(k)
            endtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(endtime))
            usetime = begintime+'----'+endtime
            qq = "insert into jd_help(coupon,ccount,keyid,roleid,batchid,usetime) values('{}',{},'{}','{}','{}','{}')".\
                format(des, batchcount, key, role,
                       'https://search.jd.com/Search?https://search.jd.com/Search?coupon_batch={}'.format(batchid), usetime)
            cursor.execute(qq)
    connect.commit()
except Exception as e:
    raise Exception(e)
finally:
    # 关闭连接
    connect.close()

