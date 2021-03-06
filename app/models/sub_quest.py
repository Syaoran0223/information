import json
from app import db
from ._base import SessionMixin

class SubQuestion(db.Model, SessionMixin):
    __tablename__ = 'sub_quest'

    def __init__(self, *args, **kwargs):
        SubQuestion.register()
        super(SubQuestion, self).__init__(*args, **kwargs)

    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer)
    quest_content = db.Column(db.Text)
    quest_content_html = db.Column(db.Text)

    quest_option_html = db.Column(db.Text)
    zhuanti = db.Column(db.String(255))
    kaodian = db.Column(db.Text)
    fenxi = db.Column(db.Text)
    jieda = db.Column(db.Text)
    dianpin = db.Column(db.Text)
    correct_answer = db.Column(db.Text)
    quest_no = db.Column(db.Integer)
    qtype = db.Column(db.String(200))
    qtype_id = db.Column(db.Integer)
    option_count = db.Column(db.Integer, default=0)
    qrows = db.Column(db.Integer, default=0)
    qcols = db.Column(db.Integer, default=0)
    qoptjson = db.Column(db.Text)
    operator_id = db.Column(db.Integer)
    group = db.Column(db.Integer, default=1) # 1-首次提交的答案 2-第二次提交的答案
    finish_state = db.Column(db.String(16), default='')

    def __repr__(self):
        return '<SubQuestion: %r>' % self.id

    def to_dict(self):
        res = super(SubQuestion, self).to_dict()
        if self.qtype_id == 1:
            res['options'] = json.loads(self.qoptjson)
        if self.qtype_id == 2:
            res['answer_list'] = json.loads(self.correct_answer)
        return res
