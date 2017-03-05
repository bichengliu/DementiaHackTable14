##Python Flask app 
Running on IBM bluemix with watson developer cloud services enabled 

3 API calls are available: 

https://memorylog.mybluemix.net/api/analyzedata
POST 3 JSON strings: 
1) "filename" is a URL for a >22kHz .wav file
2) "patient_id" is a numeric identifier for each patient 
3) "date" is a string value "yyyymmdd"
response is JSON string of key vaue pairs of metrics calculated with scipy and from IBM watson-developer-cloud services

https://memorylog.mybluemix.net/api/downloaddata
Gets the completed CSV file with headers: 
1) Patient_ID
2) Date
3) Metric name
4) "value"
5) string or numeric values 

https://memorylog.mybluemix.net/api/pivotdataupdate
Gets the completed CSV file with all values. 
