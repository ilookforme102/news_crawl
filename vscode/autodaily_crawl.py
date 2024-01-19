
import requests 
import time
import re
from datetime import datetime
from bs4 import BeautifulSoup,NavigableString, Tag#, Comment
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


def get_content_autodaily(url):
    # def get_content_autodaily()
    response = requests.get(url)
    time.sleep(5)
    soup = BeautifulSoup(response.content, 'html.parser')
    title = soup.find('h1').text.strip()
    date = soup.find('time').text.strip()
    published_date = convert_string(date)
    article = soup.find('div', class_ = 'article-detail')
    for script_or_style in article(['script', 'style','iframe']):
                script_or_style.decompose()
    related_item = article.find('div', class_ = 'item-relate')
    related_item.decompose()
    author_item = article.find_all(recursive = True)[-2:]
    for i in author_item:
        i.decompose()
    caption_text_list = article.find_all('em')
    tags_to_remove = article.find_all(['a'])
    for tag in tags_to_remove:
        """# Extract the text from the tag
        tag_text = tag.get_text()
        # Replace the tag with its text content
        tag.replace_with(tag_text)
        tag.text.strip()"""
    #for i in article.find_all('img'):
        #i.attrs = ['class', 'alt', 'src', 'data-original']
        #del i['onclick']
        #del i['style']
        #del i['class']
        #del i['alt']
    #remove all image attributes except somes from list
    list_attr = ['src','alt','data-src']
    for i in article.find_all('img'):
        attrs_to_remove = [attr for attr in i.attrs if attr not in list_attr]
        for attr in attrs_to_remove:
            del i[attr]
    img_list = article.find_all('img')
    n_img = len(img_list)
    #print(len(caption_text_list))
    for i in range(0,n_img):

        caption_start = NavigableString("[caption id=\"\" align=\"aligncenter\" width=\"800\"]")
        try:
            caption_text = NavigableString(caption_text_list[i].get_text())
            caption_end = NavigableString("[/caption]")
            # Insert the custom tags and caption text around the <img> tag
            img_list[i].insert_before(caption_start)
            img_list[i].insert_after(caption_end)
            img_list[i].insert_after(caption_text) 
        except IndexError as e:
            print(e)
        
    for i in article.find_all('img'):
        i['src'] = i['data-src']
    for i in caption_text_list:
        i.decompose()
        #print(img_list[i]['src'])
        #caption_text_list[i].decompose()
    for i in article.find_all(recursive = True):
        try:
            del i['onclick']
            i['id'] =''
            i['class']=''
            i['style'] =''
            i['href'] = ''
        except AttributeError:
            continue
        #try:
            #print(i)
            
        except TypeError:
            continue
    for i in article.find_all('img'):
        i['class'] = "aligncenter"
        i['width'] = 800
        i['height'] = 400
        del i['data-src']
    for item in article.find_all('div'):
        if item.string =="":
            item.decompose()
    try:
        article.find_all('strong', recursive = True)[-1].decompose()
    except IndexError as e:
        print(e)
    # Append the <i> tag as the last child of the <article> tag
    source_tag = soup.new_tag('i') 
    source_tag.string = "Nguồn: autodaily.vn"  # Set the content of <i> tag
    article.append(source_tag)
    #Highlight the fist paragraph by using <strong> tag
    p_tag_1st = article.find_all('p')[0]
    p_text = p_tag_1st.get_text()
    # Create a new <strong> tag with the same text
    strong_tag = soup.new_tag("strong")
    strong_tag.string = p_text
    # Replace the <p> tag with the <strong> tag
    p_tag_1st.replace_with(strong_tag)
    
    #Handling a tag 
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
    return article, title, published_date
def get_post(url):
    try:
        content,title,published_date = get_content_autodaily(url)
        return content,title,published_date
    except AttributeError as e:
        print(e)
def get_list_url(cate_url):
    response = requests.get(cate_url)
    time.sleep(3)
    soup = BeautifulSoup(response.content, 'html.parser')
    featured_posts = soup.find('ul', class_ = 'late-news-lst')
    list = featured_posts.find_all('li', class_ = 'clearfix')
    new_news = soup.find('ul',class_ = 'sub-news clearfix').find_all('li')
    news_big = soup.find('div',class_ = 'news-big').find('a',class_ = 'news-link')
    urls = []
    for i in new_news:
        url = i.find('a')['href']
        urls.append(url)
    for i in list:
        url = i.find('a')['href']
        urls.append(url)
    urls.append(news_big['href'])
    return urls
def filter_list(urls):
    filtered_urls = []
    crawl_time = datetime.fromtimestamp(time.time()-3*24*3600)
    for i in urls:
        response = requests.get(i)
        time.sleep(2)
        soup = BeautifulSoup(response.content, 'html.parser')
        try:
            #wrapper = soup.find('div', class_ = "col780 left clearafter")
            #date_posted = wrapper.find('p',class_ ='news-time left').text.strip()
            #date_posted_norm = convert_time_string(date_posted)
            date_str = soup.find('time').text.strip()
            #print(date_str)
            date_posted_norm = datetime.strptime(date_str, '%d/%m/%Y')
            #if ( (date_posted_norm.day == crawl_time.day) and (date_posted_norm.month == crawl_time.month) and (date_posted_norm.year == crawl_time.year) ):
            if date_posted_norm >= crawl_time:
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
def get_news_autodaily():
    _autodaily= {
            "home_page":"https://autodaily.vn/",
            "urls":{
                "Ô tô":
                {
                 "url":"https://autodaily.vn/#",
                 "sub-category":{  
                    0:{"name":"Ô tô",
                     "url":"https://autodaily.vn/",
                     "cate_id":58,
                      "url_list" : []},
                 }
                }
            }
        }
#
    add_list(_autodaily)
    add_post(_autodaily)
    return _autodaily
#send post content to wordpress via endpoint
def send_post_to_5goals(title,content,category_id,published_date):
    # URL of the API endpoint (this is a placeholder and needs to be replaced with the actual URL)
    url = "https://api2023.5goal.com/wp-json/custom/createPost"
    
    # Data to be sent in the POST request
    data = {
        "title": title,
        "content": content,
        "category_id": category_id,
        "token": '5goalvodichcmnl',#'draftpost',#  # Replace with your actual access token
        "published_date": published_date,
        "domain":"autodaily"
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
    _autodaily = get_news_autodaily()
    for i in list(_autodaily['urls'].keys()):
    #web_24h_com_vn2['url'][i]['cate_id']
        for j in list(_autodaily['urls'][i]['sub-category']):
            url_list =  _autodaily['urls'][i]['sub-category'][j]['url_list']
            print(url_list)
            for t in range(0,len(url_list)):
                content = _autodaily['urls'][i]['sub-category'][j]['content'][t]['text']
                title = _autodaily['urls'][i]['sub-category'][j]['content'][t]['title']
                published_date = _autodaily['urls'][i]['sub-category'][j]['content'][t]['published_date']
                cate_id = _autodaily['urls'][i]['sub-category'][j]['cate_id']
                print(title, url_list[t])
                #send_post_to_5goals(title,str(content), cate_id, published_date)
                try:
                    text_len = len(content.text)
                    if text_len <500:
                        print(content.text)
                        continue
                    else:
                         send_post_to_5goals(title,str(content),cate_id,published_date)
                except (AttributeError,TypeError):
                    continue
if __name__ == '__main__':
    main()