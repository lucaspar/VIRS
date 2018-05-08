import os

def getTXTsFromPath(path):
    files  = os.listdir(path)
    txts = [_file for _file in files if _file.lower().endswith(".txt")]
    return txts

def readTXT(path,txt):
    _file = open(path + txt, 'r')
    lines = _file.readlines()
    fileWords = []
    for line in lines :
        words = line.split()
        for word in words :
            word = word.replace(".","")
            word = word.replace(",","")
            fileWords.append(word)
    _file.close()
    return fileWords