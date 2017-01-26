import json
import codecs
import re
import gc
from suffixtrie import SuffixTrie
try:
   import cPickle as pickle
except:
   import pickle
import sys
sys.setrecursionlimit(1000000)

inputFile = 'sample_conversations.json'

def readInput(inputFile):
    data = []
    with codecs.open(inputFile,'rU','utf-8') as f:
        for line in f:
            data.append(json.loads(line));
    return data[0];
    

def parseData(data):
    #Create a new model or load from file:
    try:
        model = pickle.load(open("model.db",'r'));
    except:
        model = SuffixTrie(5, True, 2, 2, True);

    for issue in data['Issues']:        
        for message in issue['Messages']:
            for snippet in re.split("[,.?!:;\t\n]", message['Text']):
                snippet = snippet.strip();
                print("Preprocessing")
                model.preprocess(snippet);
    del data;
    gc.collect();
    return model;

def train(model):
    for line in model.lineToID:
        print("Building Trie");
        model.addTrie(line);

        modLine = "^ "+line[1:-1]+" $";
        print("Adding token-level ngram");
        model.addTokenNGram(modLine);
    for token in model.tokenToID:
        print("Adding char-level ngram");
        model.addCharNGram(token);
        
    
    #Update the model:
    print("dumping");
    pickle.dump(model, open("model.db",'wb'));

if __name__ == "__main__":
    jsonData = readInput(inputFile);
    print("parsing data");
    model = parseData(jsonData);
    print("training model");
    train(model);
    print("done training")


    

    
    
    



