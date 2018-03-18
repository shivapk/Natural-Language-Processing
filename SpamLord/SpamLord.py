import sys
import os
import re
import pprint

dot = '\s*(?:\.|\s+dom\s+|\s+do?t\s+|;)\s*'
username = '(\w+(?:' + '(?:\.|;)' + '\w+)*)'
server = '(\w+(?:' + '(?:\.|\s+dom\s+|\s+do?t\s+|;|\s+)' + '\w+)*)'
at = '\s*(?:@|\s+where\s+|\s\(?at\)?|\(at\)|&.*;)\s*'
my_first_pat = username + '(?:\s*\(follow.*by.*?)?'+ at + server + dot + '(edu|com|org|net|gov)(?:[\W\b]|\Z)'
special_email = 'obfuscate\(\'' + server + dot + '(edu|com|org|net|gov)' + '\',\'' + username + '\'\);'
no_dot_email =  username + at + '(\w+ \w+) ' + '(edu|com|org|net|gov)(?:[\W\b]|\Z)'

phone_del = '(?:(?:-|\(|\)|&.*?;)|\s+)'
phone_pat = '\(?(\d{3})\)?' + phone_del + '(\d{3})' + phone_del + '(\d{4})\D'

"""
This function takes in a filename along with the file object (actually
a StringIO object at submission time) and
scans its contents against regex patterns. It returns a list of
(filename, type, value) tuples where type is either an 'e' or a 'p'
for e-mail or phone, and value is the formatted phone number or e-mail.
The canonical formats are:
     (name, 'p', '###-###-#####')
     (name, 'e', 'someone@something')
If the numbers you submit are formatted differently they will not
match the gold answers

"""
def process_file(name, f):
    res = []
    for line in f:
        phone_line = line;
        line = line.lower().replace("-","")
        line = line.replace("lt;", "")
        matches = re.findall(my_first_pat,line, flags=re.I)
        for m in matches:
            m = (m[0].strip(),m[1].replace(" dot ", ".").replace(" dom ", ".").replace(" dt ", ".").replace(" ",".").replace(";",".").strip(), m[2])
            if (m[0].lower() == "server"):
                continue
            email = '%s@%s.%s' % m
            res.append((name,'e',email))
        matches = re.findall(special_email, line, flags=re.I)
        for m in matches:
            email = '%s@%s.%s' % (m[2], m[0], m[1])
            res.append((name,'e',email))
        matches = re.findall(no_dot_email,line, flags=re.I)
        for m in matches:
            m = (m[0].strip(),m[1].replace(" dot", " ").replace(" dt", " ").replace(" dom", " ").replace(";",".").strip().replace(" ","."), m[2])
            email = '%s@%s.%s' % m
            res.append((name,'e',email))
        matches = re.findall(phone_pat, phone_line, flags=re.I)
        for m in matches:
            phone = '%s-%s-%s' % m
            res.append((name,'p', phone))
    return res


def process_dir(data_path):
    # get candidates
    guess_list = []
    for fname in os.listdir(data_path):
        if fname[0] == '.':
            continue
        path = os.path.join(data_path,fname)
        f = open(path,'r')
        f_guesses = process_file(fname, f)
        guess_list.extend(f_guesses)
    return guess_list


def get_gold(gold_path):
    # get gold answers
    gold_list = []
    f_gold = open(gold_path,'r')
    for line in f_gold:
        gold_list.append(tuple(line.strip().split('\t')))
    return gold_list


def score(guess_list, gold_list):
    guess_list = [(fname, _type, value.lower()) for (fname, _type, value) in guess_list]
    gold_list = [(fname, _type, value.lower()) for (fname, _type, value) in gold_list]
    guess_set = set(guess_list)
    gold_set = set(gold_list)

    tp = guess_set.intersection(gold_set)
    fp = guess_set - gold_set
    fn = gold_set - guess_set

    pp = pprint.PrettyPrinter()
    #print 'Guesses (%d): ' % len(guess_set)
    #pp.pprint(guess_set)
    #print 'Gold (%d): ' % len(gold_set)
    #pp.pprint(gold_set)
    print ('True Positives (%d): ' % len(tp))
    pp.pprint(tp)
    print ('False Positives (%d): ' % len(fp))
    pp.pprint(fp)
    print ('False Negatives (%d): ' % len(fn))
    pp.pprint(fn)
    print ('Summary: tp=%d, fp=%d, fn=%d' % (len(tp),len(fp),len(fn)))


def main(data_path, gold_path):
    guess_list = process_dir(data_path)
    gold_list =  get_gold(gold_path)
    score(guess_list, gold_list)


if __name__ == '__main__':
    if (len(sys.argv) == 1):
        main('../data/dev', '../data/devGOLD')
    elif (len(sys.argv) == 3):
        main(sys.argv[1],sys.argv[2])
    else:
        print ('usage:\tSpamLord.py <data_dir> <gold_file>')
        sys.exit(0)
