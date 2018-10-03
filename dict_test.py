import datetime
import json
from HashTable import HashTable
from Catalog import Catalog, Course

###############################################################

### Greg's Catalog with Dictionary ###
data = {}

with open('catalog.txt', 'r') as f:
    data = json.loads(f.read())

start_time = datetime.datetime.now()

catalog = Catalog({})
for subject, courses in data.items():
    course_data = {}
    for course, info in courses.items():
        course_data[course] = Course(*info.values())
    catalog.subjects[subject] = course_data

print(catalog.get_subject('Special Education'))

end_time = datetime.datetime.now()
print(end_time - start_time)
###############################################################

del start_time
del end_time
del catalog
del data

### Gregs Catalog with HashTable ###
data = {}

with open('catalog.txt', 'r') as f:
    data = json.loads(f.read())

start_time = datetime.datetime.now()

catalog = Catalog()
for subject, courses in data.items():    
    course_data = HashTable(47)
    for course, info in courses.items():
        course_data[course] = Course(*info.values())
    catalog.subjects[subject] = course_data

print(catalog.get_subject('Special Education'))
#print(catalog.get_course('WCM620'))

end_time = datetime.datetime.now()
print(end_time - start_time)
###############################################################
