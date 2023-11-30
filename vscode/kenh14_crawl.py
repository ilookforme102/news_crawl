import requests 
import time
import re
from datetime import datetime
from bs4 import BeautifulSoup,NavigableString

def convert_string(input_str):
    # Extract the date part using regular expression
    pattern = r'\d{2}/\d{2}/\d{4}'
    date_part = re.search(pattern, input_str).group()
    match = re.search(pattern, input_str)
    if match:
        # Parse the date string into a datetime object
        date_obj = datetime.strptime(date_part, '%d/%m/%Y')
        formatted_date = date_obj.strftime('%Y-%m-%d')
        return formatted_date
    else:
        return ""
# return the expected content in html format
def get_content_kenh14(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    article =  soup.find('div', class_ = "klw-new-content")
    children = article.find_all(recursive=False)
    related_news =  article.find('div', class_ = 'knc-relate-wrapper relationnews')
    related_news.decompose()
    for i in children[-6:]:
        i.decompose() 
    caption_text_list =article.find_all( class_="PhotoCMS_Caption")
    img_list = article.find_all(['img','video'])[:-1]
    n_img = len(img_list)
    for i in range(0,n_img):
        caption_start = NavigableString("[caption id=\"\" align=\"aligncenter\" width=\"800\"]")
        caption_text = NavigableString(caption_text_list[i].text)
        caption_end = NavigableString("[/caption]")
        caption_text_list[i].decompose()
            # Insert the custom tags and caption text around the <img> tag
        img_list[i].insert_before(caption_start)
        img_list[i].insert_after(caption_end)
        try:
            img_list[i].insert_after(caption_text) 
        except IndexError as e:
            print(e)        #print(len(caption_text_list))
    for script_or_style in article(['script', 'style']):
            script_or_style.decompose() 
    for i in article.find_all(recursive = True):
        try:
            del i['onclick']
            del i['id']
            del i['class']
            del i['style']
        except AttributeError:
            continue
        except TypeError:
            continue            
    tags_to_remove = article.find_all(['a', 'span'])
    for tag in tags_to_remove:
        # Extract the text from the tag
        tag_text = tag.get_text()
            # Replace the tag with its text content
        tag.replace_with(tag_text)
        tag.text.strip() 
    for i in article.find_all('img'):
        i['class'] = "aligncenter"
        i['width'] = 800
        i['height'] = 400
    source_tag = soup.new_tag('i') 
    source_tag.string = "Nguồn: kenh14.vn"  # Set the content of <i> tag
    # Append the <i> tag as the last child of the <article> tag
    article.append(source_tag)
    for i in article.find_all('div', {'align': 'center'}):
        i.decompose()
    for element in article.find_all(recursive = True,string=True):
        if isinstance(element, NavigableString) and element.strip() == '':
            element.extract()
    #remove element withou child element or have children element which is empty
    for i in article.find_all(recursive = True):
        if i.children == None and i.string == None:
            i.decompose()
    for i in article.find_all(recursive = True):
        try:
            i.text.trip()
        except AttributeError as e:
            continue
    return article
def get_post(url):
    try:
        response = requests.get(url)
        time.sleep(5)
        soup = BeautifulSoup(response.content, 'html5lib')
        content = get_content_kenh14(url)
        post_time = soup.find('span', class_ = 'kbwcm-time').text.strip()
        published_date = convert_string(post_time)
        title = soup.find('h1').text.strip()
        return content,title,published_date
    except AttributeError as e:
        print(e)
def convert_time_string(posted_date):
    pattern = r'\d{2}/\d{2}/\d{4}'
    match = re.search(pattern, posted_date)

    if match:
        date_string = match.group()

        # Convert to datetime object
        datetime_obj = datetime.strptime(date_string, "%d/%m/%Y")
        return datetime_obj
    else:
        return ''
def get_list_url(cate_url):
    response = requests.get(cate_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    list_url = soup.find('div', attrs = {'data-marked-zoneid':'kenh14_detail_d3'}).find_all('li')
    list = []
    for i in list_url:
        try:
            path = i.find('a')['href']
            url = 'https://kenh14.vn'+ path
            list.append(url)
        except TypeError:
            continue
    return list
def filter_list(urls):
    filtered_urls = []
    crawl_time = datetime.fromtimestamp(time.time() - 1*24*3600)
    for i in urls:
        response = requests.get(i)
        soup = BeautifulSoup(response.content, 'html5lib')
        try:
            date_posted = soup.find('span', class_ = 'kbwcm-time').text.strip()
            date_posted_norm = convert_time_string(date_posted)
            if ( (date_posted_norm.day == crawl_time.day) and (date_posted_norm.month == crawl_time.month) and (date_posted_norm.year == crawl_time.year) ):
                filtered_urls.append(i)
                print(i)
        except AttributeError as e:
            print(e)
            continue
    return filtered_urls
def add_list(web_json_obj):
    for i in list(web_json_obj['urls'].keys()):
        for j in list(web_json_obj['urls'][i]['sub-category'].keys()):  
            urls = get_list_url(web_json_obj['urls'][i]['sub-category'][j]['url'])
            print(i,j,web_json_obj['urls'][i]['sub-category'][j]['url'])
            web_json_obj['urls'][i]['sub-category'][j]['url_list'] = filter_list(urls)

def add_post(web_json_obj):
    for i in list(web_json_obj['urls'].keys()):
        for j in list(web_json_obj['urls'][i]['sub-category'].keys()):
            web_json_obj['urls'][i]['sub-category'][j]['content'] = {}
            list_key = [v for v in range(0,len(web_json_obj['urls'][i]['sub-category'][j]['url_list']))]
            for u in list_key:
                web_json_obj['urls'][i]['sub-category'][j]['content'][u] = {}
                if u != "":
                    web_json_obj['urls'][i]['sub-category'][j]['content'][u]['text'] ,web_json_obj['urls'][i]['sub-category'][j]['content'][u]['title'],web_json_obj['urls'][i]['sub-category'][j]['content'][u]['published_date'] = get_post(web_json_obj['urls'][i]['sub-category'][j]['url_list'][u])
                    print(i,j,web_json_obj['urls'][i]['sub-category'][j]['cate_id'],web_json_obj['urls'][i]['sub-category'][j]['name'],web_json_obj['urls'][i]['sub-category'][j]['name'],web_json_obj['urls'][i]['sub-category'][j]['content'][u]['title'],web_json_obj['urls'][i]['sub-category'][j]['url_list'][u])
                
def get_news_kenh14():
    _kenh14 = {
            "home_page":"https://kenh14.vn/",
            "urls":{
                "sport":
                {
                 "url":"https://kenh14.vn/sport.chn",
                 "sub-category":{  
                    0:{"name":"Hậu trường",
                     "url":"https://kenh14.vn/sport/hau-truong.chn",
                     "cate_id":38,
                      "url_list" : []},
                    1:{"name":"Esports",
                     "url":"https://kenh14.vn/sport/esports.chn",
                     "cate_id":61,
                      "url_list" : []}
                 }
                }
            }
        }
#
    add_list(_kenh14)
    add_post(_kenh14)
    return _kenh14
def send_post_to_5goals(title,content,category_id,published_date):
    # URL of the API endpoint (this is a placeholder and needs to be replaced with the actual URL)
    url = "https://api2023.5goal.com/wp-json/custom/createPost"
    
    # Data to be sent in the POST request
    data = {
        "title": title,
        "content": content,
        "category_id": category_id,
        "token": '5goalvodichcmnl',  # Replace with your actual access token
        "published_date": published_date,
        "domain":"kenh14"
          # Replace with the actual category ID as required
    }
    
    # Sending the POST request
    response = requests.post(url, data=data)
    
    # Checking the response
    if response.status_code == 200:
        print("The post was successfully created.")
        print("Response:", response.text)  # Prints the response text from the server
    else:
        print(f"Failed to create the post. Status code: {response.status_code}")
def main():
    _kenh14 = get_news_kenh14()
    for i in list(_kenh14['urls'].keys()):
    #web_24h_com_vn2['url'][i]['cate_id']
        for j in list(_kenh14['urls'][i]['sub-category']):
            url_list =  _kenh14['urls'][i]['sub-category'][j]['url_list']
            for t in range(0,len(url_list)):
                content = _kenh14['urls'][i]['sub-category'][j]['content'][t]['text']
                title = _kenh14['urls'][i]['sub-category'][j]['content'][t]['title']
                published_date = _kenh14['urls'][i]['sub-category'][j]['content'][t]['published_date']
                cate_id = _kenh14['urls'][i]['sub-category'][j]['cate_id']
                send_post_to_5goals(title,str(content), cate_id, published_date)
                time.sleep(5)
    return _kenh14
if __name__ == '__main__':
    main()