import json
import re
from datetime import datetime
from time import sleep, strftime
from tkinter import filedialog
import os
import os.path
import random
import traceback
import filetype
import requests
import schedule

headers = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 12; Redmi K30 Pro Zoom Edition Build/SKQ1.211006.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/95.0.4638.74 Mobile Safari/537.36 (device:Redmi K30 Pro Zoom Edition) Language/zh_CN com.chaoxing.mobile/ChaoXingStudy_3_6.2.8_android_phone_1050_234 (@Kalimdor)_8c0587fc07ee4c25bdbbb5d7a90d8152'
}
# 学习通用户名，手机号或者学号
username = "19523685490"
# 学习通密码
password = "80012029Lz"
# 学校ID，当用户名为学号时需要填写，为手机号时不需要填写
schoolid = ""
# 要打卡的地址名称、经度和纬度，可在http://api.map.baidu.com/lbsapi/getpoint/index.html中获取相应位置的坐标
address = "蜀山区合肥市经开区金寨路辅路"
# 打卡位置坐标，通过上面网址查询到的的坐标点可直接粘贴在这里
location = "117.23704,31.789525"
# 这个是学习通实习打卡中的"如果发生特殊情况未能正常打卡，可以在此填写理由"中的内容，可自行填写
remark = ""
# 新版实习打卡中要提交的图片列表，填写时请使用引号包裹后写在中括号内，如下面注释所示
# pictureAry = ["3acf16259def65456fc2a68ab5e10d96"]
# 要设置多个图片请用英文逗号隔开，如下面注释所示
# pictureAry = ["3acf16259def65456fc2a68ab5e10d96","3acf16259def65456fc2a68ab5e10d95","3acf16259def65456fc2a68ab5e10d94"]
pictureAry = []

# 打卡时间配置
clock_in_time = "09:00"   # 上班打卡时间
clock_out_time = "18:00"  # 下班打卡时间
auto_clock = False        # 默认关闭自动打卡

# 添加日志相关配置
log_file = "clockin.log"
last_clockin_date = None  # 记录最后打卡日期

# 配置文件路径
CONFIG_FILE = "users.json"

# 添加一个全局变量来控制任务执行
TASK_RUNNING = False

# 添加配置文件管理函数
def load_config():
    """加载或创建配置文件"""
    if not os.path.exists(CONFIG_FILE):
        default_config = {
            "users": [
                {
                    "username": "",  # 示例用户
                    "password": "",
                    "schoolid": "",
                    "address": "示例地址",
                    "location": "117.23704,31.789525",  # 示例坐标
                    "clock_in_time": "09:00",
                    "remark": "示例用户",
                    "enabled": False,  # 默认禁用
                    "last_clockin_date": None,
                    "clockin_version": "old2"  # 默认使用 old2 版本
                }
            ]
        }
        save_config(default_config)
        print("\n[提示] 已创建默认配置文件 users.json")
        print("[提示] 请使用用户管理功能添加用户信息")
        return default_config
    
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
            # 确保每个用户都有必要的字段
            for user in config['users']:
                if 'clockin_version' not in user:
                    user['clockin_version'] = 'old2'
                if 'last_clockin_date' not in user:
                    user['last_clockin_date'] = None
                if 'enabled' not in user:
                    user['enabled'] = False
            return config
    except Exception as e:
        print(f"\n[错误] 配置文件读取失败: {str(e)}")
        print("[提示] 将创建新的配置文件")
        os.rename(CONFIG_FILE, f"{CONFIG_FILE}.bak")  # 备份损坏的配置文件
        return load_config()  # 递归调用创建新配置

def save_config(config):
    """保存配置到文件"""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"\n[错误] 配置文件保存失败: {str(e)}")

def manage_users():
    config = load_config()
    while True:
        print("\n=== 用户管理 ===")
        print("当前用户列表：")
        for i, user in enumerate(config['users'], 1):
            status = "启用" if user['enabled'] else "禁用"
            version = user.get('clockin_version', 'new')
            print(f"{i}. {user['username']} - {user['clock_in_time']} - {status} - {version}版")
        print("\n操作选项：")
        print("1. 添加用户")
        print("2. 修改用户")
        print("3. 删除用户")
        print("4. 启用/禁用用户")
        print("5. 返回主菜单")
        
        choice = input("\n请选择操作：")
        
        if choice == "1":
            new_user = {
                "username": input("请输入用户名："),
                "password": input("请输入密码："),
                "schoolid": input("请输入学校ID（可选）："),
                "address": input("请输入打卡地址："),
                "location": input("请输入经纬度坐标："),
                "clock_in_time": input("请输入打卡时间（格式如09:00）："),
                "remark": input("请输入备注（可选）："),
                "enabled": True,
                "clockin_version": input("请选择打卡版本(new/old1/old2)：") or "old1"
            }
            config['users'].append(new_user)
            save_config(config)
            print("用户添加成功！")
            
        elif choice == "2":
            user_idx = int(input("请输入要修改的用户序号：")) - 1
            if 0 <= user_idx < len(config['users']):
                user = config['users'][user_idx]
                print(f"\n修改用户 {user['username']} 的信息：")
                user['username'] = input(f"用户名 ({user['username']})：") or user['username']
                user['password'] = input(f"密码 (回车保持不变)：") or user['password']
                user['schoolid'] = input(f"学校ID ({user['schoolid']})：") or user['schoolid']
                user['address'] = input(f"打卡地址 ({user['address']})：") or user['address']
                user['location'] = input(f"经纬度坐标 ({user['location']})：") or user['location']
                user['clock_in_time'] = input(f"打卡时间 ({user['clock_in_time']})：") or user['clock_in_time']
                user['remark'] = input(f"备注 ({user['remark']})：") or user['remark']
                user['clockin_version'] = input(f"打卡版本(new/old1/old2) ({user.get('clockin_version', 'new')})：") or user.get('clockin_version', 'new')
                save_config(config)
                print("用户信息修改成功！")
            else:
                print("无效的用户序号！")
                
        elif choice == "3":
            user_idx = int(input("请输入要删除的用户序号：")) - 1
            if 0 <= user_idx < len(config['users']):
                del config['users'][user_idx]
                save_config(config)
                print("用户删除成功！")
            else:
                print("无效的用户序号！")
                
        elif choice == "4":
            user_idx = int(input("请输入要切换状态的用户序号：")) - 1
            if 0 <= user_idx < len(config['users']):
                config['users'][user_idx]['enabled'] = not config['users'][user_idx]['enabled']
                save_config(config)
                status = "启用" if config['users'][user_idx]['enabled'] else "禁用"
                print(f"用户已{status}！")
            else:
                print("无效的用户序号！")
                
        elif choice == "5":
            break

# 添加日志函数
def log_message(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}\n"
    
    print(log_entry.strip())  # 在控制台显示
    
    # 写入日志文件
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(log_entry)

def new_clockin(session, clock_type=None):
    url = "https://sx.chaoxing.com/internship/planUser/myPlanList"
    res = session.get(url, headers=headers)
    if res.url == url:
        res = res.json()
    else:
        return [0, "登录失败，请检查用户名密码后重试"]
    if res["result"] == 0 and len(res["data"]) > 0:
        planlist = []
        for d in res["data"]:
            tempdict = {"planName": d["planName"], "planId": d["planId"], "fid": d["fid"], "planUserId": d["id"]}
            if d["planStatus"] == 1:
                tempdict["planStatus"] = "进行中"
            elif d["planStatus"] == 2:
                tempdict["planStatus"] = "已结束"
            elif d["planStatus"] == 3:
                tempdict["planStatus"] = "未开始"
            if d["sxStatus"] == 0:
                tempdict["sxStatus"] = "未实习"
            elif d["sxStatus"] == 1:
                tempdict["sxStatus"] = "实习中"
            elif d["sxStatus"] == 2:
                tempdict["sxStatus"] = "免实习"
            elif d["sxStatus"] == 3:
                tempdict["sxStatus"] = "终止实习"
            tempdict["planStartTime"] = d["planStartTime"]
            tempdict["planEndTime"] = d["planEndTime"]
            tempdict["recruitNames"] = d["recruitNames"]
            planlist.append(tempdict)
        print("{} {:<50} {:<10} {:<6} {:<23} {}".format("ID", "实习计划名称", "实习计划状态", "实习状态", "实习时间", "实习岗位"))
        print("-" * 120)
        inputid = 0
        for d in planlist:
            inputid += 1
            print("{:<2} {:<40} {:<12} {:<7} {:<25} {}".format(inputid, d["planName"], d["planStatus"], d["sxStatus"], d["planStartTime"] + "-" + d["planEndTime"], d["recruitNames"]))
        while True:
            inputid = input("输入要进行实习打卡的ID：")
            try:
                inputid = int(inputid)
                if 0 < inputid <= len(planlist):
                    break
                else:
                    print("ID输入错误，请重新输入")
            except ValueError:
                print("ID输入错误，请重新输入")
        select_plan = planlist[inputid-1]
        getDataByIdurl = "https://sx.chaoxing.com/internship/planUser/getDataById?planId={}&planUserId={}".format(select_plan["planId"], select_plan["planUserId"])
        res = session.get(getDataByIdurl, headers=headers)
        if res.url == getDataByIdurl:
            res = res.json()
            if res["result"] == 0 and res["data"] is not None:
                if len(res["data"]["userPeriods"]) > 0:
                    workStart = res["data"]["userPeriods"][0]["planUserRecruit"]["recruitVo"]["workStart"]
                    workEnd = res["data"]["userPeriods"][0]["planUserRecruit"]["recruitVo"]["workEnd"]
                else:
                    workStart = ""
                    workEnd = ""
                dgsxpcurl = "https://sx.chaoxing.com/internship/dgsxpc/{}".format(select_plan["planId"])
                res = session.get(dgsxpcurl, headers=headers)
                if res.url == dgsxpcurl:
                    res = res.json()
                    if res["result"] == 0 and res["data"] is not None:
                        isontimesign = res["data"]["isontimesign"]
                        allowOffset = res["data"]["offset"] or 2000
                        dateurl = "https://sx.chaoxing.com/internship/clockin-user/get/stu/{}/date?date={}".format(
                            select_plan["planId"], 
                            datetime.now().strftime("%Y-%m-%d")
                        )
                        res = session.get(dateurl, headers=headers)
                        if res.url == dateurl:
                            res = res.json()
                            if res["result"] == 0 and res["data"] is not None:
                                cxid = res["data"]["cxid"]
                                clockinId = res["data"]["id"]
                                if clock_type is not None:
                                    clockintype = clock_type
                                    statusName = "上班" if clock_type == "0" else "下班"
                                else:
                                    while True:
                                        clockintype = input("请输入上下班打卡状态，输入0为上班打卡，输入1为下班打卡：")
                                        if clockintype != "0" and clockintype != "1":
                                            print("输入错误，请重新输入")
                                        elif clockintype == "0":
                                            statusName = "上班"
                                            break
                                        else:
                                            statusName = "下班"
                                            break
                                recruitId = res["data"]["recruitId"]
                                pcid = res["data"]["pcid"]
                                pcmajorid = res["data"]["pcmajorid"]
                                offduty = 0
                                if isontimesign:
                                    addclockinurl = "https://sx.chaoxing.com/internship/clockin-user/stu/addclockin/{}".format(cxid)
                                else:
                                    addclockinurl = "https://sx.chaoxing.com/internship/clockin-user/stu/addclockinOnceInDay/{}".format(cxid)
                                data = {
                                    "id": clockinId,
                                    "type": clockintype,
                                    "recruitId": recruitId,
                                    "pcid": pcid,
                                    "pcmajorid": pcmajorid,
                                    "address": address,
                                    "geolocation": location,
                                    "remark": remark,
                                    "workStart": workStart,
                                    "workEnd": workEnd,
                                    "images": json.dumps(pictureAry) if len(pictureAry) > 0 else "",
                                    "allowOffset": allowOffset,
                                    "offset": "NaN",
                                    "offduty": offduty,
                                    "codecolor": "",
                                    "havestar": "",
                                    "worktype": "",
                                    "changeLocation": "",
                                    "statusName": statusName,
                                    "shouldSignAddress": ""
                                }
                                res = session.post(addclockinurl, headers=headers, data=data)
                                if res.url == addclockinurl:
                                    return [1, res.text]
                                else:
                                    return [0, "登录失败，请检查用户名密码后重试"]
                            else:
                                return [2, res["errorMsg"]]
                        else:
                            return [0, "登录失败，请检查用户名密码后重试"]
                    else:
                        return [2, res["errorMsg"]]
                else:
                    return [0, "登录失败，请检查用户名密码后重试"]
            else:
                return [2, res["errorMsg"]]
        else:
            return [0, "登录失败，请检查用户名密码后重试"]
    else:
        return [2, "未找到新版实习打卡任务"]


def old_clockin1(session, user_config):
    """
    旧版页面1打卡
    :param session: 会话对象
    :param user_config: 用户配置
    """
    res = session.get("https://www.dgsx.chaoxing.com/form/mobile/signIndex", headers=headers)
    txt = res.text
    if txt != "您还没有被分配实习计划。":
        if "用户登录状态异常，请重新登录！" not in txt:
            planName = re.search(r"planName: '(.*)',", txt, re.I).groups()[0]
            clockin_type = re.search(r"type: '(.*)',", txt, re.I).groups()[0]
            signType = re.search(r"signType: '(.*)',", txt, re.I).groups()[0]
            workAddress = re.search(r'<input type="hidden" id="workAddress" value="(.*)"/>', txt, re.I).groups()[0]
            geolocation = re.search(r'<input type="hidden" id="workLocation" value="(.*)">', txt, re.I).groups()[0]
            allowOffset = re.search(r'<input type="hidden" id="allowOffset" value="(.*)"/>', txt, re.I).groups()[0]
            signSettingId = re.search(r'<input type="hidden" id="signSettingId" value="(.*)"/>', txt, re.I).groups()[0]
            data = {
                "planName": planName,
                "type": clockin_type,
                "signType": signType,
                "address": user_config['address'],
                "geolocation": user_config['location'],
                "remark": user_config.get('remark', ''),
                "images": "",
                "offset": 0,
                "allowOffset": allowOffset,
                "signSettingId": signSettingId
            }
            res = session.post("https://www.dgsx.chaoxing.com/form/mobile/saveSign", headers=headers, data=data)
            return [1, res.text]
        else:
            return [0, "登录失败，请检查用户名密码后重试"]
    else:
        return [2, "未找到旧版页面1实习打卡任务"]


def old_clockin2(session, user_config):
    """
    旧版页面2打卡
    :param session: 会话对象
    :param user_config: 用户配置
    """
    res = session.get("https://i.chaoxing.com/base/cacheUserOrg", headers=headers).json()
    site = res["site"]
    for d in site:
        fid = str(d["fid"])
        session.cookies.set("wfwfid", fid)
        res = session.get("https://www.dgsx.chaoxing.com/mobile/clockin/show", headers=headers)
        txt = res.text
        if res.status_code == 200:
            if "alert('请先登录');" in txt or 'alert("实习计划已进入总结期或实习已终止，无法签到");' in txt:
                continue
            elif "用户登录状态异常，请重新登录！" not in txt:
                clockinId = re.search(r'<input id="clockinId" type="hidden" value="(.*)">', txt, re.I).groups()[0]
                recruitId = re.search(r'<input type="hidden" id="recruitId" value="(.*)" />', txt, re.I).groups()[0]
                pcid = re.search(r'<input type="hidden" id="pcid" value="(.*)" />', txt, re.I).groups()[0]
                pcmajorid = re.search(r'<input type="hidden" id="pcmajorid" value="(.*)" />', txt, re.I).groups()[0]
                should_bntover = re.search(r'''<dd class="should_bntover" selid="(.*)" workStart='(.*)' workEnd='(.*)'>''', txt, re.I).groups()
                workStart = should_bntover[1]
                workEnd = should_bntover[2]
                allowOffset = re.search(r'<input type="hidden" id="allowOffset" value="(.*)"/>', txt, re.I).groups()[0]
                changeLocation = re.search(r'<input type="text" name="location" id="location" value="(.*)" hidden/>', txt, re.I).groups()[0]
                if re.search(r'<input id="workLocation" type="hidden" >', txt, re.I) is None:
                    if re.search(r'<input id="workLocation" type="hidden" value="(.*)">', txt, re.I) is None:
                        offset = "NaN"
                    else:
                        offset = re.search(r'<input id="workLocation" type="hidden" value="(.*)">', txt, re.I).groups()[0]
                else:
                    offset = "NaN"
                data = {
                    "id": clockinId,
                    "type": 0,
                    "recruitId": recruitId,
                    "pcid": pcid,
                    "pcmajorid": pcmajorid,
                    "address": user_config['address'],
                    "geolocation": user_config['location'],
                    "remark": user_config.get('remark', ''),
                    "workStart": workStart,
                    "workEnd": workEnd,
                    "images": "",
                    "allowOffset": allowOffset,
                    "offset": offset,
                    "offduty": 0,
                    "changeLocation": changeLocation
                }
                res = session.post("https://www.dgsx.chaoxing.com/mobile/clockin/addclockin2", headers=headers, data=data)
                print("旧版页面2打卡结果", res.text)
                return True
            else:
                return False
    return False


def clockin_main(user_config, clock_type=None):
    """
    执行打卡
    :param user_config: 用户配置字典，包含所有用户信息
    :param clock_type: 打卡类型（"0"上班，"1"下班）
    """
    session = requests.session()
    resp = session.post(
        'https://passport2.chaoxing.com/api/login?name={}&pwd={}&schoolid={}&verify=0'.format(
            user_config['username'], 
            user_config['password'], 
            user_config['schoolid']
        ), 
        headers=headers
    ).json()
    
    if resp["result"]:
        print(f"用户 {user_config['username']} 登录成功")
        
        # 修改默认版本为 old1
        version = user_config.get('clockin_version', 'old1')  # 默认使用旧版
        
        if version == 'new':
            print("使用新版打卡")
            result = new_clockin(session, user_config, clock_type)
            if result[0] == 1:
                return result[1]
            return "新版打卡失败"
        elif version == 'old1':
            print("使用旧版页面1打卡")
            result = old_clockin1(session, user_config)
            if result[0] == 1:
                return result[1]
            return "旧版页面1打卡失败"
        elif version == 'old2':
            print("使用旧版页面2打卡")
            result = old_clockin2(session, user_config)
            if result:
                return "打卡成功"
            return "旧版页面2打卡失败"
        else:
            return f"未知的打卡版本: {version}"
    else:
        print(f"用户 {user_config['username']} 登录失败，请检查用户名密码")
        return "登录失败"


def upload_img():
    session = requests.session()
    resp = session.post('https://passport2.chaoxing.com/api/login?name={}&pwd={}&schoolid={}&verify=0'.format(username, password, schoolid), headers=headers).json()
    if resp["result"]:
        while True:
            filepath = filedialog.askopenfilename(title="选择拍照图片", filetypes=(("图片文件", "*.jpg;*.png;*.gif;*.webp;*.bmp"),))
            file_type = filetype.guess(filepath)
            if file_type is None:
                print("您选择的文件不是图片文件，请重新选择")
                sleep(3)
            elif file_type.extension != "jpg" and file_type.extension != "png" and file_type.extension != "gif" and file_type.extension != "webp" and file_type.extension != "bmp":
                print("您选择的文件不是图片文件，请重新选择")
                sleep(3)
            else:
                break
        uploadurl = "https://sx.chaoxing.com/internship/usts/file"
        with open(filepath, 'rb') as file:
            files = {'file': file}
            res = session.post(uploadurl, headers=headers, files=files)
        if res.url == uploadurl:
            res = res.json()
            if res["result"] == 0:
                print("上传成功，文件ID为", res["data"]["objectid"], "可将其粘贴至pictureAry列表中，粘贴后请重新运行脚本使其生效")
            else:
                print("上传失败", res["errorMsg"])
        else:
            print("登录失败，请检查您的用户名密码是否正确")
    else:
        print("登录失败，请检查您的用户名密码是否正确")
    sleep(3)


# 修改 schedule_clock_in 函数
def schedule_clock_in():
    global TASK_RUNNING
    
    if TASK_RUNNING:
        return
        
    try:
        TASK_RUNNING = True
        config = load_config()
        current_date = datetime.now().date().isoformat()
        current_time = datetime.now().strftime("%H:%M")
        
        # 重置过期的打卡记录
        for user in config['users']:
            if user.get('last_clockin_date') and user['last_clockin_date'] != current_date:
                user['last_clockin_date'] = None
        save_config(config)
        
        # 找到需要打卡的用户
        current_users = sorted(
            [user for user in config['users'] 
             if user['enabled'] 
             and user.get('last_clockin_date') != current_date
             and user['clock_in_time'] == current_time],
            key=lambda x: x['username']
        )
        
        if not current_users:
            log_message(f"当前时间 {current_time} 没有需要打卡的用户")
            return
            
        log_message(f"=== 开始执行 {current_time} 的打卡任务 ===")
        log_message(f"待打卡用户：{', '.join(f'{u['username']}({u['remark']})' for u in current_users)}")
        
        for i, user in enumerate(current_users, 1):
            log_message(f"正在为第 {i}/{len(current_users)} 个用户打卡")
            log_message(f"开始为用户 {user['username']} ({user['remark']}) 执行打卡")
            try:
                # 执行打卡
                result = clockin_main(user, "0")
                log_message(f"打卡返回结果: {result}")
                
                # 改进打卡结果验证
                success_keywords = ["打卡成功", "今日已打卡", "已经打过卡", "签到成功"]
                is_success = any(keyword in str(result) for keyword in success_keywords)
                
                if is_success:
                    user['last_clockin_date'] = current_date
                    save_config(config)
                    log_message(f"用户 {user['username']} 自动打卡成功")
                    # 成功后等待5秒再打卡下一个用户
                    if i < len(current_users):
                        log_message(f"等待5秒后开始下一个用户的打卡...")
                        sleep(5)
                else:
                    log_message(f"用户 {user['username']} 打卡失败，返回信息: {result}")
                    # 重试一次
                    log_message(f"等待5秒后尝试重新打卡...")
                    sleep(5)
                    retry_result = clockin_main(user, "0")
                    log_message(f"重试返回结果: {retry_result}")
                    
                    is_retry_success = any(keyword in str(retry_result) for keyword in success_keywords)
                    if is_retry_success:
                        user['last_clockin_date'] = current_date
                        save_config(config)
                        log_message(f"用户 {user['username']} 重试打卡成功")
                        # 成功后等待5秒再打卡下一个用户
                        if i < len(current_users):
                            log_message(f"等待5秒后开始下一个用户的打卡...")
                            sleep(5)
                    else:
                        log_message(f"用户 {user['username']} 重试打卡失败，返回信息: {retry_result}")
                        # 失败后等待5秒再尝试下一个用户
                        if i < len(current_users):
                            log_message(f"等待5秒后开始下一个用户的打卡...")
                            sleep(5)
                
            except Exception as e:
                log_message(f"用户 {user['username']} 打卡出现异常: {str(e)}")
                traceback.print_exc()
                # 出错后等待60秒再尝试下一个用户
                if i < len(current_users):
                    log_message(f"等待60秒后开始下一个用户的打卡...")
                    sleep(60)
        
        # 打卡完成后的统计
        success_count = len([u for u in current_users if u.get('last_clockin_date') == current_date])
        log_message(f"=== {current_time} 打卡任务完成 ===")
        log_message(f"总计 {len(current_users)} 个用户，成功 {success_count} 个")
        
    finally:
        TASK_RUNNING = False

def schedule_clock_out():
    log_message(f"下班打卡")
    clockin_main("1")

def test_clockin(user_name):
    """测试单个用户的打卡功能"""
    config = load_config()
    user = next((u for u in config['users'] if u['username'] == user_name), None)
    if not user:
        print(f"未找到用户 {user_name}")
        return
        
    # 设置全局变量
    global username, password, schoolid, address, location, remark
    username = user['username']
    password = user['password']
    schoolid = user['schoolid']
    address = user['address']
    location = user['location']
    remark = user['remark']
    
    log_message(f"开始测试用户 {user_name} 的打卡功能")
    result = clockin_main("0")
    log_message(f"打卡返回结果: {result}")

if __name__ == '__main__':
    while True:
        print("\n欢迎使用学习通实习打卡签到脚本")
        print("0.手动打卡")
        print("1.上传打卡图片")
        print("2.启动自动打卡")
        print("3.用户管理")
        print("4.退出")
        useid = input("请输入功能序号：")
        
        if useid == "0":
            config = load_config()
            print("\n请选择用户：")
            for i, user in enumerate(config['users'], 1):
                print(f"{i}. {user['username']}")
            user_idx = int(input("请输入用户序号：")) - 1
            if 0 <= user_idx < len(config['users']):
                user = config['users'][user_idx]
                result = clockin_main(user)
                print(f"打卡结果: {result}")
            else:
                print("无效的用户序号！")
        elif useid == "1":
            upload_img()
        elif useid == "2":
            config = load_config()
            schedule.clear()
            
            # 为每个启用的用户设置定时任务
            enabled_users = [user for user in config['users'] if user['enabled']]
            if not enabled_users:
                print("没有启用的用户！")
                continue
            
            # 按时间排序用户
            enabled_users.sort(key=lambda x: x['clock_in_time'])
            
            # 获取所有不同的打卡时间
            unique_times = sorted(set(user['clock_in_time'] for user in enabled_users))
            
            # 显示打卡计划
            log_message("=== 打卡计划 ===")
            for time in unique_times:
                users_at_time = [u for u in enabled_users if u['clock_in_time'] == time]
                log_message(f"时间 {time}:")
                for i, user in enumerate(users_at_time, 1):
                    log_message(f"  {i}. {user['username']} ({user['remark']})")
                schedule.every().day.at(time).do(schedule_clock_in)
            
            log_message(f"日志文件位置：{os.path.abspath(log_file)}")
            print("按Ctrl+C可以终止自动打卡")
            
            try:
                while True:
                    schedule.run_pending()
                    sleep(30)
            except KeyboardInterrupt:
                log_message("自动打卡已停止")
                schedule.clear()
                continue
        elif useid == "3":
            manage_users()
        elif useid == "4":
            break
        else:
            print("输入错误，请重新输入")
