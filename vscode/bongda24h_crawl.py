import requests 
import time
import re
from datetime import datetime
from bs4 import BeautifulSoup,NavigableString#, Comment
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
# bongda24h has 2 type of time display, depends on type so we use the correct format for time converting
def get_time_string(date_str):
    if len(date_str)<=5:
        crawl_time = datetime.fromtimestamp(time.time())
        year = str(crawl_time.year)
        date_str = date_str+"/"+year
        date_obj = datetime.strptime(date_str, '%d/%m/%Y')
        date =  date_obj.strftime('%Y-%m-%d')
    else:
        date = convert_string(date_str)
        date_obj = datetime.strptime(date,'%Y-%m-%d')
    return date_obj, date

def get_content_bongda24h(url):
    response = requests.get(url)
    time.sleep(4)
    soup = BeautifulSoup(response.content, 'html.parser')
    article = soup.find('div', id = '6il5mu2rgs')
    source_tag = soup.new_tag('i') 
    source_tag.string = "Nguồn: bongda24h.vn"  # Set the content of <i> tag
    article.append(source_tag)
    title = soup.find('h1').text.strip()
    date_str = soup.find('h1').next_sibling.text.strip()
    published_date = get_time_string(date_str)[1]
    try:
        article.find('div', class_ = "ads-center ads").decompose()
    except AttributeError as e :
        print(e)
    tables = article.find_all('table')
    for table in tables:
        try:
            picture = table.find('picture')
            img = table.find('img')
            source = table.find_all('source')
            src =  source[0]['data-srcset']
            img['src'] = src
            caption_wrapper = table.find_all('tr')[1]
            caption = caption_wrapper.text.strip()
            caption_start = NavigableString("[caption id=\"\" align=\"aligncenter\" width=\"800\"]")
            caption_text = NavigableString(caption)
            caption_end = NavigableString("[/caption]")
            img.insert_before(caption_start)
            img.insert_after(caption_end)
            img.insert_after(caption_text) 
            caption_wrapper.decompose()
            for i in source:
                i.decompose()      
        except AttributeError as e:
            continue
        except NameError as e:
            continue
        except TypeError as e:
            continue
        #Error handling just just incase no caption
        except IndexError as e:
            print(e)
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
        for table in tables:
            img = table.find('img')
            img['class'] = "aligncenter"
            img['width'] = 800
            img['height'] = 400
        for video in article.find_all(['video','iframe']):
                video.decompose()
        #Extrat embedded link from text
        tags_to_remove = article.find_all(['a'])
        for tag in tags_to_remove:
             # Extract the text from the tag
            tag_text = tag.get_text()
            # Replace the tag with its text content
            tag.replace_with(tag_text)
            tag.text.strip()
        for script_or_style in article(['script', 'style']):
            script_or_style.decompose()
    return article, title, published_date
def get_post(url):
    try:
        content,title,published_date = get_content_bongda24h(url)
        return content,title,published_date
    except AttributeError as e:
        print(e)
def get_list_url(cate_url):
    response = requests.get(cate_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    featured_posts = soup.find('div', class_ = 'post-featured')
    urls = []
    for i in featured_posts:
        path = i.find('h2').find('a')['href']
        url = 'https://bongda24h.vn' + path
        urls.append(url)
    section_content = soup.find_all('div', class_= 'section-content')
    for section in section_content:
        elements = section.find_all('article', class_ = 'post-list')
        for element in elements:
            path = element.find('p').find('a')['href']
            url = 'https://bongda24h.vn' + path
            urls.append(url)
    return urls
def filter_list(urls):
    filtered_urls = []
    crawl_time = datetime.fromtimestamp(time.time()-1*24*3600)
    for i in urls:
        response = requests.get(i)
        time.sleep(5)
        soup = BeautifulSoup(response.content, 'html.parser')
        try:
            #wrapper = soup.find('div', class_ = "col780 left clearafter")
            #date_posted = wrapper.find('p',class_ ='news-time left').text.strip()
            #date_posted_norm = convert_time_string(date_posted)
            date_str = soup.find('h1').next_sibling.text.strip()
            date_posted_norm = get_time_string(date_str)[0]
            if ( (date_posted_norm.day == crawl_time.day) and (date_posted_norm.month == crawl_time.month) and (date_posted_norm.year == crawl_time.year) ):
                filtered_urls.append(i)
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
def get_news_bongda24h():
    _bongda24h = {
            "home_page":"https://bongda24h.vn/",
            "urls":{
                "hautruong":
                {
                 "url":"https://bongda24h.vn/hau-truong-c188-p1.html#",
                 "sub-category":{  
                    0:{"name":"Hậu trường",
                     "url":"https://bongda24h.vn/hau-truong-c188-p1.html",
                     "cate_id":38,
                      "url_list" : []},
                 }
                }
            }
        }
#
    add_list(_bongda24h)
    add_post(_bongda24h)
    return _bongda24h
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
        "domain":"bongda24h"
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
    _bongda24h = get_news_bongda24h()
    for i in list(_bongda24h['urls'].keys()):
    #web_24h_com_vn2['url'][i]['cate_id']
        for j in list(_bongda24h['urls'][i]['sub-category']):
            url_list =  _bongda24h['urls'][i]['sub-category'][j]['url_list']
            print(url_list)
            for t in range(0,len(url_list)):
                content = _bongda24h['urls'][i]['sub-category'][j]['content'][t]['text']
                title = _bongda24h['urls'][i]['sub-category'][j]['content'][t]['title']
                published_date = _bongda24h['urls'][i]['sub-category'][j]['content'][t]['published_date']
                cate_id = _bongda24h['urls'][i]['sub-category'][j]['cate_id']
                print(title, url_list[t])
                send_post_to_5goals(title,str(content), cate_id, published_date)
                time.sleep(5)

if __name__ == '__main__':
    main()