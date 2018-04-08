from collections import *

def build_tree(score, back, sentence, i, j):
    print "SPAN: ", " ".join(sentence[i:j])
    for key in score[i][j]:
        if score[i][j][key]:
            print "P({0}) = {1}".format(key, score[i][j][key]),
            if key in back[i][j]:
                value = back[i][j][key]
                if isinstance(value, tuple):
                    print "(BackPointer = ({0}))".format(','.join(map(str, value))),
                else:
                    print "(BackPointer = {0})".format(value),
            print ""
    print ""

def CKY(grammar_list, word_list):
    print "PROCESSINGS SENTENCE", ' '.join(word_list)
    # for A->BC
    non_terms = defaultdict(list)
    # for A->fish
    terms = defaultdict(list)
    # for A->B
    unaries = defaultdict(list)
    for grammar in grammar_list:
        prob = float(grammar[-1])
        lhs = grammar[0]
        if len(grammar) == 3:
            rhs = grammar[1]
            if rhs.islower():
                terms[lhs].append((rhs, prob))
            else:
                unaries[lhs].append((rhs, prob))
        else:
            rhs_pairs = grammar[1:-1]
            non_terms[lhs].append((rhs_pairs, prob))

    score = [[ defaultdict(float) for _ in xrange(len(word_list)+1)] for _ in xrange(len(word_list))]

    back = [[ {} for _ in xrange(len(word_list)+1)] for _ in xrange(len(word_list))]

    for i in xrange(len(word_list)):
        for A in terms:
            for B, prob in terms[A]:
                if B == word_list[i]:
                    score[i][i+1][A] = prob
        added = True
        while added:
            added = False
            for A in unaries:
                for B, prob in unaries[A]:
                    if score[i][i+1][B] > 0:
                        new_prob = prob * score[i][i+1][B]
                        if new_prob > score[i][i+1][A]:
                            score[i][i+1][A] = new_prob
                            back[i][i+1][A] = B
                            added = True
        build_tree(score, back, word_list, i, i+1)

    for span in xrange(2, len(word_list)+1):
        for begin in xrange(len(word_list)+1 - span):
            end = begin + span
            for split in xrange(begin+1, end):
                for A in non_terms:
                    for ((B,C), prob) in non_terms[A]:
                        new_prob = score[begin][split][B] * score[split][end][C] * prob
                        if new_prob > score[begin][end][A]:
                            score[begin][end][A] = new_prob
                            back[begin][end][A] = (split, B, C)
            added = True
            while added:
                added = False
                for A in unaries:
                    for B, prob in unaries[A]:
                        new_prob = prob * score[begin][end][B]
                        if new_prob > score[begin][end][A]:
                            score[begin][end][A] = new_prob
                            back[begin][end][A] = B
                            added = True
            build_tree(score, back, word_list, begin, end)


def main():
   import sys
   args = sys.argv
   if len(args) < 2:
       print "Please provide grammar file and the sentence file as command line inputs"
       return
   grammar_filename, sentence_filename = args[1], args[2]
   with open(grammar_filename, 'r') as gf, open(sentence_filename, 'r') as sf:
       grammar = gf.read()
       sentences = sf.read()
       grammar_list = [ g.split() for g in grammar.splitlines()]
       sentence_list = [ s.split() for s in sentences.splitlines()]
       [CKY(grammar_list, sent) for sent in sentence_list]

if __name__ == '__main__':
    main()