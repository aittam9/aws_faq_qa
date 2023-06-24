from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
from tqdm import tqdm
import json

URL_ORIGIN = "https://aws.amazon.com/it/certification/certified-machine-learning-specialty/"

# function to get all urls and store them in a dictionary
def collect_urls(URL_ORIGIN):
    # create the bs object and parse the html
    html = urlopen(URL_ORIGIN)
    bsObj = BeautifulSoup(html, features="html.parser")

    # extract the ursl and store them in a dictionary
    URLS = {}
    for title in bsObj.find_all("h3"):
            for u in title.find_all("a"):
                if re.match(r".*faqs.*",u.get("href")) and not re.match(r"(.*forecast.*|.*Medical.*)",u.get("href")):
                    URLS[u.get_text().strip()] = "https://aws.amazon.com/"+u.get("href")
    #TODO remove forecast, as it has no faqs
    return URLS

def qa_extractor(URL):    
    #open the html and create bs object to parse it
    html = urlopen(URL)
    bsObj = BeautifulSoup(html, "html.parser")
    #extract all the text marked with tag <p> under the qa section
    all = []
    for block in bsObj.main.find_all(class_ = "lb-grid"):
        for sub in block.find_all("div", class_ = "lb-txt-16 lb-rtxt"):
            for p in sub.find_all("p"):
                p = p.get_text().strip()
                all.append(p)
    
    #extract the ids of questions
    ids = []
    for n,stringa in enumerate(all):
        if re.match(r"(D:|Q:)", stringa):
            ids.append(n)
    # insert a dummy symbol to isolate chunks of questions and (multiple-paragraphs) answers
    i = 0
    for position in ids:
        i+=1
        all.insert(position+i-1, "\n")
    
    # join all to create a list of string made of "Question: Full-Answer(multi-par)"
    all2 = " ".join(all).split("\n")
    all2 = [i for i in all2 if i]
    #isolate the questions
    domande = []
    domande = [i.split("?")[0]+"?" for i in all2 if i]
        
    #isolate the answers
    risposte = []
    for i in range(len(all2)):
        risposte.append(all2[i].replace(domande[i], "").strip())
    
    domande = [re.sub(r"(D:|Q:)", "", i).strip().capitalize() for i in domande]
    
    #assure that list of q and list of a have the same length
    assert len(domande) == len(risposte)
    
    #built qa dictionary
    qas = dict(zip(domande,risposte))
    
    return qas

def all_qas_collector(URLS):
    all_qas = {}
    for u in tqdm(URLS):
        all_qas[u] = qa_extractor(URLS[u])
    return all_qas

#helper function to compute basic statistics and show distributions of qas over subjects
def compute_stats(all_qas):
    count = 0
    print(f"Done\nQuestion-answer pair have been scraped form {URL_ORIGIN} with the following distribution with respect to subjects:")
    for k in all_qas:
        count += len(all_qas[k])
        print(k,len(all_qas[k]))
    
    print(f"\nFor a total of {count} question-answer pair.")

def build_json(all_qas):
    #TODO create a json builder
    pass

def main():
    print(f"Scraping pages from {URL_ORIGIN}")
    URLS = collect_urls(URL_ORIGIN)
    all_qas = all_qas_collector(URLS)
    compute_stats(all_qas)


if __name__ == "__main__":
    main()