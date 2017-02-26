'''
This program is used to parse a broken XML file, find all the words
it's composed of, their quantity, their frequency

Written by Arslen REMACI
'''


from lxml import html
from unidecode import unidecode
import sqlite3 as lite
import re
import csv
import os


# Function used to clean the initial text and transform it into utf-8
def decode(text):
    text_clean = unidecode(text)
    return text_clean


# Function used to remove some special characters that will get in the list of words
def remove_special_characters(text):
    return re.compile(r'[^a-zA-Z0-9_<>?!]+', re.UNICODE).split(text)


# Function used to remove the problem of case sensitivity
# Also uses the function above
def usable_text(text):
    text_min = text.lower()
    text_final = remove_special_characters(text_min)
    return text_final


# Function who calls the others and work on the text given by the main
# Used too to fill the database
def work(elem):
    id_doc = elem.get("id")
    text_decode = decode(elem.text)
    wordlist = usable_text(text_decode)

    # Write the doc's ID in the file
    docsequence.write(id_doc)
    docsequence.write(",")

    # For all the words in the wordlist given :
    for s in wordlist:
        # We see if the word is already in the database
        c.execute("SELECT word FROM doc WHERE word == ?", (s,))
        data=c.fetchone()
        if data is None:
            # If the word is not found, we create a new entry for it
            c.execute("INSERT INTO doc (word, count, count_docs, d_id) VALUES(?, 1, 1, ?)", (s, id_doc))
        else:
            # If the word is found, we add 1 to the count and the docs' counter
            c.execute("UPDATE doc SET count = count + 1 WHERE word == ?", (s,))
            c.execute("UPDATE doc SET count_docs = count_docs + 1 WHERE word == ? AND d_id <> ?", (s, id_doc))
            # Here, I update the id_doc to the new one when I increment the counter
            # for the condition above to work
            c.execute("UPDATE doc SET d_id = ? WHERE word == ?", (id_doc, s))

        # Here we take the ID of the word, and write it in the second file
        c.execute("SELECT id FROM doc WHERE word == ?", (s,))
        docsequence.write(str(c.fetchone()[0]))
        docsequence.write(";")

    conn.commit()




# We open the database
conn = lite.connect('wiki.db')
# We take the root of the data
# Modify the name of the file here
root = html.parse("data/docbla.xml").getroot()
c = conn.cursor()

# We drop the table if it exists and recreate it
c.execute(''' CREATE TABLE doc
            (id INTEGER PRIMARY KEY AUTOINCREMENT,
            word TEXT,
            count INTEGER,
            count_docs INTEGER,
            d_id INTEGER) '''
            )
# Used to empty the csv files
cleaning = open('out/docs.csv', 'w')
cleaning.close()


# Then we reopen them
docsequence = open('out/docs.csv', 'a', encoding='utf-8')

to_explore = [root, ]
explore = 1;

#node.tag == "doc"

for node in to_explore:
    # We only take the nodes named "doc" and get rid of the categories
    if node.tag == "doc" and re.match("Category", node.get("title")) == None:
            # And we call the work function
            print("Working on %s" % (explore))
            work(node)
            docsequence.write("\n")
            explore = explore + 1
    # And then, we add all the children of this node to the list
    to_explore += node.getchildren()

with open('out/doc.vocab', 'w', newline="") as f:
    csvWriter = csv.writer(f, delimiter=',')
    rows = c.execute("SELECT id, word, count, count_docs FROM doc")
    csvWriter.writerow(['ID', 'Word', 'Count', 'Count_docs'])
    csvWriter.writerows(rows)

f.close()
docsequence.close()
conn.close()
os.remove("wiki.db")
