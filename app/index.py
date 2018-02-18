from flask_appbuilder import IndexView, expose, BaseView
from flask import redirect, render_template
from flask_login import current_user

class MyIndexView(BaseView):
    route_base = ''
    index_template = 'my_index.html'
    default_view = 'index'
    @expose('/')
    def index(self):
        if current_user.is_authenticated():
            return redirect('/home/login')
        else:
            return render_template(self.index_template, appbuilder=self.appbuilder, base_template=self.appbuilder.base_template)