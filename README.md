# RE-index-task-answer
A repo for the answer to a small task (creating an index for wikipedia pages)

## Description

I used SQLite to store the data extracted and parsed in a database, before writing it in the files.
Written and tested with Python 3.

The modules used are :
 - SQLite3     
 - LXML (for the HTML parser)
 - Unidecode (to clean the text)
 - re (for the regex)
 - csv (to write the contents of the database in a csv file)
 - os (to remove the file containing the database)
