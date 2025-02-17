from QUANTAXIS.TSBoosting.TSBoosting import TS_Boosting_predict
from QAWebServer.basehandles import QABaseHandler
from QUANTAXIS.QAUtil import QASETTING
import pandas as pd
import csv
from QUANTAXIS.QAUtil.QATransform import QA_util_to_json_from_pandas
import json
import time

# edited by jingya
import urllib.parse
####

class DownloadPredictHandler(QABaseHandler):
    def set_default_headers(self):
        print("setting headers!!! analyze")
        self.set_header("Access-Control-Allow-Origin","*")
        self.set_header("Access-Control-Allow-Headers","Content-Type, Authorization, Content-Length, X-Requested-With, x-token")
        self.set_header("Access-Control-Allow-Methods", "HEAD, GET, POST, PUT, PATCH, DELETE")
    def get(self):
        client = QASETTING.client
        database = client.mydatabase
        prediction = database.prediction
        ref_prediction = prediction.find()
        predictionDF = pd.DataFrame(list(ref_prediction)).drop(columns = '_id')
        export_csv = predictionDF.to_csv(r'prediction.csv', index=None, header=True)
        self.set_header('Content-Type', 'text/csv')
        self.set_header('Content-Disposition', 'attachment; filename=prediction.csv')
        with open('prediction.csv', encoding="utf8") as f:
            csv_reader = csv.reader(f, delimiter=',')
            for row in csv_reader:
                self.write(str(row[0])+","+str(row[1])+"\r\n")
        # self.write(open(export_csv, encoding="utf8"))

class DownloadSampleHandler(QABaseHandler):
    def set_default_headers(self):
        print("setting headers!!! analyze")
        self.set_header("Access-Control-Allow-Origin","*")
        self.set_header("Access-Control-Allow-Headers","Content-Type, Authorization, Content-Length, X-Requested-With, x-token")
        self.set_header("Access-Control-Allow-Methods", "HEAD, GET, POST, PUT, PATCH, DELETE")
    def get(self):
        client = QASETTING.client
        # database = client.mydatabase
        # prediction = database.prediction
        # ref_prediction = prediction.find()
        # predictionDF = pd.DataFrame(list(ref_prediction)).drop(columns = '_id')
        # export_csv = predictionDF.to_csv(r'prediction.csv', index=None, header=True)
        self.set_header('Content-Type', 'text/csv')
        self.set_header('Content-Disposition', 'attachment; filename=PredicT_Sample_Data.csv')
        print("Download sample data")
        with open('/home/ForecastingWeb/testData/daily-total-female-births.csv', encoding="utf8") as f:
        #with open('../testData/daily-total-female-births.csv', encoding="utf8") as f:
            csv_reader = csv.reader(f, delimiter=',')
            for row in csv_reader:
                self.write(str(row[0])+","+str(row[1])+"\r\n")
        # with open('prediction.csv', encoding="utf8") as f:
        #     csv_reader = csv.reader(f, delimiter=',')
        #     for row in csv_reader:
        #         self.write(str(row[0])+","+str(row[1])+"\r\n")
        

class TestHandler(QABaseHandler):
    def set_default_headers(self):
        print("setting headers!!! analyze")
        self.set_header("Access-Control-Allow-Origin","*")
        self.set_header("Access-Control-Allow-Headers","Content-Type, Authorization, Content-Length, X-Requested-With, x-token")
        self.set_header("Access-Control-Allow-Methods", "HEAD, GET, POST, PUT, PATCH, DELETE")
    
    def get(self):
        client = QASETTING.client
        
        # edited by jingya
        uri_json = urllib.parse.urlparse(self.request.uri)
        query_json = urllib.parse.parse_qs(uri_json.query)
        username = query_json['username'][0]
        print("in test handler...")
        print(username)
        # print(type(username))
        ####
        
        database = client.mydatabase
        
        # edited by jingya
        collection = database[username]
        ####
        
        #collection = database.uploaddata
        ref = collection.find()
        start = ref[0]['datetime']
        end = ref[ref.count()-1]['datetime']
        by = 'D'

        # edited by jingya
        collectionid = username
        pastdata = pd.DataFrame(list(ref)).drop(columns = '_id')
        ####
        
        databaseid = 'mydatabase'
        #collectionid = 'uploaddata'
        TS_Boosting_predict(start=start, end=end, by=by, databaseid=databaseid, collectionid=collectionid)

        collection_prediction = database.prediction
        ref_prediction = collection_prediction.find()
        prediction = pd.DataFrame(list(ref_prediction)).drop(columns = '_id')
        
        prediction_json = {
            'yAxisData': list(prediction['predict']),
            'xAxisData': list(map(lambda x : x.split(' ')[0],list(prediction['datetime']))),
            'label': 'Future',
            'colorPicked': '#519e19'
        }


        collection_past_predict = database.past_prediction
        ref_past_pred = collection_past_predict.find()
        past_pred = pd.DataFrame(list(ref_past_pred)).drop(columns = '_id')
        
        print("past data x-axis:")
        print(list(map(lambda x: x.split(' ')[0], list(pastdata['datetime']))))

        # adjust alignment bw historical data and predicted data
        past_x_lst = list(map(lambda x: x.split(' ')[0], list(pastdata['datetime'])))
        past_pred_x_lst = list(map(lambda x: x.split(' ')[0], list(past_pred['datetime'])))
        past_y_lst = list(pastdata['y'])
        past_pred_y_lst = list(past_pred['predict'])
        pred_x_head = past_pred_x_lst[0]
        for i in past_x_lst:
            if i == pred_x_head:
                break
            else:
                past_pred_y_lst.insert(0, None)
        padding = len(past_y_lst) - len(past_pred_y_lst)
        for i in range(0, padding):
            past_pred_y_lst.append(None)

        print(past_y_lst)
        print(len(past_y_lst))
        print(past_pred_y_lst)
        print(len(past_pred_y_lst))
        
        # past_json = {
        #     'yAxisData': list(past_pred['y_t']),
        #     'xAxisData': list(map(lambda x: x.split(' ')[0], list(past_pred['datetime']))),
        #     'label': 'Past',
        #     'colorPicked': '#999997',
        #     'twoLines': True,
        #     'yAxisData2': list(past_pred['predict']),
        #     'label2': 'Past Prediction',
        #     'colorPicked2': '#999997',

        # }
        past_json = {
            'xAxisData': past_x_lst,
            'yAxisData': past_y_lst,
            'label': 'Past',
            'colorPicked': '#999997',
            'twoLines': True,
            'yAxisData2': past_pred_y_lst,
            'label2': 'Past Prediction',
            'colorPicked2': '#999997',

        }
        messagebody = {
            'token': 'success',
            'past': past_json,
            'future': prediction_json
        }

        self.write(messagebody)
        #self.write(json.dumps(prediction_json))

    def options(self, *args, **kwargs):
        self.set_status(204)
        self.finish()
