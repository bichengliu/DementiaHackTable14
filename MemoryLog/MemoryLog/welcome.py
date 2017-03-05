# Copyright 2015 IBM Corp. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from flask import Flask, jsonify, request, send_from_directory
import json
import csv
import urllib3
import scipy
import numpy
from scipy import io
from scipy.io import wavfile
from os.path import join, dirname
from watson_developer_cloud import SpeechToTextV1 as SpeechToText
from watson_developer_cloud import AlchemyLanguageV1 as AlchemyLanguage
from watson_developer_cloud import ToneAnalyzerV3 as ToneAnalyzer

app = Flask(__name__)

def transcribe_audio(path_to_audio_file):
    username = "73be2640-402e-41b1-881a-a18e9ef863ea"
    password = "1WBfGwj2onno"
    speech_to_text = SpeechToText(username=username, password=password)
    with open(path_to_audio_file, 'rb') as audio_file:
        return speech_to_text.recognize(audio_file, content_type='audio/wav')

def get_text_sentiment(text):
    alchemy_api_key = "ce6d4fd632e66e75542c39f00d5408962ac58697"
    alchemy_language = AlchemyLanguage(api_key=alchemy_api_key)
    result = alchemy_language.sentiment(text=text)
    if result['docSentiment']['type'] == 'neutral':
        return 'netural', 0
    return result['docSentiment']['type'], result['docSentiment']['score']

def get_text_tone(text):
    tone_username = "59514251-2915-47e6-af4e-98f387d1dc43"
    tone_password = "lerc4ZeURleN"
    tone_analyzer = ToneAnalyzer(username=tone_username, password=tone_password, version='2016-05-19 ')
    tone_result = tone_analyzer.tone(text=text)
    output = {}
    for category in tone_result['document_tone']['tone_categories']:
        for item in category['tones']:
            output[item['tone_id']] = item['score']
    return output

def find_bins(y):
    x = [0,0,0,0,0,0,0,0,0,0]
    for i in range(0,len(y)):
        if abs(y[i]) < 0.1:
            x[0] = x[0] + 1
        elif abs(y[i]) < 0.2:
            x[1] = x[1] + 1
        elif abs(y[i]) < 0.3:
            x[2] = x[2] + 1
        elif abs(y[i]) < 0.4:
            x[3] = x[3] + 1
        elif abs(y[i]) < 0.5:
            x[4] = x[4] + 1
        elif abs(y[i]) < 0.6:
            x[5] = x[5] + 1
        elif abs(y[i]) < 0.7:
            x[6] = x[6] + 1
        elif abs(y[i]) < 0.8:
            x[7] = x[7] + 1
        elif abs(y[i]) < 0.9:
            x[8] = x[8] + 1
        elif abs(y[i]) < 1:
            x[9] = x[9] + 1
    max_x = numpy.amax(x)
    for i in range(0,len(x)):
        x[i] = x[i]/max_x
    return x

@app.route('/')
def Welcome():
    return app.send_static_file('index.html')

@app.route('/api/analyzedata', methods=['GET', 'POST'])
def AnalyzeData():
    ##Check if method is POST, and save audioURL, patient_id, date
    if request.method == 'POST':
        audioURL = request.json['filename']
        patient_id = request.json['patient_id']
        date = request.json['date']

    ##initialize urllib3 to copy wave file to local directory 
    http = urllib3.PoolManager()
    response = http.request('GET', audioURL)
    fname = "static/sounds/wave.wav"
    file = open(fname, 'wb')
    file.write(response.data)
    file.close()

    ##IBM Watson Speech to Text 
    result = transcribe_audio(fname)
    text = result['results'][0]['alternatives'][0]['transcript']

    ##IBM Watson text tone scores 
    outputData = get_text_tone(text)

    ##IBM Watson sentiment and sentiment score of text 
    sentiment, score = get_text_sentiment(text)

    ##Save outputs to list 
    outputData['sentiment'] = sentiment
    outputData['sentiment_score'] = score
    outputData['audio_link'] = audioURL
    outputData['word_count'] = len(text.split())

    ##now let's add our own scipy analysis 
    [length, data] = scipy.io.wavfile.read(fname)
    max_data = numpy.amax(data)
    norm_vals = []
    for i in range(0,len(data)):
        norm_vals.append(float(data[i])/max_data)
    bins_data = find_bins(norm_vals)
    bins_mean = numpy.mean(bins_data)
    bins_var = numpy.var(bins_data)
    bins_high = bins_data[9]
    bins_data.sort()
    bins_rank = 0 
    for i in range(0, 10):
        if bins_data[i] == bins_high:
            bins_rank = i
    if bins_rank == 9 or bins_rank == 8:
        bins_overpower = 1
    else:
        bins_overpower = 0;
    outputData['bins_mean'] = bins_mean
    outputData['bins_variance'] = bins_var
    outputData['rank'] = bins_rank
    outputData['overpowering'] = bins_overpower
    outputData['loudest_value'] = bins_high
    outputData['transcription'] = text
    with open('static/data.csv', 'w') as csv_file:
        writer = csv.writer(csv_file)
        for key, value in outputData.items():
           writer.writerow([patient_id, date, key, "value", value])
    return jsonify(outputData)


@app.route('/api/downloaddata')
def DownloadData():
    return send_from_directory(directory='static', filename='data.csv') 

port = os.getenv('PORT', '5000')
if __name__ == "__main__":
	app.run(host='0.0.0.0', port=int(port))
