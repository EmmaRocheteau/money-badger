from flask import Flask, render_template, request

from bokeh.charts import TimeSeries
from bokeh.embed import components
import numpy as np
from get_balance import get_balance
def line_balance(data):
    dat = get_balance("../sample_data.csv")
    data = dict(dat=dat['Cost'], Date=dat['index'])
    ser = TimeSeries(data, x='Date', ylabel='Balance/£', dash=['dat'], legend=None)
    #line = Line(xyvalues, title="line", legend="top_left", ylabel='Languages')

    return ser
