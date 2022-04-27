import threading
import time
import requests
import re
import json
from threading import Thread

# 以下的csrftoken和sessionid需要改成自己登录后的cookie中对应的字段！！！！而且脚本需在登录雨课堂状态下使用
# 登录上雨课堂，然后按F12-->选Application-->找到雨课堂的cookies，寻找csrftoken和sessionid字段，并复制到下面两行即可
# 以下字段不用改，下面的代码也不用改动

global csrftoken
csrftoken = "" 

global sessionid
sessionid = "" 

global university_id
university_id = ""

global school_url_pre
school_url_pre = ""

global user_id
user_id = ""

global headers

leaf_type = {
    "video": 0,
    "homework": 6,
    "exam": 5,
    "recommend": 3,
    "discussion": 4
}

# 获得全局变量中的基本信息
def get_basic_info():
    school_url=input("请随便打开一个视频,并黏贴网页链接\n")
    cookie = input("黏贴你在F12->网络->请求标头里找到的cookie\n")+";"
    school_url = re.search(r'(.+?).cn/',school_url)
    global school_url_pre
    school_url_pre = school_url.group(1)+".cn"

    csrftoken_re = re.search(r'csrftoken=(.+?);',cookie)
    sessionid_re = re.search(r'sessionid=(.+?);',cookie)
    university_id_re = re.search(r'university_id=(.+?);',cookie)

    global csrftoken
    csrftoken = csrftoken_re.group(1)
    global sessionid
    sessionid = sessionid_re.group(1)
    global university_id
    university_id = university_id_re.group(1)
    # print(school_url_pre)
    # print(csrftoken)
    # print(sessionid)
    # print(university_id)
    make_headers()

# 制造请求头
def make_headers():
    global headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36',
        'Content-Type': 'application/json',
        'Cookie': 'csrftoken=' + csrftoken + '; sessionid=' + sessionid + '; university_id=3'+university_id+'; platform_id=3',
        'x-csrftoken': csrftoken,
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'university-id': university_id,
        'xtbz': 'cloud',
        'referer': school_url_pre
    }

# 获取用户ID
def get_user_id():
    # 首先要获取用户的个人ID，即user_id,该值在查询用户的视频进度时需要使用
    user_id_url = school_url_pre+"/edu_admin/check_user_session/"
    id_response = requests.get(url=user_id_url, headers=headers)
    try:
        global user_id 
        user_id = re.search(r'"user_id":(.+?)}', id_response.text).group(1).strip()
    except:
        print("无法获取user_id,请重重重新运行一次该程序!")
        raise Exception("无法获取user_id,请重重重新运行一次该程序!")

# 获取教室ID
def get_classroom_id(courses):
    get_classroom_id_url = school_url_pre+"/mooc-api/v1/lms/user/user-courses/?status=1&page=1&no_page=1&term=latest&uv_id="+university_id
    
    classroom_id_response = requests.get(url=get_classroom_id_url, headers=headers)
    try:
        for ins in json.loads(classroom_id_response.text)["data"]["product_list"]:
            courses.append({
                "course_name": ins["course_name"],
                "classroom_id": ins["classroom_id"],
                "course_sign": ins["course_sign"],
                "sku_id": ins["sku_id"],
                "course_id": ins["course_id"]
            })
    except Exception as e:
        print("无法获取classroom_id,请重重重新运行一次该程序!")
        raise Exception("无法获取classroom_id,请重重重新运行一次该程序!")

# 展示课程列表
def display_your_courses(courses):
    for index, value in enumerate(courses):
        print("编号："+str(index+1)+" 课名："+str(value["course_name"]))

# 选择要刷哪门课
def choose_courses(courses):
    number = input("你想刷哪门课呢?请输入编号。输入0表示全部课程都刷一遍\n")
    number = int(number)
    print(len(courses))
    if number==0:
        #0 表示全部刷一遍
        for ins in courses:
            temp_thread=threading.Thread(target = watch_target_video,kwargs={"ins":ins})
            temp_thread.start()
            temp_thread.join()
    elif number in range(1,len(courses)+1):
        #指定序号的课程刷一遍
        watch_target_video(courses[number-1])
    else :
        print("没有这门课捏,请再选一次吧!")
        return True
    return False

# 观看指定视频
def watch_target_video(ins):
    homework_dic = get_videos_ids(ins["course_name"],ins["classroom_id"], ins["course_sign"])
    for one_video in homework_dic.items():
        temp_thread1 = threading.Thread(target=video_watcher,kwargs={"video_id":one_video[0],"video_name":one_video[1],"cid":ins["course_id"],"user_id":user_id,"classroomid":ins["classroom_id"],"skuid":ins["sku_id"]})
        temp_thread1.start()
        # temp_thread1.join()

# 获取视频ID
def get_videos_ids(course_name,classroom_id,course_sign):
    get_homework_ids = school_url_pre+"/mooc-api/v1/lms/learn/course/chapter?cid="+str(classroom_id)+"&term=latest&uv_id="+university_id+"&sign="+course_sign
    homework_ids_response = requests.get(url=get_homework_ids, headers=headers)
    homework_json = json.loads(homework_ids_response.text)
    homework_dic = {}
    # leaf_type为学习形式，每个代号表示不同的学习方法
    # data->course_chapter->section_leaf_list->class,具体可看下方返回示例
    try:
        for chapter in homework_json["data"]["course_chapter"]:
            for section_data in chapter["section_leaf_list"]:
                if "leaf_list" in section_data:
                    for class_data in section_data["leaf_list"]:
                        if class_data['leaf_type'] == leaf_type["video"]:
                            homework_dic[class_data["id"]] = class_data["name"]
                else:
                    if section_data['leaf_type'] == leaf_type["video"]:
                        homework_dic[section_data["id"]] = section_data["name"]
        print(course_name+"共有"+str(len(homework_dic))+"个作业喔！")
        return homework_dic
    except:
        print("无法获取video_ids,请重重重新运行一次该程序!")
        raise Exception("无法获取video_ids,请重重重新运行一次该程序!")

# 观看视频
def video_watcher(video_id,video_name,cid,user_id,classroomid,skuid):
    video_id = str(video_id)
    classroomid = str(classroomid)
    heart_url = school_url_pre+"/video-log/heartbeat/"
    get_url = school_url_pre+"/video-log/get_video_watch_progress/?cid="+str(cid)+"&user_id="+user_id+"&classroom_id="+classroomid+"&video_type=video&vtype=rate&video_id=" + str(video_id) + "&snapshot=1&term=latest&uv_id="+university_id
    progress = requests.get(url=get_url, headers=headers)
    if_completed = '0'
    try:
        if_completed = re.search(r'"completed":(.+?),', progress.text).group(1)
    except:
        pass
    if if_completed == '1':
        print(video_name+"已经学习完毕，跳过")
        return 1
    else:
        print(video_name+"，尚未学习，现在开始自动学习")
    
    # 变量区
    video_frame = 0
    val = 0
    learning_rate = 20
    t = time.time()
    timestamp = int(round(t * 1000))
    flag1 = True
    # 发送心跳包，伪装正在看视频的进度
    while val != "1.0" and val != '1':
        heart_data = []
        for i in range(50):
            heart_data.append(
                {   # 未作说明或者不是变量的均被写死
                    "c": cid,
                    "cards_id" :0,
                    "cc": video_id,
                    # 作者提供video_id但实际显示为一段长字符，不知含义(经过试验后并不影响使用)
                    "classroomid": classroomid,
                    "cp": video_frame,
                    "d": 4976.5,
                    "et": "loadeddata",
                    "fp": 0,
                    "i": 5,
                    "lob": "cloud4",
                    "n": "ws",
                    # n有争议，现在为ali-cdn.xuetangx.com，先作尝试(经过试验后并不影响使用)
                    "p": "web",
                    "pg": video_id,
                    "skuid": skuid,
                    "slide": 0,
                    "sp": 1,
                    "sq": 2,
                    # sq 实际随heartbeat包发送的次数增加，暂时不做修改(经过试验后并不影响使用)
                    "t": "video",
                    "tp": 0,
                    "ts": str(timestamp),
                    "u": int(user_id),
                    "uip": "",
                    "v": int(video_id),
                    "v_url" : "",
                }
            )
            video_frame += learning_rate
            max_time = int((time.time() + 3600) * 1000)
            timestamp = min(max_time, timestamp+1000*15)
        data = {"heart_data": heart_data}
        r = requests.post(url=heart_url,headers=headers,json=data)
        if flag1 :
            print(r)
            flag1=False
        try:
            error_msg = json.loads(r.text)["message"]
            if "anomaly" in error_msg:
                video_frame = 0
        except:
            pass
        try:
            delay_time = re.search(r'Expected available in(.+?)second.', r.text).group(1).strip()
            print("由于网络阻塞，万恶的雨课堂，要阻塞 " + str(delay_time) + " 秒")
            time.sleep(float(delay_time) + 0.5)
            video_frame = 0
            print("恢复工作啦～～")
            submit_url = school_url_pre+"/mooc-api/v1/lms/exercise/problem_apply/?term=latest&uv_id="+university_id
            r = requests.post(url=submit_url, headers=headers, data=data)
        except:
            pass
        progress = requests.get(url=get_url,headers=headers)
        temp_rate = re.search(r'"rate":(.+?)[,}]',progress.text)
        if temp_rate is None:
            return 0
        val = temp_rate.group(1)
        print("     学习进度为：" + str(float(val)*100) + "%/100%" + " last_point: " + str(video_frame))
        time.sleep(0.7)
    print("     video_id: "+video_id+"  "+video_name+"  学习完成!")
    return 1







if __name__ == "__main__":
    your_courses = []
    # 获取基本信息
    get_basic_info()
    # 首先要获取用户的个人ID，即user_id,该值在查询用户的视频进度时需要使用
    get_user_id()
    # 然后要获取教室id
    get_classroom_id(your_courses)
    flag=True
    while flag : 
        # 显示用户提示
        display_your_courses(your_courses)
        flag = choose_courses(your_courses)


# 提供每个url请求的标准返回数据

# get_classroom_id:
#
# {"msg": "", 
# "data": {
#     "count": 1, 
#     "is_agreement": true, 
#     "product_list": [{
#         "status": 0, 
#         "sku_id": 58****8*3, 
#         "course_name": "\u592********5eb7\u6559\u80b2", 
#         "short_name": null, 
#         "class_end": 168****88****00,
#         "created": "2022-04-08 09:34:20",
#         "course_cover": "", 
#         "class_start": 164****000,
#         "signup_end": 0, 
#         "course_sign":"7gz****f4s", 
#         "classroom_name": "2022\u6625-\u571f****6c5f\u80dc\u73cd", 
#         "classroom_id": 18****18,
#         "course_id": 8****40,
#         "classroom_term": 2****2,
#         "signup_start": 164******00, 
#         "allow_student_quit_classroom": false}
#     ]
# }, 
# "success": true}


# get_video_id:
#
# {'data': {
#     'course_id': 17******0, 
#     'course_chapter': [
#         {'section_leaf_list': [
#             {'name': '自我意识与心理健康', 
#             'is_locked': False, 
#             'start_time': 16*****00, 
#             'chapter_id': 8*****01, 
#             'section_id': None, 
#             'leaf_type': 8, 
#             'id': 20*****32, 
#             'is_show': True, 
#             'end_time': 0, 
#             'score_deadline': 0, 
#             'is_score': True, 
#             'is_assessed': False, 
#             'order': 2, 
#             'leafinfo_id': 2******45}, 
#             {'name': '大学生心理健康教育', 
#             'is_locked': False, 
#             'start_time': 165******00, 
#             'chapter_id': 85*****01, 
#             'section_id': None, 
#             'leaf_type': 8, 
#             'id': 20*****67, 
#             'is_show': True, 
#             'end_time': 0, 
#             'score_deadline': 0, 
#             'is_score': True, 
#             'is_assessed': False, 
#             'order': 1, 
#             'leafinfo_id': 20*****80}], 
#             'order': -1, 
#             'id': 8*******01, 
#             'name': '未分类教学活动'
#         }, 
#         {'section_leaf_list': [
#             {'name': '绪论课程预告', 
#             'is_locked': False, 
#             'start_time': 16******00, 
#             'chapter_id': 85****23, 
#             'section_id': None, 
#             'leaf_type': 3, 
#             'id': 20*****5, 
#             'is_show': True, 
#             'end_time': 0, 
#             'score_deadline': 0, 
#             'is_score': True, 
#             'is_assessed': False, 
#             'order': 0, 
#             'leafinfo_id': 20****3}, 
#             {'order': 1, 
#             'leaf_list': [
#                 {'name': '1-1心理健康', 
#                 'is_locked': False, 
#                 'start_time': 16*****000, 
#                 'chapter_id': 8*****3, 
#                 'section_id': 4****5, 
#                 'leaf_type': 0, 
#                 'id': 2*******0, 
#                 'is_show': True, 
#                 'end_time': 0, 
#                 'score_deadline': 0, 
#                 'is_score': True, 
#                 'is_assessed': False, 
#                 'order': 0, 
#                 'leafinfo_id': 2*****8}], 
#                 'chapter_id': 8*****3, 
#                 'id': 4******5, 
#                 'name': '第一节  心理健康'},
#             {'order': 2, 
#             'leaf_list': [
#                 {'name': '2-1大学生心理健康的标准与身心发展特点', 
#                 'is_locked': False, 
#                 'start_time': 16*******00, 
#                 'chapter_id': 8*****3, 
#                 'section_id': 4******6, 
#                 'leaf_type': 0, 
#                 'id': 2****1, 
#                 'is_show': True, 
#                 'end_time': 0, 
#                 'score_deadline': 0, 
#                 'is_score': True, 
#                 'is_assessed': False, 
#                 'order': 0, 
#                 'leafinfo_id': 2*****9}], 
#                 'chapter_id': 88*****3, 
#                 'id': 4******6, 
#                 'name': '第二节  大学生心理健康的标准与身心发展特点'}, 
#             {'order': 3, 
#             'leaf_list': [{
#                 'name': '3-1关于高校心理咨询', 
#                 'is_locked': False, 