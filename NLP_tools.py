import os
import string
import re
import time
import paths
import random
import collections


class NLP(object):
    def __init__(self,data_type,label_type,data_path):
        self.datasets = ['msra','resume','weibo','renmin']
        self.labelsets = ['bmes','bio','bioes']
        self.chinese_punc = '！？｡＂＃＄％＆＇（）＊＋，－／：；＜＝＞＠［＼］＾＿｀｛｜｝～｟｠｢｣､、〃》「」『』【】〔〕〖〗〘〙〚〛〜〝〞〟〰〾〿–—‘’‛“”„‟…‧﹏.'
        self.data_type = data_type
        self.label_type = label_type
        self.data_path = data_path
        self.lexicon_path = paths.word_path
        self.global_tree = Tree()
        self.local_tree = Tree()

        if self.data_type not in self.datasets:
            raise Exception('Data type must be one of msra/resume/weibo/renmin, got '+self.data_type)
        if self.lable_type not in self.lablesets:
            raise Exception('Label type must be one of bmes/bio/bioes, got '+ self.label_type)

        self.global_lexicon,self.local_lexicon = self.load_lexicon()

    def reform_data(self):
        """
        Only msra dataset is supported.
        """
        train_path = "./train1.txt"
        test_path = "./testright1.txt"

        train_bmes = "./train.char.bmes"
        test_bmes = "./test.char.bmes"

        ftrain = open(paths.msra_path+train_path, "r", encoding="utf-8")
        fbmes = open(paths.msra_path+train_bmes, "w", encoding="utf-8")

        ftest = open(paths.msra_path+test_path, "r", encoding="utf-8")
        testbmes = open(paths.msra_path+test_bmes, "w", encoding="utf-8")
        if self.data_type == 'msra' and self.label_type == 'bmes':
            lines = ftrain.readlines()
            for line in lines:
                line = line.strip()
                words = line.split()
                for traindata in words:
                    char_lable = traindata.split("/")
                    index = 0

                    for i in char_lable[0]:
                        if i in ['。', '！', '？'] and char_lable[1].lower() == "o":
                            fbmes.write(i + ' S-' + char_lable[1].upper() + '\n')
                        elif char_lable[1] == "o":
                            if len(char_lable[0]) == 1:
                                fbmes.write(i + ' S-' + char_lable[1].upper() + '\n')
                            else:
                                if i == char_lable[0][0] and index == 0:
                                    fbmes.write(i + ' B-' + char_lable[1].upper() + '\n')
                                    index += 1

                                elif i == char_lable[0][-1] and index == len(char_lable[0]) - 1:
                                    fbmes.write(i + ' E-' + char_lable[1].upper() + '\n')

                                else:
                                    fbmes.write(i + ' M-' + char_lable[1].upper() + '\n')
                                    index += 1

                        else:
                            if len(char_lable[0]) == 1:
                                fbmes.write(i + ' S-' + char_lable[1].upper() + '\n')
                            elif i == char_lable[0][0]:
                                fbmes.write(i + ' B-' + char_lable[1].upper() + '\n')
                                index += 1

                            elif i == char_lable[0][-1]:
                                fbmes.write(i + ' E-' + char_lable[1].upper() + '\n')

                            else:
                                fbmes.write(i + ' M-' + char_lable[1].upper() + '\n')
                                index += 1

                fbmes.write('\n')
                print("msra training data is done at "+train_bmes)
        else:
          raise Exception('Only msra and bmes is supported now!')

    def insert_search_tree(self):
        for global_word in self.global_lexicon:
            self.global_tree.insert(global_word)

        for local_word in self.local_lexicon:
            self.local_tree.insert(local_word)


    def get_BMES_freq(self,sentence):
        """
        Matching local lexicon in the given sentence and return a sequence of (B M E S) frequence.
        :param sentence:
        :return:
        """

        char_freq = []
        for i in sentence:
            if i == sentence[0]:
                char_freq.append([1, 0, 0, 0])
            elif i == sentence[-1]:
                char_freq.append([0, 0, 1, 0])
            elif i in self.chinese_punc:
                char_freq.append([0, 0, 0, 1])
            else:
                B = 0
                M = 0
                E = 0
                S = 0


                char_freq.append([B, M, E, S])
        return char_freq

    def add_segment_lexicon(self,word_freq):
        """
        Add words to local_lexicon.
        :param word_freq: How many times the word occurred
        :return:
        """
        file = paths.chinese_seg_path
        lexicon = []
        with open(paths.word_path, "r", encoding="utf-8") as g:
            ls = g.readlines()
            for line in ls:
                if line != '\n':
                    word = line.split()[0]
                    lexicon.append(word)
        f = open(file, "r", encoding="utf-8")
        lines = f.readlines()
        local_lexicon = {}
        f.close()
        for line in lines:
            words = line.split()
            for word in words:
                if word not in local_lexicon.keys():
                    local_lexicon[word] = 1
                else:
                    local_lexicon[word] = local_lexicon[word] + 1
        #static frequence of word
        with open(paths.local_lexicon, "a", encoding="utf-8") as f:
            for word in local_lexicon.keys():
                if (word not in lexicon) and len(word) > 1 and local_lexicon[word] > word_freq:
                    f.write(word+" 0.0 \n")
                    #add word to local_lexicon without embedding (No need for my work)


    def load_lexicon(self):
        global_lexicon = []
        with open(paths.word_path, "r", encoding="utf-8") as g:
            ls = g.readlines()
            for line in ls:
                if line != '\n':
                    word = line.split()[0]
                    global_lexicon.append(word)
        local_lexicon=[]
        with open(paths.local_lexicon, "r", encoding="utf-8") as g:
            ls = g.readlines()
            for line in ls:
                if line != '\n':
                    word = line.split()[0]
                    local_lexicon.append(word)
        return global_lexicon, local_lexicon

















class TreeNode(object):
    def __init__(self):
        self.children = collections.defaultdict(TreeNode)
        self.is_w = False



class Tree(object):
    def __init__(self):
        self.root = TreeNode()

    def insert(self,w):
        current = self.root
        for c in w:
            current = current.children[c]
        current.is_w = True


    def search(self,w):
        current = self.root
        for c in w:
            current = current.children.get(c)
            if current is None:
                return -1

        if current.is_w:
            return 1
        else:
            return 0

    def get_lexicon(self, sentence):
        matching = []
        for i in range(len(sentence)):
            current = self.root
            for j in range(i, len(sentence)):
                current = current.children.get(sentence[j])
                if current is None:
                    break
                if current.is_w:
                    matching.append(sentence[i:j + 1])
        return matching




