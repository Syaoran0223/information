import json
from app.exceptions import JsonOutputException, FormValidateError
from app.decorators import api_login_required, permission_required
from app.models import Attachment, Exam, User, Message
from app.utils import upload, pagination
from flask import request, g
from flask.ext.login import login_required
from .forms import SmsForm, PaperUploadForm
from werkzeug.datastructures import MultiDict
from app.const import EXAM_STATUS,QUEST_IMAGE_STATUS
from . import api_blueprint
from app.models import Region, School, ExamReviewLog, QuestImage
from app.sms import SmsServer
from app.utils import render_api

import datetime
@api_blueprint.route('/province')
def province():
    title = request.args.get('title', '')
    provinces = Region.get_province(title)
    return {
        'code': 0,
        'data': provinces
    }

@api_blueprint.route('/city')
def city():
    pro_id = request.args.get('pro_id')
    title = request.args.get('title', '')
    if not pro_id:
        raise JsonOutputException('need pro_id')
    cities = Region.get_city(pro_id, title)
    return {
        'code': 0,
        'data': cities
    }

@api_blueprint.route('/area')
def area():
    city_id = request.args.get('city_id')
    title = request.args.get('title', '')
    if not city_id:
        raise JsonOutputException('need city_id')
    areas = Region.get_area(city_id, title)
    return {
        'code': 0,
        'data': areas
    }

@api_blueprint.route('/school')
def school():
    ctid = request.args.get('ctid')
    title = request.args.get('title', '')
    if not ctid:
        raise JsonOutputException('need ctid')
    schools = School.get_schools_by_ctid(ctid, title)
    return {
        'code': 0,
        'data': schools
    }

@api_blueprint.route('/sms')
def send_msg():
    form = SmsForm(request.args)
    if not form.validate():
        raise FormValidateError(form.errors)
    phone = form.phone.data
    sms = SmsServer()
    success, code = sms.generate_code(phone)
    if not success:
        return {
            'code': 15,
            'msg': '请求太频繁，请稍后重试'
        }
    return sms.send_code(code, phone)


@api_blueprint.route('/uploads', methods=['POST'])
@api_login_required
@permission_required('UPLOAD_PERMISSION')
def upload_attachment():
    file = request.files.get('file')
    thumb = bool(request.args.get('thumb', False))
    if not file:
        raise JsonOutputException('请选择要上传的文件')
    file_type = request.form.get('type', '')
    data = upload(file, thumb)
    if data.get('status') is True:
        attachment = Attachment(
            name=data.get('original', ''),
            url=data.get('url', ''),
            user_id=g.user.id,
            file_type=file_type)
        attachment.save()
        #attachment.id
        return {
            'code': 0,
            'data': [attachment.url]
        }
    raise JsonOutputException('上传失败')

#上传试卷
@api_blueprint.route('/paper/upload', methods=['POST'])
@api_login_required
@permission_required('UPLOAD_PERMISSION')
def paper_upload():
    data = MultiDict(mapping=request.json)
    form = PaperUploadForm(data)
    if not form.validate():
        raise FormValidateError(form.errors)
    # todo 插入数据库
    attachments = request.json.get('attachments', [])
    exam = Exam(name=form.name.data, section=form.section.data, subject=form.subject.data, paper_types=form.paper_types.data, \
                province_id=form.province_id.data, city_id=form.city_id.data, area_id=form.area_id.data,\
                school_id=form.school_id.data,
                year=form.year.data, grade=form.grade.data, state=0, attachments=attachments, upload_user=g.user.id)
    result = exam.save()
    if result.id is not None:
        return {
            'code': 0,
            'data': ''
        }
    raise JsonOutputException('添加失败')

#试卷列表
@api_blueprint.route('/paper/upload', methods=['GET'])
@api_login_required
@permission_required('UPLOAD_PERMISSION')
def get_exams():
    data = Exam.get_exams(g.user.id)
    return {
        'code': 0,
        'data': data
    }

#试卷明细查看
@api_blueprint.route('/paper/upload/<int:id>', methods=['GET'])
@api_login_required
@permission_required('UPLOAD_PERMISSION')
def get_exam(id):
    data = Exam.get_exam(id)
    if data is not None:
        return {
            'code': 0,
            'data': data
        }
    else:
        raise JsonOutputException('没有数据')

#试卷更新
@api_blueprint.route('/paper/upload/<int:id>', methods=['PUT'])
@api_login_required
@permission_required('UPLOAD_PERMISSION')
def update_exam(id):
    data = MultiDict(mapping=request.json)
    form = PaperUploadForm(data)
    if not form.validate():
        raise FormValidateError(form.errors)
    attachments = request.json.get('attachments', [])
    exam = Exam.query.get(int(id))
    exam.name = form.name.data
    exam.section = form.section.data
    exam.subject = form.subject.data
    exam.paper_types = form.paper_types.data
    exam.province_id = form.province_id.data
    exam.city_id = form.city_id.data
    exam.area_id = form.area_id.data
    exam.school_id = form.school_id.data
    exam.year = form.year.data
    exam.grade = form.grade.data
    exam.attachments = attachments
    exam.save()
    if data is not None:
        return {
            'code': 0,
            'data': data
        }
    else:
        raise JsonOutputException('更新失败')

#试卷删除
@api_blueprint.route('/paper/upload/<int:id>', methods=['DELETE'])
@api_login_required
@permission_required('UPLOAD_PERMISSION')
def delexam(id):

    exam = Exam.query.get(int(id))
    if exam is None or exam.state > EXAM_STATUS['未审核']:
        raise JsonOutputException('删除失败')
    else:
        exam.state = EXAM_STATUS['已删除']
        exam.save()
        return {
            'code': 0,
            'data': ''
        }
#试卷未审核列表
@api_blueprint.route('/paper/confirm/wait',methods=['GET'])
@api_login_required
@permission_required('CONFIRM_PERMISSION')
def listexam():
    data = Exam.list_exams(EXAM_STATUS['未审核'])
    return {
            'code': 0,
            'data': data
    }

#试卷审核 读取
@api_blueprint.route('/paper/confirm/review/<int:id>', methods=['GET'])
@api_login_required
@permission_required('CONFIRM_PERMISSION')
def review_exam(id):
    data = Exam.get_exam(id)
    #审核倒计时 30分钟 （秒）
    data['countdown'] = 1800
    #更新审核
    exam = Exam.query.get(int(id))
    examReviewLog = ExamReviewLog.query.filter(ExamReviewLog.exam_id == exam.id, ExamReviewLog.review_state == EXAM_STATUS['正在审核'] ).order_by(ExamReviewLog.created_at.desc())
    examReviewLog = examReviewLog.all()

    #正在审核状态
    if exam.state == EXAM_STATUS['正在审核']:
        #并且不为本人操作
        if len(examReviewLog) > 0:
            if examReviewLog[0].reviewer_id != g.user.id:
                raise JsonOutputException('任务已被领取')
            else:
                data['countdown'] = 1800 - (datetime.datetime.now() - examReviewLog[0].review_date).seconds;

    if exam.state == EXAM_STATUS['已审核']: #试卷已审核通过
        raise JsonOutputException('该试卷已经通过审核，不能重复审核')

    if len(examReviewLog) == 0:
        exam.state = EXAM_STATUS['正在审核']
        exam.review_date = datetime.datetime.now()
        exam.save()

        examReview = ExamReviewLog(exam_id = exam.id, reviewer_id = g.user.id, review_state = EXAM_STATUS['正在审核'],review_memo='')
        examReview.save()

    return {
            'code': 0,
            'data': data
    }

#试卷审核 提交、写入
@api_blueprint.route('/paper/confirm/review/<int:id>', methods=['PUT'])
@api_login_required
@permission_required('CONFIRM_PERMISSION')
def review_exam_update(id):
    data = MultiDict(mapping=request.json)

    #查询是否已审核
    exam = Exam.query.get(i)
    if data['state'] is None or data['state']=='':
        raise JsonOutputException('缺少审核结果,审核失败')
    examReviewLog = ExamReviewLog.query.filter(ExamReviewLog.reviewer_id == g.user.id, ExamReviewLog.exam_id == id,\
                                               ExamReviewLog.review_state == EXAM_STATUS['正在审核']).all()
    if len(examReviewLog) == 0:
        raise JsonOutputException('已审核过，不能重复审核')
    if (datetime.datetime.now() - examReviewLog[0].review_date).seconds > 1800:
        raise JsonOutputException('超过审核时间')

    examReviewLog = examReviewLog[0]
    examReviewLog.review_date = datetime.datetime.now()
    examReviewLog.review_memo = data['memo']
    examReviewLog.reviewer_id = g.user.id
    examReviewLog.review_state = data['state']
    examReviewLog.save()

    exam = Exam.query.get(int(id))
    exam.state = data['state']
    exam.review_date = datetime.datetime.now()
    exam.save()

    return {
        'code': 0,
        'data': ''
    }

#登录用户审核记录
@api_blueprint.route('/examreview/list', methods=['GET'])
@api_login_required
@permission_required('CONFIRM_PERMISSION')
def list_examreview_log():
    return render_api(ExamReviewLog.list_log(g.user.id))

#获取用户个人信息
@api_blueprint.route('/user/info', methods=['GET'])
@api_login_required
def user_info():
    data = g.user.to_dict()
    data = School.bind_auto(data, 'name')
    data = Region.bind_auto(data, 'name', 'city_id', 'id', 'city')
    data = Region.bind_auto(data, 'name', 'province_id', 'id', 'province')
    data = Region.bind_auto(data, 'name', 'area_id', 'id', 'area')
    return render_api(data)

#更新用户信息
@api_blueprint.route('/user/info', methods=['PUT'])
@api_login_required
def user_info_update():
    password = request.json.get('password')
    repassword = request.json.get('rePassword')
    valid_code = request.json.get('validCode')
    phone = request.json.get('phone')
    email = request.json.get('email')
    province_id = request.json.get('province_id', 0)
    city_id = request.json.get('city_id', 0)
    area_id = request.json.get('area_id', 0)
    school_id = request.json.get('school_id', 0)
    grade_id = request.json.get('grade_id', 0)

    user = User.query.filter_by(phone=phone).first()
    if user is not None and user.id != g.user.id:
        raise JsonOutputException('该手机号已被使用')
    if not valid_code:
        raise JsonOutputException('请输入验证码')
    sms = SmsServer()
    # 验证码验证
    if not sms.check_code(valid_code, phone):
        raise JsonOutputException('验证码错误')
    if password:
        if password != repassword:
            raise JsonOutputException('两次输入密码不一致')
        g.user.password = password
    g.user.phone = phone
    g.user.email = email
    g.user.province_id = province_id
    g.user.city_id = city_id
    g.user.area_id = area_id
    g.user.school_id = school_id
    g.user.grade_id = grade_id
    g.user.save()
    return render_api({})

# 积分记录
@api_blueprint.route('/user/score')
@api_login_required
def user_score():
    data = pagination(g.user.scores)
    return render_api(data)
    
# 消息记录
@api_blueprint.route('/user/message')
@api_login_required
def user_message():
    data = pagination(g.user.messages)
    message_ids = [str(item['id']) for item in data['items']]
    Message.set_is_read(message_ids)
    return render_api(data)



#试卷待处理列表
@api_blueprint.route('/paper/deal/wait',methods=['GET'])
@api_login_required
def list_deal_wait():
    data = Exam.list_exams(EXAM_STATUS['已审核'])
    return {
            'code': 0,
            'data': data
    }


@api_blueprint.route('/paper/preprocess/list',methods=['GET'])
def list_exam_file_pre_process():
    data = Exam.list_exams(EXAM_STATUS['审核结束'])
    return {
        'code': 0,
        'data': data
    }

@api_blueprint.route('/paper/preprocess/view/<int:id>',methods=['GET'])
def view_exam_file_pre_process(id):
    exam = Exam.get_exam(id)
    examReviewLog = ExamReviewLog.query.filter(ExamReviewLog.reviewer_id == g.user.id, ExamReviewLog.exam_id == id, \
                                               ExamReviewLog.review_state == EXAM_STATUS['预处理']).all()
    if len(examReviewLog) == 0:
        raise JsonOutputException('已处理过')

    examReviewLog = examReviewLog[0]
    examReviewLog.review_date = datetime.datetime.now()
    examReviewLog.review_memo = EXAM_STATUS['预处理']
    examReviewLog.reviewer_id = g.user.id
    examReviewLog.review_state = EXAM_STATUS['预处理']
    examReviewLog.save()

    exam = Exam.query.get(int(id))
    exam.state = EXAM_STATUS['预处理']
    exam.review_date = datetime.datetime.now()
    exam.save()

    data = Exam.get_exam(id)
    
    return {
        'code': 0,
        'data': data
    }


#预处理结束生成图片,题目图片列表
@api_blueprint.route('/paper/image/list', methods=['GET'])
def list_quest_image():
    data = QuestImage.list_image(QUEST_IMAGE_STATUS['未处理'])
    return {
        'code': 0,
        'data': data
    }



#查看图片
@api_blueprint.route('/paper/image/view/<int:id>', methods=['GET'])
def view_quest_image(id):

    data = QuestImage.view_quest_image_detail(id)
    return {
        'code': 0,
        'data': data
    }

#
#def add_quest_image():
#    quest_no = request.json.get('quset_no')

