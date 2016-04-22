import os, lucene, json
from app import app
from app.database import store_outlinks
from bs4 import BeautifulSoup, Comment
from java.io import File
from org.apache.lucene.analysis.core import StopFilter
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.document import Document, Field, StringField, TextField
from org.apache.lucene.index import IndexWriter, IndexWriterConfig
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.util import Version

class IndexFiles(object):

    def __init__(self, indexDir):
        if not os.path.exists(indexDir):
            os.mkdir(indexDir)

        store = SimpleFSDirectory(File(indexDir))

        analyzer = StandardAnalyzer(Version.LUCENE_CURRENT)

        config = IndexWriterConfig(Version.LUCENE_CURRENT, analyzer)
        config.setOpenMode(IndexWriterConfig.OpenMode.CREATE_OR_APPEND)
        
        self.writer = IndexWriter(store, config)

    def index(self, file, duplicates):
        exact = [duplicate['duplicate'] for duplicate in duplicates if duplicate['sim'] == 1]
        near = [duplicate['duplicate'] for duplicate in duplicates if duplicate['sim'] < 1]

        with open(file) as file:
            for document in file:
                data = json.loads(document)
                if (data['url'] in exact):
                    continue

                doc = self.createDoc(data['url'], data['html'], data['url'] in near)
                self.writer.addDocument(doc)
                store_outlinks(data['url'], data['outlinks'])

    	self.writer.commit()

        return self.writer.numDocs()

    def createDoc(self, url, html, duplicate):
        title, contents = self.parseHtml(url, html)

        doc = Document()
        doc.add(StringField("title", title, Field.Store.YES))
        doc.add(StringField("url", url, Field.Store.YES))
        doc.add(StringField("duplicate", str(duplicate).lower(), Field.Store.YES))

        if len(contents) > 0:
            doc.add(TextField("contents", contents, Field.Store.YES))
        else:
            print "Warning: No content in %s" % url

        return doc

    def close(self):
    	self.writer.close()

    def parseHtml(self, url, html):
        soup = BeautifulSoup(html, 'lxml')
        title = self.getTitle(url, soup)
        body = self.getBody(soup)

        return title, body

    def getTitle(self, url, soup):
        if soup.title:
            title = soup.title.get_text().strip()
        elif soup.find("h1"):
            title = " ".join(soup.find("h1").get_text().split())
        else:
            title = url.split("/")[-1]

        return title

    def getBody(self, soup):
        comments = soup.findAll(text=lambda text:isinstance(text, Comment))
        [comment.extract() for comment in comments]
        [style.decompose() for style in soup.find_all('style')]
        [script.decompose() for script in soup.find_all('script')]

        if soup.body:
            return soup.body.get_text(" ", strip=True)
        else:
            return soup.get_text(" ", strip=True)