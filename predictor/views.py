# -*- coding: utf-8 -*-
from __future__ import unicode_literals

#from django.utils import simplejson

import json

from django.shortcuts import render

from django.http import HttpResponse

from . config import initiateDb

import pandas

import numpy

import threading

from sklearn import tree

from bson.objectid import ObjectId


from . helpers import fetchTrainingData, fetchLabels, createProcessId, getSampleData, insertRecord, changeTrainingStatus


# Create your views here.


def fetchData(request):
	db = initiateDb()
	year = int(request.GET.get('year',0))
	q = {}
	if year:
		q = {
			"year":year,
			"diseaseType": {"$exists": True}
		}
	records = list(db.users.find(q,{'_id':0}))
	res = json.dumps({"data": records})
	return HttpResponse(res)


def fetchEachYearData(request):
	"""
	Getting data according to a year
	"""
	year = int(request.GET.get('year',0))
	db = initiateDb()
	q = {}
	if year:
		q = {"year":year}
	records = list(db.users.find(q,{'_id':0}))
	res = json.dumps({"data": records})
	return HttpResponse(res)

def fetchYearDelta(request):
	"""
	Getting delta of a year
	"""
	year = request.GET.get('year')
	db = initiateDb()
	distinct_disease = db.users.find({"year":int(year)},{'diseaseType':1}).distinct("diseaseType")
	disease_delta_list = []
	if len(distinct_disease):
		for i in distinct_disease:
			disease_type_obj = {}	
			current_year_cnt = db.users.find({"diseaseType":i,"year":int(year)},{'_id':0}).count()
			previous_year_cnt = db.users.find({"diseaseType":i,"year": int(year)-1},{'_id':0}).count()
			disease_type_obj.update({"delta":current_year_cnt - previous_year_cnt,"disease_type":i})
			disease_delta_list.append(disease_type_obj)

	res = json.dumps({"data": disease_delta_list})
	return HttpResponse(res)

def makePredictions(dataset_classifier, year, id):
	print "make predictions called"
	data = getSampleData(year)
	for doc in data:
		sample_set = [
			doc.get('ppmLevel'),
			doc.get('bacteriaTypeInAir'),
			doc.get('phLevel'),
			doc.get('bacteriaTypeInWater'),
			doc.get('foodFiberContent'),
		]
		output = dataset_classifier.predict([sample_set])
		doc['diseaseType'] = output[0]
		insertRecord(doc)
	changeTrainingStatus(id)
	print "Returning"
	return

def beginTraining(year, id): 
	"Feeds previous year data to train system"
	print "called"

	training_data_set = pandas.DataFrame()
	properties = [
		"ppmLevel",
		"bacteriaTypeInAir",
		"phLevel",
		"bacteriaTypeInWater",
		"foodFiberContent",
		"diseaseType"
	]
	features = fetchTrainingData(properties)
	labels = fetchLabels(properties)
	dataset_classifier = tree.DecisionTreeClassifier()
	dataset_classifier = dataset_classifier.fit(features, labels)
	makePredictions(dataset_classifier, year, id)
	return 

def trainSystem(request):
	year = int(request.GET.get('year',2016))
	id = createProcessId()
	t = threading.Thread(target=beginTraining(year, id), args=())
	t.setDaemon(True)
	t.start()
	return HttpResponse(json.dumps({"processId": str(id)}))


def fetchLegend(request):
	"""
	Getting legend data according to a year
	"""
	year = int(request.GET.get('year',2016))
	db = initiateDb()
	records = list(db.users.aggregate([
    {'$match':{"year":year}},
    {"$group" : {'_id':"$diseaseType", 'count':{'$sum':1}}}
	]))

	for i in records:
		disease_color = list(db.legendcolor.find({"map_id":i.get('_id')},{'map_value':1,'_id':0}))
		if len(disease_color):
			i.update(disease_color[0]['map_value'])
	if len(records):
		res = json.dumps(records)
	else:
		res = {}			
	return HttpResponse(res)	

def getTrainingStatus(request):
	db = initiateDb()
	objId = request.GET.get('objId')
	record = list(db.TrainingStatus.find({"_id": ObjectId(str(objId))}, {'_id': 0}))
	return HttpResponse(json.dumps(record[0]))

def getPredictionResult(request):
	db = initiateDb()
	year = int(request.GET.get('year',0))
	q = {}
	if year:
		q = {
			"year":year,
			"diseaseType": {"$exists": True}
		}
	records = list(db.PredictionOutput.find(q,{'_id':0}))
	res = json.dumps({"data": records})
	return HttpResponse(res)
