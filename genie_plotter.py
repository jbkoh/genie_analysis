import plotter
reload(plotter)
from localdb import localdb
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.colors as col
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
import csv
from datetime import datetime, timedelta
from collections import OrderedDict, defaultdict
import operator
import pandas as pd


class genie_plotter:

	genierawdb = None
	thermrawdb = None
	genieprocdb = None
	thermprocdb = None
	generaldb = None
	zonelist = None
	geniezonelist = None
	notgenielist = list()
	figdir = 'figs/'
	figsize = (4,2)
	

	def __init__(self):
		self.genierawdb = localdb('genieraws.shelve')
		self.thermrawdb = localdb('thermraws.shelve')
		self.genieprocdb = localdb('genieprocessed.shelve')
		self.thermprocdb = localdb('thermprocessed.shelve')
		self.generaldb = localdb('general.shelve')
		self.zonelist = self.csv2list('metadata\zonelist.csv')
		self.geniezonelist = self.csv2list('metadata\geniezonelist.csv')
		for zone in self.zonelist:
			if zone not in self.geniezonelist:
				self.notgenielist.append(zone)
	
#	def save_fig(self, fig, name):
#		pp = PdfPages(self.figdir+name+'.pdf')
#		pp.savefig(fig, bbox_inches='tight')
#		pp.close()
	
	def csv2list(self, filename):
		outputList = list()
		with open(filename, 'r') as fp:
			reader = csv.reader(fp, delimiter=',')
			for row in reader:
				outputList.append(row[0])
		return outputList
	
	def plot_setpnt_dev_assist(self, setpntDev, sortedFlag, xlabel, xtickTagIn=None, title=None, axis=None):
		avgs = dict()
		stds = dict()
		setpntCounts = dict()
		for key in setpntDev.iterkeys():
			if len(setpntDev[key])==0:
				avgs[key] = 0
				stds[key] = 0
			else:
				avgs[key] = np.mean(setpntDev[key])
				stds[key] = np.std(setpntDev[key])
			setpntCounts[key] = len(setpntDev[key])

		sortedSetpntCounts = list()
		sortedAvgs = dict(zip(setpntDev.keys(), avgs.values()))
		sortedStds = list()
		if sortedFlag:
			sortedAvgs = OrderedDict(sorted(sortedAvgs.items(), key=operator.itemgetter(1)))
		for key in sortedAvgs.iterkeys():
			sortedStds.append(stds[key])
			sortedSetpntCounts.append(setpntCounts[key])

		
		ylabel = u'Temperature Setpoint \nDifference ($^\circ$F)'
		plotData = list()
		plotData.append(np.array(sortedAvgs.values()))
		stdData = list()
		stdData.append(np.array(sortedStds))
		clist = ['skyblue']
		eclist= ['royalblue']
		#fig = plotter.plot_multiple_stacked_bars(list().append(np.array(sortedAvgs.values())), (4,2), xlabel, ylabel, 0)
		plotter.plot_multiple_stacked_bars(plotData, 0, xlabel=xlabel, ylabel=ylabel, xtickTag=xtickTagIn, title=title, stdSeries=stdData, axis=axis, clist=clist, eclist=eclist)

		return sortedSetpntCounts


	def plot_weighted_setpnt_dev_zone(self, sortIndicator):
		#title = 'Weighted Setpoint Deviation vs Zone: x axes are shared.'
		title = None
		genieData = self.genieprocdb.load('weighted_setpoint_dev_zone')
		thermData = self.thermprocdb.load('weighted_wcad_dev_zone') 

		genieAvgListGenie = list()
		genieAvgListTherm = list()
		nonGenieAvgListTherm = list()
		genieStdListGenie = list()
		genieStdListTherm = list()
		nonGenieStdListTherm = list()
		
		sortedThermDict = {key: thermData[key] for key in self.notgenielist}
		if sortIndicator=='sorted':
			sortedGenieDict = OrderedDict(sorted(genieData.items(), key=operator.itemgetter(1)))
			sortedThermDict = OrderedDict(sorted(sortedThermDict.items(), key=operator.itemgetter(1)))
		else:
			sortedGenieDict = {key: genieData[key] for key in self.geniezonelist}

		for zone in sortedGenieDict.keys():
			genieAvgListGenie.append(genieData[zone][0])
			genieStdListGenie.append(genieData[zone][1])
			genieAvgListTherm.append(thermData[zone][0])
			genieStdListTherm.append(thermData[zone][1])

		for zone, val in sortedThermDict.iteritems():
			#nonGenieAvgListTherm.append(val[0])
			#nonGenieStdListTherm.append(val[1])
			if zone in self.notgenielist:
				genieAvgListTherm.append(thermData[zone][0])
				genieStdListTherm.append(thermData[zone][1])


		#plotData = [genieAvgListTherm, genieAvgListGenie]
		#stdData = [genieStdListTherm, genieStdListGenie]
		plotData = [genieAvgListGenie]
		stdData = [genieStdListGenie]
#		legend1 = 'Thermostats setpoint deviation in zones with Genie'
		legend1 = 'Genie setpoint deviation'
		legend3 = 'Thermostats setpoint deviation in zones without Genie'
		xlabel = 'Zone'
		ylabel = u'Setpoint deviation ($^\circ$F)'

		fig, (axis1,axis2) = plt.subplots(2,1, sharex=True)
		ylim = (64.9,75.1)
		clist = ['c','y']
		linewidth=0.1
		plotter.plot_multiple_stacked_bars(plotData, 0, xlabel=xlabel, ylabel=ylabel, ylim=ylim, axis=axis1, fig=fig, dataLabels=[legend1], clist=clist, linewidth=linewidth, stdSeries=stdData, title=title)
		
		#plotData = [nonGenieAvgListTherm]
		#stdData = [nonGenieStdListTherm]
		plotData = [genieAvgListTherm]
		stdData = [genieStdListTherm]
		ylim=(-5,5)
		plotter.plot_multiple_stacked_bars(plotData, 0, xlabel=xlabel, ylabel=ylabel, ylim=ylim, axis=axis2, fig=fig, dataLabels=[legend3], linewidth=linewidth, stdSeries=stdData)
		plt.show()

		plotter.save_fig(fig, self.figdir+'stp_dev_comp.pdf')
		
		

		
	def plot_setpnt_dev(self):
		genie_setpnt_dev_zone = self.genieprocdb.load('setpoint_diff_per_zone')
		genie_setpnt_dev_hour = self.genieprocdb.load('setpoint_diff_per_hour')
		genie_setpnt_dev_month = self.genieprocdb.load('setpoint_diff_per_month')
		therm_setpnt_dev_zone = self.thermprocdb.load('wcad_diff_per_zone')
		therm_setpnt_dev_hour = self.thermprocdb.load('wcad_diff_per_hour')
		therm_setpnt_dev_month = self.thermprocdb.load('wcad_diff_per_month')

		monthTag = plotter.make_month_tag()
	
		genieBaseTitle = 'Averaged Deviation in Setpoint due to'
		#title1 = genieBaseTitle + "Genie Usage " + ' vs Zone'
		#title2 = genieBaseTitle + "Genie Usage " + ' vs Hour'
		#title3 = genieBaseTitle + "Genie Usage " + ' vs Month'
		thermBaseTitle = 'Averaged Deviation in Setpoint due to'
		#title4 = thermBaseTitle + "Thermostat Usage " + ' vs Zone'
		#title5 = thermBaseTitle + "Thermostat Usage " + ' vs Hour'
		#title6 = thermBaseTitle + "Thermostat Usage " + ' vs Month'
		title1 = None
		title2 = None
		title3 = None
		title4 = None
		title5 = None
		title6 = None


		
		figGenie, (ax1, ax2, ax3) = plt.subplots(3,1)
		figGenie.set_size_inches(6,8)
		self.plot_setpnt_dev_assist(genie_setpnt_dev_zone, True, 'Zone', title=title1, axis=ax1)
		self.plot_setpnt_dev_assist(genie_setpnt_dev_hour, False, 'Time (Hour)', title=title2, axis=ax2)
		self.plot_setpnt_dev_assist(genie_setpnt_dev_month, False, 'Time (Month)', xtickTagIn=monthTag, title=title3, axis=ax3)
		plt.subplots_adjust(hspace=0.5)
		#plt.show()

		figTherm, (ax4, ax5, ax6) = plt.subplots(3,1)
		figTherm.set_size_inches(6,8)
		self.plot_setpnt_dev_assist(therm_setpnt_dev_zone, True, 'Zone', title=title4, axis=ax4)
		self.plot_setpnt_dev_assist(therm_setpnt_dev_hour, False, 'Time (Hour)',title=title5, axis=ax5)
		self.plot_setpnt_dev_assist(therm_setpnt_dev_month, False, 'Time (Month)', xtickTagIn=monthTag,title=title6, axis=ax6)
		plt.subplots_adjust(hspace=0.5)

#		plotter.save_fig(fig1, self.figdir+'spt_dev_genie_zone.pdf')
#		plotter.save_fig(fig2, self.figdir+'spt_dev_genie_hour.pdf')
#		plotter.save_fig(fig3, self.figdir+'spt_dev_genie_month.pdf')
#		plotter.save_fig(fig4, self.figdir+'spt_dev_therm_zone.pdf')
#		plotter.save_fig(fig5, self.figdir+'spt_dev_therm_hour.pdf')
#		plotter.save_fig(fig6, self.figdir+'spt_dev_therm_month.pdf')
		plotter.save_fig(figGenie, self.figdir+'spt_dev_genie.pdf')
		plotter.save_fig(figTherm, self.figdir+'spt_dev_therm.pdf')
	
	def plot_setpnt_dev_vs_usability(self, genieFlag, dataType):
		baseTitle1 = 'Setpoint deviation vs ' + dataType
		baseTitle2 = 'Usability of setpoint change vs ' + dataType
		if genieFlag:
			procdb = self.genieprocdb
			setpntDev = procdb.load('setpoint_diff_per_'+dataType)
			filename = 'genie_'+'setdev_vs_usage_'+dataType + '.pdf'
			#title1 = 'Genie\'s ' + baseTitle1 + ': x axes are shared';
			#title2 = 'Genie\'s ' + baseTitle2
		else:
			procdb = self.thermprocdb
			setpntDev = procdb.load('wcad_diff_per_'+dataType)
			filename = 'therm_'+'setdev_vs_usage_'+dataType + '.pdf'
			#title1 = 'Thermostats\' ' + baseTitle1 + ': x axes are shared';
			#title2 = 'Thermostats\' ' + baseTitle2
		title1 = None
		title2 = None

		if dataType=='month':
			xtickTag = plotter.make_month_tag()
		else:
			xtickTag = None
		if dataType=='zone':
			sortedFlag = True
		else:
			sortedFlag = False

		ylabelUsability = '# Changes'
	
		#fig, (ax1, ax2) = plt.subplots(2,1, sharex=True)
		fig = plt.figure(figsize=(6,6))
		gs = gridspec.GridSpec(2,1,height_ratios=[2,1])
		ax1 = plt.subplot(gs[0])
		ax2 = plt.subplot(gs[1])
		usability = self.plot_setpnt_dev_assist(setpntDev, sortedFlag, None, xtickTagIn=xtickTag, axis=ax1, title=title1)
		plotData = [usability]
		plotter.plot_multiple_stacked_bars(plotData, 0, xlabel=dataType, ylabel=ylabelUsability, xtickTag=xtickTag, axis=ax2, title=title2, clist=['skyblue'])
		plt.subplots_adjust(hspace=0.2)
		figsize = (4,3)
		fig.set_size_inches(figsize)
		plotter.save_fig(fig, self.figdir+filename)
	
	def plot_zone_temp_flow_vs_setpnt_asisst(self, xnum, xmin, xmax, xgran, ynum, ymin, ymax, ygran, dataDict):
		tmap = np.ndarray([ynum,xnum], offset=0)
		normTmap = np.ndarray([ynum,xnum], offset=0)
		#init tmap
		for i in range(0,xnum):
			for j in range(0, ynum):
				tmap[j,i] = 0
				normTmap[j,i] = 0

		# Calc tmap
		for tempObj in dataDict:
			currTemp = tempObj.keys()[0]
			if currTemp > xmax:
				continue
			elif currTemp < xmin:
				continue
			x = round((currTemp-xmin)/xgran)-1
			setpnt = np.float64(tempObj.values()[0])
			setpntDiff = setpnt
			if setpntDiff > ymax:
				continue
			elif setpntDiff < ymin:
				continue
			y = round((setpntDiff-ymin)/ygran) - 1
			tmap[y,x] += 1

		# Normalize
		weights = tmap.sum(axis=0)
		for i in range(0,xnum):
			for j in range(0,ynum):
				if weights[i]==0:
					normTmap[j,i] = 0
				else:
					normTmap[j,i] = tmap[j,i]/weights[i]
		return tmap, normTmap

	def plot_zone_temp_flow_vs_setpnt(self, genieFlag, zone):
		if genieFlag:
			tempDict = self.genierawdb.load('temp_vs_setpnt_diff_'+zone)
			flowDict = self.genierawdb.load('flow_vs_setpnt_diff_'+zone)
		else:
			tempDict = self.thermrawdb.load('temp_vs_wcad_diff'+zone)
			flowDict = self.thermrawdb.load('flow_vs_wcad_diff'+zone)


		if genieFlag:
			flowFilename = 'genie_flow_vs_setpnt_diff_'+zone
			tempFilename = 'genie_temp_vs_setpnt_diff_'+zone
		else:
			flowFilename = 'therm_flow_vs_setpnt_diff_'+zone
			tempFilename = 'therm_temp_vs_setpnt_diff_'+zone

		ymin = -4.25
		ymax = 4.25
		ygran = 0.5
		ytickNum = 6
		ylabel = u'Setpoint Change \n ($^\circ$F)'
		tempTitle = zone + ' Zone Temperature vs setpnt Change'
		flowTitle = zone + ': Air Flow vs setpnt Change'
		tempNormTitle = zone + ' Zone Temperature vs setpnt Change: \nnormalized'
		flowNormTitle = zone + ': Air Flow vs setpnt Change: \nnormalized'
		ynum = int((ymax-ymin)/ygran)
		ytickTag = list()
		ytickRange = np.arange(0,ynum+1, int(ynum/(ytickNum-1)))
		for i in range(0,ytickNum):
			ytickTag.append(str(ymin+i*(ymax-ymin)/(ytickNum-1)))

		tempmin = 70
		tempmax = 76
		tempgran = 0.5
		tempnum = int((tempmax-tempmin)/tempgran)
		tmap, normTmap = self.plot_zone_temp_flow_vs_setpnt_asisst(tempnum, tempmin, tempmax, tempgran, ynum, ymin, ymax, ygran, tempDict)
		flowmin = 0
		flowmax = 2400
		flowgran = 100
		flownum = int((flowmax-flowmin)/flowgran)
		fmap, normFmap = self.plot_zone_temp_flow_vs_setpnt_asisst(flownum, flowmin, flowmax, flowgran, ynum, ymin, ymax, ygran, flowDict)


		# Actual Plotting
		xtickRange = np.arange(0,21,5)
#		xtickTag = ['65', '67.5', '70', '72.5', '75', '77.5', '80']
		xtickTag = ['67.5', '70', '72.5', '75', '77.5']
		cbarLabel = "Count (Number)"
		templabel = u'Zone temperature ($^\circ$F)'
		flowlabel = u'Air Flow'
#		fig = plotter.plot_colormap(tmap, (4,2), xlabel, ylabel, cbarLabel, cm.Blues, ytickRange, ytickTag, xtickRange=xtickRange, xtickTag=xtickTag, title=title)
		figTemp = plotter.plot_colormap_upgrade(tmap, (4,2), templabel, ylabel, cbarLabel, cm.Blues, ytickRange, ytickTag, title=tempTitle, xmin=tempmin, xmax=tempmax, xgran=tempgran, ymin=ymin, ymax=ymax, ygran=ygran)
		plotter.save_fig(figTemp, self.figdir+'zones/'+tempFilename+'.pdf')
		figNormTemp = plotter.plot_colormap_upgrade(normTmap, (4,2), templabel, ylabel, cbarLabel, cm.Blues, ytickRange, ytickTag, title=tempNormTitle, xmin=tempmin, xmax=tempmax, xgran=tempgran, ymin=ymin, ymax=ymax, ygran=ygran)
		plotter.save_fig(figNormTemp, self.figdir+'zones/'+tempFilename+'_norm.pdf')
		
		figFlow = plotter.plot_colormap_upgrade(fmap, (4,2), flowlabel, ylabel, cbarLabel, cm.Blues, ytickRange, ytickTag, title=flowTitle, xmin=flowmin, xmax=flowmax, xgran=flowgran, ymin=ymin, ymax=ymax, ygran=ygran)
		plotter.save_fig(figFlow, self.figdir+'zones/'+flowFilename+'.pdf')
		figNormFlow = plotter.plot_colormap_upgrade(normFmap, (4,2), flowlabel, ylabel, cbarLabel, cm.Blues, ytickRange, ytickTag, title=flowNormTitle, xmin=flowmin, xmax=flowmax, xgran=flowgran, ymin=ymin, ymax=ymax, ygran=ygran)
		plotter.save_fig(figNormFlow, self.figdir+'zones/'+flowFilename+'_norm.pdf')
		return figTemp, figFlow

	def plot_temp_vs_setpnt(self, genieFlag, diffFlag):
		# TODO: Add a guideline where ZT=Setpnt
		if genieFlag and diffFlag:
			tempDict= self.genierawdb.load('temp_vs_setpnt_diff')
			filename = 'genie_temp_vs_setpnt_diff'
			ymin = -4.25
			ymax = 4.25
			ygran = 0.5
			ytickNum = 6
			ylabel = u'Setpoint Change \n ($^\circ$F)'
			#title = 'Genie User\'s Temperature Setpoint Changes vs Zone Temperature: \n Each block indicates count of setpoint changes.'
			title = None
		elif genieFlag and not diffFlag:
			tempDict= self.genierawdb.load('temp_vs_setpnt')
			filename = 'genie_temp_vs_setpnt'
			ymin = 64.75
			ymax =77.25
			ygran = 0.5
			ytickNum = 7
			#ytickTag = ['-6', '-4','-2','0','2','4','6']
			#ytickRange = np.arange(0,25,4)
			ylabel = u'Temperature \nsetpoint ($^\circ$F)'
			#title = "Genie User's Setpoints per Zone Temperature"
			title = None
		elif not genieFlag and diffFlag:
			tempDict= self.thermrawdb.load('temp_vs_wcad_diff')
			filename = 'therm_temp_vs_setpnt_diff'
			ymin = -4.25
			ymax = 4.25
			ygran = 0.5
			ytickNum = 6
			ylabel = u'Warm Cool Adjust Change \n ($^\circ$F)'
			#title = 'Thermostats\' warm-cool adjust changes over Zone Temperature: \n each point indicates nubmber of such warm-cool adjust change at certain temperature'
			title = None
		elif not genieFlag and not diffFlag:
			tempDict= self.thermrawdb.load('temp_vs_wcad')
			filename = 'therm_temp_vs_setpnt'
			ymin = -4.25
			ymax = 4.25
			ygran = 0.5
			ytickNum = 6
#			ytickTag = ['-6', '-4','-2','0','2','4','6']
#			ytickRange = np.arange(0,25,4)
			ylabel = u'Warm Cool Adjust \n ($^\circ$F)'
			#title = "Thermostat's Warm Cool Adjust over Zone Temperatures: \nMany users set Warm Cool Adjust to the middle."
			title = None
		
		ynum = int((ymax-ymin)/ygran)
		ytickTag = list()
		ytickRange = np.arange(0,ynum+1, int(ynum/(ytickNum-1)))
		for i in range(0,ytickNum):
			ytickTag.append(str(ymin+i*(ymax-ymin)/(ytickNum-1)))

		#xmin = 67.5
		#xmax = 77.5
		xmin = 70
		xmax = 76
		xgran = 0.5
		xnum = int((xmax-xmin)/xgran)
#		xtickRange = np.arange(0,xnum+1, 2.5)
#		xtickNum = 5
#
#		xtickTag = list()
#		xtickRange = np.arange(0,xnum+1, 5)
#		for i in range(0,xtickNum):
#			xtickTag.append(str(float(xmin+i*float((xmax-xmin)/(xtickNum-1)))))

		tmap = np.ndarray([ynum,xnum], offset=0)
		normTmap = np.ndarray([ynum,xnum], offset=0)
		#init tmap
		for i in range(0,xnum):
			for j in range(0, ynum):
				tmap[j,i] = 0
				normTmap[j,i] = 0

		# Calc tmap
		for tempObj in tempDict:
			currTemp = tempObj.keys()[0]
			if currTemp > xmax:
				continue
			elif currTemp < xmin:
				continue
			#x = int((xmax-currTemp)/xgran)-1
			x = round((currTemp-xmin)/xgran)-1
			setpnt = np.float64(tempObj.values()[0])
			setpntDiff = setpnt
			if setpntDiff > ymax:
				continue
			elif setpntDiff < ymin:
				continue
			#y = int((ymax-setpntDiff)/ygran) - 1
			y = round((setpntDiff-ymin)/ygran) - 1
			tmap[y,x] += 1

		# Normalize
		weights = tmap.sum(axis=0)
		for i in range(0,xnum):
			for j in range(0,ynum):
				normTmap[j,i] = tmap[j,i]/weights[i]

		# Actual Plotting
		xtickRange = np.arange(0,21,5)
#		xtickTag = ['65', '67.5', '70', '72.5', '75', '77.5', '80']
		xtickTag = ['67.5', '70', '72.5', '75', '77.5']
		cbarLabel = "Count (Number)"
		xlabel = u'Zone temperature ($^\circ$F)'
#		fig = plotter.plot_colormap(tmap, (4,2), xlabel, ylabel, cbarLabel, cm.Blues, ytickRange, ytickTag, xtickRange=xtickRange, xtickTag=xtickTag, title=title)
		fig = plotter.plot_colormap_upgrade(tmap, (4,2), xlabel, ylabel, cbarLabel, cm.Blues, ytickRange, ytickTag, xtickRange=xtickRange, xtickTag=xtickTag, title=title, xmin=xmin, xmax=xmax, xgran=xgran, ymin=ymin, ymax=ymax, ygran=ygran)
		plotter.save_fig(fig, self.figdir+filename+'.pdf')
		
		fig = plotter.plot_colormap_upgrade(normTmap, (4,2), xlabel, ylabel, cbarLabel, cm.Blues, ytickRange, ytickTag, xtickRange=xtickRange, xtickTag=xtickTag, title=title, xmin=xmin, xmax=xmax, xgran=xgran, ymin=ymin, ymax=ymax, ygran=ygran)
		plotter.save_fig(fig, self.figdir+filename+'_normalized.pdf')
		return fig
	
	def plot_energy_save_waste(self, genieFlag):
		if genieFlag:
			db = self.genieprocdb
			titleBase = "Energy consumptions of 24 hours \n before and after users' activities are compared. \n Positive is saving, negative is wastage."
			titleMonth = "Genie's " + "Energy Savings vs Month: " + titleBase
			titleZone = "Genie's " + "Energy Savings vs Zone: " + titleBase

		else:
			db = self.thermprocdb
			titleBase = "Energy consumptions of 24 hours \nbefore and after users' activities are compared."
			titleMonth = "Thermostats' " + "Energy Savings per Month: " + titleBase
			titleZone = "Thermostats' " + "Energy Savings per Zone: " + titleBase
		titleZone = None
		titleMonth = None
		energySaveMonth= db.load('energy_save_month')
		energySaveZone= db.load('energy_save_zone')
		energyWasteMonth= db.load('energy_waste_month')
		energyWasteZone= db.load('energy_waste_zone')

		ylabel = u'Energy Saving (kWh)'
		xlabelMonth = 'Time (Month/Year)'
		xlabelZone = 'Zone'
		figMonth = plotter.plot_up_down_bars(np.array(energySaveMonth.values())/3600, np.array(energyWasteMonth.values())/3600, (4,2), xlabelMonth, ylabel, title=titleMonth)
		figZone = plotter.plot_up_down_bars(np.array(energySaveZone.values())/3600, np.array(energyWasteZone.values())/3600, (4,2), xlabelZone, ylabel,title=titleZone)

		if genieFlag:
			plotter.save_fig(figMonth, self.figdir+'genie_energy_save_waste_month.pdf')
			plotter.save_fig(figZone, self.figdir+'genie_energy_save_waste_zone.pdf')
		else:
			plotter.save_fig(figMonth, self.figdir+'therm_energy_save_waste_month.pdf')
			plotter.save_fig(figZone, self.figdir+'therm_energy_save_waste_zone.pdf')
	
	def plot_energy_diff(self, genieFlag):
		titleMonth1 = 'Changes in Total Energy Consumption vs Month due to '
		titleMonth2 = '\nWe aggregate changes in energy for each control action, \nactuation and temperature setpoint changes, measured over 24 hours before and after the action.'
		titleZone1 = 'Changes in Total Energy Consumption vs Zone due to '
		titleZone2 = ''
		if genieFlag:
			db = self.genieprocdb
			titleMonth = titleMonth1 + "Genie Control: " +titleMonth2
			titleZone = titleZone1 + "Genie Control: " + titleZone2
		else:
			db = self.thermprocdb
			titleMonth = titleMonth1  + "Thermostats control " +titleMonth2
			titleZone = titleZone1 + "Thermostats control " + titleZone2
		titleMonth = None
		titleZone = None
		energyDiffMonth = db.load('energy_diff_month')
		energyDiffZone = db.load('energy_diff_zone')
		ylabel = 'Energy Consumption Change (kWh)'
		xlabelMonth = 'Time (Month/Year)'
		xlabelZone = 'Zone'
		plotDataMonth = list()
		plotDataMonth.append(np.array(energyDiffMonth.values())/3600)
		plotDataZone = list()
		plotDataZone.append(np.array(energyDiffZone.values())/3600)
		monthTag = plotter.make_month_tag()
		figMonth = plotter.plot_multiple_stacked_bars(plotDataMonth, 0, xlabel=xlabelMonth, ylabel=ylabel, xtickTag=monthTag, title=titleMonth)
		figZone = plotter.plot_multiple_stacked_bars(plotDataZone, 0, xlabel=xlabelZone, ylabel=ylabel, title=titleZone)
		
		if genieFlag:
			plotter.save_fig(figMonth, self.figdir+'genie_energy_diff_month.pdf')
			plotter.save_fig(figZone, self.figdir+'genie_energy_diff_zone.pdf')
		else:
			plotter.save_fig(figMonth, self.figdir+'therm_energy_diff_month.pdf')
			plotter.save_fig(figZone, self.figdir+'therm_energy_diff_zone.pdf')
	
	def plot_setpnt_energy_diff(self, genieFlag, timeDiff):
		postfixTimeDiff = str(timeDiff.total_seconds()/3600)
		titleMonth1 = 'Changes in Total Energy Consumption vs Month in Weekdays due to '
		titleMonth2 = '\nWe aggregate changes in energy for each control action, \nactuation and temperature setpoint changes, measured over 24 hours before and after the action.'
		titleZone1 = 'Changes in Total Energy Consumption vs Zone in Weekdays due to '
		titleZone2 = ''
		titleHour1 = 'Changes in Total Energy Consumption vs Hour in Weekdays due to '
		if genieFlag:
			db = self.genieprocdb
			titleMonth = titleMonth1 + "Genie Users\' Setpnt Change: " +titleMonth2
			titleZone = titleZone1 + "Genie Users\' Setpnt Change: " + titleZone2
			titleHour = titleHour1 + "Genie Users\' Setpnt Change: " + titleZone2
			setpntMonth = db.load('setpoint_per_month')
			setpntHour = db.load('setpoint_per_hour')
			rawSetpntZone = db.load('setpoint_per_zone')
		else:
			db = self.thermprocdb
			titleMonth = titleMonth1  + "Thermostats\' Setpnt Change: " +titleMonth2
			titleZone = titleZone1 + "Thermostats\' Setpnt Change: " + titleZone2
			titleHour = titleHour1 + "Thermostats\' Setpnt Change: " + titleZone2
			setpntMonth = db.load('wcad_per_month')
			setpntHour = db.load('wcad_per_hour')
			rawSetpntZone = db.load('wcad_per_zone')
		titleMonth = None
		titleZone = None
		titleHour = None
		
		energyDiffMonth = db.load('setpnt_energy_diff_month_' + postfixTimeDiff)
		energyDiffZone = db.load('setpnt_energy_diff_zone_' + postfixTimeDiff)
		energyDiffHour = db.load('setpnt_energy_diff_hour_' + postfixTimeDiff)
		setpntZone = list()
		for zone in energyDiffZone.keys():
			setpntZone.append(rawSetpntZone[zone])

		ylabelEnergy = 'Energy Consumption Change \n(kWh)'
		ylabelUtil = 'Number of Setpoint Changes'
		xlabelMonth = 'Time (Month/Year)'
		xlabelZone = 'Zone'
		xlabelHour= 'Hour'

		monthTag = plotter.make_month_tag()
		plotDataMonth = list()
		plotDataMonth.append(np.array(energyDiffMonth.values())/3600)
		plotDataUtilMonth = [np.array(setpntMonth.values())]
		figMonth, (axEnergyMonth, axUtilMonth) = plt.subplots(2,1, sharex=True)
		figMonth.set_size_inches(6,6)
		plotter.plot_multiple_stacked_bars(plotDataMonth, 0, xlabel=xlabelMonth, ylabel=ylabelEnergy, xtickTag=monthTag, title=titleMonth, axis=axEnergyMonth, fig=figMonth)
		plotter.plot_multiple_stacked_bars(plotDataUtilMonth, 0, xlabel=xlabelMonth, ylabel=ylabelUtil, xtickTag=monthTag, title=titleMonth, axis=axUtilMonth, fig=figMonth)
		plt.subplots_adjust(hspace=0.5)
		#plt.show()
		
		plotDataZone = list()
		plotDataZone.append(np.array(energyDiffZone.values())/3600)
		plotDataUtilZone = [np.array(setpntZone)]
		figZone, (axEnergyZone, axUtilZone) = plt.subplots(2,1, sharex=True)
		figZone.set_size_inches(6,6)
		plotter.plot_multiple_stacked_bars(plotDataZone, 0, xlabel=xlabelZone, ylabel=ylabelEnergy, title=titleZone, axis=axEnergyZone, fig=figZone)
		plotter.plot_multiple_stacked_bars(plotDataUtilZone, 0, xlabel=xlabelZone, ylabel=ylabelUtil, title=titleZone, axis=axUtilZone, fig=figZone)
		plt.subplots_adjust(hspace=0.5)
		#plt.show()
		
		plotDataHour = [np.array(energyDiffHour.values())/3600]
		plotDataUtilHour = [np.array(setpntHour.values())]
		figHour, (axEnergyHour, axUtilHour) = plt.subplots(2,1, sharex=True)
		figHour.set_size_inches(6,6)
		plotter.plot_multiple_stacked_bars(plotDataHour, 0, xlabel=xlabelHour, ylabel=ylabelEnergy, title=titleHour, axis=axEnergyHour, fig=figHour)
		plotter.plot_multiple_stacked_bars(plotDataUtilHour, 0, xlabel=xlabelHour, ylabel=ylabelUtil, title=titleHour, axis=axUtilHour, fig=figHour)
		plt.subplots_adjust(hspace=0.5)
		#plt.show()
		
		if genieFlag:
			plotter.save_fig(figMonth, self.figdir+'genie_setpnt_energy_diff_month.pdf')
			plotter.save_fig(figZone, self.figdir+'genie_setpnt_energy_diff_zone.pdf')
			plotter.save_fig(figHour, self.figdir+'genie_setpnt_energy_diff_hour.pdf')
		else:
			plotter.save_fig(figMonth, self.figdir+'therm_setpnt_energy_diff_month.pdf')
			plotter.save_fig(figZone, self.figdir+'therm_setpnt_energy_diff_zone.pdf')
			plotter.save_fig(figHour, self.figdir+'therm_setpnt_energy_diff_hour.pdf')
	
	def plot_calendar_sample(self):
		occSamples = self.genierawdb.load('occ_samples')
		beforeOcc = occSamples['2109'][0]
		afterOcc = occSamples['2109'][1]

		tsList = list()
		tsList.append(beforeOcc['timestamp'])
		tsList.append(afterOcc['timestamp'])
		occList = list()
		occList.append(beforeOcc['value'])
		occList.append(afterOcc['value'])
		xlabel = 'Time'
		ylabel = 'Occupied Command'

		ytick = [1,2,3]
		yticks = [ytick,ytick]
		xtickTag = ['Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun', 'Mon']
		xtickTagsIn = [xtickTag, xtickTag]
		ytickTag = ["Unoccupied", "Standby", "Occupied"]
		ytickTagsIn = [ytickTag, ytickTag]
		title1 = 'Occupied Command of a Conference Room for a Week before Google Calendar System'
		title2 = 'Occupied Command of a Conference Room for a Week after Google Calendar System'
		title1 = None
		title2 = None
		titles = [title1, title2]
		fig, axes = plotter.plot_multiple_timeseries(tsList, occList, xlabel, ylabel, xtickTags=xtickTagsIn, yticks=yticks, ytickTags=ytickTagsIn, titles=titles)
		#fig, axes = plt.subplots(nrows=2)
		axes[0].set_ylim([0.9,3.1])
		axes[1].set_ylim([0.9,3.1])
		plt.show()
		
		plotter.save_fig(fig, self.figdir+'calendar_sample.pdf')
		return fig

	def plot_actuate_setpnt_ts_assist(self, genieFlag):
		if genieFlag:
			setpntDict = self.genierawdb.load('setpoint_per_zone')
			actuateDict = self.genierawdb.load('actuate_per_zone')
		else:
			setpntDict = self.thermrawdb.load('wcad_per_zone_filtered')
			actuateDict = self.thermrawdb.load('actuate_per_zone')
		actuateTS = defaultdict(int)
		setpntTS = defaultdict(int)

		for actuate in actuateDict.values():
			for tp in actuate['timestamp']:
				actuateTS[(tp.year-2013)*12+tp.month] += 1
		for setpnt in setpntDict.values():
			for tp in setpnt['timestamp']:
				setpntTS[(tp.year-2013)*12+tp.month] += 1
		return setpntTS, actuateTS

	def plot_an_activity_zone(self, dataType, sortIndicator):
		title = 'Number of ' + dataType + ' vs zone'
		title = None
		genieData = self.genieprocdb.load(dataType+'_per_zone')
		if dataType == 'setpoint':
			thermData = self.thermprocdb.load('wcad_per_zone')
		else:
			thermData = self.thermprocdb.load('actuate_per_zone')

		genieListGenie = list()
		genieListTherm = list()
		notGenieListTherm = list()
		
		sortedThermDict = {key: thermData[key] for key in self.notgenielist}
		if sortIndicator=='sorted':
			sortedGenieDict = OrderedDict(sorted(genieData.items(), key=operator.itemgetter(1)))
			sortedThermDict = OrderedDict(sorted(sortedThermDict.items(), key=operator.itemgetter(1)))
		else:
			sortedGenieDict = {key: genieData[key] for key in self.geniezonelist}

		for zone in sortedGenieDict.keys():
			genieListGenie.append(genieData[zone])
			genieListTherm.append(thermData[zone])

		for i in range(0,len(self.notgenielist)):
			genieListTherm.append(0)
			genieListGenie.append(0)
		for i in range(0,len(self.geniezonelist)):
			notGenieListTherm.append(0)
		notGenieListTherm = notGenieListTherm + sortedThermDict.values()
			

		plotData = [genieListTherm, genieListGenie, notGenieListTherm]

		legend1 = 'Thermostat with Genie'
		legend2 = 'Genie'
		legend3 = 'Thermostat without Genie'
		xlabel = 'Zone'
		if dataType == 'setpoint':
			ylabel = '# Setpoint Changes'
		elif dataType == 'actuate':
			ylabel = '# Actuation'

		fig, (axis1) = plt.subplots(1,1)
		ylim = (0,700)
		clist = ['skyblue','peachpuff','yellowgreen']
		linewidth=0
		hatch=['xx','oo', '--']
		plotter.plot_multiple_stacked_bars(plotData, 0, xlabel=xlabel, ylabel=ylabel, ylim=ylim, axis=axis1, fig=fig, dataLabels=[legend1,legend2, legend3], clist=clist, linewidth=linewidth, hatchSeries=hatch)
		

		#plotData = [sortedThermDict.values()]
		#xtickLabel = [83,93,103,113,123,133,143,153]
		#plotter.plot_multiple_stacked_bars(plotData, 0, xlabel=xlabel, ylabel=ylabel, ylim=ylim, axis=axis2, fig=fig, dataLabels=[legend3], linewidth=linewidth, xtickTag=xtickLabel, xtickRotate=0, clist=clist)
		figsize = (8,3)
		fig.set_size_inches(figsize)
		fig.subplots_adjust(hspace=0.3)
		plt.show()

		plotter.save_fig(fig, self.figdir+dataType+'_zone_'+sortIndicator+'.pdf')
		
	def plot_actuate_setpnt_zone(self, genieFlag):

		# Each element: key:Zone, val: [setpntNum, actuNum]
		setpntDict= dict()
		actuDict= dict()
		sumDict = dict()
		if genieFlag:
			localZoneList = self.geniezonelist
			setpoints = self.genieprocdb.load('setpoint_per_zone')
			actuates = self.genieprocdb.load('actuate_per_zone')
			title = "Utilization of Genie: \nEach bar is the total number of the activity per zone"
		else:
			localZoneList = self.notgenielist
			setpoints = self.thermprocdb.load('wcad_per_zone')
			actuates= self.thermprocdb.load('actuate_per_zone')
			title = "Utilization of Thermostats: \nEach bar is the total number of the activity per zone"
		title = None
		
		for zone in localZoneList:
			actuDict[zone] = 0
			setpntDict[zone] = 0
			sumDict[zone] = 0

		for zone in localZoneList:
			setpntDict[zone] = setpoints[zone]
			actuDict[zone] = actuates[zone]
			sumDict[zone] = setpoints[zone]+actuates[zone]
		sortedSumDict = OrderedDict(sorted(sumDict.items(), key=operator.itemgetter(1)))

#NOTE: Following does not work. How can I sort actuDict and setpntDict more elegantly?
#		sortedSetpntDict = {zone:setpntDict[zone] for zone in sortedSumDict.keys()}
#		sortedActuDict = {zone:actuDict[zone] for zone in sortedSumDict.keys()}
#		plotData = [sortedSetpntDict.values(), sortedActuDict.values()]

		sortedSetpntList = list()
		sortedActuList = list()
		for zone in sortedSumDict.keys():
			sortedSetpntList.append(setpntDict[zone])
			sortedActuList.append(actuDict[zone])

		plotData = [sortedSetpntList, sortedActuList]

		xlabel = 'Zone'
		ylabel = 'Number of Activities'
		fig, axis = plt.subplots(1,1)
		clist = ['c','m']
		dataLabels = ['Setpoint Change', 'Actuation']
		plotter.plot_multiple_stacked_bars(plotData, 1, xlabel=xlabel, ylabel=ylabel, axis=axis, fig=fig, clist=clist, title=title,dataLabels=dataLabels)
		
		if genieFlag:
			plotter.save_fig(fig, self.figdir+'zones/genie_'+'utilization_zone.pdf')
		else:
			plotter.save_fig(fig, self.figdir+'zones/therm_'+'utilization_zone.pdf')

		

	def plot_actuate_setpnt_month(self):
		GenieFlag = True
		ThermFlag = False
#		genieSetpnt, genieActuate = self.plot_actuate_setpnt_ts_assist(GenieFlag)
#		thermSetpnt, thermActuate = self.plot_actuate_setpnt_ts_assist(ThermFlag)
		genieSetpnt = self.genieprocdb.load('setpoint_per_month')
		genieActuate = self.genieprocdb.load('actuate_per_month')
		thermSetpnt = self.thermprocdb.load('wcad_per_month')
		thermActuate = self.thermprocdb.load('actuate_per_month')

		x =np.arange(0,len(genieSetpnt))

		fig = plt.figure(figsize=(4,2), linewidth=0)
		p1 = plt.bar(x-0.15, np.array(genieSetpnt.values()), width=0.3, align='center', color='b', label='Genie Setpoint', linewidth=0)
		p2 = plt.bar(x-0.15, np.array(genieActuate.values()), bottom=np.array(genieSetpnt.values()), width=0.3, align='center', color='c', label='Genie Actuate', linewidth=0)
		p3 = plt.bar(x+0.15, np.array(thermSetpnt.values()), width=0.3, align='center', color='magenta', label='Thermostat Warm-Cool Adjust', linewidth=0)
		p4 = plt.bar(x+0.15, np.array(thermActuate.values()), bottom=np.array(thermSetpnt.values()), width=0.3, align='center', color='y', label='Thermostat Actuate', linewidth=0)
		#TODO: range should be changed.
		plt.legend(handles=[p1,p2,p3,p4], fontsize=5)

		plt.xlabel('Time (Month)')
		plt.ylabel('Count (Number)')
		plt.xticks(x, plotter.make_month_tag(), fontsize=7,rotation=70)
		plt.xlim(-1,19.1)

		title = "Utilization of Genie and Thermostats: \nEach bar is the total number of the activity per month"
		title = None
		plt.title(title)

		plt.show()
		plotter.save_fig(fig, self.figdir+'utilization_actu_setpnt_month.pdf')
		return fig
	
	def plot_an_activity_month(self, dataType):
		title = 'Comparison of the number of ' + dataType + ' activities vs month'
		title = None
		genieData = self.genieprocdb.load(dataType+'_per_month')
		if dataType == 'setpoint':
			genieThermData = self.thermprocdb.load('genie_wcad_per_month')
			notgenieThermData = self.thermprocdb.load('notgenie_wcad_per_month')
		else:
			genieThermData = self.thermprocdb.load('genie_actuate_per_month')
			notgenieThermData = self.thermprocdb.load('notgenie_actuate_per_month')

		plotData = [genieData.values(), genieThermData.values(), notgenieThermData.values()]
		xlabel = 'Time (Month/Year)'
		#ylabel = 'Number of ' + dataType
		if dataType == 'setpoint':
			ylabel = '# Setpoint Changes'
		elif dataType=='actuate':
			ylabel = '# Actuation'
		xtickLabel = plotter.make_month_tag()

		fig, axis = plt.subplots(1,1)
		if dataType=='actuate':
			ylim = (0,800)
		elif dataType=='setpoint':
			ylim= (0,350)
		clist = ['skyblue','peachpuff','yellowgreen']
		#figsize = self.figsize
		figsize = (4,3)
		legends = ['Genie', 'Thermostat with Genie', 'Thermostat without Genie']
		hatch = ['xx', 'oo', '--']
		plotter.plot_multiple_stacked_bars(plotData, 0, xlabel=xlabel, ylabel=ylabel, xtickRange=None, xtickTag=xtickLabel, ytickRange=None, ytickTag=None, title=title, stdSeries=None, axis=axis, fig=fig, clist=clist, dataLabels=legends,ylim=ylim, hatchSeries=hatch)
		fig.set_size_inches(figsize)

		plotter.save_fig(fig, self.figdir+'usage_' + dataType+'_month.pdf')

	
	def plot_one_zone_setpnt_actu(self, genieFlag, zone):
		titleBase = 'Zone ' + zone + '\'s Activities vs Time (Month) due to'
		if genieFlag:
			title = titleBase + ' Genie Usage'
			rawdb = self.genierawdb
			setpoints = rawdb.load('setpoint_per_zone')
		else:
			title = titleBase + ' Thermostat Usage'
			rawdb = self.thermrawdb
			setpoints = rawdb.load('wcad_per_zone_filtered')
		title = None
		actuates = rawdb.load('actuate_per_zone')

		weekendEnergy = self.generaldb.load('zone_weekend_energy_per_month')[zone]
		weekdayEnergy = self.generaldb.load('zone_weekday_energy_per_month')[zone]

		if zone in setpoints.keys():
			setpoint = setpoints[zone]
		else:
			setpoint = pd.DataFrame()
		if zone in actuates.keys():
			actuate = actuates[zone]
		else:
			actuate = pd.DataFrame()
		setpointMonth = dict()
		actuateMonth = dict()
		for month in range(12,31):
			setpointMonth[month] = 0
			actuateMonth[month] = 0

		for row in setpoint.iterrows():
			tp = row[1]['timestamp']
			setpointMonth[(tp.year-2013)*12+tp.month] += 1
		for row in actuate.iterrows():
			tp = row[1]['timestamp']
			actuateMonth[(tp.year-2013)*12+tp.month] += 1

#		plotData = [setpointMonth.values(), actuateMonth.values()]
		xtickTagIn = plotter.make_month_tag()
		xlabel = 'Time (Month/Year)'
		ylabel = 'Number of Activities'
		ylim1 = (0,100)
		ylim2 = (0,4500000)

		fig, axis = plt.subplots(4,1, sharex=True)
		colors = ['c','m']
		plotter.plot_multiple_stacked_bars([setpointMonth.values()], 0, xlabel=xlabel, ylabel=ylabel, xtickTag=xtickTagIn, title=title, axis=axis[0], clist=colors, dataLabels=['Setpoints'], ylim=ylim1)
		plotter.plot_multiple_stacked_bars([actuateMonth.values()], 0, xlabel=xlabel, ylabel=ylabel, xtickTag=xtickTagIn, title=None, axis=axis[1], clist=colors, dataLabels=['Actuates'], ylim=ylim1)
		plotter.plot_multiple_stacked_bars([weekendEnergy.values()], 0, xlabel=xlabel, ylabel=ylabel, xtickTag=xtickTagIn, title=None, axis=axis[2], clist=colors, dataLabels=['Weekend Energy'], ylim=ylim2)
		plotter.plot_multiple_stacked_bars([weekdayEnergy.values()], 0, xlabel=xlabel, ylabel=ylabel, xtickTag=xtickTagIn, title=None, axis=axis[3], clist=colors, dataLabels=['Weekday Energy'], ylim=ylim2)
		plt.subplots_adjust(hspace=0.5)
		
		if genieFlag:
			plotter.save_fig(fig, self.figdir+'genie_'+zone+'_utilization.pdf')
		else:
			plotter.save_fig(fig, self.figdir+'therm_'+zone+'_utilization.pdf')
		plt.show()

	def plot_energy(self):
		endGenieAvg = self.genieprocdb.load('zone_weekend_energy_per_month_avg')
		dayGenieAvg = self.genieprocdb.load('zone_weekday_energy_per_month_avg')
		endThermAvg = self.thermprocdb.load('zone_weekend_energy_per_month_avg')
		dayThermAvg = self.thermprocdb.load('zone_weekday_energy_per_month_avg')
		endGenieStd = self.genieprocdb.load('zone_weekend_energy_per_month_std')
		dayGenieStd = self.genieprocdb.load('zone_weekday_energy_per_month_std')
		endThermStd = self.thermprocdb.load('zone_weekend_energy_per_month_std')
		dayThermStd = self.thermprocdb.load('zone_weekday_energy_per_month_std')

#		endPlotData = [np.array(endGenieAvg.values())/3600, np.array(endThermAvg.values())/3600]
#		dayPlotData = [np.array(dayGenieAvg.values())/3600, np.array(dayThermAvg.values())/3600]
		endAvgData = [endGenieAvg, endThermAvg]
		endStdData = [endGenieStd, endThermStd]
		dayAvgData = [dayGenieAvg, dayThermAvg]
		dayStdData = [dayGenieStd, dayThermStd]

		titleBase = 'Comparison of Normalized Energy Consumption vs Month'
		dayTitle = 'Weekday\'s ' + titleBase
		endTitle = 'Weekend and night\'s ' + titleBase
		dayTitle = None
		endTitle = None

		clist = ['skyblue','peachpuff']
		xlabel = 'Time (Month/Year)''Month'
		ylabel = 'Energy during \nWeekdays (kWh)'
		xtickLabel= plotter.make_month_tag()
		fig, (endAxis, dayAxis) = plt.subplots(2,1)
		legends = ['Genie', 'Thermostat']
		ylim = (0,3)
		hatch = ['xx','oo']
		plotter.plot_multiple_stacked_bars(dayAvgData, 0, xlabel=None, ylabel=ylabel, xtickTag=[], title=dayTitle, axis=endAxis, clist=clist, dataLabels=legends, stdSeries=dayStdData, ylim=ylim, hatchSeries=hatch)
		plotter.plot_multiple_stacked_bars(endAvgData, 0, xlabel=xlabel, ylabel=ylabel, xtickTag=xtickLabel, title=endTitle, axis=dayAxis, clist=clist, dataLabels=legends, stdSeries=endStdData, ylim=ylim, hatchSeries=hatch)
		figsize = (4,3)
		fig.set_size_inches(figsize)
		fig.subplots_adjust(hspace=0.2)

		plotter.save_fig(fig, self.figdir+'weekday_weekend_energy.pdf')

	def plot_temp_flow_vs_setpnt_all_zones(self):
		self.plot_zone_temp_flow_vs_setpnt(False,'4150')
		self.plot_zone_temp_flow_vs_setpnt(False,'2146')
		self.plot_zone_temp_flow_vs_setpnt(False,'4114')
		self.plot_zone_temp_flow_vs_setpnt(False,'3140')
		self.plot_zone_temp_flow_vs_setpnt(True,'2140')
		self.plot_zone_temp_flow_vs_setpnt(True,'2150')
		self.plot_zone_temp_flow_vs_setpnt(True,'2272')
		self.plot_zone_temp_flow_vs_setpnt(True,'3202')
	
	def publish(self):
		GenieFlag = True
		ThermFlag = False
		self.plot_an_activity_month('setpoint')
		self.plot_an_activity_month('actuate')
		self.plot_an_activity_zone('setpoint', 'fixed')
		self.plot_an_activity_zone('actuate', 'fixed')
		self.plot_setpnt_dev_vs_usability(GenieFlag, 'zone')
		self.plot_setpnt_dev_vs_usability(GenieFlag, 'hour')
		self.plot_setpnt_dev_vs_usability(ThermFlag, 'zone')
		self.plot_setpnt_dev_vs_usability(ThermFlag, 'hour')
		self.plot_energy()
	
	def test(self):
		GenieFlag = True
		ThermFlag = False
		self.plot_setpnt_energy_diff(GenieFlag, timedelta(hours=2))
		self.plot_setpnt_energy_diff(ThermFlag, timedelta(hours=2))


	def plot_all(self):
		GenieFlag = True
		ThermFlag = False
		self.plot_weighted_setpnt_dev_zone('sorted')
		self.plot_one_zone_setpnt_actu(False, '4114')
		self.plot_energy()
		self.plot_an_activity_month('setpoint')
		self.plot_an_activity_month('actuate')
		self.plot_an_activity_zone('setpoint', 'fixed')
		self.plot_an_activity_zone('actuate', 'fixed')
		self.plot_an_activity_zone('setpoint', 'sorted')
		self.plot_an_activity_zone('actuate', 'sorted')
		self.plot_setpnt_dev()
		self.plot_temp_vs_setpnt(GenieFlag, True)
		self.plot_temp_vs_setpnt(GenieFlag, False)
		self.plot_temp_vs_setpnt(ThermFlag, True)
		self.plot_temp_vs_setpnt(ThermFlag, False)
		#self.plot_energy_diff(GenieFlag)
		#self.plot_energy_diff(ThermFlag)
		#self.plot_energy_save_waste(GenieFlag)
		#self.plot_energy_save_waste(ThermFlag)
		self.plot_calendar_sample()
		self.plot_actuate_setpnt_month()
		self.plot_setpnt_energy_diff(GenieFlag)
		self.plot_setpnt_energy_diff(ThermFlag)
		self.plot_actuate_setpnt_zone(True)
		self.plot_actuate_setpnt_zone(False)
		self.plot_setpnt_dev_vs_usability(GenieFlag, 'zone')
		self.plot_setpnt_dev_vs_usability(GenieFlag, 'hour')
		self.plot_setpnt_dev_vs_usability(ThermFlag, 'zone')
		self.plot_setpnt_dev_vs_usability(ThermFlag, 'hour')
