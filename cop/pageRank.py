from cop.collection import Collection
from bs4 import BeautifulSoup
import collections
import os

#Create the page ranking of a collection
class PageRank(object):

    def __init__(self, collection_path, err_threshold=0.01, alpha=0.1):

        self.collection_path = collection_path
        self.err_threshold = err_threshold      # convergence error threshold
        self.alpha = alpha                      # teleport probability

        # set a reference to collection processing module
        self.cc = Collection(self.collection_path)
        self.file_list = self.cc.file_list

        # get friendly filenames
        self.friendly_filenames = {}
        for _file in self.file_list:
            self.friendly_filenames[_file] = '.'.join(_file.split('.')[1:])

        # create a dict that all methods can use
        self.node = self.getStructure()

        # get number of files in collection
        self.N = len(self.file_list)

    # get links of the file in file list
    def getLinksOfFile(self, filename):
        links = []

        # open doc xml format
        _file = open( os.path.join(self.collection_path, filename) )
        soup = BeautifulSoup(_file, "lxml")

        # find tag <a> in html page
        for link in soup.find_all('a'):

            # get href data and append in a list
            if link.get('href') not in links:
                links.append(link.get('href'))

        return links

    # get all reference of the file in file list
    def getDocsReferenceFile(self, filename):
        docs = []
        for _file in self.file_list:

            # open doc xml format
            doc = open(os.path.join(self.collection_path, _file))
            soup = BeautifulSoup(doc, "lxml")

            # find tag <a> in html page
            for link in soup.find_all('a'):

                # save doc if reference filename in href data
                if link.get('href') == self.friendly_filenames[filename]:
                    docs.append(_file)
                    break
        return docs

    # mount a structure (dict) of documents with Mi, Li and PR of each one
    def getStructure(self):
        node = {}
        for filename in self.file_list:
            node[filename] = {}
            node[filename].update({'Mi': self.getDocsReferenceFile(filename)})
            node[filename].update({'Li': self.getLinksOfFile(filename)})
            node[filename].update({'PR': 1/len(self.file_list)})
        return node

    # set PR for a node by filename
    def setPRNode(self, filename):
        SumJ = 0

        # complement
        Comp = (1 - self.alpha)

        # for all nodes that reference filename
        for doc in self.node[filename]['Mi']:

            # get values
            PRj = self.node[doc]['PR']
            Lj = len(self.node[doc]['Li'])

            # calc sum
            SumJ += PRj/Lj

        # calc PRi
        PRi = (self.alpha/self.N) + (Comp*SumJ)

        # check if error < error threshold
        if abs(PRi - self.node[filename]['PR']) < self.err_threshold:

            # update PR node
            self.node[filename].update({'PR': PRi})
            return 1

        # else, update node
        self.node[filename].update({'PR': PRi})
        return 0

    # set PRs for all nodes until stabilize
    def finalPageRank(self):
        # control
        check = 0

        # loop to check all error
        while check != 1:
            check = 1

            # for all nodes, calc PR
            for key, values in self.node.items():
                if self.setPRNode(key) == 0 :
                    check = 0

        # sort dict by PR score (reversed)
        self.node = collections.OrderedDict(
            sorted(
                self.node.items(),
                reverse=True,
                key=lambda node: node[1]['PR'])
            )

        # return graph
        return self.node
