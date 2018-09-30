import json

catalog = {}

with open('catalog.txt', 'r') as f:
    catalog = json.loads(f.read())

# print all nested lists
for subject, courses in catalog.items():
    print(subject)
    for course, data in courses.items():
        print(course)
        for value in data.values():
            print(value)
            
        

    
    
    

        
    

#print(catalog['Computer Science'])

#print(catalog)

