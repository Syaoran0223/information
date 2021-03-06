from app.exceptions import JsonOutputException
from app.decorators import api_login_required, permission_required
from app.models import Exam, Question, QuestLog, ExamLog, School, Preprocess, Region
from app.utils import pagination
from flask import request, g
from app.const import EXAM_STATUS, QUEST_STATUS
from . import api_blueprint
from app.utils import render_api
from app import db


#试卷待处理列表
@api_blueprint.route('/paper/deal/wait',methods=['GET'])
@api_login_required
@permission_required('DEAL_PERMISSION')
def list_deal_wait():
    data = Exam.list_exams(EXAM_STATUS['已采纳'])
    return render_api(data)

#进行处理
@api_blueprint.route('/paper/preprocess/view/<int:id>', methods=['GET'])
@api_login_required
@permission_required('DEAL_PERMISSION')
def view_exam_file_pre_process(id):
    exam = Exam.query.get(int(id))
    if not exam:
        raise JsonOutputException('试卷不存在')
    if not exam.state in (EXAM_STATUS['已采纳'], EXAM_STATUS['预处理']):
        raise JsonOutputException('试卷状态错误')
    process_data = Preprocess.query.\
        filter_by(exam_id=id, state=EXAM_STATUS['预处理']).\
        order_by(Preprocess.created_at.desc()).\
        first()
    if process_data and not process_data.operator_id == g.user.id:
        raise JsonOutputException('任务已被领取')
    if not process_data:
        process_data = Preprocess(exam_id=id,
            operator_id=g.user.id, state=EXAM_STATUS['预处理'],
            memo='')
        process_data.save()
        ExamLog.log(exam.id, g.user.id, EXAM_STATUS['预处理'], 'DEAL')
    exam.state = EXAM_STATUS['预处理']
    exam.save()
    data = exam.get_dtl()
    questList = Question.query.\
        filter_by(exam_id=exam.id).\
        filter(Question.state != QUEST_STATUS['已删除']).\
        all()
    data['quest_list'] = [item.to_dict() for item in questList]
    return render_api(data)

# 录入试卷结构
@api_blueprint.route('/paper/preprocess/struct/<int:id>', methods=['PUT'])
@api_login_required
@permission_required('DEAL_PERMISSION')
def add_struct(id):
    exam = Exam.query.get(int(id))
    if not exam:
        raise JsonOutputException('试卷不存在')
    if not exam.state==EXAM_STATUS['预处理']:
        raise JsonOutputException('试卷状态错误')
    process_data = Preprocess.query.\
        filter_by(exam_id=id, state=EXAM_STATUS['预处理']).\
        order_by(Preprocess.created_at.desc()).\
        first()
    if not process_data:
        raise JsonOutputException('无法处理')
    if not process_data.operator_id == g.user.id:
        raise JsonOutputException('该试卷已经被他人领取')
    struct = request.json.get('struct', [])
    attachments = request.json.get('attachments', [])
    is_word = request.json.get('is_word', False)
    if not struct:
        raise JsonOutputException('请输入试卷结构')
    exam.struct = struct
    # word文档直接生成题目
    if is_word:
        for tip in struct:
            quest_image = attachments
            for i in range(int(tip['start_no']), int(tip['end_no']) + 1):
                quest = Question(exam_id=id, quest_no=i,
                    quest_image=quest_image,
                    state=QUEST_STATUS['未处理'],
                    insert_user_id=g.user.id)
                db.session.add(quest)
        db.session.commit()
        process_data.state = EXAM_STATUS['预处理完成']
        process_data.save()
        exam.state = EXAM_STATUS['预处理完成']
    exam.has_struct = True
    exam.save()
    return render_api({})

#添加上题目图片
@api_blueprint.route('/paper/preprocess/view',methods=['POST'])
@api_login_required
@permission_required('DEAL_PERMISSION')
def add_pre_review_quest_image():
    quest_no = request.json.get('quest_no')
    exam_id = request.json.get('exam_id')
    quest_type_id = request.json.get('quest_type_id')
    option_count = request.json.get('option_count')
    quest_image = request.json.get('quest_image')
    review_memo = request.json.get('review_memo')
    answer_image = request.json.get('answer_image')
    has_sub = 0
    if quest_type_id == '3':
        has_sub = 1

    #添加题目数据
    res = Question.add_pre_process_quest(exam_id, quest_no,
        has_sub, quest_type_id, option_count, quest_image,
        g.user.id, review_memo, answer_image)
    #添加题目上传日志
    quest_log = QuestLog(exam_id=exam_id, quest_no=quest_no, refer_user_id=g.user.id, log_state=QUEST_STATUS['未处理'],
                         log_type='ADD')
    quest_log.save()
    return render_api(res)

#修改题目
@api_blueprint.route('/paper/preprocess/view',methods=['PUT'])
@api_login_required
@permission_required('DEAL_PERMISSION')
def update_question():
    id = request.json.get('id')
    quest_type_id = request.json.get('quest_type_id')
    quest_image = request.json.get('quest_image')
    answer_image = request.json.get('answer_image')
    quest_no= request.json.get('quest_no')
    option_count = request.json.get('option_count')
    
    quest = Question.query.get(id)
    if quest is None:
        raise JsonOutputException('未找到题目')
    #非未处数据不能进行修改
    if quest.state != QUEST_STATUS['未处理']:
        raise JsonOutputException('该题不能修改')
    elif quest.insert_user_id != g.user.id: #非本人操作无法修改
        raise JsonOutputException("您无权修改该题目")

    if quest_type_id is not None:
        quest.quest_type_id = quest_type_id
    if quest_image is not None:
        quest.quest_image = quest_image
    if answer_image is not None:
        quest.answer_image = answer_image
    if quest_no is not None:
        quest.quest_no = quest_no
    if option_count is not None:
        quest.option_count = option_count
    if quest.quest_type_id == '3':
        quest.has_sub = 1
    quest.save()
    quest = Question.query.get(id)
    return render_api(quest.to_dict())

@api_blueprint.route('/paper/preprocess/view/<int:id>',methods=['DELETE'])
@api_login_required
@permission_required('DEAL_PERMISSION')
def del_quest(id):
    quest = Question.query.get(id)
    if quest is None:
        raise JsonOutputException('未找到该试题')
    if quest.state != QUEST_STATUS['未处理']:
        raise JsonOutputException('该题目已进入其它处理流程,不能删除')
    if quest.insert_user_id != g.user.id:
        raise JsonOutputException('您无权删除该题目')
    exam = Exam.query.get(quest.exam_id)
    if exam is None:
        raise JsonOutputException('未找到该试卷')

    quest.state = QUEST_STATUS['已删除']
    quest.save()
    return render_api('')

#查看预处理记录
@api_blueprint.route('/paper/preprocess/list', methods=['GET'])
@api_login_required
@permission_required('DEAL_PERMISSION')
def list_quest_review_log():

    query = Preprocess.query.\
        filter_by(operator_id=g.user.id).\
        order_by(Preprocess.created_at.desc()).\
        join(Exam, Exam.id==Preprocess.exam_id)
    if request.args.get('name'):
        query = query.filter(Exam.name.like('%{}%'.format(request.args.get('name'))))
    if request.args.get('subject'):
        query = query.filter(Exam.subject==request.args.get('subject'))
    if request.args.get('paper_types'):
        query = query.filter(Exam.paper_types==request.args.get('paper_types'))
    if request.args.get('province_id'):
        query = query.filter(Exam.province_id==request.args.get('province_id'))
    if request.args.get('city_id'):
        query = query.filter(Exam.city_id==request.args.get('city_id'))
    if request.args.get('area_id'):
        query = query.filter(Exam.area_id==request.args.get('area_id'))
    if request.args.get('school_id'):
        query = query.filter(Exam.school_id==request.args.get('school_id'))
    if request.args.get('year'):
        query = query.filter(Exam.year==request.args.get('year'))
    if request.args.get('grade'):
        query = query.filter(Exam.grade==request.args.get('grade'))
    res = pagination(query)
    items = res.get('items', [])
    items = Exam.bind_auto(items, ['name', 'section', 'school_id', 'subject', 'grade', 'paper_types', 'province_id', 'city_id', 'area_id'])
    items = School.bind_auto(items, 'name', 'exam_school_id', 'id', 'school')
    items = Region.bind_auto(items, 'name', 'exam_province_id', 'id', 'province')
    items = Region.bind_auto(items, 'name', 'exam_city_id', 'id', 'city')
    items = Region.bind_auto(items, 'name', 'exam_area_id', 'id', 'area')
    res['items'] = items
    return render_api(res)

# 试卷详情
@api_blueprint.route('/paper/preprocess/list/<int:id>', methods=['GET'])
@api_login_required
@permission_required('DEAL_PERMISSION')
def get_preprocess_exam(id):
    data = Exam.get_exam(id)
    if data is not None:
        return {
            'code': 0,
            'data': data
        }
    else:
        raise JsonOutputException('没有数据')

# 试卷预处理
@api_blueprint.route('/paper/preprocess/tips', methods=['POST'])
@api_login_required
@permission_required('DEAL_PERMISSION')
def exam_process():
    id = request.json.get('exam_id')
    if not id:
        raise JsonOutputException('请输入试卷id')
    exam = Exam.query.get(id)
    if not exam:
        raise JsonOutputException('试卷不存在')
    if not exam.state==EXAM_STATUS['预处理']:
        raise JsonOutputException('试卷状态错误')
    process_data = Preprocess.query.\
        filter_by(exam_id=id, state=EXAM_STATUS['预处理']).\
        order_by(Preprocess.created_at.desc()).\
        first()
    if not process_data:
        raise JsonOutputException('无法处理')
    if not process_data.operator_id == g.user.id:
        raise JsonOutputException('该试卷已经被他人领取')
    struct = request.json.get('struct', [])
    if not struct:
        raise JsonOutputException('请录入试卷结构')
    exam.struct = struct
    exam.has_struct = True
    tips = request.json.get('tips', [])
    if not tips:
        raise JsonOutputException('请输入试卷切割信息')
    for tip in tips:
        quest_image = tip.get('formData', {}).get('quest_image', [])
        answer_image = tip.get('formData', {}).get('answer_image', [])
        for i in range(int(tip['formData']['start_no']), int(tip['formData']['end_no']) + 1):
            quest = Question(exam_id=id, quest_no=i,
                quest_image=quest_image,
                answer_image=answer_image,
                state=QUEST_STATUS['未处理'],
                insert_user_id=g.user.id,
                order=exam.order)
            db.session.add(quest)
    db.session.commit()
    process_data.state = EXAM_STATUS['预处理完成']
    process_data.save()
    exam.state = EXAM_STATUS['预处理完成']
    exam.save()
    return render_api({})


#试卷预处理完成
@api_blueprint.route('/paper/preprocess/finish',methods=['POST'])
@api_login_required
@permission_required('DEAL_PERMISSION')
def finish_exam_pre_process():
    id = request.json.get("id")
    exam = Exam.query.get(id)
    review_memo = request.json.get('review_memo', '')
    user_id = g.user.id
    if not exam:
        raise JsonOutputException('未找到该试卷')
    if exam.state != EXAM_STATUS['预处理']:
        raise JsonOutputException('试卷状态错误')
    
    questions = Question.query.\
        filter_by(exam_id=exam.id).\
        filter(Question.state != QUEST_STATUS['已删除']).\
        all()
    
    if not len(questions):
        raise JsonOutputException('未录入题目，无法完成')

    preprocess_data = Preprocess.query.filter_by(exam_id=exam.id).\
        filter_by(operator_id=g.user.id).\
        filter_by(state=EXAM_STATUS['预处理']).\
        first()
    if not preprocess_data:
        raise JsonOutputException('预处理记录不存在')

    preprocess_data.state = EXAM_STATUS['预处理完成']
    preprocess_data.save()

    ExamLog.log(exam.id, g.user.id, EXAM_STATUS['预处理完成'], 'DEAL')

    exam.state = EXAM_STATUS['预处理完成']
    exam.save()
    exam = Exam.query.get(id)
    return render_api(exam.to_dict())