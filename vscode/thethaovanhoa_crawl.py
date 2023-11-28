import requests 
import time
import re
from datetime import datetime
from bs4 import BeautifulSoup,NavigableString, Comment
def convert_string(input_str):
    # Regular expression pattern to match a date in the format dd-mm-yyyy
    pattern = r'\b\d{2}/\d{2}/\d{4}\b'
    
    # Search for the pattern in the string
    match = re.search(pattern, input_str)
    if match:
    # Extract and print the date if found
        date_str = match.group(0)
        date_obj = datetime.strptime(date_str, '%d/%m/%Y')
        date =  date_obj.strftime('%Y-%m-%d')

        return date
    else:
        'No date found'    
#convert time string to datetime object
def convert_time_string(posted_date):
    # Regular expression pattern to match a date in the format dd-mm-yyyy
    pattern = r'\b\d{2}/\d{2}/\d{4}\b'

    # Search for the pattern in the string and extract the date
    match = re.search(pattern, posted_date)
    if match:
        date_str = match.group(0)
        # Convert the extracted date string to datetime object
        date_obj = datetime.strptime(date_str, '%d/%m/%Y')
        return date_obj
    else:
        return None 
def get_content_thethaovanhoa(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    wrapper = soup.find('div', class_ = "col780 left clearafter")
    title = wrapper.find('h1').text.strip()
    date_str = wrapper.find('p',class_ ='news-time left').text
    published_date = convert_string(date_str)
    article = soup.find('div', class_ ="entry-body normal clearafter")
    #bottom_div = article.find_all(recursive = True)
    #for i in bottom_div:
        #i.decompose()
    try:
        preview_div = article.find_all('div', class_ ='VCSortableInPreviewMode alignCenter type-7_preview')
    except AttributeError as e:
        print(e)
        
    for i in preview_div:
        i.decompose()
    try:
        readmore_div = article.find('div', class_ ='VCSortableInPreviewMode link-content-footer')
        readmore_div.decompose()
    except AttributeError as e:
        print(e)
    source_tag = soup.new_tag('i') 
    source_tag.string = "Nguồn: thethaovanhoa.vn"  # Set the content of <i> tag
    article.append(source_tag)
    figures = article.find_all('figure', class_ = "VCSortableInPreviewMode")
    for figure in figures:
        try:
            img = figure.find('img')
            img['class'] = "aligncenter"
            img['width'] = 800
            img['height'] = 400
            caption_element = figure.find('figcaption', class_="PhotoCMS_Caption")
            caption = caption_element.find('p').text.strip()
            caption_start = NavigableString("[caption id=\"\" align=\"aligncenter\" width=\"800\"]")
            caption_text = NavigableString(caption)
            caption_end = NavigableString("[/caption]")
            #caption_text_list[i].decompose()
            # Insert the custom tags and caption text around the <img> tag
            img.insert_before(caption_start)
            img.insert_after(caption_end)
        except AttributeError as e:
            print(e)
        except NameError as e:
            continue
        except TypeError as e:
            continue
        try:
            img.insert_after(caption_text) 
        except IndexError as e:
            print(e)
        
        for video in article.find_all(['video','iframe']):
            video.decompose()
        readmore_btn = article.find_all('div', class_ = 'VCSortableInPreviewMode link-content-footer')
        for i in readmore_btn:
            i.decompose()
        tags_to_remove = article.find_all(['a'])
        for tag in tags_to_remove:
             # Extract the text from the tag
            tag_text = tag.get_text()
            # Replace the tag with its text content
            tag.replace_with(tag_text)
            tag.text.strip()
        for script_or_style in article(['script', 'style']):
            script_or_style.decompose()
        #fig_captions = article.find_all('figcaption', class_="PhotoCMS_Caption")
        #for fig in fig_captions:
            #fig.decompose()
    for cap in article.find_all('figcaption', class_ = 'PhotoCMS_Caption'):
        cap.decompose()
    return article, title, published_date
    
def get_post(url):
    try:
        content,title,published_date = get_content_thethaovanhoa(url)
        return content,title,published_date
    except AttributError as e:
        print(e)
def get_list_url(cate_url): 
    response = requests.get(cate_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    post_content_div = soup.find('ul', class_ ="news-stream col550 left col547")
    list_url = post_content_div.find_all('li')
    urls = []
    for i in list_url:
        path = i.find('a',class_='img left show-popup visit-popup')
    
        try:
            url = 'https://thethaovanhoa.vn' + path['href']
            urls.append(url)
        except TypeError as e:
            continue
    return urls
def filter_list(urls):
    filtered_urls = []
    crawl_time = datetime.fromtimestamp(time.time())
    for i in urls:
        response = requests.get(i)
        soup = BeautifulSoup(response.content, 'html.parser')
        try:
            wrapper = soup.find('div', class_ = "col780 left clearafter")
            date_posted = wrapper.find('p',class_ ='news-time left').text.strip()
            date_posted_norm = convert_time_string(date_posted)
            if ( (date_posted_norm.day == crawl_time.day) and (date_posted_norm.month == crawl_time.month) and (date_posted_norm.year == crawl_time.year) ):
                filtered_urls.append(i)
                print(i)
        except AttributeError as e:
            print(e)
            break
    return filtered_urls
#add list url to json
def add_list(web_json_obj):
    for i in list(web_json_obj['urls'].keys()):
        for j in list(web_json_obj['urls'][i]['sub-category'].keys()):  
            urls = get_list_url(web_json_obj['urls'][i]['sub-category'][j]['url'])
            print(i,j,web_json_obj['urls'][i]['sub-category'][j]['url'])
            web_json_obj['urls'][i]['sub-category'][j]['url_list'] = filter_list(urls)
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
def get_news_thethaovanhoa():
    _thethaovanhoa = {
            "home_page":"https://bongdaplus.vn/",
            "urls":{
                "hautruong":
                {
                 "url":"https://thethaovanhoa.vn/the-gioi-sao.htm#",
                 "sub-category":{  
                    0:{"name":"Thế giới sao",
                     "url":"https://thethaovanhoa.vn/the-gioi-sao.htm",
                     "cate_id":38,
                      "url_list" : []},
                 }
                }
            }
        }
#
    add_list(_thethaovanhoa)
    add_post(_thethaovanhoa)
    return _thethaovanhoa
#send post content to wordpress via endpoint
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
        "domain":"bongdaplus"
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
    _thethaovanhoa = get_news_thethaovanhoa()
    for i in list(_thethaovanhoa['urls'].keys()):
    #web_24h_com_vn2['url'][i]['cate_id']
        for j in list(_thethaovanhoa['urls'][i]['sub-category']):
            url_list =  _thethaovanhoa['urls'][i]['sub-category'][j]['url_list']
            print(url_list)
            for t in range(0,len(url_list)):
                content = _thethaovanhoa['urls'][i]['sub-category'][j]['content'][t]['text']
                title = _thethaovanhoa['urls'][i]['sub-category'][j]['content'][t]['title']
                published_date = _thethaovanhoa['urls'][i]['sub-category'][j]['content'][t]['published_date']
                cate_id = _thethaovanhoa['urls'][i]['sub-category'][j]['cate_id']
                print(title, url_list[t])
                send_post_to_5goals(title,str(content), cate_id, published_date)
                time.sleep(5)
if __name__ == '__main__':
    main()