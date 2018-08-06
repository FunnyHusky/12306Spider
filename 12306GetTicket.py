# -*- coding:UTF-8 -*-
'''
Created on 2018年1月3日

@author: Administrator
'''
import requests,re,os,random,json
import time
import urllib
import time
from tkinter import * 
orderMessageUrl="https://kyfw.12306.cn/otn/confirmPassenger/initDc"
submitUrl="https://kyfw.12306.cn/otn/leftTicket/submitOrderRequest"
initurl="https://kyfw.12306.cn/otn/login/init" #登录页面
loginUrl="https://kyfw.12306.cn/passport/web/login" #提交用户名和密码
userLogin ="https://kyfw.12306.cn/otn/passport?redirect=/otn/login/userLogin"
#第一次验证
authUrl1 ="https://kyfw.12306.cn/passport/web/auth/uamtk"
#第二次验证
authUrl2 ="https://kyfw.12306.cn/otn/uamauthclient"
checkUrl="https://kyfw.12306.cn/passport/captcha/captcha-check" #验证码提交
yanZhengMaUrl="https://kyfw.12306.cn/passport/captcha/captcha-image?login_site=E&module=login&rand=sjrand&"
# tickMainUrl ="https://kyfw.12306.cn/otn/leftTicket/init"
#查票网址
checkTitckUrl ="https://kyfw.12306.cn/otn/leftTicket/query?leftTicketDTO.train_date=%s&leftTicketDTO.from_station=%s&leftTicketDTO.to_station=%s&purpose_codes=%s"
checkUser ="https://kyfw.12306.cn/otn/login/checkUser"
confirmDc ='https://kyfw.12306.cn/otn/confirmPassenger/initDc'
getPassenger="https://kyfw.12306.cn/otn/confirmPassenger/getPassengerDTOs"
username="用户名"
password ="用户密码"
session = requests.Session()
lnitheader={
        "User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36",
        "Host":"kyfw.12306.cn"
        }
loginData={
           "username":username,
           "password":password,
           "appid":"otn"
           }

        
#查票
def checkTicket(Godate,fromDesction,toDesction,purpose_codes='ADULT',Backdate=time.strftime("%Y-%m-%d")):
    fromCode =''
    toCode=''
#     ticketIndex = getTicketIndex(ticketType)
    with open(os.getcwd()+"/city.txt",'r',encoding='utf8') as f:
        result =json.load(f)
        di = json.loads(result)
        fromCode = di[fromDesction]
        toCode = di[toDesction]
    if  fromCode and toCode: 
        headers ={
        'Host':'kyfw.12306.cn',
        'If-Modified-Since':'0',
        'Referer':'https://kyfw.12306.cn/otn/leftTicket/init',
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36',
        'X-Requested-With':'XMLHttpRequest'
        } 
        url = checkTitckUrl%(Godate,fromCode,toCode,purpose_codes)
        while True:
            res = session.get(url,headers=headers)
            if res.status_code ==200:
                response = res.json()
#                 print("checkTicket",response)
                if response['status'] ==True:
                    ticketList = response["data"]["result"]
                    if isinstance(ticketList, list) and len(ticketList) >0:
                       tkStart(ticketList)
                       checi = input("请输入要乘坐的车次")
                       zuowei = input("请输入车次座位")
                       for x in ticketList:
                           results = x.split("|")
                           ches = results[3]
                           if checi !=ches: #不是我要的车次
                               continue
                           if results and len(results)>33:
                                 secretStr =results[0]
                                 ticketCode = getTicketCode(zuowei)
                                 leftticket = results[12]
                                 train_location = results[15]
                                 if secretStr and leftticket and train_location:
                                     if preOrder():
                                         submitResults =submitOrder(secretStr, Godate, Backdate,fromDesction, toDesction)
                                         if submitResults ==True:
                                              submitToken,key_check =initDC()
                                              if submitToken and key_check:
                                                  if getPasserengerMessage(submitToken):
                                                      if checkOrderInfo(submitToken):
                                                          if not getQueneCount(submitToken, leftticket, train_location, key_check,ticketCode):
                                                              print("购买车票不成功，请重新选择要购买的车票")
                                                              break
                                                              
                                         else:
                                             continue
                                 else:
                                     continue
            else: #网络问题获取不到车票信息，休眠2秒后继续获取
                time.sleep(2)
                continue
            
def header(tk):
    Label(tk,text=" 车次     |").grid(row=0,column=0)
    Label(tk,text=" 出发时间    |").grid(row=0,column=1)
    Label(tk,text=" 到达时间     |").grid(row=0,column=2)
    Label(tk,text=" 出发站    |").grid(row=0,column=3)
    Label(tk,text=" 到达站    |").grid(row=0,column=4)
    Label(tk,text=" 历时      |").grid(row=0,column=5)
    Label(tk,text=" 特等座    |").grid(row=0,column=6)
    Label(tk,text=" 一等座     |").grid(row=0,column=7)
    Label(tk,text=" 二等座    |").grid(row=0,column=8)
    Label(tk,text=" 高级软卧    |").grid(row=0,column=9)
    Label(tk,text=" 软卧    |").grid(row=0,column=10)
    Label(tk,text=" 动卧     |").grid(row=0,column=11)
    Label(tk,text=" 硬卧    |").grid(row=0,column=12)
    Label(tk,text=" 软座    |").grid(row=0,column=13)
    Label(tk,text=" 硬座   |").grid(row=0,column=14)
    Label(tk,text=" 无座    |").grid(row=0,column=15)
def tableGrid(results,app):
    labels =[3,4,5,8,9,10,32,31,30,21,23,33,28,24,29,26]
    for x in range(len(results)):
        for y in range(len(labels)):
            c = results[x].split("|") 
            Label(app,text=getResult(c[labels[y]])).grid(row=x+1,column=y)
def getResult(result): 
    if  not result:
        result ="--"
    return result      
def tkStart(results):
    tk=Tk()
    tk.title("12306座位信息")
    tk.geometry('1000x600+500+200')
    header(tk)
    tableGrid(results, tk)
    mainloop()
def initDC():
    headers ={
    'Host':'kyfw.12306.cn',
    'Origin':'https://kyfw.12306.cn',
    'Referer':'https://kyfw.12306.cn/otn/leftTicket/init',
    'Upgrade-Insecure-Requests':'1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3423.2 Safari/537.36'
    } 
    data ={
        '_json_att':''
        } 
    res = session.post(confirmDc,data,headers=headers) 
    if res.status_code ==200:
        text = res.text
        pattern="var globalRepeatSubmitToken = '(.*?)'"
        res = re.findall(pattern, text, re.S) 
        print("submitToken",res)
        pattern2 = "key_check_isChange':'(.*?)',"
        res2 = re.findall(pattern2, text, re.S)
        print("key_check",res2)
        if res and res2:
            return res[0],res2[0] 
def getPasserengerMessage(submitCode):
        data ={
            '_json_att':'', 
            'REPEAT_SUBMIT_TOKEN': submitCode
            }
        headers ={
            'Host':'kyfw.12306.cn',
            'Origin':'https://kyfw.12306.cn',
            'Referer':'https://kyfw.12306.cn/otn/confirmPassenger/initDc',
            'User-Agent':'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3423.2 Safari/537.36',
            'X-Requested-With':'XMLHttpRequest'
            }
        res =session.post(getPassenger,data,headers=headers)
        if res.status_code==200:
            passenger = res.json()
            print("passerengerMessage",passenger)
            if passenger['status']==True:
                return True
def checkOrderInfo(submitCode):
    passengerTicketStr ="" #这两个字段可以抓包获取
    oldPassengerStr =""
    url ="https://kyfw.12306.cn/otn/confirmPassenger/checkOrderInfo"
    data ={
        'cancel_flag':'2',
        'bed_level_order_num':'000000000000000000000000000000',
        'passengerTicketStr': passengerTicketStr,
        'oldPassengerStr':oldPassengerStr,
        'tour_flag':'dc',
        'randCode':'',
        'whatsSelect':'1',
        '_json_att':'',
        'REPEAT_SUBMIT_TOKEN': submitCode
        }
    headers={
        'Host':'kyfw.12306.cn',
        'Origin':'https://kyfw.12306.cn',
        'Referer':'https://kyfw.12306.cn/otn/confirmPassenger/initDc',
        'User-Agent':'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3423.2 Safari/537.36',
        'X-Requested-With':'XMLHttpRequest'
        }
    res = session.post(url,data,headers)
    if res.status_code==200:
        orderJson = res.json()
        print("orderJson",orderJson)
        if orderJson['status'] ==True:
            return True
def getTicketCode(ticketType):
    ticketCode =''
    if ticketType =='动卧':
        ticketCode=='F'
    elif ticketType =='商务座' or ticketType =="特等座":
        ticketCode='9'
    elif ticketType =='高级软卧':
        ticketCode='6'
    elif ticketType =='一等座':
        ticketCode='M'
    elif ticketType =='二等座':
        ticketCode='O'
    elif ticketType =='软卧':
        ticketCode='4'
    elif ticketType =='硬卧':
        ticketCode='3'
    elif ticketType =='软座':
        ticketCode='2'
    elif ticketType =='硬座':
        ticketCode='1'
    return ticketCode
def getQueneCount(submitCode,leftTicket,train_location,key_check,ticketCode):
    url ="https://kyfw.12306.cn/otn/confirmPassenger/confirmSingleForQueue"
    passengerTicketStr =""
    oldPassengerStr=""
    data ={
        'passengerTicketStr': ticketCode+passengerTicketStr  #抓包获取這个key的值，其中ticketCode是不同的，其他都一样
        'oldPassengerStr': oldPassengerStr
        'randCode':'' ,
        'purpose_codes': '00',
        'key_check_isChange': key_check,
        'leftTicketStr': leftTicket,
        'train_location': train_location,
        'choose_seats': '',
        'seatDetailType': '000',
        'whatsSelect': '1',
        'roomType': '00',
        'dwAll': 'N',
        '_json_att':'' ,
        'REPEAT_SUBMIT_TOKEN':submitCode,
        }
    headers={
        'Host':'kyfw.12306.cn',
        'Origin':'https://kyfw.12306.cn',
        'Referer':'https://kyfw.12306.cn/otn/confirmPassenger/initDc',
        'User-Agent':'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3423.2 Safari/537.36',
        'X-Requested-With':'XMLHttpRequest'
        }
    res =session.post(url,data,headers)
    if res.status_code ==200:
        queneJson = res.json()
        print("getQueneCount",queneJson)
        if queneJson['status']==True:
            #print(queneJson)
            print("购票成功")
            return True
        else:
            return False               
def preOrder():
    headers ={
        'Host':'kyfw.12306.cn',
        'If-Modified-Since':'0',
        'Referer':'https://kyfw.12306.cn/otn/leftTicket/init',
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36',
        'X-Requested-With':'XMLHttpRequest'
        } 
    data ={
        '_json_att':''
        } 
    res =session.post(checkUser,data,headers=headers)
    if res.status_code ==200:
        resJson = res.json()
        print("preOrder",resJson)
        if resJson['status'] ==True:
            return True
        else:
            return False
    else:
        return False
       
def getCityAndCode():
    url ="https://kyfw.12306.cn/otn/resources/js/framework/station_name.js?station_version=1.9061"
    res = requests.get(url,headers=header)
    if res.status_code ==200:
        text = res.text
        cityString = text.split("=")[1]
        citys = cityString.split("@")
        cityDict ={}
        for x in citys:
            if x and "|" in x:
                results = x.split("|")
                if results:
                    cityName =results[1]
                    cityCode = results[2]
                    cityDict[cityName]=cityCode
                    
        jsondata = json.dumps(cityDict)
        with open(os.getcwd()+"/city.txt",'w',encoding="utf8") as f:
            json.dump(jsondata,f)   
def getRandom():
    result=""
    for x in range(16):
      result+=str(random.randint(0,9))
    return "0."+result
def submitOrder(secretStr,train_date,back_trian_date,query_from_station_name,query_to_station_name):
    datas={
         'secretStr':urllib.request.unquote(secretStr),
         'train_date':train_date,
         'back_train_date':back_trian_date,
         'tour_flag':'dc',
         'purpose_codes':'ADULT',
         'query_from_station_name':query_from_station_name,
         'query_to_station_name':query_to_station_name,
         'undefined':'' 
           }
    print(datas,submitUrl)
    try:
        headers ={
        'Host':'kyfw.12306.cn',
        'Referer':'https://kyfw.12306.cn/otn/leftTicket/init',
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36',
        'X-Requested-With':'XMLHttpRequest'
        } 
        res = session.post(submitUrl,data=datas,headers=headers)
        if res.status_code ==200:
            response = res.json()
            print("submit Order",response)
            if response["status"] ==True: #可以买票
                return True
    except Exception as e:
        print(e)
        return True
#验证1函数
def auth1():
    headers ={
        'Host':'kyfw.12306.cn',
        'Referer':'https://kyfw.12306.cn/otn/passport?redirect=/otn/login/userLogin',
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36',
        'X-Requested-With':'XMLHttpRequest'
        }
    authData ={
        'appid':'otn'
        }
    res = session.post(authUrl1,data=authData,headers=headers)
    if res.status_code ==200:
        authJson = res.json()  #{"result_message":"验证通过","result_code":0,"apptk":null,"newapptk":"097slpLU9ijWf0q0hxrUBayvvl5uRonOEwdF1WTMvQQ511110"}
        print("auth1",authJson)
        if authJson['result_code'] ==0: #验证通过
            tk = authJson['newapptk']
            return tk
        else:
            return None
    return None

#验证函数2
def auth2(tk):
    headers ={
        'Host':'kyfw.12306.cn',
        'Referer':'https://kyfw.12306.cn/otn/passport?redirect=/otn/login/userLogin',
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36',
        'X-Requested-With':'XMLHttpRequest'
        }
    authData ={
        'tk':tk
        }
    res = session.post(authUrl2, data=authData, headers=headers)
    if res.status_code ==200:
        authJson = res.json()
        print("auth2",authJson)
        if authJson['result_code'] ==0:
            return True
    return False
#获取验证码图片和验证
def login():
    initres = session.get(initurl,headers=lnitheader) #请求登录表单的页面
    res = session.get(yanZhengMaUrl+getRandom())
    if res.status_code==200:
        rescontent = res.content
        Imagepath=os.getcwd()+"\\12306.png"
        with open(Imagepath,"wb") as f:
            f.write(rescontent)
        print("下载图片完成")
        answer=input("请输入验证码:")
        checkData={
               'answer':answer,
               'login_site':'E',
               'rand':'sjrand'
               }
#         print(checkData)
        res = session.post(checkUrl,headers=lnitheader,data=checkData)
        response = res.json()
        print("Json",response)
        if response["result_code"] =='4': #验证码验证成功
            #验证成功开始登录
            loginresponse = session.post(loginUrl,headers=lnitheader,data=loginData)
            loginJson = loginresponse.json()
            print("用户提交登录",loginJson)
            if loginJson["result_code"] ==0: #登录成功   
                data ={
                    '_json_att':''
                } 
                headers ={
                    'Host': 'kyfw.12306.cn',
                'Origin': 'https://kyfw.12306.cn',
                'Referer': 'https://kyfw.12306.cn/otn/login/init',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3423.2 Safari/537.36'
                    } 
                res =requests.post("https://kyfw.12306.cn/otn/login/userLogin",data=data,headers=headers) 
                userGetHeaders ={
                    'Host': 'kyfw.12306.cn',
                    'Referer':'https://kyfw.12306.cn/otn/login/init',
                    'Upgrade-Insecure-Requests':'1',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3423.2 Safari/537.36'
                    }  
                url ='https://kyfw.12306.cn/otn/passport?redirect=/otn/login/userLogin' 
                res =requests.get(url,headers=userGetHeaders)              
                tk = auth1()
                if tk:
                    if auth2(tk):
                        res =session.get("https://kyfw.12306.cn/otn/leftTicket/init",headers=headers)
                        ticketDate =input("请输入坐车日期,如2018-07-28")
                        fromLocation = input("坐车站地点")
                        toLocation = input("到达地点")
                        checkTicket(ticketDate, fromLocation,toLocation)
if __name__ =="__main__":
    login()



