import web
import json
import suggestorNaive
import suffixtrie
import pickle
import sys
sys.setrecursionlimit(1000000)

urls = (
    '/(.*)', 'autosuggest'
)

print("Loading data ... ...");
try:
    model = pickle.load(open("model.db",'rb'));
    print("Ready to use");
except:
    print("Model file not found!");
    raise;

class autosuggest:
    def GET(self, input):
        global model;

        #Responding using loaded model:
        results = model.query(input);
        suggestions = {"suggestions":results};

        json.dump(suggestions, open('suggestions.txt','w'));

        #Dumping the model file again to reflect the new additions:
        #pickle.dump(model, open("model.db",'wb'));

        return json.dumps(suggestions);

if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()