from collections import Counter
import heapq
import editdistance

class TrieNode:
    def __init__(self):
        self.dict = {};
        self.cnt = Counter();
    
    def clear(self):
        self.dict.clear();
        self.cnt.clear();
    
    def cutoff(self, k):
        self.cnt = Counter(self.cnt.most_common(k));

class SuffixTrie:
    def __init__(self, topk=2, useFuzzyMatch=1, useTokenNGram=0, useCharNGram=0, useOnlineLearning=False, queryMode=0):
        self.trie = TrieNode();

        #The number of autosuggestions that you want:
        self.k = topk;

        #useFuzzyMatch == 0 --> Will not use FuzzyMatch when autosuggesting;
        #useFuzzyMatch > 0 --> Will include tokens of levenstein distance == useFuzzyMatch;
        self.useFuzzyMatch = useFuzzyMatch;
        
        #Keeping a tally of counts of chars and tokens
        self.charCount = Counter();    
        self.tokenCount = Counter();
        
        #useTokenNGram == 0 or 1 --> Will not use token-level ngram;
        #useCharNGram == 0 or 1 --> Will not use char-level ngram;
        #............ > 1 --> Will build ngram model of corresponding order, ie, Markov model of (x-1) order
        self.useTokenNGram = useTokenNGram;
        self.useCharNGram = useCharNGram;
        self.charNGram = {};
        self.tokenNGram = {};

        #Mapping of token to a unique id and mapping of line to a unique id and their inverts
        self.tokenToID = {};
        self.lineToID = {};
        self.IDToLine = {};
        self.IDToToken = {};

        #Make the model learn on-line or not:
        self.useOnlineLearning = useOnlineLearning;
        
        #QueryMode == 1 --> Suffix Trie; default mode;
        #QueryMode == 2 --> Char-level NGram only;
        #QueryMode == 3 --> Token-level NGram only;
        self.queryMode = queryMode;
    
    def __del__(self):
        self.IDToLine.clear();
        self.IDToToken.clear();
        self.tokenToID.clear();
        self.lineToID.clear();
        self.tokenNGram.clear();
        self.tokenCount.clear();
        self.charNGram.clear();
        self.charCount.clear();
        self.trie.clear();
    
    def preprocess(self, string):
        curStr = "^"+string;
        curStr += "$";
        if curStr not in self.lineToID:
            curID = len(self.lineToID);
            self.lineToID[curStr] = curID;
            self.IDToLine[curID] = curStr;
        for c in curStr:
            self.charCount[c] += 1;

        curStr = "^ "+string;
        curStr += " $";
        tokens = curStr.split();
        for token in tokens:
            if token not in self.tokenToID:
                curID = len(self.tokenToID);
                self.tokenToID[token] = curID;
                self.IDToToken[curID] = token;
        for token in curStr.split():
            self.tokenCount[token] += 1; 

    #Add a new string into the model
    def addTrie(self, string):
        for i in range(len(string)):
            branch = self.trie;
            for c in string[i : ]:
                if c not in branch.dict:
                    branch.dict[c] = TrieNode();
                branch.dict[c].cnt[self.lineToID[string]] += 1;
                branch = branch.dict[c];

    #Add in NGram support; not active if self.use*NGram<1:
    def addCharNGram(self, string):
        n = self.useCharNGram;
        if n > 1:
            for token in string.split(' '):
                for i in range(len(token)-n+1):
                    ngram = token[i:i+n];
                    pre = ngram[:-1];
                    pos = ngram[-1];
                    if pre not in self.charNGram:
                        self.charNGram[pre] = Counter();
                    self.charNGram[pre][pos] += 1;

    def addTokenNGram(self, string):
        n = self.useTokenNGram;
        if n > 1:
            tokens = string.split();
            for i in range(len(tokens)-n+1):
                ngram = tokens[i:i+n];
                pre = tuple([self.tokenToID[token] for token in ngram[:-1]]);
                pos = self.tokenToID[ngram[-1]];
                if pre not in self.tokenNGram:
                    self.tokenNGram[pre] = Counter();
                self.tokenNGram[pre][pos] += 1; 
                    
    #Normalize NGram language model and smooth:
    def normalize(self, ngram):
        pass;

    #Truncate model; keeping only top K, treating others as unknown:
    def truncate(self):
        pass;

    #Implement Levenshtein distance for fuzzy match when no exact match exists:
    def editDistance(self,s,t):
        return editdistance.eval(s,t);
        '''
        if s == t:
            return 0;
        if len(s) == 0 or len(t) == 0:
            return len(s) | len(t);

        cost = 0 if (s[-1]==t[-1]) else 1;    
        return min(self.editDistance(s[:-1],t)+1, self.editDistance(s,t[:-1])+1, self.editDistance(s[:-1],t[:-1])+cost);
        '''

    #Suggest based on fuzzy matches: a score of token freq and editDistance:
    def fuzzySuggest(self, string):
        results = [];
        for token in self.tokenCount:
            freq = (self.tokenCount[self.tokenToID[token]]+0.0)/(sum(self.tokenCount.values()));
            dist = self.editDistance(token, string);

            if dist <= self.useFuzzyMatch:
                score = freq/(dist+0.1e-10);
                if len(results) < self.k:
                    heapq.heappush(results, (score, self.tokenToID[token]));
                else:
                    heapq.heappushpop(results, (score, self.tokenToID[token]));
        return [self.IDToToken[result[1]] for result in heapq.nlargest(self.k, results)];
               
    #Follow down the tree all chars in string;
    #Return subtrie rooted with the last char or None;
    def follow(self, string):
        branch = self.trie;
        for c in string:
            if c not in branch.dict:
                if self.useOnlineLearning == True:
                    self.preprocess(string);
                    self.addTrie("^"+string+"$");
                    self.addCharNGram("^"+string+"$");
                    self.addTokenNGram("^ "+string+" $");

                if self.useFuzzyMatch < 1:
                    return [True, branch];
                else:
                    return [False, self.fuzzySuggest(string)];
            else:
                branch = branch.dict[c];
        return [True, branch];

    #Query the model; show top k results:
    def query(self, string):
        if self.queryMode == 0:
            results = self.follow(string);
            if results[0] == True:
                return [self.IDToLine[result[0]][1:-1] for result in results[1].cnt.most_common(self.k)];
            else:
                return results[1];
        elif self.queryMode == 1:
            #pre-mature
            n = self.useCharNGram;
            pre = string[1-n:];
            return [post[0] for post in self.charNGram[pre].most_common(self.k)];
        elif self.queryMode == 2:
            #pre-mature
            n = self.useTokenNGram;
            pre = string.split()[1-n:];
            return [ post[0] for post in self.tokenNGram[pre].most_common(self.k)];
            
               
    
