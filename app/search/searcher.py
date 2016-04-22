import lucene, math
from app import app
from java.io import File, StringReader
from org.apache.lucene.analysis.core import StopFilter
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.index import DirectoryReader, Term
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.search import IndexSearcher, BooleanClause, BooleanQuery, TermQuery, TopScoreDocCollector
from org.apache.lucene.search.highlight import Highlighter, QueryScorer, SimpleFragmenter
from org.apache.lucene.util import Version

class SearchIndex(object):

    def __init__(self):
        vm_env = lucene.getVMEnv()
        vm_env.attachCurrentThread()

        indexDir = SimpleFSDirectory(File(app.config['INDEX_PATH']))
        self.searcher = IndexSearcher(DirectoryReader.open(indexDir))

        self.analyzer = StandardAnalyzer(Version.LUCENE_CURRENT)

        self.parser = QueryParser(Version.LUCENE_CURRENT, "contents", self.analyzer)


    def search(self, q, page = 1, duplicates = False):
        query = self.parser.parse(q)

        if not duplicates:
            query = self.addDuplicatesQuery(query)
        
        perPage = 10
        start = (page - 1) * perPage

        results = TopScoreDocCollector.create(1000, True)
        self.searcher.search(query, results)

        highlighter = Highlighter(QueryScorer(query))
        highlighter.setTextFragmenter(SimpleFragmenter(40))

        docs = []
        for scoreDoc in results.topDocs(start, perPage).scoreDocs:
            doc = self.searcher.doc(scoreDoc.doc)
            tokenStream = self.analyzer.tokenStream("contents", StringReader(doc['contents']))
            highlight = highlighter.getBestFragments(tokenStream, doc['contents'], 3, "...")
            
            docs.append({
                'title': doc['title'],
                'url': doc['url'],
                'duplicate': doc['duplicate'],
                'highlight': highlight}
            )

        del self.searcher
        
        totalPages = int(math.ceil(results.getTotalHits()/float(perPage)))

        return totalPages, docs

    def addDuplicatesQuery(self, query):
        not_duplicate = TermQuery(Term('duplicate', 'false'))
        booleanQuery = BooleanQuery()
        booleanQuery.add(not_duplicate, BooleanClause.Occur.MUST)
        booleanQuery.add(query, BooleanClause.Occur.MUST)
        return booleanQuery