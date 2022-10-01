import ffmpeg
import pandas as pd
from pytube import Playlist 
from pytube import Channel
import json, gzip, os, torch, re
from bs4 import BeautifulSoup
from nltk.corpus import words
import urllib.request, urllib, json 
import sys, wave, io
from pytube import YouTube
from vosk import Model, KaldiRecognizer
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import JSONFormatter
from sentence_transformers import SentenceTransformer, CrossEncoder, util
from tqdm import tqdm
from bs4 import BeautifulSoup
from nltk.corpus import words
import json, gzip, os, torch, re

# model = Model('/content/drive/MyDrive/SmartSearch/vosk-model-en-us-0.22')
class NoTranscript: 
  def __init__(self, link): 
    self.link = link 

  def get_wave_file(self): 
    yt = YouTube(self.link)
    stream_url = yt.streams.all()[0].url  
    audio, err = (ffmpeg.input(stream_url).output("pipe:", format='wav', acodec='pcm_s16le').run(capture_stdout=True))
    return io.BytesIO(audio)

  def get_transcript_dic(self): 
    by = self.get_wave_file()
    wf = wave.open(by, 'rb')
    rec = KaldiRecognizer(model, wf.getframerate())
    rec.SetWords(True)

    results = []
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            part_result = json.loads(rec.Result())
            results.append(part_result)

    part_result = json.loads(rec.FinalResult())
    results.append(part_result)

    words_list = []
    for i in range(len(results)): 
      words_list.append((results[i]['text']))

    starting_word_time_stamp = []
    for i in range(len(results)): 
      try: 
        starting_word_time_stamp.append(results[i]['result'][0]['start'])
      except: 
        starting_word_time_stamp.append('no time for this')

    everything = []
    for i in range(len(words_list)): 
      dic = {}
      dic['text'] = words_list[i]
      dic['start'] = starting_word_time_stamp[i]
      dic['link'] = self.link 
      
      everything.append(dic)
    formatter = JSONFormatter()
    full = formatter.format_transcript(everything)

    return full 


class TranscriptSaverChannel: 
  def __init__(self, channel_link): 
    self.channel_link = channel_link 

  def get_channel_url(self): 
    channel = list(Channel(self.channel_link)) 
    return channel 
  
  def get_transcript(self): 
    urls = self.get_channel_url()

    all_transcripts = []
    formatter = JSONFormatter() 

    for i in tqdm(range(len(urls))): 
      video_id = urls[i].split('=')[1]
      try: 
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        for su in transcript: 
          su['link'] = urls[i]

        json_formatted = formatter.format_transcript(transcript)
        all_transcripts.append(json_formatted)

      except: 
        # c = NoTranscript(urls[i]).get_transcript_dic()
        # all_transcripts.append(c)
        pass 

    return all_transcripts


class DFMaker: 
  def __init__(self, list): 
    self.list = list  
    self.bi_encoder = SentenceTransformer('multi-qa-MiniLM-L6-cos-v1')
    
  def decontracted(self, phrase: str) -> str:
    phrase = re.sub(r"won't", "will not", phrase)
    phrase = re.sub(r"can\'t", "can not", phrase)
    phrase = re.sub(r"n\'t", " not", phrase)
    phrase = re.sub(r"\'re", " are", phrase)
    phrase = re.sub(r"\'s", " is", phrase)
    phrase = re.sub(r"\'d", " would", phrase)
    phrase = re.sub(r"\'ll", " will", phrase)
    phrase = re.sub(r"\'t", " not", phrase)
    phrase = re.sub(r"\'ve", " have", phrase)
    phrase = re.sub(r"\'m", " am", phrase)

    return phrase

  def clean_code(self, sentance: str) -> str:
    sentance = sentance.replace("\n","")
    sentance = re.sub(r"http\S+", "", sentance)
    sentance = BeautifulSoup(sentance, 'lxml').get_text() 
    sentance = self.decontracted(sentance)
    sentance = re.sub(r"\S*\d\S*", "", sentance).strip() 
    sentance = re.sub('[^A-Za-z]+', ' ', sentance) 
    sentance = ' '.join(e.lower() for e in sentance.split())

    return sentance

  def generate_N_grams(self, sentences: str,ngram :int=1) -> list:
    words = [self.clean_code(sentence) for sentence in sentences]  
    temp = zip(*[words[i:] for i in range(0,ngram)])
    ans = [' '.join(ngram) for ngram in temp]

    return ans 

  def df(self) -> pd.DataFrame: 
    df_text_time = pd.DataFrame(columns=['Sentance_3_cleaned','Sentance_3','Embeddings','time','link'])
    count = 0 

    for name in self.list: 
      text, start, n_3_grams, total_emb, sentences, link , corpus_sentences = [], [], [], [], [], [], []
 
      js = json.loads(name)  
      for i in js:
        text.append(i['text'])
        start.append(i['start'])
        link.append(i['link'])
      n_3_grams = self.generate_N_grams(text,3)

      for sen in n_3_grams:
        total_emb.append(self.bi_encoder.encode(sen,convert_to_numpy=True))

      df = pd.DataFrame()
      df['Sentance_3_cleaned'] = n_3_grams
      df['Embeddings'] = total_emb
      df['Sentance_3'] = text[:-2]
      df['time'] = start[:-2]
      df['link'] = link[:-2] 
      df_text_time = df_text_time.append(df)

    df_text_time.reset_index(inplace = True)
    df_text_time = df_text_time.drop('index', axis = 1)


    return df_text_time

class SemanticSearch: 
  def __init__(self, query: str, dataframe, top_k : int=10): 
    self.query = query 
    self.top_k = top_k 
    self.dataframe = dataframe  
    self.bi_encoder = SentenceTransformer('multi-qa-MiniLM-L6-cos-v1')
    self.cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')  

  def data_loader(self): 
    DF_text_time = self.dataframe 
    embd = list(DF_text_time['Embeddings'])
    total_text_set_list = list(DF_text_time['Sentance_3_cleaned'])
    time = list(DF_text_time['time'])
    link = list(DF_text_time['link'])

    data_tf=[]
    for i in embd:
        data_tf.append(torch.from_numpy(i))

    return DF_text_time, embd, total_text_set_list,  time, link, data_tf 
    
  def search(self): 
    DF_text_time, embd, total_text_set_list, time, link, data_tf = self.data_loader()

    question_embedding = self.bi_encoder.encode(self.query, convert_to_tensor=True) 
    hits = util.semantic_search(question_embedding, data_tf, top_k = self.top_k)[0] 

    cross_inp = [[self.query, total_text_set_list[hit['corpus_id']]] for hit in hits]
    cross_scores = self.cross_encoder.predict(cross_inp)

    for idx in range(len(cross_scores)):
      hits[idx]['cross-score'] = cross_scores[idx]
    hits = sorted(hits, key=lambda x: x['cross-score'], reverse=True)

    times, links = [], []
    for i in range(len(hits)):
        if(i!=0 and abs(int(time[hits[i]['corpus_id']]) - int(time[hits[i-1]['corpus_id']])) >= 10):
            times.append(int(time[hits[i]['corpus_id']]))
            links.append(link[hits[i]['corpus_id']])

        if(i==0):
            times.append(int(time[hits[i]['corpus_id']]))
            links.append(link[hits[i]['corpus_id']])

    return times, links 
