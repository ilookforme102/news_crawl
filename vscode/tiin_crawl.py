import requests 
import time
import re
from datetime import datetime
from bs4 import BeautifulSoup,NavigableString, Comment, Tag
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


def remove_div(article):
    divs = article.find_all('div')
    empty_divs = [div for div in divs if not div.text.strip() and not div.contents]
    if not empty_divs:
        return  # No more empty divs, stop recursion
    for div in empty_divs:
        div.decompose()
def get_content_tiin(url):
    # def get_content_autodaily()
    response = requests.get(url)
    time.sleep(2)
    soup = BeautifulSoup(response.content, 'html.parser')
    title = soup.find('h1', class_ = 'detail-title').text.strip()
    h2 = soup.find('h2', class_ = 'detail-lead')
    date = soup.find('h2', class_ = 'detail-lead').find_next_sibling('div', class_ = 'clearfix').find('p').text.strip()    
    published_date = convert_string(date)
    article = soup.find('div', class_ = 'detail-content')
    article.insert(0,h2)
    for img in article.find_all('img'):
        img['src'] = img['data-src']
        img['class'] = "aligncenter"
        if 'svg' in img['data-src']:
                i.decompose()
    element = article.find('div', recursive= True)  # Example: remove comments from the first <div> element
    for comment in element.find_all(string=lambda text: isinstance(text, Comment)):
        comment.decompose()
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
    article.find('div', class_ = 'more-detail bg_cms_vang').decompose()
    article.find('div', class_ = 'hot_news_img').find_next_sibling('p', class_ = 'isNote').decompose()
    article.find('div', class_ = 'hot_news_img').decompose()
    for i in article.find_all(recursive = True):
        if i.name not in ['figcaption', 'p']:
            try:
                del i['onclick']
                del i['id']
                del i['class']
                del i['style']
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
    for script_or_style in article(['script', 'style','iframe','video']):
        script_or_style.decompose()
    source_tag = soup.new_tag('i') 
    source_tag.string = "Nguồn: tiin.vn"  # Set the content of <i> tag
    article.append(source_tag)
    return article, title, published_date
def get_post(url):
    try:
        content,title,published_date = get_content_tiin(url) 
        return content,title,published_date
    except AttributeError as e:
        return
    
def get_list_url(cate_url):
    response = requests.get(cate_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    container = soup.find('div', class_ = 'category')
    img_tags = container.find_all('img')[:-2]
    urls = []
    for i in img_tags:
        url = i.parent['href']
        urls.append(url)
    return urls
def filter_list(urls):
    filtered_urls = []
    crawl_time = datetime.fromtimestamp(time.time()-0*24*3600)
    for i in range(0,len(urls)):
        try:
            published_date = get_content_tiin(urls[i])[2]
            date_posted_norm = datetime.strptime(published_date, '%Y-%m-%d')
            #if ( (date_posted_norm.day == crawl_time.day) and (date_posted_norm.month == crawl_time.month) and (date_posted_norm.year == crawl_time.year) ):
            if date_posted_norm >= crawl_time:   
                filtered_urls.append(urls[i])
                #print(i)
        except AttributeError as e:
            #print(e)
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
def get_news_tiin():
    _tiin= {
            "home_page":"https://tiin.vn/",
            "urls":{
                "Người đẹp":
                {
                 "url":"https://tiin.vn/sao.html#",
                 "sub-category":{  
                    0:{"name":"Sao",
                     "url":"https://tiin.vn/sao.html",
                     "cate_id":59,#63,
                      "url_list" : []
                      },
                    }
                }
            }
        }
#
    add_list(_tiin)
    add_post(_tiin)
    return _tiin
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
        "domain":"tiin"
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
    _tiin = get_news_tiin()
    for i in list(_tiin['urls'].keys()):
    #web_24h_com_vn2['url'][i]['cate_id']
        for j in list(_tiin['urls'][i]['sub-category']):
            url_list =  _tiin['urls'][i]['sub-category'][j]['url_list']
            print(url_list)
            for t in range(0,len(url_list)):
                content = _tiin['urls'][i]['sub-category'][j]['content'][t]['text']
                title = _tiin['urls'][i]['sub-category'][j]['content'][t]['title']
                published_date = _tiin['urls'][i]['sub-category'][j]['content'][t]['published_date']
                cate_id = _tiin['urls'][i]['sub-category'][j]['cate_id']
                print(title, url_list[t])
                #send_post_to_5goals(title,str(content), cate_id, published_date)
                try:
                    text_len = len(content.text)
                    if text_len <450:
                        print(content.text)
                        continue
                    else:
                        send_post_to_5goals(title,str(content),cate_id,published_date)
                        print("Good job, well done!!!")
                except (AttributeError,TypeError):
                    continue

if __name__ == '__main__':
    main()