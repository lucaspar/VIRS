#from cop.collection import Collection
from bs4 import BeautifulSoup
from collections import deque
import os

#Create the page ranking of a collection
class pageRanking(object):

    def __init__(self, collection_path):

        # set collection path
        self.collection_path = collection_path
       
        # set a reference to collection processing module

        #TODO remove #
        #self.cc = Collection(self.collection_path)
        #self.file_list = self.cc.file_list
        #---------------------------------------------

        #TODO delete
        self.file_list = self.getFileList()
        #---------------------------------------------


    #TODO: remove and use for collection.py
    # Get a file list from @path
    def getFileList(self):
        files  = os.listdir(self.collection_path)
        texts = [_file for _file in files]
        return texts
    #----------------------------------------


    #Get links of the file in file list
    def getLinksOfFile(self, filename): 
        _file = open(self.collection_path + filename)
        soup = BeautifulSoup(_file, "lxml")
        
        links = []
        for link in soup.find_all('a'):
            if link.get('href') not in links:
                links.append(link.get('href'))
        return links
    
    #Get all reference of the file in file list
    def getDocsReferenceFile(self, filename):
        docs = []
        for _file in self.file_list:
            doc = open(self.collection_path +_file)
            soup = BeautifulSoup(doc, "lxml")
            for link in soup.find_all('a'):
                if link.get('href') == filename:
                    docs.append(_file)
                    break
        return docs

    #Mount a structure (dict) of documents with Mi, Li and PR of each one
    def getStructure(self):
        docs = {}
        for filename in self.file_list:
            docs[filename] = deque([])
            docs[filename].append(('Mi', self.getDocsReferenceFile(filename)))
            docs[filename].append(('Li', self.getLinksOfFile(filename)))
            docs[filename].append(('PR', 1/len(self.file_list)))
        return docs

    

pg = pageRanking("../uploads/collections/teste/")
docs = pg.getStructure()
for key, values in docs.items():
    print(key)
    for value in values:
        print (value)
    print('-------------------------------------------------------')