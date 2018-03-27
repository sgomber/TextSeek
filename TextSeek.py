from math import log, sqrt
from collections import defaultdict
import nltk
import sys,os
from stat import *
reload(sys)
sys.setdefaultencoding("ISO-8859-1")

# Preprocess all the files in directory and store them as dictionary vectors
def iterate_over_all_docs():
	global nos_of_documents

	for filenames in os.listdir(a):

		with open(os.path.join(a, filenames)) as myfile:
			if filenames[-4:]!=".swp":
				nos_of_documents+=1
				content = myfile.read()
				token_list = get_tokenized_and_normalized_list(content)
				vect = create_vector(token_list)
				vects_for_docs.append(vect)
def ammend(l):
    for z in l:
        with open(os.path.join(a,z[0])) as mf:
            cont = mf.read()
            tl = get_tokenized_and_normalized_list(cont)
            v = create_vector(tl)
            v_length = 0.0

            for word1 in v:
	            word_frequ = v[word1]
	            tempu = calc_tf_idf(word1, word_frequ)
	            v[word1] = tempu
	            v_length += tempu**2
            for word1 in v:
            	v[word1] /= sqrt(v_length)

            vects_for_docs[z[1]]=v

# This function returns a list of tokenized words of any text
def get_tokenized_and_normalized_list(d):
    tokens = nltk.word_tokenize(d)
    stemmed = []
    for words in tokens:
        stemmed.append(words.lower())
    return stemmed

# Creates a vector storing (Word:Frequency) from the list of words in a file
def create_vector(l1):
    vect = {}  
    global document_freq_vect

    for token in l1:
        if token in vect:
            vect[token] += 1
        else:
            vect[token] = 1
            if token in document_freq_vect:
                document_freq_vect[token] += 1
            else:
                document_freq_vect[token] = 1
    return vect

# Creates a vector storing (Word:Frequency) from the list of words in a query
def create_vector_from_query(l1):
    vect = {}
    for token in l1:
        if token in vect:
            vect[token] += 1.0
        else:
            vect[token] = 1.0
    return vect

# Stores file of occurence for each word
def generate_inverted_index():
    count1 = 0
    for vector in vects_for_docs:
        for word1 in vector:
            inverted_index[word1].append(count1)
        count1 += 1

# Prints the line numbers of occurence of words in query in a given file
def get_lines(s,q,p,alt):
    if alt!=2:
    	for w in q:
    		print "\n" + w + " occurs in line(s) :"
    		l=1
    		for line in open(p):
    			if w in get_tokenized_and_normalized_list(line):
    				print l,
    			l+=1

        print "\n"

    else:

        print "\n" + s + " occurs in line(s) :"
        os.system("grep -i -n '" + s + "' " + p + " | cut -d : -f 1")
        

# Creates unit vector - no. of words dimensions, dimension coefficient = score of word in file/norm of vector
def create_tf_idf_vector():
    for vect in vects_for_docs:
    	vect_length = 0.0
        for word1 in vect:
            word_freq = vect[word1]
            temp = calc_tf_idf(word1, word_freq)
            vect[word1] = temp
            vect_length += temp ** 2

        vect_length = sqrt(vect_length)
        for word1 in vect:
            vect[word1] /= vect_length

# Creates unit vector - no. of words dimensions, dimension coefficient = score of word in query/norm of vector
def get_tf_idf_from_query_vect(query_vector1):
    vect_length = 0.0
    for word1 in query_vector1:
        word_freq = query_vector1[word1]
        if word1 in document_freq_vect:  # I have left out any term which has not occurred in any document because
            query_vector1[word1] = calc_tf_idf(word1, word_freq)
        else:
            query_vector1[word1] = log(1 + word_freq) * log(nos_of_documents)  

        vect_length += query_vector1[word1] ** 2
    vect_length = sqrt(vect_length)
    if vect_length != 0:
        for word1 in query_vector1:
            query_vector1[word1] /= vect_length

# Calculates ranking score of a word
def calc_tf_idf(word1, word_freq):
	# print (word_freq)
	return log(1 + word_freq) * log(1 + nos_of_documents/document_freq_vect[word1])

# Restore original file permissions while exiting
def ender():
    print ("Exiting.......")
   

# Create command to highlight word in vim
def prepare_command(query_list,addpg,alt):
    if alt!=2:
        qs="/\\v"
        wc=1
        for x in query_list:
            if wc==1:
                qs+='<'
                qs+=x
                qs+='>'
            else:
                qs+='|'
                qs+='<'
                qs+=x
                qs+='>'
            wc+=1

        temp = 'vim -c \\":set ic\\" -c \\":set hlsearch\\" -c \\"'+qs+'\\" '+addpg
        ret = "gnome-terminal -e 'bash -c \""
        ret+=temp
        ret+=";bash\"'"
        return ret
    else:
        qs="/\\v"
        qs+='<'
        qs+=query
        qs+='>'
        temp = 'vim -c \\":set ic\\" -c \\":set hlsearch\\" -c \\"'+qs+'\\" '+addpg
        ret = "gnome-terminal -e 'bash -c \""
        ret+=temp
        ret+=";bash\"'"
        return ret

# Calculates the dot product of vector1 and vector2
def get_dot_product(q,vector1,f,vector2,alt):
    if len(vector1) > len(vector2):  # this will ensure that len(dict1) < len(dict2)
        temp = vector1
        vector1 = vector2
        vector2 = temp
    keys1 = vector1.keys()
    l = len(keys1)
    keys2 = vector2.keys()
    sum1 = 0
    c=0
    for i in keys1:
        if i in keys2:
        	c+=1
        	sum1 += vector1[i] * vector2[i]

    if alt==0:
    	return sum1
    elif alt==1:
        if c==l:
            return sum1
        else:
            return 0
    else:
    	if c!=l:
    		return 0
    	if c==l:
	        f_add = os.path.join(a,file_name_dict[f])
	        os.system('vim -c ":set ic" -c "redir! > vimout | :silent! %s/' + q + '//gn | redir END | q" '+ f_add)
	        f_lines = open('vimout').readlines()
	        w_list=f_lines[1].split(' ')
	        if w_list[0]=='Error':
	            return 0
	        else:
	            score = float(w_list[0])
	            f_len = 0
	            for lin in open(f_add):
	                f_len += len(lin.split())
	            return score*100/f_len





# Returns a sorted list of tuples of (DocID,score)
def get_result_from_query_vect(query,query_vector1,alt):
    parsed_list = []
    for i in range(nos_of_documents - 1):
        dot_prod = get_dot_product(query,query_vector1,i, vects_for_docs[i], alt)
        parsed_list.append((i, dot_prod))
        parsed_list = sorted(parsed_list, key=lambda x: x[1])
    return parsed_list[::-1]

#---------------------------------------M-A-I-N--------------------------------------------------#
print ("_____________________Welcome to TextSeek_________________________________")

#Ask user for directory to search in
print ("Enter the address of your folder: ")
a = raw_input()

quit = False
if not os.path.exists(a):
    while True:
        print ("Enter valid address (0 to quit)")
        a = raw_input()
        if os.path.exists(a):
            break
        if a=="0":
            quit = True
            print ("Thanks for using!!")
            break

if quit:
    sys.exit()


file_name_dict={}

z=0;
for x in os.listdir(a):
    file_name_dict[z]=x;
    z+=1


inverted_index = defaultdict(list)
nos_of_documents = 1
vects_for_docs = []  # we will need nos of docs number of vectors, each element is a dictionary
document_freq_vect = {}  # sort of equivalent to initializing the number of unique words to 0
#document_freq_vect[x] denotes number of documents in which x appears


# this is the first function that is executed.
# It updates the vects_for_docs variable with vectors of all the documents.
# def iterate_over_all_docs():
#   global nos_of_documents
#   for xe in os.listdir(a):

#       add = a + '/' + xe

#       # fil = open(add,'r')
#       # doc_text = fil.read()
#       # fil.close()

#         token_list = get_tokenized_and_normalized_list(open(add,'r').read())
#         print token_list
#         vect = create_vector(token_list)
#         print vect
#         vects_for_docs.append(vect)

import time

start_time = time.time()
# initializing the vects_for_docs variable

# print("Processing.......")
iterate_over_all_docs()

# nos_of_documents = counter+1


# print(time.time()-start_time)
start_time = time.time()

# self explanatory
generate_inverted_index()

# print(time.time()-start_time)
start_time = time.time()

# changes the frequency values in vects_for_docs to tf-idf values
create_tf_idf_vector()


# print(time.time()-start_time)
start_time = time.time()

# print("Here is a list of 15 tokens along with its docIds (sorted) in the inverted index")
# count = 1
# for word in inverted_index:
#     if count >= 16:
#         break
#     print('token num ' + str(count) + ': ' + word + ': '),
#     for docId in inverted_index[word]:
#         print(str(docId) + ', '),
#     print()
#     count += 1




print

open_list = [] 
while True:
    ammend(open_list)
    open_list=[]
    query = raw_input("Please enter your query....(Hit Enter to exit)\n")
    if len(query) == 0:
    	ender()
    	print ("Thanks for using :)")
        break
    
    alt = 0
    query_list = get_tokenized_and_normalized_list(query)
    query_vector = create_vector_from_query(query_list)

    if len(query_list) > 1:
        mode = raw_input("Enter type of search.....(2 for exact / 1 for all / 0 for any)")
        alt=int(mode)

    get_tf_idf_from_query_vect(query_vector)
    result_set = get_result_from_query_vect(query,query_vector, alt)

    temp=0

    reader={}
    sn = 1

    for tup in result_set:

    	if tup[1]==0:
    		print ("End of results")
    		break
        print(str(sn)+'. '+file_name_dict[tup[0]] + " : " + "Score : " + str(round(tup[1]*100,2)))
        reader[sn]=[file_name_dict[tup[0]],tup[0]]
        sn+=1
        temp+=1

       	if len(result_set)<sn or result_set[sn-1][1]==0:
       		print ("End of results")
        	while True:
	        	choice = raw_input("n for new query/o to open a file\n")
	        	if choice=='n':
	        		break
	        	elif choice=='o':
	        		pg = raw_input("Enter serial no. of the file \n")
	        		pg = int(pg)
	        		if pg in reader:
	        			addpg = a + '/' + reader[pg][0]
                        open_list.append(reader[pg])
                        os.system(prepare_command(query_list,addpg,alt))
                        get_lines(query,query_list,addpg,alt)

	        if choice=='n':
	        	break

        elif temp==10:

        	while True:
	        	choice = raw_input("n for new query/Enter for more results/o to open a file\n")
	        	if choice=='n':
	        		break
	        	elif choice=='o':
	        		pg = raw_input("Enter serial no. of the file \n")
	        		pg = int(pg)
	        		if pg in reader:
	        			addpg = a + '/' + reader[pg][0]
                        open_list.append(reader[pg])
                        os.system(prepare_command(query_list,addpg,alt))
                        get_lines(query,query_list,addpg,alt)
                else:
	        		temp=0
	        		break

	        if choice=='n':
	        	break

    print
