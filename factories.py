#coding:utf-8
class Jinja2:
    @staticmethod
    def init_app(app):
        app.jinja_env.variable_start_string = "{$="
        app.jinja_env.variable_end_string = "}"