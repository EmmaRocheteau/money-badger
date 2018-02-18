from flask import Flask, render_template, request

from bokeh.charts import Line
from bokeh.embed import components
import numpy as np
def line_balance(data):
    xyvalues = np.array([[2, 3, 7, 5, 26], [12, 33, 47, 15, 126], [22, 43, 10, 25, 26]])

    line = Line(xyvalues, title="line", legend="top_left", ylabel='Languages')

    return line
