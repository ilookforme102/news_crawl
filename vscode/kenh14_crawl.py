import requests 
import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import re
from datetime import datetime
from bs4 import BeautifulSoup

#main functions
def is_element_exist():
    try:
        driver.find_element(By.CLASS_NAME, 'view-more-detail.clearboth').find_element(By.TAG_NAME,'a')
        return True
    except NoSuchElementException:
        return False
def is_element_display():
    return driver.find_element(By.CLASS_NAME, 'view-more-detail.clearboth').find_element(By.TAG_NAME,'a').is_displayed()

def smooth_scroll_to_bottom(delay):
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Scroll down to the bottom.
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait for the page to load.
        time.sleep(delay)

        # Calculate new scroll height and compare with last scroll height.
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
def readmore_click():
    while is_element_display()==False:
        smooth_scroll_to_bottom(delay=4)
        warapper = driver.find_element(By.CLASS_NAME,'kbwcb-left-wrapper')
        last_post_date_string = warapper.find_elements(By.CLASS_NAME,'knswli-time')[-1].get_attribute('title')
        datetime_obj = datetime.fromisoformat(last_post_date_string)
        if is_element_display():
            if datetime_obj >= datetime(2023, 11, 11, 0, 0, 0):
                driver.find_element(By.CLASS_NAME, 'view-more-detail.clearboth').find_element(By.TAG_NAME,'a').click()
            else:
                break
def get_url_list(category_url):
    driver.get(category_url)
    url_list = []
    readmore_click()
    warapper  = driver.find_element(By.CLASS_NAME,'kbwcb-left-wrapper')
    list_elements = warapper.find_elements(By.CLASS_NAME,'knswli.need-get-value-facebook.clearfix.done-get-type.done-get-sticker')
    for i in range(0,len(warapper.find_elements(By.CLASS_NAME,'knswli-time'))):
        if datetime.fromisoformat(driver.find_elements(By.CLASS_NAME,'knswli-time')[i].get_attribute('title')) >= datetime(2023, 9, 1, 0, 0, 0):
            src = list_elements[i].find_element(By.TAG_NAME,'h3').find_element(By.TAG_NAME,'a').get_attribute('href')
            url = src 
            print(url)
            url_list.append(url)
    return url_list     
def add_url_list(_kenh14):
    for i in list(_kenh14['urls'].keys()):
        for j in _kenh14['urls'][i]:
            for v in list(_kenh14['urls'][i]['sub-category'].keys()):
                cat_url =  _kenh14['urls'][i]['sub-category'][v]['url']
                _kenh14['urls'][i]['sub-category'][v]['url_list'] = get_url_list(cat_url)
def get_post(url):
    try:
        response = requests.get(url)
        time.sleep(3)
        soup = BeautifulSoup(response.content, 'html5lib')
        parent_div = soup.find('div', id = 'k14-detail-content').find('div',class_ ='knc-content')
        post_time = soup.find('span', class_ ='kbwcm-time')['title']
        title = soup.find('h1').text.strip()
        h2 = soup.find('h2').text.strip()
        #images_src = [i.attrs['src'] for i in soup.find('article', class_= 'cate-24h-foot-arti-deta-info').find_all('img')[:-1] if 'svg' not in i.attrs['src']]
        images_src = [img['data-original'] for img in parent_div.find_all('img')]
        text_list = [ child.text.strip() for child in parent_div if child.text.strip() != ""]
        text_list = [h2] + text_list
        print(url)
        return text_list, images_src,title,post_time
    except AttributeError as e:
        print(e)
        text_list = ''
        images_src = ''
        title= ''
        post_time =''
        return text_list, images_src,title,post_time                
def add_post():
    for i in list(_kenh14['urls'].keys()):
        for j in _kenh14['urls'][i]:
            for v in list(_kenh14['urls'][i]['sub-category'].keys()):
                n_post = len(_kenh14['urls'][i]['sub-category'][v]['url_list'])
                _kenh14['urls'][i]['sub-category'][v]['content'] = {}
                for item in range(0,n_post):
                    post_url = _kenh14['urls'][i]['sub-category'][v]['url_list'][item]
                    _kenh14['urls'][i]['sub-category'][v]['content'][item]['text_list'],_kenh14['urls'][i]['sub-category'][v]['content'][item]['images_src'],_kenh14['urls'][i]['sub-category'][v]['content'][item]['title'],_kenh14['urls'][i]['sub-category'][v]['content'][item]['post_time'] = getpost(post_url)   

def main():
    driver = uc.Chrome(headless = True, use_subprocess=False,version_main=119)#, user_data_dir = "c:\temp\profile")#, version_main=117)
    _kenh14 = {
        "home_page":"https://kenh14.vn/",
        "urls":{
            "sport":
            {
             "url":"https://kenh14.vn/sport.chn",
             "sub-category":{
                0:{
                    "name":"Bóng đá",
                     "url":"https://kenh14.vn/sport/bong-da.chn",
                     "url_list" : []},
                1:{"name":"Hậu trường",
                 "url":"https://kenh14.vn/sport/hau-truong.chn",
                  "url_list" : []},
                2:{"name":"Esports",
                 "url":"https://kenh14.vn/sport/esports.chn",
                  "url_list" : []}
             }
            }
        }
    }
    add_url_list(_kenh14)
    driver.quit()
    add_post(_kenh14)
    #add_post()
    return _kenh14                       