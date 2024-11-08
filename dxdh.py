import os
import re
import sys
import ssl
import time
import json
import execjs
import base64
import random
import certifi
import aiohttp
import asyncio
import certifi
import datetime
import requests
import binascii
from lxml import etree
from http import cookiejar
from Crypto.Cipher import AES
from Crypto.Cipher import DES3
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from Crypto.Util.Padding import pad, unpad
from aiohttp import ClientSession, TCPConnector
from concurrent.futures import ThreadPoolExecutor
run_num=os.environ.get('reqNUM') or "40"
diffValue=2
'''
变量: 手机号@服务密码
多个变量&隔开
corn 58 9,13,23 * * *
'''
MAX_RETRIES = 3
RATE_LIMIT = 10  # 每秒请求数限制

class RateLimiter:
    def __init__(self, rate_limit):
        self.rate_limit = rate_limit
        self.tokens = rate_limit
        self.updated_at = time.monotonic()

    async def acquire(self):
        while self.tokens < 1:
            self.add_new_tokens()
            await asyncio.sleep(0.1)
        self.tokens -= 1

    def add_new_tokens(self):
        now = time.monotonic()
        time_since_update = now - self.updated_at
        new_tokens = time_since_update * self.rate_limit
        if new_tokens > 1:
            self.tokens = min(self.tokens + new_tokens, self.rate_limit)
            self.updated_at = now

class AsyncSessionManager:
    def __init__(self):
        self.session = None
        self.connector = None

    async def __aenter__(self):
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        ssl_context.set_ciphers('DEFAULT@SECLEVEL=1')
        self.connector = TCPConnector(ssl=ssl_context, limit=1000)
        self.session = ClientSession(connector=self.connector)
        return self.session

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()
        await self.connector.close()

async def retry_request(session, method, url, **kwargs):
    for attempt in range(MAX_RETRIES):
        try:
            await asyncio.sleep(1)
            async with session.request(method, url, **kwargs) as response:
                return await response.json() 
                # return await response.json() 
            
        except (aiohttp.ClientConnectionError, aiohttp.ServerTimeoutError) as e:
            print(f"请求失败，第 {attempt + 1} 次重试: {e}")
            if attempt == MAX_RETRIES - 1:
                raise 
            await asyncio.sleep(2 ** attempt)

class BlockAll(cookiejar.CookiePolicy):
    return_ok = set_ok = domain_return_ok = path_return_ok = lambda self, *args, **kwargs: False
    netscape = True
    rfc2965 = hide_cookie2 = False
    
def printn(m):  
    print(f'\n{m}')

context = ssl.create_default_context()
context.set_ciphers('DEFAULT@SECLEVEL=1')  # 低安全级别0/1
context.check_hostname = False  # 禁用主机
context.verify_mode = ssl.CERT_NONE  # 禁用证书

class DESAdapter(requests.adapters.HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        kwargs['ssl_context'] = context
        return super().init_poolmanager(*args, **kwargs)

requests.packages.urllib3.disable_warnings()
# urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)  
ss = requests.session()
ss.headers={"User-Agent":"Mozilla/5.0 (Linux; Android 13; 22081212C Build/TKQ1.220829.002) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.97 Mobile Safari/537.36","Referer":"https://wapact.189.cn:9001/JinDouMall/JinDouMall_independentDetails.html"}    
ss.mount('https://', DESAdapter())       
ss.cookies.set_policy(BlockAll())
runTime = 0
key = b'1234567`90koiuyhgtfrdews'
iv = 8 * b'\0'

public_key_b64 = '''-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDBkLT15ThVgz6/NOl6s8GNPofdWzWbCkWnkaAm7O2LjkM1H7dMvzkiqdxU02jamGRHLX/ZNMCXHnPcW/sDhiFCBN18qFvy8g6VYb9QtroI09e176s+ZCtiv7hbin2cCTj99iUpnEloZm19lwHyo69u5UMiPMpq0/XKBO8lYhN/gwIDAQAB
-----END PUBLIC KEY-----'''

public_key_data = '''-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC+ugG5A8cZ3FqUKDwM57GM4io6JGcStivT8UdGt67PEOihLZTw3P7371+N47PrmsCpnTRzbTgcupKtUv8ImZalYk65dU8rjC/ridwhw9ffW2LBwvkEnDkkKKRi2liWIItDftJVBiWOh17o6gfbPoNrWORcAdcbpk2L+udld5kZNwIDAQAB
-----END PUBLIC KEY-----'''

def get_first_three(value):
    # 处理数字情况
    if isinstance(value, (int, float)):
        return int(str(value)[:3])
    elif isinstance(value, str):
        return str(value)[:3]
    else:
        raise TypeError("error")

def run_Time(hour,miute,second):    
    date = datetime.datetime.now()
    date_zero = datetime.datetime.now().replace(year=date.year, month=date.month, day=date.day, hour=hour, minute=miute, second=second)
    date_zero_time = int(time.mktime(date_zero.timetuple()))
    return date_zero_time

def encrypt(text):    
    cipher = DES3.new(key, DES3.MODE_CBC, iv)
    ciphertext = cipher.encrypt(pad(text.encode(), DES3.block_size))
    return ciphertext.hex()

def decrypt(text):
    ciphertext = bytes.fromhex(text)
    cipher = DES3.new(key, DES3.MODE_CBC, iv)
    plaintext = unpad(cipher.decrypt(ciphertext), DES3.block_size)
    return plaintext.decode()
    
def b64(plaintext):
    public_key = RSA.import_key(public_key_b64)
    cipher = PKCS1_v1_5.new(public_key)
    ciphertext = cipher.encrypt(plaintext.encode())
    return base64.b64encode(ciphertext).decode()
    
def encrypt_para(plaintext):
    if not isinstance(plaintext, str):
        plaintext = json.dumps(plaintext)
    public_key = RSA.import_key(public_key_data)  
    cipher = PKCS1_v1_5.new(public_key)
    ciphertext = cipher.encrypt(plaintext.encode())
    return binascii.hexlify(ciphertext).decode() 

def encode_phone(text):
    encoded_chars = []
    for char in text:
        encoded_chars.append(chr(ord(char) + 2))
    return ''.join(encoded_chars)


def getApiTime(api_url):
        try:
             with requests.get(api_url) as response:
                if(not response or not response.text):
                    return time.time()
                json_data = json.loads(response.text)
                if (json_data.get("api")and json_data.get("api")not in("time") ):
                    timestamp_str = json_data.get('data', {}).get('t', '')
                else:
                    timestamp_str = json_data.get('currentTime', {}) 
                timestamp = int(timestamp_str) / 1000.0  # 将毫秒转为秒
                difftime=time.time()-timestamp
                return difftime;   
        except Exception as e:
            print(f"获取时间失败: {e}")
            return 0; 


def userLoginNormal(phone,password):
    alphabet = 'abcdef0123456789'
    uuid = [''.join(random.sample(alphabet, 8)),''.join(random.sample(alphabet, 4)),'4'+''.join(random.sample(alphabet, 3)),''.join(random.sample(alphabet, 4)),''.join(random.sample(alphabet, 12))]
    timestamp=datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    loginAuthCipherAsymmertric = 'iPhone 14 15.4.' + uuid[0] + uuid[1] + phone + timestamp + password[:6] + '0$$$0.'
    r = ss.post('https://appgologin.189.cn:9031/login/client/userLoginNormal',json={"headerInfos": {"code": "userLoginNormal", "timestamp": timestamp, "broadAccount": "", "broadToken": "", "clientType": "#9.6.1#channel50#iPhone 14 Pro Max#", "shopId": "20002", "source": "110003", "sourcePassword": "Sid98s", "token": "", "userLoginName": phone}, "content": {"attach": "test", "fieldData": {"loginType": "4", "accountType": "", "loginAuthCipherAsymmertric": b64(loginAuthCipherAsymmertric), "deviceUid": uuid[0] + uuid[1] + uuid[2], "phoneNum": encode_phone(phone), "isChinatelecom": "0", "systemVersion": "15.4.0", "authentication": password}}},verify=certifi.where()).json()
    l = r['responseData']['data']['loginSuccessResult']
    if l:
        ticket = get_ticket(phone,l['userId'],l['token']) 
        return ticket
    return False
        
async def exchangeForDay(phone, session, run_Time, rid, stime):
    async def delayed_conversion(delay):
        await asyncio.sleep(delay)
        await conversionRights(phone, rid,session)
    tasks = [asyncio.create_task(delayed_conversion(i * stime)) for i in range(int(run_Time))]
    await asyncio.gather(*tasks)
def get_ticket(phone,userId,token):
    r = ss.post('https://appgologin.189.cn:9031/map/clientXML',data='<Request><HeaderInfos><Code>getSingle</Code><Timestamp>'+datetime.datetime.now().strftime("%Y%m%d%H%M%S")+'</Timestamp><BroadAccount></BroadAccount><BroadToken></BroadToken><ClientType>#9.6.1#channel50#iPhone 14 Pro Max#</ClientType><ShopId>20002</ShopId><Source>110003</Source><SourcePassword>Sid98s</SourcePassword><Token>'+token+'</Token><UserLoginName>'+phone+'</UserLoginName></HeaderInfos><Content><Attach>test</Attach><FieldData><TargetId>'+encrypt(userId)+'</TargetId><Url>4a6862274835b451</Url></FieldData></Content></Request>',headers={'user-agent': 'CtClient;10.4.1;Android;13;22081212C;NTQzNzgx!#!MTgwNTg1'},verify=certifi.where())
    tk = re.findall('<Ticket>(.*?)</Ticket>',r.text)
    if len(tk) == 0:        
        return False
    return decrypt(tk[0])

async def exchange(s, phone, title, aid,jsexec, ckvalue):
    try:
        url="https://wapact.189.cn:9001/gateway/stand/detailNew/exchange"
        # getck = await asyncio.to_thread(jsexec.call, "getck") # 两种方式，一种用ck，一种用后缀
        # getck = getck.split(';')[0].split('=')
        # ckvalue[getck[0]] = getck[1]

        # async with s.post(url, cookies=ckvalue, json={"activityId": aid}) as response:

        # 通过 retry_request 实现重试机制
        # response = await retry_request(s, 'POST', get_url, cookies=ckvalue, json={"activityId": aid})

        get_url = await asyncio.to_thread(jsexec.call,"getUrl", "POST",url)
        async with s.post(get_url, cookies=ckvalue, json={"activityId": aid}) as response:
            pass
    except Exception as e:
        print(e)

       

async def check(s,item,ckvalue):
    checkGoods = s.get('https://wapact.189.cn:9001/gateway/stand/detailNew/check?activityId=' + item, cookies=ckvalue).json()
    return checkGoods

async def conversionRights(phone, aid,session):
    value = {
        "phone": phone,
        "rightsId": aid
    }
    paraV=encrypt_para(value)
    response = session.post('https://wapside.189.cn:9001/jt-sign/paradise/conversionRights',json={"para":paraV})
    login = response.json()
    printn(f"{get_first_three(phone)},{str(datetime.datetime.now())[11:23]}:{login} ")

async def getLevelRightsList(phone,session):
    value = {
        "phone": phone
    }
    paraV=encrypt_para(value)
    data = session.post('https://wapside.189.cn:9001/jt-sign/paradise/getLevelRightsList',json={"para":paraV}).json()
    if data.get('code') == 401:
        print(f"获取失败:{data},原因大概是sign过期了")
        return None
    current_level = int(data['currentLevel'])
    key_name = 'V' + str(current_level)
    ids = [item['id'] for item in data.get(key_name, []) if item.get('name') == '话费']
    return ids

async def getSign(ticket,session):
    try:
        response_data = session.get('https://wapside.189.cn:9001/jt-sign/ssoHomLogin?ticket=' + ticket).json()
        if response_data.get('resoultCode') == '0':
            sign = response_data.get('sign')
            return sign
        else:
            print(f"获取sign失败[{response_data.get('resoultCode')}]: {response_data}")
    except Exception as e:
        print(e)
    return None

async def login_request(ss,url,payload):
    global ckvalue,js_codeRead
    url = "https://wapact.189.cn:9001/unified/user/login"
    headers = {
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Origin': 'https://wapact.189.cn:9001',
    'Pragma': 'no-cache',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'X-Requested-With': 'XMLHttpRequest',
    'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Android WebView";v="126"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'Content-Type': 'application/json;charset=UTF-8'
    }
    response = ss.post(url, headers=headers, data=json.dumps(payload))
    rsCK = re.findall('yiUIIlbdQT3fO=([^;]+)',response.headers['Set-Cookie'])[0]
    # print(response.status_code)
    if response.status_code == 412:
        print("检测到瑞数特征码412,正在尝试调用js")
    else:
        print("未检测到瑞数.")
        return  response,None,rsCK
    html=etree.HTML(response.text)
    arg1=html.xpath('//meta/@content')[-1]
    arg2=html.xpath('//script/text()')[0]
    arg3=html.xpath('//meta/@id')[-1]
    js_code = js_codeRead.replace("contentCODE", arg1).replace('"tsCODE"', arg2).replace('"tsID"',f'"{arg3}"')
    
    jsexec = execjs.compile(js_code)
    ck=await asyncio.to_thread(jsexec.call, "getck")
    get_url=await asyncio.to_thread(jsexec.call,"getUrl","POST",url)
    def parse_cookies(ck):
        cookies = {}
        for part in ck.split(';'):
            part = part.strip()
            if '=' in part:
                key, value = part.split('=', 1)
                if 'path' not in key and 'expires' not in key and 'Secure' not in key and 'SameSite' not in key:
                    cookies[key] = value
        return cookies
    ck=parse_cookies(ck)
    ck["yiUIIlbdQT3fO"] = rsCK
    ckvalue=ck
    res=ss.post(get_url, headers=headers,data=json.dumps(payload),cookies=ckvalue)
    if res.status_code == 200:
        print("瑞数返回状态码200,开始下一步.")
        return res,jsexec,ckvalue
    else:
        print("瑞数破解失败,调用重试机制")
        return res,jsexec,None
    # return res,jsexec,ckvalue#ckvalue这里直接返回，没直接塞session里面.

async def qgNight(phone, ticket, timeValue,isTrue):
    if isTrue:
        runTime = run_Time(23,59,19) + 0.65
    else:
        runTime = run_Time(0,0,0) + 0.65

    if runTime >(time.time()+timeValue):
        difftime = runTime - time.time() - timeValue
        printn(f"当前时间:{str(datetime.datetime.now())[11:23]},跟设定的时间不同,等待{difftime}秒开始兑换每天一次的")
        await asyncio.sleep(difftime)
    session = requests.Session()
    session.mount('https://', DESAdapter())
    session.verify = False  # 禁用证书验证
    sign =await getSign(ticket,session)
    if sign:
        print(f"当前时间:{str(datetime.datetime.now())[11:23]}获取到了Sign:"+sign)
        session.headers={"User-Agent":"Mozilla/5.0 (Linux; Android 13; 22081212C Build/TKQ1.220829.002) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.97 Mobile Safari/537.36","sign":sign}
    else:
        print("未能获取sign。")
        return
    # await asyncio.sleep(10)直接延迟也行，或者用下面的等待一段时间。之所以这样是要先获取sign省一些步骤。
    if isTrue:
        runTime2 = run_Time(23,59,59) + 0.65
    else:
        runTime2 = run_Time(0,0,0) + 0.65
    if runTime2 >(time.time()+timeValue):
        difftime = runTime2 - time.time() - timeValue
        printn(f"获得到sign等待下")
        await asyncio.sleep(difftime)
    rightsId =await getLevelRightsList(phone,session);
    if rightsId:
        print("获取到了rightsId:"+rightsId[0])
    else:
        print("未能获取rightsId。")
        return
    printn(f"{str(datetime.datetime.now())[11:23]} 时间到开始兑换每天一次的")
    await exchangeForDay(phone,session,5,rightsId[0],4.625)
async def qgDay(phone, ticket,  timeValue, isTrue):
    global runTime,js_codeRead
    async with AsyncSessionManager() as s:
      pass
async def main(timeValue,isTRUE,hour):
    global runTime,js_codeRead
    tasks = []
    # with open("e:/work/vscode1/python/电信/rs6.js", "r", encoding="utf-8") as f:
    #     js_codeRead = f.read()
    phone_list = PHONES.split('&')  
    # diffValue=len(phone_list)
    for phoneV in phone_list:
        value = phoneV.split('@')
        phone, password = value[0], value[1]
        printn(f'{get_first_three(phone)}开始登录')
        ticket = userLoginNormal(phone,password)
        if ticket:
            # hour=datetime.datetime.now().hour
            # hour=23
            if hour > 15:#凌晨场次
                tasks.append(qgNight(phone, ticket, timeValue, isTRUE))
                # await asyncio.sleep(0.1)
            else:#十点//十四点场次
                tasks.append(qgDay(phone, ticket, timeValue, isTRUE))
                # await asyncio.sleep(0.1)
        else:
            printn(f'{phone} 登录失败')
    await asyncio.gather(*tasks)
 
PHONES=os.environ.get('PHONES1') or "17788888888@888888&19955555555@666666"    
if __name__ == "__main__":
    h = datetime.datetime.now().hour
    h=22                           #手动设置场次的时间
    print("当前小时为: "+str(h))    
    if 10 >h >0:
        print("当前小时为: "+str(h)+"已过0点但未到10点开始准备抢十点场次")
        wttime= run_Time(9,59,8) #抢十点场次  
    elif 14 >= h >=10:
        print("当前小时为: "+str(h) +"已过10点但未到14点开始准备抢十四点场次")
        wttime= run_Time(13,59,8) #抢十四点场次
    else:
        print("当前小时为: "+str(h)+"已过14点开始准备抢凌晨")
        wttime= run_Time(23,58,58) #抢凌晨
    isTRUE=False
    #isTRUE=True                
    if(wttime >time.time()) :
        wTime=wttime-time.time()
        print("未到时间,计算后差异:"+str(wTime)+"秒") 
        if isTRUE:
            print("开始等待:")
            time.sleep(wTime)
    global timeValue,timeDiff
    timeValue = getApiTime("https://f.m.suning.com/api/ct.do")
    timeDiff = timeValue if timeValue > 0 else 0
    asyncio.run(main(timeDiff, isTRUE,h))
    print("所有任务都已执行完毕!")
