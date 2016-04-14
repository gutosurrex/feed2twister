# -*- coding: utf-8 -*-

import os
import random

main_dir = os.path.split(os.path.abspath(__file__))[0]


class LoremIpsum(object):
    MIN_WORDS = 2
    MAX_WORDS = 15

    def __init__(self):
        self.words = set()

        with open(os.path.join(main_dir, 'lorem_ipsum.txt'), 'r') as f:
            for word in f:
                word = word.strip()
                self.words.add(word)

        self.words = frozenset(self.words)

    def get_sentence(self):
        """
        :returns: string with sentence
        :rtype: str
        """
        return self.get_sentences_list()[0]

    def get_sentences_list(self, sentences=1):
        """
        :param int sentences: how many sentences
        :returns: list of strings with sentence
        :rtype: list
        """
        if sentences < 1:
            raise ValueError('Param "sentences" must be greater than 0.')

        sentences_list = []

        while sentences:
            num_rand_words = random.randint(self.MIN_WORDS, self.MAX_WORDS)
            random_sentence = self.make_sentence(random.sample(self.words, num_rand_words))
            sentences_list.append(random_sentence)
            sentences -= 1
        return sentences_list

    def get_sentences(self, sentences=1):
        """
        :param int sentences: how many sentences
        :returns: string with sentences
        :rtype: str
        """
        return ' '.join(self.get_sentences_list(sentences))

    def make_sentence(self, list_words):
        """Make a sentence from list of words

        :param list list_words: list of words
        :returns: sentence
        :rtype: str
        """
        lw_len = len(list_words)
        if lw_len > 6:
            list_words.insert(lw_len / 2 + random.choice(xrange(-2, 2)), ',')
        sentence = ' '.join(list_words).replace(' ,', ',')
        return sentence[0].upper() + sentence[1:] + '.'
