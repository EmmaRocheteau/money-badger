from flask import Flask, render_template, request
from machine_learning import make_dataframes as d
from bokeh.charts import TimeSeries
from datetime import datetime
from bokeh.embed import components
import numpy as np
from get_balance import get_balance


def line_balance(data):
    #dat = get_balance("../sample_data.csv")
    dat = d.dataframer()
    data = dict(balance_x=dat['Balance_x'], balance_y=dat['Balance_y'],
                Date=dat['Date'])
    ser = TimeSeries(data, x='Date', ylabel='Balance/£', legend=None,
                     width=1000)
    #line = Line(xyvalues, title="line", legend="top_left", ylabel='Languages')
    return ser

#line_balance('')
