import pandas as pd
from datetime import datetime, timedelta
import numpy as np
import operator
import matplotlib
import matplotlib.colors as col
import matplotlib.cm as cm
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt

#class plotter:
# dataSeries (2-dimensional np.ndarray), figSize (tuple, length=2) -> fig
# each row of dataSeries is one data type.
# Other details should be implemented in inheritor
# NOTE: This is a subset of plot_multiple_stacked_bars


def save_fig(self, fig, name):
	pp = PdfPages(self.figdir+name+'.pdf')
	pp.savefig(fig, bbox_inches='tight')
	pp.close()


def plot_multiple_simple_bars_deprecated(self, dataSeries, figSizeIn, xlabel, ylabel):
	fig = plt.figure(figsize = figSizeIn)
	barNum = len(dataSeries)
	totalBlockWidth = 0.5
	oneBlockWidth = float(0.5/float(barNum))

	x = np.arange(0,len(dataSeries[0]))
	for idx, data in enumerate(dataSeries):
		plt.bar(x-totalBlockWidth/2.0 + oneBlockWidth*idx + oneBlockWidth/2.0, data, width = oneBlockWidth, align='center')
	plt.show()
	return fig

# dataSeries (2-dimensional np.ndarray), figSize (tuple, length=2) -> fig
# stackNum starts from 0, which means no stack but just a bar.
# each row of dataSeries is one data type.
# number of stackNum indicates the dats to be stacked.
# e.g., if length of dataSeries is 6, and stack Num is 2,
# dataSeries[0] and dataSereis[1] should be stacked on same bar
# dataSeries[1] and dataSereis[2] should be stacked on same bar
# dataSeries[3] and dataSereis[4] should be stacked on same bar
# Other details should be implemented in inheritor
def plot_multiple_stacked_bars(self, dataSeries, figSizeIn, xlabel, ylabel, stackNum):
	fig = plt.figure(figsize=figSizeIn)
	barNum = len(dataSeries)/(stackNum+1)
	totalBlockWidth = 0.5
	oneBlockWidth = float(0.5/float(barNum))
	x = np.arange(0,len(dataSeries[0]))
	for barIdx in range(0,barNum):
		xpos = x-totalBlockWidth/2.0 + oneBlockWidth*idx + oneBlockWidth/2.0
		plt.bar(xpos, dataSeries[barIdx*stackNum], width = oneBlockWidth, align='center')
		offset = dataSeries[barIdx]
		for stackIdx in range(1,stackNum):
			plt.bar(xpos, dataSeries[barIdx*stackNum+stackIdx], width=oneBlockWidth, bottom=offset, align='center')
			offset += dataSeries[barIdx*stackNum+stackIdx]
	plt.show()
	return fig

def plot_up_down_bars(self, upData, downData, figsizeIn, xlabel, ylabel):
	fig = plt.figure(figsize = figSizeIn)
	barNum = len(upData)
	if barNum != len(downData):
		print "data lengh mismatch"
		return None
	blockWidth = 0.5
	x = np.arange(0,barNum)
	plt.bar(x,upData)
	plt.bar(x,downData,top=0)
	plt.ylabel(ylabel, labelpad=-2)
	plt.xlabel(xlabel, labelpad=-2)
	plt.tight_layout()
	plt.show()
	return fig

def plot_colormap(self, data, figSizeIn, xlabel, ylabel, cbarlabel, cmapIn):
	fig = plt.figure(figsize = figsizeIn)
	plt.pcolor(data, cmap=cmapIn)
	cbar = plt.colorbar()
	cbar.set_label(cbarlabel, labelpad=-0.1)
	plt.xlabel(xlabel)
	plt.ylabel(ylabel)
	plt.tight_layout()
	plt.show()
	return fig

# x (list of np.array(datetime)), y (list of np.array(number)) -> fig 
def plot_multiple_timeseries(self, xs, ys, xlabel, ylabel):
	dataNum = len(data)
	fig, axes = plt.subplots(dataNum)
	for i, axis in enumerate(axes):
		axis.plot_date(xs[i], ys[i], linestyle='0', marker='None')
		plt.xlabel(xlabel)
		plt.ylabel(ylabel)
	plt.show()
	return fig, axes


