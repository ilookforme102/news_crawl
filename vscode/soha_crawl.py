
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

def get_content_soha(url):
    response = requests.get(url)
    time.sleep(3)
    soup = BeautifulSoup(response.content, 'html.parser')
    title = soup.find('h1').text.strip()
    date = soup.find('time').text.strip()
    published_date = convert_string(date)
    article = soup.find('article').find('div',class_ = 'detail-body')
    h2 = soup.find('h2')
    h2.string = h2.text.strip()
    for script_or_style in article(['script', 'style','iframe']):
                script_or_style.decompose()
    try:
        i_tag = article.find('div', class_ = 'VCSortableInPreviewMode').parent.find_all('i',recursive = True)
        for i in i_tag:
            if "Nguồn" in i.text or "Tham khảo" in i.text:
                i.decompose()
    except Exception as e:
        print(e)
    try:
        related_item = article.find('div', id = 'relationnews').decompose()
        article.find('p', class_ = 'VCObjectBoxRelatedNewsItemSapo').parent.decompose()
        
        #article.find('div', class_ = 'VCSortableInPreviewMode').decompose()
        #article.find('div', class_ = 'VCSortableInPreviewMode link-content-footer IMSCurrentEditorEditObject').decompose()
    except Exception as e:
        print(e)
    try:
        article.find('div', class_ = 'bottom-info clearfix').decompose()
        article.find('div', class_ = 'VCSortableInPreviewMode').decompose()
        article.find('div', class_ = 'VCSortableInPreviewMode alignRight').decompose()
    except Exception as e:
        print(e))
    tags_to_remove = article.find_all(['span'])
    for tag in tags_to_remove:
        # Extract the text from the tag
        tag_text = tag.get_text()
        # Replace the tag with its text content
        tag.replace_with(tag_text)
        tag.text.strip()
    
    for video in article.find_all('video'):
        video.decompose()
    for caption in article.find_all('figcaption', class_ = 'PhotoCMS_Caption'):
        i =  caption.find('p')
        i['style'] = "text-align: center;"
        #i['class'] = "aligncenter"
        del i['class']
    figures = article.find_all('figure')
    for fig in figures:
        del fig['style']
        del fig['allow-zoom']
        del fig['type']
        del fig['data-originalw']
        del fig['class']
        del fig['data-originalh']
    for i in article.find_all(recursive = True):
        try:
            del i['onclick']
            del i['id']
            del i['class']
            del i['href']
        except AttributeError:
            continue
        #try:
            #print(i)
            
        except TypeError:
            continue
    for i in article.find_all('img'):
        if 'data-original' in i.attrs.keys():
            i['src'] = i.get('data-original')
        #i.attrs = ['class', 'alt', 'src', 'data-original']
        del i['onclick']
        del i['style']
        i['class'] = "aligncenter"
        i['width'] = 800
        i['height'] = 400
    # Append the <i> tag as the last child of the <article> tag
    source_tag = soup.new_tag('i') 
    source_tag.string = "Nguồn: soha.vn"  # Set the content of <i> tag
    article.append(source_tag)
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
    for element in article.find_all(recursive = True,string=True):
        if isinstance(element, NavigableString) and element.strip() == '':
            element.extract()
    for i in article.find_all('div'):
        if i.children == None and i.string == None:
            i.decompose()
    return article, title, published_date
def get_post(url):
    try:
        content,title,published_date = get_content_soha(url)
        return content,title,published_date
    except AttributeError as e:
        print(e)
def get_list_url(cate_url):
    response = requests.get(cate_url)
    urls = []
    time.sleep(3)
    soup = BeautifulSoup(response.content, 'html.parser')
    featured_posts = soup.find('div', class_ = 'sh_bigleft list-need-load-thread').find('div',class_ = 'box-category-middle')
    list = featured_posts.find_all('div', class_ = 'box-category-item')
    for i in list:
        path = i.find('a')['href']
        url = 'https://soha.vn' +  path
        urls.append(url)
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
            date_posted_norm = convert_time_string(date_str)
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
def get_news_soha():
    _soha= {
            "home_page":"https://soha.vn/",
            "urls":{
                "Ô tô":
                {
                 "url":"https://soha.vn/xe.htm#",
                 "sub-category":{  
                    0:{"name":"Ô tô",
                     "url":"https://soha.vn/xe.htm",
                     "cate_id":58,
                      "url_list" : []},
                 }
                }
            }
        }
#
    add_list(_soha)
    add_post(_soha)
    return _soha
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
        "domain":"soha"
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
    _soha = get_news_soha()
    for i in list(_soha['urls'].keys()):
    #web_24h_com_vn2['url'][i]['cate_id']
        for j in list(_soha['urls'][i]['sub-category']):
            url_list =  _soha['urls'][i]['sub-category'][j]['url_list']
            print(url_list)
            for t in range(0,len(url_list)):
                content = _soha['urls'][i]['sub-category'][j]['content'][t]['text']
                title = _soha['urls'][i]['sub-category'][j]['content'][t]['title']
                published_date = _soha['urls'][i]['sub-category'][j]['content'][t]['published_date']
                cate_id = _soha['urls'][i]['sub-category'][j]['cate_id']
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