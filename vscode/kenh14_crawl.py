import requests 
import time
import re
from datetime import datetime
from bs4 import BeautifulSoup,NavigableString, Tag
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
    article =  soup.find('div', class_ = "knc-content")
    h2_tag =  soup.find('h2', class_ = 'knc-sapo')
    article.insert(0, h2_tag)
    caption_text_list =article.find_all( class_="PhotoCMS_Caption")
    post_time = soup.find('span', class_ = 'kbwcm-time').text.strip()
    published_date = convert_string(post_time)
    title = soup.find('h1').text.strip()
    album_captions = soup.find_all('div', class_ = 'LayoutAlbumCaptionWrapper')
    for caption in album_captions:
        try:
            caption.decompose()
        except (TypeError, AttributeError):
            continue
    for caption in caption_text_list:
        img_container = caption.previous_sibling
        img = img_container.find('img')
        try:
            img['src'] = img['data-original']
        except TypeError as e:
             print(e)
        caption_start = NavigableString("[caption id=\"\" align=\"aligncenter\" width=\"800\"]")
        try:
            caption_text = NavigableString(caption.find('p').text.strip())
        except (IndexError, AttributeError):
            caption_text = ''
        caption_end = NavigableString("[/caption]")
        img.insert_before(caption_start)
        img.insert_after(caption_end)
        img.insert_after(caption_text)
        caption.decompose()
    for script_or_style in article(['script', 'style']):
            script_or_style.decompose() 
    for i in article.find_all(recursive = True):
        try:
            del i['onclick']
            del i['id']
            del i['class']
            del i['style']
            del i['data-original']
            del i['type']
            del i['rel']
            del i['url']
            del i['photoid']
        except AttributeError:
            continue
        except TypeError:
            continue            
    tags_to_remove = article.find_all(['span'])
    
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
    a_tags = soup.find_all('a')
    for a_tag in a_tags:
        # Check if the <a> tag has no child tags
        if all(not isinstance(child, Tag) for child in a_tag.children):
            # Convert <a> tag to its text if it has no child tags
            a_tag.replace_with(a_tag.get_text())
        else:
            # If <a> tag has child elements, replace it with a <span> tag but keep the children
            new_span = soup.new_tag("span")
            new_span.extend(a_tag.contents)  # Use extend to add all child elements
            a_tag.replace_with(new_span)  
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
    return article, title, published_date
def get_post(url):
    try:
        content,title,published_date = get_content_kenh14(url)
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
    list = []
    
    try: 
        h2_list = soup.find('div', class_ = 'klw-fashion-topnews clearfix').find_all('h2')
        for i in h2_list:
            path = i.find('a')['href']
            url = 'https://kenh14.vn'+ path
            list.append(url)
    except AttributeError as e:
        print(e)
    try: 
        list_url = soup.find_all('h3', class_ = "knswli-title")
        for i in list_url:
            try:
                path = i.find('a')['href']
                url = 'https://kenh14.vn'+ path
                list.append(url)
            except TypeError:
                continue
    except AttributeError as e:
        print(e)
    return list
def filter_list(urls):
    filtered_urls = []
    crawl_time = datetime.fromtimestamp(time.time() -2*24*3600).replace(hour=0, minute=0, second=0, microsecond=0)
    for i in urls:
        response = requests.get(i)
        soup = BeautifulSoup(response.content, 'html5lib')
        try:
            date_posted = soup.find('span', class_ = 'kbwcm-time').text.strip()
            date_posted_norm = convert_time_string(date_posted)
            #if ( (date_posted_norm.day == crawl_time.day) and (date_posted_norm.month == crawl_time.month) and (date_posted_norm.year == crawl_time.year) ):
            if  date_posted_norm >= crawl_time:
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
# add post content from get content function to json object
def add_post(web_json_obj):
    for i in list(web_json_obj['urls'].keys()):
        for j in list(web_json_obj['urls'][i]['sub-category'].keys()):
            web_json_obj['urls'][i]['sub-category'][j]['content'] = {}
            list_key = [v for v in range(0,len(web_json_obj['urls'][i]['sub-category'][j]['url_list']))]
            for u in list_key:
                web_json_obj['urls'][i]['sub-category'][j]['content'][u] = {}
                if u != "":
                    try:
                        web_json_obj['urls'][i]['sub-category'][j]['content'][u]['text'] ,web_json_obj['urls'][i]['sub-category'][j]['content'][u]['title'],web_json_obj['urls'][i]['sub-category'][j]['content'][u]['published_date'] = get_post(web_json_obj['urls'][i]['sub-category'][j]['url_list'][u])
                        print(i,j,web_json_obj['urls'][i]['sub-category'][j]['cate_id'],web_json_obj['urls'][i]['sub-category'][j]['name'],web_json_obj['urls'][i]['sub-category'][j]['name'],web_json_obj['urls'][i]['sub-category'][j]['content'][u]['title'],web_json_obj['urls'][i]['sub-category'][j]['url_list'][u])
                    except TypeError:
                        continue
                else:
                    continue
#add all necessary information to json object
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
                },
                "người đẹp":
                {
                 "url":"https://kenh14.vn/sport.chn",
                 "sub-category":{  
                    0:{"name":"Người đẹp",
                     "url":"https://kenh14.vn/beauty-fashion/star-style.chn",
                     "cate_id":63,
                      "url_list" : []},
                    1:{"name":"Làm đẹp",
                     "url":"https://kenh14.vn/beauty-fashion/lam-dep.chn",
                     "cate_id":63,
                      "url_list" : []},
                    2:{"name":"Thời trang",
                     "url":"https://kenh14.vn/beauty-fashion/thoi-trang.chn",
                     "cate_id":63,
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
        "token": '5goalvodichcmnl',  # 'draftpost', Replace with your actual access token
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
        for j in list(_kenh14['urls'][i]['sub-category'].keys()):
            url_list =  _kenh14['urls'][i]['sub-category'][j]['url_list']
            for t in range(0,len(url_list)):
                try:
                    content = _kenh14['urls'][i]['sub-category'][j]['content'][t]['text']
                    title = _kenh14['urls'][i]['sub-category'][j]['content'][t]['title']
                    published_date = _kenh14['urls'][i]['sub-category'][j]['content'][t]['published_date']
                    cate_id = _kenh14['urls'][i]['sub-category'][j]['cate_id']
                    send_post_to_5goals(title,str(content), cate_id, published_date)
                except KeyError:
                    continue
                time.sleep(5)
    
if __name__ == '__main__':
    main()