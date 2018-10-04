import sys
import json
import urllib
import time
import re
import datetime
from selenium import webdriver 
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 
from selenium.common.exceptions import TimeoutException

# global variables
driver = webdriver.Chrome()

def cleanse_elems(elems):
    return [e for e in elems if len(e.text) > 0]

def write_json_to_file(file, json_data):
    with open(file, 'w') as f:
        f.write(json.dumps(json_data))

def wait_for_element(elem_xpath):
    global driver
    timeout = 20
    
    try:
        WebDriverWait(driver, timeout).until(
            EC.visibility_of_element_located(
                (By.XPATH, elem_xpath)
            )
        )
    except TimeoutException:
        print("Timed out waiting for elements to load.")
        driver.quit()

def main():
    global driver
    start_time = datetime.datetime.now()
    print(f"Started at {start_time}")

    url = 'https://www.snhu.edu/admission/academic-catalogs/coce-catalog#/courses'    
    catalog = []
    
    # start driver and open to url    
    driver.get(url)
    
    # wait for main elements to load
    wait_for_element("//div[@class='_3BWDQhaI']")

    print("Page Loaded!")
    
    # get all subjects in catalog    
    subject_elems = driver.find_elements_by_xpath("//h2[@class='_3xceO49R']")
    subjects = cleanse_elems(subject_elems)
    subjects = [s.text for s in subjects]

    # TODO: Spin up thread for each subject to increase efficiency
    for subject in subjects:
        print(f"Subject: {subject}")
        
        # urlify the subject text
        subject_url = urllib.parse.quote_plus(subject)

        # Change browser to new URL
        driver.get(f'{url}?group={subject_url}')

        # wait for element to appear
        wait_for_element("//div[@class='_3BWDQhaI']")

        # get all course headers
        course_headers = driver.find_elements_by_xpath("//h3[@class='t4J2HAme']")
        course_ahrefs = [c.find_element(By.TAG_NAME, 'a') for c in course_headers]
        course_links = cleanse_elems(course_ahrefs)

        # process each of the courses
        courses = []
        
        for c in course_links:
            course_text = c.text

            url_text = c.get_attribute('href')        
            
            # open url and switch to new tab
            driver.execute_script(f'window.open("{url_text}", "new_window")')
            driver.switch_to_window(driver.window_handles[1])

            wait_for_element("//h3[@class='_3qov3mur']")

            # get description and credits
            headers = cleanse_elems(driver.find_elements_by_class_name('_3qov3mur'))
            headers = [h.text for h in headers]
            divs = cleanse_elems(driver.find_elements_by_class_name('iHFbKrta'))
            print(len(divs))

            #desc_div = divs[headers.index('Description')] if 'Description' in headers else None
            #creds_div = divs[headers.index('Credits')] if 'Credits' in headers else None
            #reqs_div = divs[headers.index('Requisites')] if 'Requisites' in headers else None

            if 'Description' in headers:
                description = divs[headers.index('Description')].find_element_by_tag_name('div').text
            else:
                description = ""

            if 'Credits' in headers:
                creds = divs[headers.index('Credits')].find_element_by_tag_name('div').text
            else:
                creds = ""

            if 'Requisites' in headers:
                reqs = divs[headers.index('Requisites')].text
            else:
                reqs = None
            
            
            # reqs_links = reqs_div.find_elements_by_tag_name('a') if reqs_div else None

            # reqs = []
            # if reqs_links:
            #     reqs = [req.text for req in reqs_links]                

            course_text_split = [x.strip() for x in course_text.split('-', 1)]

            course_id = course_text_split[0]
            title = course_text_split[1]

            course = {
                'id': course_id,
                'title': title, 
                'description': description,
                'credits': creds,
                'requisites': reqs
            }

            courses.append(course)
            
            print(f"id: {course_id}, title: {title}, credits: {creds}, reqs: {reqs}")

            driver.close()
            driver.switch_to_window(driver.window_handles[0])        
        
        subject_dict = {'title': subject, 'courses': courses}
        catalog.append(subject_dict)

        # output subject json to file
        pattern = re.compile('[\W_]+')  # Whitespace
        subject = pattern.sub('', subject) # Remove Whitespace for file naming
        write_json_to_file(f'{subject}.txt', subject_dict)      

    # output completed catalog json to file
    # TODO: Stich catalog together from existing files, to allow for restarting the program
    write_json_to_file('catalog.txt', catalog)

    end_time = datetime.datetime.now()
    print(f"Ended at: {end_time}")
    print(f"Elapsed: {end_time - start_time}")    

if __name__ == "__main__":
    # TODO: Allow for restarting by passing in command line argument of Subject
    main()
