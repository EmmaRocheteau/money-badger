from datetime import timedelta as td
from itertools import combinations

import numpy as np
import pandas as pd
from flask import session, redirect, flash, request, url_for, render_template, jsonify
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder import ModelView, BaseView, expose, has_access

import parsing_splitwise as sp
import parsing_starling as st
from app import appbuilder, db
from flask_login import current_user
from flask_oauth import OAuth
import requests
from splitwise import Splitwise
import config as Config
from data_classes import *
from merchants import *

import json
from app import app

from app.graphs import line_balance
from bokeh.embed import components

oauth = OAuth()
splitwise = oauth.remote_app('splitwise',
base_url='https://secure.splitwise.com/api/v3.0/',
request_token_url='https://secure.splitwise.com/oauth/request_token',
access_token_url='https://secure.splitwise.com/oauth/access_token',
authorize_url='https://secure.splitwise.com/oauth/authorize',
consumer_key='QhKCiloQAS3UKPQm9yrI59WGfIsJcv2VO0llHsmX',
consumer_secret='yPIQ0El2AwF8kg4RjdPjZIBKHRHTKBviycTqyHOh')


def get_merchants(file_name):
    json1_file = open(file_name)
    json1_str = json1_file.read()
    data = json.loads(json1_str)

    merchants = []
    for transaction in data['_embedded']['transactions']:
        amount = -transaction['amount']
        if 'merchantLocation' in transaction['_links']:
            getreq = str(transaction['_links']['merchantLocation']['href'])
            merchant_loc = str(getreq.split('/')[-1])
            merchant = str(getreq.split('/')[-3])
            merchant_data = get_starling(
                "idBjil3J7CS0ZCa1wqSN4vReAiM3oq2Sl0iaE6MY1MN9Bj0B0skZBxdd3X7vMRKY",
                'merchants/{}/locations/{}'.format(merchant, merchant_loc))
            merchants.append([merchant_data['merchantName'], merchant_data[
                'locationName'], merchant_data['googlePlaceId'], amount])
    merchants = pd.DataFrame(merchants, columns=[
        'Merchant Name', 'Location Name', 'Place ID', 'Cost']).groupby(
        ['Merchant Name', 'Location Name', 'Place ID'])['Cost'].agg('sum')
    merchants = merchants.to_frame(name='Cost').reset_index()

    ms = []
    for index, row in merchants.iterrows():
        ms.append(Merchant(row['Merchant Name'], row['Location Name'],
                           row['Place ID'], row['Cost']))

    return ms


def get_sample_data():

    # Get data from starling and format to a pandas dataframe.
    #stdata = st.json_read('data/sample-starling-data.txt')
    stdata = get_starling(
        "idBjil3J7CS0ZCa1wqSN4vReAiM3oq2Sl0iaE6MY1MN9Bj0B0skZBxdd3X7vMRKY",
        'transactions/')
    cleaned = st.cleanup(stdata)

    # Get data from spltwise and format to a pandas dataframe.
    spdata = sp.yaml_read('./data/expenses.yaml')
    #spdata = session['expenses']
    mine = sp.get_owed(spdata, user_id=5090950)
    df = sp.cleanup(mine, user_id=5090950)

    # For now, isolate to GBP.
    df = df[df['Currency'] == 'GBP']
    df2 = sp.date_filter(df, date_from='01/01/2017', to='26/12/2017')

    df3 = df2.rename(index=str, columns={"Paid": "Cost"})

    def compare_and_merge(df1, df2):
        df1['Category'] = np.nan
        df1['Group ID'] = np.nan
        df1['Payment'] = False
        df1['Owe'] = df1['Cost']
        df1['Source'] = 'Starling'
        df2['Source'] = 'Splitwise'
        combined = pd.concat([df1, df2])
        sorted = combined.sort_values('Date')
        """unique_costs = np.unique(pd.to_numeric(sorted['Cost']))
        rows_to_delete = []
        rows_to_both = []
        for cost in unique_costs:
            repeats = np.where(sorted['Cost'] == cost)[0]
            if len(repeats) >= 2:
                for pair in list(combinations(repeats, 2)):
                    if sorted.loc[pair[0], 3] - td(days=5) <= sorted.iloc[
                        pair[1], 3] <= sorted.iloc[pair[0], 3] + td(
                        days=5):
                        # repeated transaction
                        if sorted.iloc[pair[0], -1] == 'starling':
                            #sorted = sorted.drop(sorted.index[pair[0]])
                            #sorted.iloc[pair[1], -1] = 'both'
                            rows_to_delete.append(pair[0])
                            rows_to_both.append(pair[1])
                        else:
                            #sorted = sorted.drop(sorted.index[pair[1]])
                            #sorted.iloc[pair[0], -1] = 'both'
                            rows_to_delete.append(pair[1])
                            rows_to_both.append(pair[0])
        sorted.iloc[rows_to_both, -1] = 'both'
        rows_to_delete.sort(reverse=True)
        sorted = np.delete(np.array(sorted), rows_to_delete, 0)"""
        return pd.DataFrame(sorted, columns=['Category', 'Cost', 'Currency',
                                             'Date', 'Description',
                                             'Group ID', 'Owe', 'Payment',
                                             'Source'])
    return compare_and_merge(cleaned, df3)


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
    return render2('404.html'), 404

def render2(html, **kwargs):
    return render_template(html, base_template=appbuilder.base_template, appbuilder=appbuilder, **kwargs)

class Starling(BaseView):
    route_base = '/starling'

    @expose('/login/')
    #@has_access
    def login(self):
        return redirect('/starling/auth')
        #return self.render_template('output.html',
         #                   getresp = str(expenses_list))
    @expose('/auth/')
    #@has_access
    #@splitwise.authorized_handler
    def authed(self):
        access_token = "idBjil3J7CS0ZCa1wqSN4vReAiM3oq2Sl0iaE6MY1MN9Bj0B0skZBxdd3X7vMRKY"
        session['starling_access_token'] = access_token
        #getreq = 'transactions/mastercard'

        # with open('card_transactions.json', 'w') as f:
        #     json.dump(data, f)
        # print("\n\n\n\n\n\n")
        # print(url)
        #print(data)
        #print(get_starling(access_token, 'transactions/mastercard/', transactionUid='bc5e394-1829-4368-ac59-9b6b6b2d9892'))
        return redirect('/home/login')

    @expose('/hint')
    def starling(self):
        return render2('welcome.html', top_text="Now log in to your banking Provider",
                               auth="Starling Bank", redirect="/starling/login", img="starling")


def get_starling(access_token, getreq, **kwargs):
    
    url = "https://api-sandbox.starlingbank.com/api/v1/"+getreq
    return requests.get(url, headers={'Authorization': 'Bearer ' +
                                                       access_token}, data=kwargs).json()


# def get_splitwise(access_token, url, **kwargs):
#     options = kwargs
#     sObj = Splitwise(Config.consumer_key,Config.consumer_secret)
#     sObj.setAccessToken(access_token)
#     # url += sObj.__prepareOptionsUrl(options)
#     content = sObj.__makeRequest(url)
#     return json.loads(content.decode("utf-8"))


class Welcome(BaseView):
    route_base = '/welcome'
    default_view = '/'

    @expose('/')
    def welcome(self):
        return render2('welcome.html', top_text="Get started by logging in to Splitwise",
                               auth="Splitwise", redirect="/splitwise/login", img="splitwise")


@splitwise.tokengetter
def get_splitwise_token(token=None):
    return session['splitwise_token']

# class Splitwise(BaseView):
#     route_base = '/splitwise'

    

def friendsload(js):
    js = js['friends']
    out = []
    for fr in js:
        if len(fr['balance'])>0:
            for ba in fr['balance']:
                if ba['currency_code'] == 'GBP' and float(ba['amount']) <0:
                    # print(fr['first_name'], fr['last_name'])
                    out.append(Debtor(fr['first_name'], -float(ba['amount'])))
    
    return out

class Home(BaseView):
    route_base = '/home'
    default_view = '/home'
    @expose('/login')
    def login(self):
        sw_auth = 'access_token' in session
        sl_auth = 'starling_access_token' in session
        return render2("login.html", splitwise_auth=sw_auth, starling_auth = sl_auth)
                               #base_template=appbuilder.base_template, appbuilder=appbuilder)

    @expose('/settle')
    def settle(self):
        sObj = Splitwise(Config.consumer_key,Config.consumer_secret)
        sObj.setAccessToken(session['access_token'])
        content = sObj.getExpenses()
        session['expenses'] = content

        friends = sObj.getFriends()
        self.debtors = friendsload(friends)
        
        d = []
        d.append(Debtor("Hugh Mungus", 69.0))
        d.append(Debtor("Gareth Funk", 100000))
        d.append(Debtor("The Queen", 1000000000.01))
        return render2("settle.html", debtors=self.debtors)

    @expose('/remove_debtor')
    def remove_debtor(self):
        print("remove_debtor called")
        nm = request.args.get('nm', "", type=str)
        print(nm)
        for i, debtor in enumerate(self.debtors):
            if debtor.name == nm:
                print("Posting amount", debtor.amount)

                tmps = {"payment": {"currency": "GBP", "amount": debtor.amount},  "destinationAccountUid": "7f03a23a-bafc-4479-8d4d-abb6a9119d27",  "reference": "Splitwise"}
                url = "https://api-sandbox.starlingbank.com/api/v1/payments/local/"
                access_token = session['starling_access_token']
                resp = requests.post(url, headers={'Authorization': 'Bearer ' +
                                                       access_token}, data={'body': json.dumps(tmps)})
                del(self.debtors[i])
                print("Deleting debtor " + str(i) + " called " + debtor.name)
                break
        return jsonify(False)

    @expose('/map')
    def map(self):
        ids = get_merchants('card_transactions.json')
        return render2("test_map2.html", ids=ids)

    @expose('/home')
    def root(self):
        if 'calculated_records' not in session:
            df = get_sample_data()
            self.r = create_records(df)
            session['calculated_records'] = True
        return render2("root.html", records=self.r)
    
    @expose('/balance')
    def balance(self):
        chart = line_balance("data")
        script, div = components(chart)
        return render2("graphs.html", script=script, div=div)

    @expose('/splitwise/login/')
    #@has_access
    def splogin(self):
        # do something with param1
        # and render template with param
        sObj = Splitwise(Config.consumer_key,Config.consumer_secret)
        url, secret = sObj.getAuthorizeURL()
        session['secret'] = secret
        #url ='/splitwise/auth'
        return redirect(url)

    @expose('/splitwise/auth/')
    #@has_access
    #@splitwise.authorized_handler
    def spauthed(self):
        if 'secret' not in session:
            return redirect('/home/login')

        oauth_token    = request.args.get('oauth_token')
        oauth_verifier = request.args.get('oauth_verifier')

        sObj = Splitwise(Config.consumer_key,Config.consumer_secret)
        access_token = sObj.getAccessToken(oauth_token,session['secret'],oauth_verifier)
        session['access_token'] = access_token

        return redirect('/home/login')

    @expose('/splitwise/expenses')
    def get_expenses(self):
        sObj = Splitwise(Config.consumer_key,Config.consumer_secret)
        sObj.setAccessToken(session['access_token'])
        content = sObj.getExpenses()
        session['expenses'] = content

        friends = sObj.getFriends()
        self.debtors = friendsload(friends)
        #print(friendsload(friends))
        #print("\n\n\n\n\n\n" , content)
        #resp = splitwise.get('get_current_user')
        return render2('output.html', getresp="waddup")

# class Root(BaseView):


# appbuilder.add_view_no_menu(Splitwise())
appbuilder.add_view_no_menu(Starling())
appbuilder.add_view_no_menu(Home())

#appbuilder.add_view(Welcome, "Welcome", category='Charts')
# appbuilder.add_view(Home, "/home/home")
appbuilder.add_link("Settle", "/home/settle", label="Settle")
appbuilder.add_link("Analytics", "/home/balance", label="Analytics")
appbuilder.add_link("Transactions", "/home/home", label="Transactions")
# appbuilder.add_view_no_menu(Welcome())
# appbuilder.add_link("Splitwise", href='/splitwise_login/', category='Login')
# appbuilder.add_view(Home, '/balance', category="Analytics")
  
db.create_all()
