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
def get_content_eva(url):
    # def get_content_autodaily()
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    title = soup.find('h1', id = 'tieu_de_bai_viet').text.strip()
    date = soup.find('div', class_ = 'eva-author-time-art mar-b-25').text.strip()
    published_date = convert_string(date)
    article = soup.find('article', class_ = 'eva-cont-art no-copy')    
    #h2_tag = soup.new_tag('h2')
    #h2 = soup.find('h2')
    #try:
    article.insert(0,soup.find('h2'))
    for script_or_style in article(['script', 'style','iframe']):
        script_or_style.decompose()
    element = article.find('div', recursive= True)  # Example: remove comments from the first <div> element
    for comment in element.find_all(string=lambda text: isinstance(text, Comment)):
        comment.decompose()
    videos = article.find_all('div', align="center")
    related_article =  article.find('div', class_ = 'evtBox evtBoxPrBt')
    related_article.decompose()
    for video in videos:
        video.find_next_sibling('p', class_ = 'img_chu_thich_0407 eva-cont-art__cap-img text-center').decompose()
        video.decompose()
    for caption in article.find_all('p', class_ = "img_chu_thich_0407 eva-cont-art__cap-img text-center"):
        img_container = caption.find_previous_sibling()
        try:
            src = img_container.find('img')['data-original']
            img_tag = soup.new_tag('img')
            img_tag['src'] = src
            caption.insert_before(img_tag)
            caption_start = NavigableString("[caption id=\"\" align=\"aligncenter\" width=\"800\"]")
            caption_text = NavigableString(caption.text.strip())
            caption_end = NavigableString("[/caption]")
                # Insert the custom tags and caption text around the <img> tag
            img_tag.insert_before(caption_start)
            img_tag.insert_after(caption_end)
            img_tag.insert_after(caption_text)
            img_container.decompose()
            caption.decompose()
            #print(src)
        except TypeError:
            continue
    for i in article.find_all('img'):
            i['class'] = "aligncenter"
    for i in article.find_all('div', style="display: none"):
        i.decompose()
    for a_tag in article.find_all('a'):
        a_tag['href'] = 'javascript:void(0)'    
    for i in article.find_all(recursive = True):
        try:
            del i['onclick']
            i['id'] =''
            i['class']=''
            i['style'] =''
        except AttributeError:
            continue
        except TypeError:
            continue
    for item in article.find_all('div'):
        if item.string =="":
            item.decompose()
    source_tag = soup.new_tag('i') 
    source_tag.string = "Nguồn: eva.vn"  # Set the content of <i> tag
    remove_div(article)
    # Append the <i> tag as the last child of the <article> tag
    article.append(source_tag)
    #except AttributeError as e:
        #print(e, url)
    # Replace the <p> tag with the <strong> tag
    return article, title, published_date
def get_post(url):
    try:
        content,title,published_date = get_content_eva(url) 
        return content,title,published_date
    except AttributeError as e:
        print(e)
    
def get_list_url(cate_url):
    response = requests.get(cate_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    list = soup.find_all('article', class_ = 'eva-news-trend-h-items d-flex')
    urls = []
    for i in list:
        url = i.find('a')['href']
        urls.append(url)
    return urls
def filter_list(urls):
    filtered_urls = []
    crawl_time = datetime.fromtimestamp(time.time()-4*24*3600)
    for i in range(0,len(urls)):
        try:
            published_date = get_content_eva(urls[i])[2]
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
def get_news_eva():
    _eva= {
            "home_page":"https://eva.vn/",
            "urls":{
                "Nhân vật đẹp":
                {
                 "url":"https://eva.vn/nhan-vat-dep-c262.html#",
                 "sub-category":{  
                    0:{"name":"Người đẹp",
                     "url":"https://eva.vn/nhan-vat-dep-c262.html",
                     "cate_id":63,
                      "url_list" : []},
                 }
                }
            }
        }
#
    add_list(_eva)
    add_post(_eva)
    return _eva
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
        "domain":"eva.vn"
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
    _eva = get_news_eva()
    for i in list(_eva['urls'].keys()):
    #web_24h_com_vn2['url'][i]['cate_id']
        for j in list(_eva['urls'][i]['sub-category']):
            url_list =  _eva['urls'][i]['sub-category'][j]['url_list']
            print(url_list)
            for t in range(0,len(url_list)):
                content = _eva['urls'][i]['sub-category'][j]['content'][t]['text']
                title = _eva['urls'][i]['sub-category'][j]['content'][t]['title']
                published_date = _eva['urls'][i]['sub-category'][j]['content'][t]['published_date']
                cate_id = _eva['urls'][i]['sub-category'][j]['cate_id']
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