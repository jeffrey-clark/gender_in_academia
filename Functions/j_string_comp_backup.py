import re


class StringList(object):
    def __init__(self, input_list=None):
        if input_list == None:
            self.list = []
        else:
            self.list = input_list

        self.word_count = None
        self.letter_count = None

        # run methods
        self.update_count()

    def update_count(self):
        if self.list == None:
            pass
        else:
            self.word_count = len(self.list)
            self.letter_count = len("".join(self.list))

    def append(self, word):
        self.list.append(word)
        self.update_count()

    def remove(self, word):
        self.list.remove(word)
        self.update_count()

    def count(self, word):
        return self.list.count(word)


class SequenceList(StringList):
    def __init__(self, word1_index, word2_index, input_list=None):
        StringList.__init__(self, input_list)
        self.word1_index = word1_index
        self.word2_index = word2_index
        self.s1_start_index = word1_index
        self.s2_start_index = word2_index

    def print_sequence(self):
        print("Sequence found of length:", self.word_count, "start at indices s1:", self.s1_start_index, "and s2:",
              self.s2_start_index)
        print(self.list)


class SC_String(object):
    def __init__(self, input, comp_string):
        self.raw_string = input
        self.clean_string = None
        self.words = StringList()
        # we need to complement list as well, to compute match percentages
        self.comp_list = StringList()
        # list for matched words
        self.matched = StringList()
        self.matched_weak = StringList()
        self.remainder = StringList()
        self.remainder_weak = StringList()

        self.percent_words_matched = None
        self.percent_letters_matched = None
        self.percent_words_matched_weak = None
        self.percent_letters_matched_weak = None

        # run methods
        self.make_word_list(comp_string)

    def make_word_list(self, comp_string):
        # process the main string
        s = self.raw_string.lower().strip()
        c = re.sub(r'[.:;,/\[\]]*', "", s)
        self.clean_string = re.sub(r'\s+', " ", c)
        l = self.clean_string.split(" ")
        while True:
            if "" in l:
                l.remove("")
            else:
                break
        self.words = StringList(l)

        # process the comparison string
        s = comp_string.lower().strip()
        c = re.sub(r'[.:;,/\[\]]*', "", s)
        l = re.sub(r'\s+', " ", c).split(" ")
        while True:
            if "" in l:
                l.remove("")
            else:
                break
        self.comp_list = StringList(l)

    def calculate_match(self):
        self.percent_words_matched = 100 * self.matched.word_count / self.comp_list.word_count
        self.percent_letters_matched = 100 * self.matched.letter_count / self.comp_list.letter_count
        self.percent_words_matched_weak = 100 * self.matched_weak.word_count / self.comp_list.word_count
        self.percent_letters_matched_weak = 100 * self.matched_weak.letter_count / self.comp_list.letter_count


class String_Comparison(object):

    def __init__(self, s1, s2, allowed_spelling_mistakes, allowed_sequence_mistakes):
        self.s1 = SC_String(s1, s2)
        self.s2 = SC_String(s2, s1)
        self.allowed_spelling_mistakes = allowed_spelling_mistakes
        self.allowed_sequence_mistakes = allowed_sequence_mistakes
        self.matched_both = StringList()
        self.exact_match = None
        # self.sequences is a list containing StringLists of matched sequences
        self.sequences = []

        self.subset = None
        # subset_weak allows for specified spelling and sequence mistakes
        self.subset_weak = None
        self.max_percent_words_matched = None
        self.max_percent_letters_matched = None
        self.max_percent_words_matched_weak = None
        self.max_percent_letters_matched_weak = None

        # run methods
        self.check_matches()
        self.calculate_matches()
        # self.both_word = []

    def new_sequence(self):
        self.sequences.append(StringList())
        return self.sequences[-1]

    def check_matches(self):
        # first we compute the exact match result
        if self.s1.clean_string == self.s2.clean_string:
            self.exact_match = True
        else:
            self.exact_match = False

        # first strict computations

        # now we loop through all the words in string 1
        for word in self.s1.words.list:
            # compare the word iteratively with all words in string 2
            if word in self.s2.words.list:
                word_count_in_str2 = self.s2.words.list.count(word)
                word_count_in_matched = self.s1.matched.count(word)
                # if the word is matched then append it to the matched list. However, we control in a conditional
                # that the word already has not been matched
                if word_count_in_matched < word_count_in_str2:
                    self.s1.matched.append(word)
                    # also append the word to the matched_both list, a property of the String_comparison
                    self.matched_both.append(word)
                else:
                    # if the word has already matched to the number of occurances in str2, then add to remainder
                    self.s1.remainder.append(word)
            else:
                # if the word is not matched, add it to the remainder of string 1
                self.s1.remainder.append(word)

        for word in self.s2.words.list:
            if word in self.s1.words.list:
                self.s2.matched.append(word)
            else:
                self.s2.remainder.append(word)

        # now weak computations
        self.s1.matched_weak = StringList(self.s1.matched.list.copy())
        self.s1.remainder_weak = StringList(self.s1.remainder.list.copy())
        self.s2.matched_weak = StringList(self.s2.matched.list.copy())
        self.s2.remainder_weak = StringList(self.s2.remainder.list.copy())

        shorter_list = None
        longer_list = None

        weak_candidates = []
        for word1 in self.s1.remainder.list:
            for word2 in self.s2.remainder.list:
                l1 = list(word1)
                l2 = list(word2)
                if abs(len(l1) - len(l2)) <= 2:
                    if len(l1) >= len(l2):
                        shorter_list = l2
                        longer_list = l1
                    elif len(l2) > len(l1):
                        shorter_list = l1
                        longer_list = l2
                    diff = len(longer_list) - len(shorter_list)

                    mistakes_combos = []
                    for j in range(0, diff + 1):
                        start_index = j
                        # print("new combo, start index", start_index)
                        mistakes = 0
                        for i in range(0, len(longer_list)):
                            if i < start_index:
                                # print("buffer")
                                mistakes = mistakes + 1
                            else:
                                try:
                                    shorter_letter = shorter_list[i - start_index]
                                except:
                                    shorter_letter = ""
                                try:
                                    longer_letter = longer_list[i]
                                except:
                                    longer_letter = ""
                                # print("words are:", word1, word2, "longer letter is", longer_letter, "short letter is", shorter_letter)
                                if longer_letter != shorter_letter:
                                    mistakes = mistakes + 1

                        # print("mistakes:", mistakes)
                        if mistakes <= self.allowed_spelling_mistakes:
                            mistakes_combos.append({'word1': word1, 'word2': word2,
                                                    'mistakes': mistakes})

                    mistake_combos = sorted(mistakes_combos, key=lambda i: i['mistakes'])
                    if len(mistake_combos) > 0:
                        weak_candidates.append(mistake_combos[0])

        # now we sort the candidates with strongest first
        weak_candidates = sorted(weak_candidates, key=lambda i: i['mistakes'])
        # print('weak candidates are', weak_candidates)

        # now we remove the strongest of the weak candidates in an interative loop
        for c in weak_candidates:
            if c['word1'] in self.s1.remainder_weak.list and c['word2'] in self.s2.remainder_weak.list:
                self.s1.remainder_weak.remove(c['word1'])
                self.s2.remainder_weak.remove(c['word2'])
                self.s1.matched_weak.append(c['word1'])
                self.s2.matched_weak.append(c['word2'])

        ###############
        ## NEW CODE  ##
        ###############

        # new address sequence in separate loops to keep things understandable
        word1_index = 0
        word2_index = 0
        for word1 in self.s1.words.list:
            for word2 in self.s2.words.list:
                for seq in self.sequences:
                    # now if both og the current loop indices are 1 more than the indices stored in the SequenceList,
                    # then we append to the sequence object
                    if (word1_index == seq.word1_index + 1) and (word2_index == seq.word2_index + 1):
                        if word1 == word2:
                            seq.append(word1)
                            seq.word1_index = seq.word1_index + 1
                            seq.word2_index = seq.word2_index + 1
                if word1 == word2:
                    self.sequences.append(SequenceList(word1_index, word2_index, [word1]))
                word2_index += 1
            word1_index += 1
            word2_index = 0

        # now we need to reduce sequences, i.e eliminate sequences that are subsets of other sequences
        reduced_sequences = self.sequences.copy()
        print("reduced sequences are", reduced_sequences)
        for seq1 in self.sequences:
            for seq2 in self.sequences:
                if seq1.list == seq2.list:
                    pass
                elif set(seq1.list).issubset(set(seq2.list)):
                    if seq1 in reduced_sequences:
                        reduced_sequences.remove(seq1)
                elif set(seq2.list).issubset(set(seq1.list)):
                    if seq2 in reduced_sequences:
                        reduced_sequences.remove(seq2)
        self.sequences = reduced_sequences.copy()

    def calculate_matches(self):
        self.s1.calculate_match()
        self.s2.calculate_match()

        # compute subsets
        if self.s1.percent_words_matched == 100 or self.s2.percent_words_matched == 100:
            self.subset = True
        else:
            self.subset = False

        if self.s1.percent_words_matched_weak == 100 or self.s2.percent_words_matched_weak == 100:
            self.subset_weak = True
        else:
            self.subset_weak = False

        # compute max match scores between the two strings
        if self.s1.percent_words_matched >= self.s2.percent_words_matched:
            self.max_percent_words_matched = self.s1.percent_words_matched
        else:
            self.max_percent_words_matched = self.s2.percent_words_matched

        if self.s1.percent_letters_matched >= self.s2.percent_letters_matched:
            self.max_percent_letters_matched = self.s1.percent_letters_matched
        else:
            self.max_percent_letters_matched = self.s2.percent_letters_matched

        if self.s1.percent_words_matched_weak >= self.s2.percent_words_matched_weak:
            self.max_percent_words_matched_weak = self.s1.percent_words_matched_weak
        else:
            self.max_percent_words_matched_weak = self.s2.percent_words_matched_weak

        if self.s1.percent_letters_matched_weak >= self.s2.percent_letters_matched_weak:
            self.max_percent_letters_matched_weak = self.s1.percent_letters_matched_weak
        else:
            self.max_percent_letters_matched_weak = self.s2.percent_letters_matched_weak

    def print_analysis(self):
        print('\nSTRING COMPARISON ANALYSIS')
        print("\nString 1:", self.s1.raw_string, "\nString 2", self.s2.raw_string)

        print("\nCleanString 1:", self.s1.clean_string, "\nCleanString 2", self.s2.clean_string)

        print("\nList 1:", self.s1.words.list, "\nString 2", self.s2.words.list)

        print("\nList 1: word count:", self.s1.words.word_count, "letter count:", self.s1.words.letter_count,
              "\nList 2: word count:", self.s2.words.word_count, "letter count:", self.s2.words.letter_count)

        print("\nMatched:", self.matched_both.list)

        print("\nRemainder 1:", self.s1.remainder.list, "\nRemainder 2:", self.s2.remainder.list)

        print("\nMatched Weak 1:", self.s1.matched_weak.list, "\nMatched Weak 2:", self.s2.matched_weak.list)

        print("\nRemainder Weak 1:", self.s1.remainder_weak.list, "\nRemainder Weak 2:", self.s2.remainder_weak.list)

        print("\nMatch results String 1")
        print("Percent words:", self.s1.percent_words_matched, "weak:", self.s1.percent_words_matched_weak)
        print("Percent letters:", self.s1.percent_letters_matched, "weak:", self.s1.percent_letters_matched_weak)
        print("\nMatch results String 2")
        print("Percent words:", self.s2.percent_words_matched, "weak:", self.s2.percent_words_matched_weak)
        print("Percent letters:", self.s2.percent_letters_matched, "weak:", self.s2.percent_letters_matched_weak)

        print("\nsubset:", self.subset, "subset_weak:", self.subset_weak)
        print("\nmax percent words:", self.max_percent_words_matched, "\nmax percent words weak:",
              self.max_percent_words_matched_weak)
        print("max percent letters:", self.max_percent_letters_matched, "\nmax percent letters weak:",
              self.max_percent_letters_matched_weak)

        print("\nSequence Report:\n")
        for seq in self.sequences:
            seq.print_sequence()


if __name__ == "__main__":
    # s1 = "Gimeno LA, Calderón A, Prados A, Revilla C, Diaz E. Patterns of pharmaceutical use for immigrants to Spain and Norway: a comparative study of prescription databases in two European countries. Int J Equity Health 2016;24;15(1):32. IF: 1.80"
    # s2 = "LAND MOBILE RADIO"
    # x = String_Comparison(s1, s2, 2)
    # x.print_analysis()
    #
    # s3 = "(*) Calderón A, Diaz E, Poblador B, Gimeno LA, Abad JM, Prados A. Non-adherence to antihypertensive medication: the role of mental and physical comorbidity. Int J Cardiol 2016;15;207:310-6. IF: 4.04"
    # s4 = "Non-adherence to antihypertensive medication: The role of mental and physical comorbidity"
    # x = String_Comparison(s3, s4, 2)
    # x.print_analysis()

    # s1 = "Gimeno LA, Calderón A, Prados A, Revilla C, Diaz E. Patterns of pharmaceutical use for immigrants to Spain and Norway: a comparative study of prescription databases in two European countries. Int J Equity Health 2016;24;15(1):32. IF: 1.80"
    # s2 = "Observation of a New Xi(b) Baryon"
    s1 = "A text of happiness"
    s2 = "a tept of happines"

    x = String_Comparison(s1, s2, 2, 1)
    x.print_analysis()