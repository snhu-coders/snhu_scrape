import sys
import os
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
from selenium.common.exceptions import TimeoutException, SessionNotCreatedException


class SNHUScraper:

    def __init__(self):
        try:
            self.driver = webdriver.Chrome()
        except SessionNotCreatedException as ex:
            print(ex.msg)
            sys.exit("Error loading Selenium WebDriver. Check previous messages.")

        self.completed = []
        self.catalog = []

        self.get_completed_files()
        self.process_completed_files()

    def cleanse_elems(self, elems):
        return [e for e in elems if len(e.text) > 0]

    def write_json_to_file(self, file, json_data):
        with open(file, 'w') as f:
            f.write(json.dumps(json_data))

    def wait_for_element(self, elem_xpath):
        timeout = 20
        
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(
                    (By.XPATH, elem_xpath)
                )
            )
        except TimeoutException:
            print("Timed out waiting for elements to load.")
            self.driver.quit()

    def get_completed_files(self):
        files = os.listdir(os.path.dirname(__file__))

        completed = [f for f in files if f.endswith(".txt")]

        self.completed = completed

    def process_completed_files(self): 
        for filename in self.completed:
            with open(filename, 'r') as f:
                data = json.load(f)

                self.catalog.append(data)

    def main(self):
        start_time = datetime.datetime.now()
        print(f"Started at {start_time}")

        url = 'https://www.snhu.edu/admission/academic-catalogs/coce-catalog#/courses'        
        
        # start driver and open to url    
        self.driver.get(url)
        
        # wait for main elements to load
        self.wait_for_element("//div[@class='_2rXQ2pA3']")

        print("Page Loaded!")
        
        # get all subjects in catalog
        subject_elems = self.driver.find_elements_by_class_name("_2QKOWbAy")
        #subjects = [s.text for s in self.cleanse_elems(subject_elems)]

        for elem in subject_elems:
            self.driver.execute_script("return arguments[0].scrollIntoView(alignTo=true);", elem)
            #webdriver.ActionChains(self.driver).move_to_element(elem).perform()
            
            subject = elem.get_attribute("name")
            print(subject)

            if subject.replace(' ', '') + '.txt' in self.completed:
                continue

            print(f"Subject: {subject}")

            button = elem.find_element_by_class_name("_1Rqvc9jE")

            button.click()

            time.sleep(1)
        
            # wait for element to appear
            self.wait_for_element("//div[@class='_3mrXgGIi']")

            # get all course headers
            course_headers = self.driver.find_elements_by_xpath("//h3[@class='t4J2HAme']")
            course_ahrefs = [c.find_element(By.TAG_NAME, 'a') for c in course_headers]
            course_links = self.cleanse_elems(course_ahrefs)

            # process each of the courses
            courses = []
            
            for c in course_links:
                course_text = c.text

                url_text = c.get_attribute('href')        
                
                # open url and switch to new tab
                self.driver.execute_script(f'window.open("{url_text}", "new_window")')
                self.driver.switch_to.window(self.driver.window_handles[1])

                self.wait_for_element("//h3[@class='_3qov3mur']")

                # get description and credits
                headers = self.cleanse_elems(self.driver.find_elements_by_class_name('_3qov3mur'))
                headers = [h.text for h in headers]
                divs = self.cleanse_elems(self.driver.find_elements_by_class_name('iHFbKrta'))
                print(len(divs))

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

                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0])
            
            subject_dict = {'title': subject, 'courses': courses}
            self.catalog.append(subject_dict)

            # output subject json to file
            pattern = re.compile(r'[\s\/]+')  # Whitespace
            subject = pattern.sub('', subject) # Remove Whitespace for file naming
            self.write_json_to_file(f'{subject}.txt', subject_dict)

            button.click()
            time.sleep(1)

        # output completed catalog json to file
        self.write_json_to_file('catalog.txt', self.catalog)

        end_time = datetime.datetime.now()
        print(f"Ended at: {end_time}")
        print(f"Elapsed: {end_time - start_time}")    

if __name__ == "__main__":
    scraper = SNHUScraper()
    scraper.main()
