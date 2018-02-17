from flask import render_template
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder import ModelView, BaseView, expose, has_access
from app import appbuilder, db
from flask import render_template
from flask_login import current_user
from flask_oauth import OAuth

oauth = OAuth()
splitwise = oauth.remote_app('splitwise',
base_url='https://secure.splitwise.com/api/v3.0/',
request_token_url='https://secure.splitwise.com/oauth/request_token',
access_token_url='https://secure.splitwise.com/oauth/access_token',
authorize_url='https://secure.splitwise.com/oauth/authorize',
consumer_key='QhKCiloQAS3UKPQm9yrI59WGfIsJcv2VO0llHsmX',
consumer_secret='yPIQ0El2AwF8kg4RjdPjZIBKHRHTKBviycTqyHOh')
from flask import session, redirect, flash, request, url_for
from app import app


@splitwise.tokengetter
def get_splitwise_token(token=None):
    return session.get('oauth_token')

"""
    Create your Views::


    class MyModelView(ModelView):
        datamodel = SQLAInterface(MyModel)


    Next, register your Views::


    appbuilder.add_view(MyModelView, "My View", icon="fa-folder-open-o", category="My Category", category_icon='fa-envelope')
"""

"""
    Application wide 404 error handler
"""

@appbuilder.sm.oauth_user_info_getter
def my_user_info_getter(sm, provider, response=None):
    if provider == 'splitwise':
        me = sm.oauth_remotes[provider].get('get_current_user').data['user']
        return {'username': str(me['id']),
                'first_name': me['first_name'],
                'last_name': me['last_name'],
                'email': me['email']}
    else:
        return {}


@appbuilder.app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', base_template=appbuilder.base_template, appbuilder=appbuilder), 404



@app.route('/split_login')
def login():
    return splitwise.authorize(callback=url_for('auth', next=request.args.get('next') or request.referrer or None))

@app.route('/auth')

def auth(resp):
    next_url = request.args.get('next') or url_for('index')
    if resp is None:
        flash(u'You denied the request to sign in.')
        return redirect(next_url)

    session['splitwise_token'] = (
        resp['oauth_token'],
        resp['oauth_token_secret']
    )
    session['splitwise_user'] = resp['first_name']

    flash('You were signed in as %s' % resp['first_name'])
    return redirect(next_url)

class Splitwise(BaseView):
    route_base = '/splitwise'

    @expose('/login/')
    #@has_access
    def auth(self):
        # do something with param1
        # and render template with param

        return splitwise.authorize(callback='/splitwise/auth')
        #return self.render_template('output.html',
         #                   getresp = str(expenses_list))
    @expose('/auth/')
    #@has_access
    @splitwise.authorized_handler
    def authed(self, resp):
        next_url = request.args.get('next') or url_for('index')
        if resp is None:
            flash(u'You denied the request to sign in.')
            return redirect(next_url)

        session['splitwise_token'] = (
            resp['oauth_token'],
            resp['oauth_token_secret']
        )
        session['splitwise_user'] = resp['first_name']

        flash('You were signed in as %s' % resp['first_name'])
        return redirect(next_url)

    @expose('/welcome')
    def welcome(self):
        return render_template('welcome.html', top_text="Get started by logging in to Splitwise",
                               auth="Splitwise", redirect="/splitwise/login", img="splitwise",
                               base_template=appbuilder.base_template, appbuilder=appbuilder)

    @expose('/starling')
    def starling(self):
        return render_template('welcome.html', top_text="Now log in to your banking Provider",
                               auth="Starling Bank", redirect="/starling/login", img="starling",
                               base_template=appbuilder.base_template, appbuilder=appbuilder)


class Starling(BaseView):
    route_base = '/starling'

appbuilder.add_view_no_menu(Splitwise())
appbuilder.add_view_no_menu(Starling())
#appbuilder.add_link("Splitwise", href='/splitwise_login/', category='Login')
  
db.create_all()


