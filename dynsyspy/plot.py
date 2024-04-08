import plotly.express as px
import plotly.graph_objects as go
from dynsyspy.system import Stock, Module, System
from dynsyspy.problem import Problem


"""


def plot_phase_space(self, syms, w=500, h=500):
    fig = go.Figure()
    fig.update_layout(
        #title="{} Stock".format(sym),
        width=w, height=h,
    )

    fig.add_trace(go.Scatter(x=self.results[syms[0]], y=self.results[syms[1]],
                                    mode='lines'))
    fig.show()
    print("")

def plot_all(self, w=None, h=None):
    for sym in self.system._stock_syms:
        self.plot(sym.name, w=None, h=None)


def _plot(results, stocks, w=None, h=None):
    fig = go.Figure()
    fig.update_layout(
        title="{} Stock".format(sym),
        width=w, height=h,
    )

    fig.add_trace(go.Scatter(x=self.t_span, y=self.results[sym],
                                mode='lines'))
    return fig

def one(problem: Problem, stock: Stock):
    _plot(problem.results, [stock])
"""

def _plot_many(res, syms, title="", w=None, h=None):
    fig = go.Figure()
    fig.update_layout(
        title=title,
        width=w, height=h,
    )

    for sym in syms:
        fig.add_trace(go.Scatter(x=res.Time, y=res[sym],
                                    mode='lines',
                                    name=sym))
        
    fig.show()
    print("")


def all_stocks(problem: Problem):
    for m in problem.system.modules:
        for s in m.stocks:
            _plot_many(problem.results, [s.name], title=s.name + " (" + s.description + ")" )
            print("")

def many(problem: Problem, items):
    _plot_many(problem.results, items, title=problem.system.name)
