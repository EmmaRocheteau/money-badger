from flask_appbuilder import IndexView, expose, BaseView
from flask import redirect


class MyIndexView(IndexView):
    index_template = 'my_index.html'
    @expose('/')
    def root(self):
    
        return redirect('/home/login')