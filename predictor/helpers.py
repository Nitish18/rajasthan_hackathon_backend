from . config import initiateDb
from bson.objectid import ObjectId


def fetchTrainingData(training_properties):
	db = initiateDb()
	bucket = []
	historical_data = list(db.users.find({}, {"ppmLevel": 1, "bacteriaTypeInAir":1, "phLevel":1, "bacteriaTypeInWater":1, "foodFiberContent":1, "_id": 0}))
	for doc in historical_data:
		doc  = doc.values()
		bucket.append(doc)
	return bucket

def fetchLabels(training_properties):
	db = initiateDb()
	historical_data = list(db.users.find({}, {"_id": 0, "diseaseType":1}))
	labels = []
	for doc in historical_data:
		labels.append(doc.get('diseaseType'))
	return labels		

def createProcessId():
	db = initiateDb()
	process_obj = {
		"status": "pending"
	}
	return db.TrainingStatus.insert(process_obj)

def getSampleData(year):
	db = initiateDb()
	q = {
		"diseaseType": {"$exists": True}
	}
	if year:
		q['year'] = int(year)
	records = list(db.users.find(q, {'_id': 0}))
	return records

def insertRecord(doc):
	db = initiateDb()
	db.PredictionOutput.insert(doc)

def changeTrainingStatus(id):
	print "Change status callled"
	print id
	db = initiateDb()
	print list(db.TrainingStatus.find({"_id":ObjectId(id)}))
	db.TrainingStatus.update({"_id": ObjectId(id)}, {"$set":{"status": "completed"}})
	print "returning"
	return 
