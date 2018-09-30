import json
import urllib
import time
import re
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

    url = 'https://www.snhu.edu/admission/academic-catalogs/coce-catalog#/courses'    
    catalog = {}
    
    # start driver and open to url    
    driver.get(url)
    
    # wait for main elements to load
    wait_for_element("//div[@class='_3BWDQhaI']")

    print("Page Loaded!")
    
    # get all subjects in catalog    
    subject_elems = driver.find_elements_by_xpath("//h2[@class='_3xceO49R']")
    subjects = cleanse_elems(subject_elems)
    subjects = [s.text for s in subjects]    

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
        courses = {}
        
        for c in course_links:
            course_text = c.text

            url_text = c.get_attribute('href')        
            
            # open url and switch to new tab
            driver.execute_script(f'window.open("{url_text}", "new_window")')
            driver.switch_to_window(driver.window_handles[1])

            wait_for_element("//h3[@class='_3qov3mur']")

            # get description and credits
            desc_div = driver.find_element_by_xpath("//div[@class='iHFbKrta']")
            cred_div = driver.find_element_by_xpath("(//div[@class='iHFbKrta'])[2]")

            description = desc_div.find_element_by_tag_name('div').text
            creds = cred_div.find_element_by_tag_name('div').text

            course_text_split = [x.strip() for x in course_text.split('-', 1)]

            course_num = course_text_split[0]
            course_title = course_text_split[1]

            courses[course_num] = {
                'title': course_title, 
                'description': description,
                'credits': creds            
                }

            print(f"Course: {course_num}, Title: {course_title}")

            driver.close()
            driver.switch_to_window(driver.window_handles[0])

        catalog[subject] = courses

        pattern = re.compile('[\W_]+')
        subject = pattern.sub('', subject)

        # output subject json to file
        write_json_to_file(f'{subject}.txt', courses)        

    # output completed catalog json to file
    write_json_to_file('catalog.txt', catalog)

if __name__ == "__main__":
    main()