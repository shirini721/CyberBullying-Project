#!/usr/bin/python
# Filename: crawl.py
from BeautifulSoup import BeautifulSoup
import urllib2
import codecs
import copy
import re
import argparse


with open("likers2.out") as f:
    content = f.readlines()

out = "{\"results\":{"

output_file = open('likers.out','w')

def extract_pic(in1):
        in2 = str(in1)
        if "zoom_photo_answer" in in2:
                s = BeautifulSoup(str(in2))
                try:
                    img_url = s.find("img", {"class": "photoAnswer-XL photoAnswer-headSpace"});
                    m = re.search('src=\"(.+)\" />', str(img_url))
                    url = m.group(1)
                except AttributeError:
                    img_url = s.find("img", {"class": "photoAnswer-XL"});
                    m = re.search('src=\"(.+)\" />', str(img_url))
                    url = m.group(1)
                aa = in2.split("<a href=")[0]
                bb = aa + url
                return  bb.replace("'", "").replace('"','').replace("<br />","").replace("\n", "").strip()
        else:
                return in2.replace("'", "").replace('"','').replace("<br />","").strip()

line_no = 0
already_crawled = []
for line in content:
    if line not in already_crawled:
        line = "http://ask.fm/" + line
        already_crawled.append(line)
        line_no = line_no + 1
        line = line.strip()
        response = urllib2.urlopen(line)
        html = response.read()

        soup = BeautifulSoup(html)
        profiles_crawled = []   
        out += "\"result_" + str(line_no) + "\": {\"url\":\"" + line + "\", \"recent_questions\": { "
        #prints top 25 questions and answers {question,answer,questioner, number of likes}
        qus = []
        answers = []
        index = 1
        for question in soup.findAll("div", {"class": "questionBox"}):
            s = BeautifulSoup(str(question))
            ques = s.find("span", {"class": "text-bold"});
            ans = s.find("div", {"class": "answer"});
            ques = str(ques).replace("\n","").replace("\\", "")
            m = re.search('ltr\">(.+)</span></span>', str(ques))
            try:
                qu = m.group(1).replace('"','').replace("'","")
            except AttributeError:
                qu = "NOT_VALID"
            try:
                an = str(ans).replace("<div class=\"answer-paragraph\"></div>", "").split("class=\"answer\" dir=\"ltr\">")[1].split("</div>")[0].replace("\\", "").strip()	
                pic_url = extract_pic(an)
            except AttributeError:
                an = "NOT_VALID"
                pic_url = "NOT_VALID"
            except IndexError:
                an = "NOT_VALID"
                pic_url = "NOT_VALID"
            out +=  "\"Q" + str(index) +"\": \"" + qu + "\", " + "\"A" + str(index) + "\": \"" + pic_url + "\"" + "," 
            index += 1

        out = out[:-1] + "}, \"popular_questions\": {"

        url = line + "/best"
        response = urllib2.urlopen(url)
        html = response.read()
        soup = BeautifulSoup(html)
        index = 1
        first_flag = True
        first = []
        for question in soup.findAll("div", {"class": "questionBox"}):
            s = BeautifulSoup(str(question))
            ques = s.find("span", {"class": "text-bold"});
            ans = s.find("div", {"class": "answer"});
            ques = str(ques).replace("\n", "").replace("\\", "")
            m = re.search('ltr\">(.+)</span></span>', str(ques))
            try:
                qu = m.group(1).replace('"','').replace("'","")
                an = str(ans).replace("<div class=\"answer-paragraph\"></div>", "").split("class=\"answer\" dir=\"ltr\">")[1].split("</div>")[0].replace("\\", "").strip()
                pic_url = extract_pic(an)
            except AttributeError:
                qu = "NOT_VALID"
                an = "NOT_VALID"
                pic_url = "NOT_VALID"
            except IndexError:
                qu = "NOT_VALID"
                an = "NOT_VALID"
                pic_url = "NOT_VALID"

            out +=  "\"Q" + str(index) +"\": \"" + qu + "\", " + "\"A" + str(index) + "\": \"" + pic_url  + "\", " + "\"LIKERS" + str(index) +"\": ["
            likers = s.find("div", {"class": "like-face-container"})
            num = 0
	
            for liker in likers.findAll("a"):
                l = re.search("<a href=\"/(.+)\"><img",str(liker))
                le = l.group(1)
                num = num + 1
                if first_flag:
                    first.append(le)
                    output_file.write(le)
                    output_file.write("\n")
                    out += "\"" + le + "\","

            index += 1
            out = out[:-1] + "] "

        out = out + "}},"


print out[:-1] + "}"
