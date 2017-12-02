from pymongo import MongoClient

def initiateDb():
	client = MongoClient()
	db = client.hackercamp
	return db