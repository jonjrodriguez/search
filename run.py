import argparse, lucene, os, shutil
from app import app
from app.database import init_db, query_db, store_duplicates
from app.search.indexer import IndexFiles
from app.search.minhash import MinHash
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

def init(args):
    init_db(app.config['ADMIN_USER'])

    indexDir = app.config['INDEX_PATH']

    if os.path.exists(indexDir):
        shutil.rmtree(indexDir)

def crawl(args):
    process = CrawlerProcess(get_project_settings())
    process.crawl('crawler')
    process.start()

def index(args):
    if args.file:
        file = args.file
    else:
        file = query_db("select * from crawls order by crawl_date desc", [], True)['filepath']

    print "Indexing ", file

    minHash = MinHash(app.config['SHINGLE_SIZE'], app.config['PERMUTATIONS'], app.config['DUPLICATE_THRESHOLD'])
    duplicates = minHash.findDuplicates(file)

    print "Storing documents"
    store_duplicates(duplicates)

    indexer = IndexFiles(app.config['INDEX_PATH'])

    try:
        numIndexed = indexer.index(file, duplicates)
    except Exception, e:
        print "Failed: ", e
        raise e
    else:
        indexer.close()

    print "Indexed %i documents" % numIndexed

def serve(args):
    app.run()

if __name__ == '__main__':
    lucene.initVM(vmargs=['-Djava.awt.headless=true'])

    parser = argparse.ArgumentParser(description='Course Project: Search Engine with Near-Duplicate Detection')
    parser.add_argument('method', choices=['init', 'crawl', 'index', 'serve'], help='The functionality you wish to invoke')
    parser.add_argument('--file', help='The file to index')
    args = parser.parse_args()

    switcher = {
        'init': init,
        'crawl': crawl,
        'index': index,
        'serve': serve
    }

    func = switcher.get(args.method)
    func(args)