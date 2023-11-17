
#importing library
from bs4 import BeautifulSoup
import requests
import time
import re
from datetime import datetime

def get_post(url):
    try:
        response = requests.get(url)
        time.sleep(3)
        soup = BeautifulSoup(response.content, 'html5lib')
        post_time = soup.find('time').text.strip()
        title = soup.find('h1').text.strip()
        h2 = soup.find('h2').text.strip()
        #images_src = [i.attrs['src'] for i in soup.find('article', class_= 'cate-24h-foot-arti-deta-info').find_all('img')[:-1] if 'svg' not in i.attrs['src']]
        images_src = [img['data-original'] if 'https://image-us.24h.com.vn' not in img['src'] else img['src'] if 'svg' not in img['src'] else '' for img in soup.find('article', class_ = 'cate-24h-foot-arti-deta-info').find_all('img')[:-1]]
        text_list = [ child.text for child in soup.find('article', class_= 'cate-24h-foot-arti-deta-info').find_all('p')[:-3] if re.sub(r'\n+', '', child.text) != ""]
        text_list = [h2] + text_list
        return text_list, images_src,title,post_time
    except AttributeError as e:
        print(e)
        text_list = ''
        images_src = ''
        title= ''
        post_time =''
        return text_list, images_src,title,post_time
def conver_time_string(posted_date):
    pattern = r'\d{2}/\d{2}/\d{4}'
    match = re.search(pattern, posted_date)

    if match:
        date_string = match.group()

        # Convert to datetime object
        datetime_obj = datetime.strptime(date_string, "%d/%m/%Y")
        return datetime_obj
    else:
        return ''
def filter_list(urls):
    filtered_urls = []
    crawl_time = datetime.fromtimestamp(time.time()-5*24*3600)
    for i in urls:
        response = requests.get(i)
        soup = BeautifulSoup(response.content, 'html5lib')
        try:
            date_posted = soup.find('time').text.strip()
            date_posted_norm = conver_time_string(date_posted)
            if ( (date_posted_norm.day == crawl_time.day) and (date_posted_norm.month == crawl_time.month) and (date_posted_norm.year == crawl_time.year) ):
                filtered_urls.append(i)
                print(i)
        except AttributeError as e:
            print(e)
            break
    return filtered_urls
def get_list_url(cat_url):
    urls = []
    response = requests.get(cat_url)
    time.sleep(3)
    soup = BeautifulSoup(response.content,'html5lib')
    news_block  = soup.find('section', id = 'tin_bai_noi_bat_khac')
    url_list = news_block.find_all('a')
    for url in url_list:
        if 'https://www.24h.com.vn/' in url['href']:
            if url['href'] not in urls:
                urls.append(url['href'])
    return urls
def add_list(_24h_com_vn):
    for i in list(_24h_com_vn['urls'].keys()):
        for j in list(_24h_com_vn['urls'][i]['sub-category'].keys()):
            urls = get_list_url(_24h_com_vn['urls'][i]['sub-category'][j]['url'])
            _24h_com_vn['urls'][i]['sub-category'][j]['url-list'] = filter_list(urls)

def add_post(_24h_com_vn):
    for i in list(_24h_com_vn['urls'].keys()):
        for j in list(_24h_com_vn['urls'][i]['sub-category'].keys()):
            _24h_com_vn['urls'][i]['sub-category'][j]['content'] = {}
            list_key = [v for v in range(0,len(_24h_com_vn['urls'][i]['sub-category'][j]['url_list']))]
            for u in list_key:
                _24h_com_vn['urls'][i]['sub-category'][j]['content'][u]['images_src'] = get_post(_24h_com_vn['urls'][i]['sub-category'][j]['url_list'][u])[1]
                print(i,j,_24h_com_vn['urls'][i]['sub-category'][j]['name'],_24h_com_vn['urls'][i]['sub-category'][j]['name'],_24h_com_vn['urls'][i]['sub-category'][j]['content'][u]['title'],_24h_com_vn['urls'][i]['sub-category'][j]['url_list'][u])
            


def main():
    _24h_com_vn = {
        "home_page":"https://www.24h.com.vn/",
        "urls":{
            "tech":
            {
             "url":"https://www.24h.com.vn/cong-nghe-thong-tin-c55.html",
             "sub-category":{
                0:{"name":"Game",
                 "url":"https://www.24h.com.vn/game-c69.html"},
                1:{"name":"Phần mềm",
                 "url":"https://www.24h.com.vn/phan-mem-ngoai-c302.html"}
          
             }
            }
         }
    }

    add_list(_24h_com_vn)
    #add_post()
    return _24h_com_vn
if __name__ == '__main__':
    main()