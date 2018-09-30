import datetime
import json
from HashTable import HashTable

data = {}

with open('catalog.txt', 'r') as f:
    data = json.loads(f.read())

print("Python Dictionary: ")
start_time = datetime.datetime.now()
print(data.get('Computer Science').get('CS200').get('description'))
end_time = datetime.datetime.now()
print(end_time - start_time)

# Load the hash table
catalog_ht = HashTable(100)
for subject, courses in data.items():
    courses_ht = HashTable(50)
    for course, data in courses.items():
        data_ht = HashTable(3)
        for key, value in data.items():
            data_ht[key] = value
        courses_ht[course] = data_ht
    catalog_ht[subject] = courses_ht          

print("Greg's Hash Table:")
start_time = datetime.datetime.now()
print(catalog_ht.get('Computer Science').get('CS200').get('description'))
end_time = datetime.datetime.now()
print(end_time - start_time)
