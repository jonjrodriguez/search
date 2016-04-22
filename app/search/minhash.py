import string, json
from itertools import combinations
from bs4 import BeautifulSoup, Comment
from cityhash import CityHash64, CityHash64WithSeed

class MinHash(object):

    def __init__(self, shingle_size, permutations, threshold):
        self.shingle_size = shingle_size
        self.permutations = permutations
        self.threshold = threshold
        self.max_hash_value = 2**63-1

    def findDuplicates(self, file):
        print "Creating MinHash Signatures"

        signatures = self.createSignatures(file)

        print "Checking for duplicates"

        duplicates = self.deduplicate(signatures)

        print len(duplicates), "duplicates found"

        return duplicates

    def createSignatures(self, file):
        signatures = {}
        with open(file) as file:
            for document in file:
                data = json.loads(document)
                signatures[data['url']] = self.minhashSignature(data['html'])

        return signatures

    def minhashSignature(self, html):
        words = self.parseHtml(html)
        shingles = self.shingle(words)

        signature = set()
        for i in range(self.permutations):
            minhash_value = self.max_hash_value
            for shingle in shingles:
                temp = CityHash64WithSeed(shingle,i)
                if minhash_value > temp:
                    minhash_value = temp

            signature.add(minhash_value)

        return signature

    def shingle(self, words):
        shingles = set()
        for index in range(0, len(words) - (self.shingle_size - 1)):
            shingle = " ".join(words[index:index+self.shingle_size])
            shingles.add(str(CityHash64(shingle)))

        return shingles

    def deduplicate(self, signatures):
        duplicates = []
        for url1, url2 in combinations(signatures.keys(), 2):
            sim = self.jaccard(signatures[url1], signatures[url2])
            if (sim >= self.threshold):
                duplicates.append({
                    'document': url1,
                    'duplicate': url2,
                    'sim': sim    
                })

        return duplicates

    def jaccard(self, minhash1, minhash2):
        matches = len(minhash1.intersection(minhash2))
        length = len(minhash1.union(minhash2))

        return matches / float(length)

    def parseHtml(self, html):
        soup = BeautifulSoup(html, 'lxml')
        
        comments = soup.findAll(text=lambda text:isinstance(text, Comment))
        [comment.extract() for comment in comments]
        [style.decompose() for style in soup.find_all('style')]
        [script.decompose() for script in soup.find_all('script')]

        if soup.body:
            text = soup.body.get_text(" ", strip=True)
        else:
            text = soup.get_text(" ", strip=True)

        remove_chars = dict.fromkeys(map(ord, string.punctuation), u' ')
        text = text.translate(remove_chars)

        return [word for word in text.split(" ") if word.strip()]