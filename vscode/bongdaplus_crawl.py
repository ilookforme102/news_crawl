import requests 
import time
import re
from datetime import datetime
from bs4 import BeautifulSoup,NavigableString, Comment 
#convert time string to the right format
def convert_string(input_str):
    # Regular expression pattern to match a date in the format dd-mm-yyyy
    pattern = r'\b\d{2}-\d{2}-\d{4}\b'
    
    # Search for the pattern in the string
    match = re.search(pattern, input_str)
    if match:
    # Extract and print the date if found
        date_str = match.group(0)
        date_obj = datetime.strptime(date_str, '%d-%m-%Y')
        date =  date_obj.strftime('%Y-%m-%d')

        return date
    else:
        'No date found'
    
#convert time string to datetime object
def convert_time_string(posted_date):
    # Regular expression pattern to match a date in the format dd-mm-yyyy
    pattern = r'\b\d{2}-\d{2}-\d{4}\b'

    # Search for the pattern in the string and extract the date
    match = re.search(pattern, posted_date)
    if match:
        date_str = match.group(0)
        # Convert the extracted date string to datetime object
        date_obj = datetime.strptime(date_str, '%d-%m-%Y')
        return date_obj
    else:
        return None  # Or raise an exception if appropriate
def get_content_bongdaplus(url):
    response = requests.get(url)
    time.sleep(5)
    soup = BeautifulSoup(response.content, 'html.parser')
    post_content_div =  soup.find('div', id = 'postContent')

    #get main content
    text_div =  soup.find('div', class_ = 'details')
        #extract time: 
    time_div = text_div.find('div', class_ = 'dtepub')
    post_time = time_div.text.strip()
    published_date = convert_string(post_time)
    # extract h1
    title = text_div.find('h1').text.strip()
    #extract the h2
    h2_text =  text_div.find('div', class_ = 'summary').get_text()
    h2_tag = soup.new_tag('h2') 
    h2_tag.string = h2_text # Set the content of <i> tag
    #author_div = text_div.find('div', class_ = 'mobover')
    #author_div.decompose()
    #text_div.insert(0,h2_tag)
    post_content_div.insert(0,h2_tag)
    #remove the bottomdiv
    #bottom_div = text_div('div', recursive = False)[-1]
    #bottom_div.decompose()
    #main_content = text_div.find('div', id = 'postContent')
    #img_list =  main_content.find_all('img')
    img_list =  post_content_div.find_all('img')
    #create list of caption base on img alt attribute
    caption_text_list = []
    for img in img_list:
        caption = img.get('alt', '')
        caption_text_list.append(caption)
    n_img = len(img_list)
    #print(len(caption_text_list))
    #create caption for the images
    for i in range(0,n_img):
        caption_start = NavigableString("[caption id=\"\" align=\"aligncenter\" width=\"800\"]")
        caption_text = NavigableString(caption_text_list[i])
        caption_end = NavigableString("[/caption]")
        #caption_text_list[i].decompose()
        # Insert the custom tags and caption text around the <img> tag
        img_list[i].insert_before(caption_start)
        img_list[i].insert_after(caption_end)
        try:
            img_list[i].insert_after(caption_text) 
        except IndexError as e:
            print(e)    
   
    
    #remove a elements:
     #find a and remove tag with text
    tags_to_remove = post_content_div.find_all(['a'])
    for tag in tags_to_remove:
         # Extract the text from the tag
        tag_text = tag.get_text()
        # Replace the tag with its text content
        tag.replace_with(tag_text)
        tag.text.strip()
    for script_or_style in post_content_div(['script', 'style']):
        script_or_style.decompose()
    
    for i in post_content_div.find_all(recursive = True):
        try:
            del i['onclick']
            del i['id']
            del i['class']
            del i['style']
        except AttributeError:
            continue
        except TypeError:
            continue
    for i in post_content_div.find_all('img'):
        i['class'] = "aligncenter"
        i['width'] = 800
        i['height'] = 400
    for video in post_content_div.find_all('video'):
        video.parent.decompose()
        #video.decompose()
    # Append the <i> tag as the last child of the <article> tag
    source_tag = soup.new_tag('i') 
    source_tag.string = "Nguồn: bongdaplus.vn"  # Set the content of <i> tag
    
    post_content_div.append(source_tag)
    for i in text_div.find_all('div', {'align': 'center'}):
        i.decompose()
    for element in post_content_div.find_all(recursive = True,string=True):
        if isinstance(element, NavigableString) and element.strip() == '':
            element.extract()
    #remove element withou child element or have children element which is empty
    for i in post_content_div.find_all(recursive = True):
        if i.children == None and i.string == None:
            i.decompose()
    for i in post_content_div.find_all(recursive = True):
        try:
            i.text.trip()
        except AttributeError as e:
            continue
    return post_content_div, title, published_date
def get_post(url):
    try:
        content,title,published_date = get_content_bongdaplus(url)
        return content,title,published_date
    except AttributeError as e:
        print(e)
def get_list_url(cate_url):
    response = requests.get(cate_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    news_box = soup.find_all('div', class_ = "newslst")
    urls = []
    for i in news_box:
        li_list =  i.find_all('li')
        for li in li_list:
            path = li.find('a')
            try:
                url = 'https://bongdaplus.vn' + path['href']
                urls.append(url)
            except TypeError:
                continue
    return urls
    
def filter_list(urls):
    filtered_urls = []
    crawl_time = datetime.fromtimestamp(time.time() - 1*24*3600)
    for i in urls:
        response = requests.get(i)
        soup = BeautifulSoup(response.content, 'html.parser')
        try:
            date_posted = soup.find('div', class_ = 'details').find('div', class_ = 'dtepub').text.strip()
            date_posted_norm = convert_time_string(date_posted)
            if ( (date_posted_norm.day == crawl_time.day) and (date_posted_norm.month == crawl_time.month) and (date_posted_norm.year == crawl_time.year) ):
                filtered_urls.append(i)
                print(i)
        except AttributeError as e:
            print(e)
            break
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

def get_news_bongdaplus():
    _bongdaplus = {
            "home_page":"https://bongdaplus.vn/",
            "urls":{
                "chuyende":
                {
                 "url":"https://bongdaplus.vn/hau-truong-bong-da#",
                 "sub-category":{  
                    0:{"name":"Hậu trường",
                     "url":"https://bongdaplus.vn/hau-truong-bong-da",
                     "cate_id":38,
                      "url_list" : []},
                 }
                }
            }
        }
#
    add_list(_bongdaplus)
    add_post(_bongdaplus)
    return _bongdaplus
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
    _bongdaplus = get_news_bongdaplus()
    for i in list(_bongdaplus['urls'].keys()):
    #web_24h_com_vn2['url'][i]['cate_id']
        for j in list(_bongdaplus['urls'][i]['sub-category']):
            url_list =  _bongdaplus['urls'][i]['sub-category'][j]['url_list']
            print(url_list)
            for t in range(0,len(url_list)):
                content = _bongdaplus['urls'][i]['sub-category'][j]['content'][t]['text']
                title = _bongdaplus['urls'][i]['sub-category'][j]['content'][t]['title']
                published_date = _bongdaplus['urls'][i]['sub-category'][j]['content'][t]['published_date']
                cate_id = _bongdaplus['urls'][i]['sub-category'][j]['cate_id']
                print(title, url_list[t])
                send_post_to_5goals(title,str(content), cate_id, published_date)
                time.sleep(5)
if __name__ == "__main__":
    main()