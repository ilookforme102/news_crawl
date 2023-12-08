import requests 
import time
import re
from datetime import datetime
from bs4 import BeautifulSoup,NavigableString, Comment

def convert_string(input_str):
    # Regular expression pattern to match a date in the format dd-mm-yyyy
    pattern =r'\d+/\d+/\d+'
    
    # Search for the pattern in the string
    match = re.search(pattern, input_str)
    if match:
    # Extract and print the date if found
        date_str = match.group(0)
        date_obj = datetime.strptime(date_str, '%d/%m/%Y')
        date_str = date_obj.strftime('%Y-%m-%d')
        return date_str,date_obj
    else:
        return None

def get_datetime_obj(string):

    # Regular expression pattern to match the date
    pattern = r'\d{2}/\d{2}/\d{4}'
    
    # Search for the pattern in the string and extract the date
    match = re.search(pattern, string)
    if match:
        date_str = match.group(0)
        # Convert the extracted date string to datetime object
        date_obj = datetime.strptime(date_str, '%d/%m/%Y')
        date_str = date_obj.strftime('%Y-%m-%d')
    else:
        date_obj = None
        date_str = None
    
    return date_obj,date_str
def get_content_vtv(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    title = soup.find('h1').text.strip()
    date = soup.find('p', class_ = 'news-info').text.strip()
    published_date = get_datetime_obj(date)[1]
    first_paragraph = soup.find('h2', class_  = 'sapo')
    article = soup.find('div', id = 'entry-body')
    #strong_tag = soup.new_tag('strong') 
    #strong_tag.string = first_paragraph.text # Set the content of <i> tag
    # Insert the new element as the first child
    article.insert(0, first_paragraph)
    
    for script_or_style in article(['script', 'style','iframe','video',]):
                script_or_style.decompose()
    
    caption_text_list = article.find_all('div', class_ ='PhotoCMS_Caption')
    tags_to_remove = article.find_all(['a', 'span'])
    for tag in tags_to_remove:
        # Extract the text from the tag
        tag_text = tag.get_text()
        # Replace the tag with its text content
        tag.replace_with(tag_text)
        tag.text.strip()
    #remove all image attributes except somes from list
    list_attr = ['src','alt','data-original']
    for i in article.find_all('img'):
        for j in list(i.attrs.keys()):
            if j not in list_attr:
                i.attrs.pop(j)
    img_list = article.find_all('img')
    n_img = len(img_list)
    for i in range(0,n_img):
           
        caption_start = NavigableString("[caption id=\"\" align=\"aligncenter\" width=\"800\"]")
        try:
            caption_text = NavigableString(caption_text_list[i].find('p').get_text())
        except (IndexError,AttributeError):
            continue
        caption_end = NavigableString("[/caption]")
        # Insert the custom tags and caption text around the <img> tag
        img_list[i].insert_before(caption_start)
        img_list[i].insert_after(caption_end)
        img_list[i].insert_after(caption_text) 
    for i in article.find_all('img'):
        try:
            i['src'] = i['data-src']
        except KeyError:
            continue
    for i in caption_text_list:
        i.decompose()
    # add avatar photo on top
    first_photo = soup.find('img', class_ = 'news-avatar')
    try:
        article.insert(0, first_photo)
    except ValueError as e:
        print(e)
    # centering the image
    for i in article.find_all('img'):
        i['class'] = "aligncenter"
        #i['width'] = 800
       # i['height'] = 400
        del i['data-src']
    list_attr = ['src','alt','data-ogiginal','class']
    for i in article.find_all(recursive = True):
        for j in list(i.attrs.keys()):
            if j not in list_attr:
                i.attrs.pop(j)
    #remove empty div or empty space from element
    for item in article.find_all('div'):
        if item.string =="":
            item.decompose()
    for element in article.find_all(recursive = True,string=True):
        if isinstance(element, NavigableString) and element.strip() == '':
            element.extract()
    #remove html comment from element   
    article.find_all('p',recursive = True)[-1].decompose()
    for comment in article.find_all(string=lambda text: isinstance(text, Comment)):
        comment.extract()
    
    #article.find_all(recursive = True)[-1].decompose()
    #article.find('div', class_ ='width_common box-tinlienquanv2').decompose()
    source_tag = soup.new_tag('i') 
    source_tag.string = "Nguồn: vtv.vn"  # Set the content of <i> tag
    article.append(source_tag)
    return article, title, published_date
def get_post(url):
    try:
        content,title,published_date = get_content_vtv(url)
        return str(content),title,published_date
    except AttributeError as e:
        print(e)
def get_list_url(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    items = soup.find_all('h3')
    urls = []
    for i in items:
        path = i.find('a')['href']
        url = 'https://vtv.vn/'+ path
        urls.append(url)
    return urls
def filter_list(urls):
    filtered_urls = []
    crawl_time = datetime.fromtimestamp(time.time()-1*24*3600)
    for i in range(0,len(urls)):
        try:
            published_date = get_content_vtv(urls[i])[2]
            date_posted_norm = datetime.strptime(published_date, '%Y-%m-%d')
            if ( (date_posted_norm.day == crawl_time.day) and (date_posted_norm.month == crawl_time.month) and (date_posted_norm.year == crawl_time.year) ):
                filtered_urls.append(urls[i])
                #print(i)
        except AttributeError as e:
            print(e)
            continue
    return filtered_urls
#add list url to json
#add list url to json
def add_list(web_json_obj):
    for i in list(web_json_obj['urls'].keys()):
        for j in list(web_json_obj['urls'][i]['sub-category'].keys()):  
            urls = get_list_url(web_json_obj['urls'][i]['sub-category'][j]['url'])
            print(i,j,web_json_obj['urls'][i]['sub-category'][j]['url'])
            web_json_obj['urls'][i]['sub-category'][j]['url_list'] = filter_list(urls)
# add post content from get content function to json object
# add post content from get content function to json object
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
#add all necessary information to json object
def get_news_vtv():
    _vtv= {
            "home_page":"https://vtv.vn/",
            "urls":{
                "Quần vọt":
                {
                 "url":"https://vtv.vn/the-thao/tennis.htm#",
                 "sub-category":{  
                    0:{"name":"Tennis",
                     "url":"https://vtv.vn/the-thao/tennis.htm",
                     "cate_id":62,
                      "url_list" : []},
                 }
                }
            }
        }
#
    add_list(_vtv)
    add_post(_vtv)
    return _vtv
#send post content to wordpress via endpoint
def send_post_to_5goals(title,content,category_id,published_date):
    # URL of the API endpoint (this is a placeholder and needs to be replaced with the actual URL)
    url = "https://api2023.5goal.com/wp-json/custom/createPost"
    
    # Data to be sent in the POST request
    data = {
        "title": title,
        "content": content,
        "category_id": category_id,
        "token": 'draftpost',#'5goalvodichcmnl',  # Replace with your actual access token
        "published_date": published_date,
        "domain":"vtv"
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
    _vtv = get_news_vtv()
    for i in [list(_vtv['urls'].keys())[0]]:
    #web_24h_com_vn2['url'][i]['cate_id']
        for j in list(_vtv['urls'][i]['sub-category']):
            url_list =  _vtv['urls'][i]['sub-category'][j]['url_list']
            print(url_list)
            for t in range(0,len(url_list)):
                content = _vtv['urls'][i]['sub-category'][j]['content'][t]['text']
                title = _vtv['urls'][i]['sub-category'][j]['content'][t]['title']
                published_date = _vtv['urls'][i]['sub-category'][j]['content'][t]['published_date']
                cate_id = _vtv['urls'][i]['sub-category'][j]['cate_id']
                print(title, url_list[t],published_date)
                send_post_to_5goals(title,content, cate_id, published_date)
                time.sleep(2)
if __name__ == '__main__':
    main()