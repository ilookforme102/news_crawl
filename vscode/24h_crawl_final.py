
#importing library
from bs4 import BeautifulSoup,NavigableString, Comment, Tag
import requests
import time
import re
from datetime import datetime
import html5lib
def remove_div(article):
    divs = article.find_all('div')
    empty_divs = [div for div in divs if not div.text.strip() and not div.contents]
    if not empty_divs:
        return  # No more empty divs, stop recursion
    for div in empty_divs:
        div.decompose()
def get_content(url):
    response = requests.get(url)
    time.sleep(3)
    soup = BeautifulSoup(response.content,  'html.parser')
    try:
        article = soup.find('article', class_ = 'cate-24h-foot-arti-deta-info')
        #remove the last 4 element
        try:
            article.find('p', class_ = 'tuht_all').decompose()
            article.find('div',class_  = 'bv-lq').decompose()
            article.find('div', id = 'zone_banner_sponser_product').decompose()
            #article.find('p', class_ = 'linkOrigin').decompose()
            article.find('div', class_ ='pgS2 txtCent grnBxBg bld clrGrn mgt20').decompose()
            article.find('div', class_ = 'block-quiz').decompose()
            article.find('div', class_ = 'podcasts-eva-t').decompose()
        except AttributeError as e:
            print(e)
        tags_to_remove = article.find_all(['span'])
        for tag in tags_to_remove:
            # Extract the text from the tag
            tag_text = tag.get_text()
            # Replace the tag with its text content
            tag.replace_with(tag_text)
            tag.text.strip()
        a_tags_to_remove = article.find_all('a', class_ = "TextlinkBaiviet" )
        for a in a_tags_to_remove:
            # Extract the text from the tag
            tag_text = a .get_text()
            # Replace the tag with its text content
            a .replace_with(tag_text)
            a .text.strip()
        # set attribut for img
        # set attribut for img
        b = article.find_all('img')
        for i in b:
            if '.svg' in i['src']:
                i.decompose()
        for i in article.find_all('img'):
            if 'data-original' in i.attrs.keys():
                i['src'] = i.get('data-original')
            #i.attrs = ['class', 'alt', 'src', 'data-original']
            del i['onclick']
            del i['style']
            del i['class']
        #remove js  and css
        h2 = soup.find('article', class_ = 'cate-24h-foot-arti-deta-info').find('h2')
        h2_text = '\n'.join(line.strip() for line in h2.get_text().split('\n') if line.strip())
        # Update the text of the h2 tag
        h2.string = h2_text
        #soup2 = BeautifulSoup("", 'html.parser')
        #soup2.append(h2)
        for script_or_style in article(['script', 'style']):
            script_or_style.decompose()
        for i in article.find_all(recursive = True):
            if i.name != 'p':
                try:
                    del i['onclick']
                    del i['id']
                    del i['class']
                    del i['style']
                except AttributeError:
                    continue
                except TypeError:
                    continue
        for i in article.find_all('img'):
            i['class'] = "aligncenter"
            i['width'] = 800
            i['height'] = 400
        for video in article.find_all('video'):
            video.decompose()
        for i in article.find_all('p', class_ = 'img_chu_thich_0407'):
                i['style'] = "text-align: center;"
                del i['class']
        for i in article.find_all('div', {'align': 'center'}):
            i.decompose()
        for element in article.find_all(recursive = True,string=True):
            if isinstance(element, NavigableString) and element.strip() == '':
                element.extract()
        for i in article.find_all('div'):
            if i.children == None and i.string == None:
                i.decompose()
        source_tag = soup.new_tag('i') 
        source_tag.string = "Nguồn: 24h.com.vn"  # Set the content of <i> tag
        # Append the <i> tag as the last child of the <article> tag
        article.append(source_tag)
        """a_tags_to_remove = article.find_all('a', class_ ="TextlinkBaiviet")
        for a in a_tags_to_remove:
            # Extract the text from the tag
            tag_text = a .get_text()
            # Replace the tag with its text content
            a.replace_with(tag_text)
            a.text.strip()"""
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
        remove_div(article)
        article.find('p', class_ = 'linkOrigin').decompose()
    except (AttributeError, IndexError, TypeError):
        try:
            article = soup.find('div', id= 'magazine_news')
            strong_text = article.find('div', class_ = 'titZing').find('p').text.strip()
            source_tag = soup.new_tag('h2') 
            source_tag.string = strong_text
            article.insert(0,source_tag)
            article.find('div', class_ = 'titZing').decompose()
            videos = article.find_all('div', class_ = 'videoUpload24h')
            vd_captions = article.find_all('div', class_ = 'mg-video-caption')
            for vd_caption in vd_captions:
                vd_caption.decompose()
            for video in videos:
                video.decompose()
            tags_to_remove = article.find_all(['span'])
            for tag in tags_to_remove:
                # Extract the text from the tag
                tag_text = tag.get_text()
                # Replace the tag with its text content
                tag.replace_with(tag_text)
                tag.text.strip()
            a_tags_to_remove = article.find_all('a', class_ ="TextlinkBaiviet")
            for a in a_tags_to_remove:
                # Extract the text from the tag
                tag_text = a .get_text()
                # Replace the tag with its text content
                a.replace_with(tag_text)
                a.text.strip()
            # set attribut for img
            b = article.find_all('img')
            for i in b:
                if '.svg' in i['src']:
                    i.decompose()
            b = article.find_all('img')
            for i in article.find_all('img'):
                try:
                    if 'imgFullMobile_chuan' in  i.parent['class'] or 'imgFullMobile' in  i.parent['class']:
                        i.decompose()
                except KeyError as e:
                    print(e)   
            for i in article.find_all('img'):
                if 'data-original' in i.attrs.keys():
                    i['src'] = i.get('data-original')
                #i.attrs = ['class', 'alt', 'src', 'data-original']
                #del i['onclick']
                #del i['style']
                #del i['class']
                list_attr = ['src','alt','data-src']
                for i in article.find_all('img'):
                    for j in list(i.attrs.keys()):
                        if j not in list_attr:
                            i.attrs.pop(j)
                for i in article.find_all('img'):
                    if 'https://image-us.24h.com.vn/' not in i['src']:
                        i['src']= i['data-src']
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
            for i in article.find_all('img'):
                i['class'] = "aligncenter"
                i['width'] = 800
                i['height'] = 400
            source_tag = soup.new_tag('i') 
            source_tag.string = "Nguồn: 24h.com.vn"  # Set the content of <i> tag
            #remove empty div or empty space from element
            for i in article.find_all('div',recursive= True):
                if i.string == None:
                    if i.text =='':
                        i.decompose()
            for element in article.find_all(recursive = True,string=True):
                if isinstance(element, NavigableString) and element.strip() == '':
                    element.extract()
            #remove html comment from element   
            for comment in article.find_all(string=lambda text: isinstance(text, Comment)):
                comment.extract()
            # Append the <i> tag as the last child of the <article> tag
            article.append(source_tag)
            """a_tags_to_remove = article.find_all('a', class_ = "TextlinkBaiviet")
            for a in a_tags_to_remove:
                # Extract the text from the tag
                tag_text = a .get_text()
                # Replace the tag with its text content
                a.replace_with(tag_text)
                a.text.strip()"""
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
            remove_div(article)
        except AttributeError as e:
            print(e)
    return article
#convert time from post to the format of output
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
#Convert time from post to datetime format
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

def get_post(url):
    try:
        response = requests.get(url)
        time.sleep(3)
        soup = BeautifulSoup(response.content, 'html5lib')
        content = get_content(url)
        post_time = soup.find('time', class_ = 'cate-24h-foot-arti-deta-cre-post').text.strip()
        published_date = convert_string(post_time)
        title = soup.find('h1').text.strip()
        #h2 = soup.find('h2').text.strip()
        #images_src = [i.attrs['src'] for i in soup.find('article', class_= 'cate-24h-foot-arti-deta-info').find_all('img')[:-1] if 'svg' not in i.attrs['src']]
        #images_src = [img['data-original'] if 'https://image-us.24h.com.vn' not in img['src'] else img['src'] if 'svg' not in img['src'] else '' for img in soup.find('article', class_ = 'cate-24h-foot-arti-deta-info').find_all('img')[:-1]]
        #text_list = [ child.text for child in soup.find('article', class_= 'cate-24h-foot-arti-deta-info').find_all('p')[:-3] if re.sub(r'\n+', '', child.text) != ""]
        #text_list = [h2] + text_list
        #return content,title,published_date
    except AttributeError:
        try:
            response = requests.get(url)
            time.sleep(3)
            soup = BeautifulSoup(response.content, 'html5lib')
            content = get_content(url)
            post_time = soup.find('div', class_ = 'magazine_event_date').text.strip()
            published_date = convert_string(post_time)
            title = soup.find('div', class_ = 'titZing').text.strip()
        except AttributeError as e:
            print(e)
            content = ''
            title = ''
            published_date= ''
    return content,title,published_date
def get_list_url_cntt(cate_url):
    urls = []
    response = requests.get(cate_url)
    time.sleep(3)
    soup = BeautifulSoup(response.content,'html5lib')
    try:
        news_block  =soup.find('section', id = 'tin_bai_noi_bat_khac').find_all('a')[:-1]
        for i in news_block:
            url = i['href']
            if url not in urls:
                urls.append(url)
    except Exception as e:
        print(e)
    try:
        recent_news =  soup.find('div', class_ = 'coll-left pos-rel').find_all('a')
        for i in recent_news:
            url = i['href']
            if url not in urls:
                urls.append(url)
    except Exception as e:
        print(e)
    try:
        recent_news2 =   soup.find('div', class_ = 'coll-right').find_all('a')
        for i in recent_news2:
            url = i['href']
            if url not in urls:
                urls.append(url)    
    except Exception as e:
        print(e)
    return urls
def get_list_url_sao(cate_url):
    urls = []
    response = requests.get(cate_url)
    time.sleep(3)
    soup = BeautifulSoup(response.content,'html5lib')
    try:
        news_block  =soup.find('div', id = 'left').find_all('a')[:-1]
        for i in news_block:
            url = i['href']
            if 'https://us.24h.com.vn/' in url:
                if url not in urls:
                    urls.append(url)
    except Exception as e:
        print(e)
    try:
        recent_news =  soup.find('div', class_ = 'coll-left pos-rel').find_all('a')
        for i in recent_news:
            url = i['href']
            if url not in urls:
                urls.append(url)
    except Exception as e:
        print(e)
    try:
        recent_news2 =   soup.find('div', class_ = 'coll-right').find_all('a')
        for i in recent_news2:
            url = i['href']
            if url not in urls:
                urls.append(url)    
    except Exception as e:
        print(e)
    return urls
def get_list_url_nguoidep(cate_url):
    urls = []
    response = requests.get(cate_url)
    time.sleep(3)
    soup = BeautifulSoup(response.content,'html5lib')
    try:
        news_block  =soup.find('div', class_ = 'cate-24h-foot-home-latest-list').find_all('a')[:-1]
        for i in news_block:
            url = i['href']
            if 'https://us.24h.com.vn/' in url:
                if url not in urls:
                    urls.append(url)
    except Exception as e:
        print(e)
    try:
        recent_news =  soup.find('div', class_ = 'coll-middle pos-rel').find_all('a')
        for i in recent_news:
            url = i['href']
            if url not in urls:
                urls.append(url)
    except Exception as e:
        print(e)
    try:
        recent_news2 =   soup.find('div', class_ = 'coll-right').find_all('a')
        for i in recent_news2:
            url = i['href']
            if url not in urls:
                urls.append(url)    
    except Exception as e:
        print(e)
    return urls
def filter_list(urls):
    filtered_urls = []
    crawl_time = datetime.fromtimestamp(time.time() -2*24*3600)
    for i in urls:
        response = requests.get(i)
        soup = BeautifulSoup(response.content, 'html5lib')
        try:
            date_posted = soup.find('time').text.strip()
            date_posted_norm = convert_time_string(date_posted)
            if ( (date_posted_norm.day == crawl_time.day) and (date_posted_norm.month == crawl_time.month) and (date_posted_norm.year == crawl_time.year) ):
            #if date_posted_norm >= crawl_time:
                filtered_urls.append(i)
                print(i)
        except AttributeError as e:
            print(e)
            break
    return filtered_urls
def get_list_url(cat_url):
    urls = []
    response = requests.get(cat_url)
    time.sleep(3)
    soup = BeautifulSoup(response.content,'html5lib')
    try:
        news_block  = soup.find('section', id = 'tin_bai_noi_bat_khac')
        try:
            url_list = news_block.find_all('a')
            #print(len(url_list))
            for url in url_list:
                if 'https://www.24h.com.vn/' in url['href']:
                    if url['href'] not in urls:
                        urls.append(url['href'])
            print(len(urls))
        except AttributeError as e:
            print(e)
    except AttributeError as e:
        print(e)
    try:
        news_block  = soup.find('div', class_ = 'cate-24h-foot-home-latest-list')
        try:
            url_list = news_block.find_all('a')
            #print(len(url_list))
            for url in url_list:
                if 'https://www.24h.com.vn/' in url['href']:
                    if url['href'] not in urls:
                        urls.append(url['href'])
            print(len(urls))
        except AttributeError as e:
            print(e)
    except AttributeError as e:
        print(e)
    return urls
def add_list(web_24h_com_vn):
    for i in list(web_24h_com_vn['urls'].keys()):
        for j in list(web_24h_com_vn['urls'][i]['sub-category'].keys()):  
            #urls = get_list_url(web_24h_com_vn['urls'][i]['sub-category'][j]['url'])
            urls = web_24h_com_vn['urls'][i]['sub-category'][j]['get_list']
            print(i,j,web_24h_com_vn['urls'][i]['sub-category'][j]['url'])
            web_24h_com_vn['urls'][i]['sub-category'][j]['url_list'] = filter_list(urls)

def add_post(web_24h_com_vn):
    for i in list(web_24h_com_vn['urls'].keys()):
        for j in list(web_24h_com_vn['urls'][i]['sub-category'].keys()):
            web_24h_com_vn['urls'][i]['sub-category'][j]['content'] = {}
            list_key = [v for v in range(0,len(web_24h_com_vn['urls'][i]['sub-category'][j]['url_list']))]
            for u in list_key:
                web_24h_com_vn['urls'][i]['sub-category'][j]['content'][u] = {}
                if u != "":
                    web_24h_com_vn['urls'][i]['sub-category'][j]['content'][u]['text'] ,web_24h_com_vn['urls'][i]['sub-category'][j]['content'][u]['title'],web_24h_com_vn['urls'][i]['sub-category'][j]['content'][u]['published_date'] = get_post(web_24h_com_vn['urls'][i]['sub-category'][j]['url_list'][u])
                    print(i,j,web_24h_com_vn['urls'][i]['cate_id'],web_24h_com_vn['urls'][i]['sub-category'][j]['name'],web_24h_com_vn['urls'][i]['sub-category'][j]['name'],web_24h_com_vn['urls'][i]['sub-category'][j]['content'][u]['title'],web_24h_com_vn['urls'][i]['sub-category'][j]['url_list'][u])
                
def get_news():
    web_24h_com_vn = {
        "home_page":"https://www.24h.com.vn/",
        "urls":{
            "tech":
            {
             "url":"https://www.24h.com.vn/cong-nghe-thong-tin-c55.html",
             "cate_id":57,
             "sub-category":{
                0:{"name":"Game",
                 "get_list": get_list_url_cntt("https://www.24h.com.vn/game-c69.html"),
                 "url":"https://www.24h.com.vn/game-c69.html"},
                1:{"name":"Phần mềm",
                   "get_list": get_list_url_cntt("https://www.24h.com.vn/phan-mem-ngoai-c302.html"),
                 "url":"https://www.24h.com.vn/phan-mem-ngoai-c302.html"},
                2:{"name":"Khoa học",
                   "get_list": get_list_url_cntt("https://www.24h.com.vn/khoa-hoc-c782.html"),
                 "url":"https://www.24h.com.vn/khoa-hoc-c782.html"},
                3:{"name":"Mạng xã hội",
                   "get_list": get_list_url_cntt("https://www.24h.com.vn/mang-xa-hoi-c889.html"),
                 "url":"https://www.24h.com.vn/mang-xa-hoi-c889.html"},
                4:{"name":"Thủ thuật - Tiện ích",
                   "get_list": get_list_url_cntt("https://www.24h.com.vn/thu-thuat-tien-ich-c68.html"),
                 "url":"https://www.24h.com.vn/thu-thuat-tien-ich-c68.html"},
                5:{"name":"Sợ Virus",
                   "get_list": get_list_url_cntt("https://www.24h.com.vn/tim-hieu-virus-c57.html"),
                 "url":"https://www.24h.com.vn/tim-hieu-virus-c57.html"},
                6:{"name":"Máy in/phụ kiện",
                   "get_list": get_list_url_cntt("https://www.24h.com.vn/may-in/phu-kien-c291.html"),
                 "url":"https://www.24h.com.vn/may-in/phu-kien-c291.html"},
                7:{"name":"Khám phá công nghệ",
                   "get_list": get_list_url_cntt("https://www.24h.com.vn/kham-pha-cong-nghe-c675.html"),
                 "url":"https://www.24h.com.vn/kham-pha-cong-nghe-c675.html"}
                     }
                },
            "youths":
            {
            "url":"https://www.24h.com.vn/ban-tre-cuoc-song-c64.html",
            "cate_id":60,
             "sub-category":{
                0:{"name":"Chuyện công sở",
                   "get_list": get_list_url_cntt("https://www.24h.com.vn/chuyen-cong-so-c180.html"),
                   "url":"https://www.24h.com.vn/chuyen-cong-so-c180.html"},
                1:{"name":"Tình yêu - Giới Tính",
                   "get_list": get_list_url_cntt("https://www.24h.com.vn/tinh-yeu-gioi-tinh-c306.html"),
                   "url":"https://www.24h.com.vn/tinh-yeu-gioi-tinh-c306.html"},
                2:{"name":"Ngoại tình",
                   "get_list": get_list_url_cntt("https://www.24h.com.vn/ngoai-tinh-c435.html"),
                   "url":"https://www.24h.com.vn/ngoai-tinh-c435.html"},
                3:{"name":"Giới trẻ",
                   "get_list": get_list_url_cntt("https://www.24h.com.vn/gioi-tre-c434.html"),
                   "url":"https://www.24h.com.vn/gioi-tre-c434.html"},
                4:{"name":"Hotgirl - Hotboy",
                   "get_list": get_list_url_cntt("https://www.24h.com.vn/hotgirl-hot-boy-c64e3398.html"),
                   "url":"https://www.24h.com.vn/hotgirl-hot-boy-c64e3398.html"},
                5:{"name":"Nhịp sống trẻ",
                   "get_list": get_list_url_cntt("https://www.24h.com.vn/nhip-song-tre-c685.html"),
                   "url":"https://www.24h.com.vn/nhip-song-tre-c685.html"}
             }
            },
            "showbiz":
            {
            "cate_id":59,
            "url":"https://www.24h.com.vn/doi-song-showbiz-c729.html",
             "sub-category":{
                0:{"name":"Sao Việt",
                   "get_list": get_list_url_sao("https://www.24h.com.vn/sao-viet-c757.html"),
                   "url":"https://www.24h.com.vn/sao-viet-c757.html"},
                1:{"name":"24h gặp gỡ",
                   "get_list": get_list_url_sao("https://www.24h.com.vn/gap-go-24h-c729e6820.html"),
                   "url":"https://www.24h.com.vn/gap-go-24h-c729e6820.html"},
                2:{"name":"Talk với sao",
                   "get_list": get_list_url_sao("https://www.24h.com.vn/doi-thoai-cung-sao-c730.html"),
                   "url":"https://www.24h.com.vn/doi-thoai-cung-sao-c730.html"},
                3:{"name":"Sao châu Á",
                   "get_list": get_list_url_sao("https://www.24h.com.vn/sao-chau-a-c759.html"),
                   "url":"https://www.24h.com.vn/sao-chau-a-c759.html"},
            }
            },
            "cars":
            {
            "cate_id":58,
            "url":"https://www.24h.com.vn/o-to-c747.html",
             "sub-category":{
                0:{"name":"Tin tức ô tô",
                   "get_list": get_list_url_sao("https://www.24h.com.vn/tin-tuc-o-to-c332.html"),
                   "url":"https://www.24h.com.vn/tin-tuc-o-to-c332.html"},
                1:{"name":"Bảng giá xe ô tô",
                   "get_list": get_list_url_sao("https://www.24h.com.vn/bang-gia-xe-o-to-c807.html"),
                   "url":"https://www.24h.com.vn/bang-gia-xe-o-to-c807.html"},
                2:{"name":"Tư vấn",
                   "get_list": get_list_url_sao("https://www.24h.com.vn/tu-van-c240.html"),
                   "url":"https://www.24h.com.vn/tu-van-c240.html"},
                3:{"name":"Ngắm xe",
                   "get_list": get_list_url_sao("https://www.24h.com.vn/anh-nguoi-dep-va-xe-c199.html"),
                   "url":"https://www.24h.com.vn/anh-nguoi-dep-va-xe-c199.html"},
                4:{"name":"Đánh giá xe",
                   "get_list": get_list_url_sao("https://www.24h.com.vn/so-sanh-xe-c805.html"),
                   "url":"https://www.24h.com.vn/so-sanh-xe-c805.html"},
            }
            },
            "người đẹp":
            {
            "cate_id":63,
            "url":"https://www.24h.com.vn/hau-truong-ngoi-sao-the-thao-c797.html#",
             "sub-category":{
                0:{"name":"người đẹp thể thao",
                   "get_list": get_list_url_nguoidep("https://www.24h.com.vn/hau-truong-ngoi-sao-the-thao-c797.html"),                   
                   "url":"https://www.24h.com.vn/hau-truong-ngoi-sao-the-thao-c797.html"}
            }
            }
            
    }}
#
    add_list(web_24h_com_vn)
    add_post(web_24h_com_vn)
    return web_24h_com_vn
def send_post_to_5goals(title,content,category_id,published_date):
    # URL of the API endpoint (this is a placeholder and needs to be replaced with the actual URL)
    url = "https://api2023.5goal.com/wp-json/custom/createPost"
    
    # Data to be sent in the POST request
    data = {
        "title": title,
        "content": content,
        "category_id": category_id,
        "token": '5goalvodichcmnl',  # Replace with your actual access token
        "published_date": published_date
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
    web_24h_com_vn = get_news()
    for i in list(web_24h_com_vn['urls'].keys()):
    #web_24h_com_vn2['url'][i]['cate_id']
        for j in list(web_24h_com_vn['urls'][i]['sub-category']):
            url_list =  web_24h_com_vn['urls'][i]['sub-category'][j]['url_list']
            for t in range(0,len(url_list)):
                text = web_24h_com_vn['urls'][i]['sub-category'][j]['content'][t]['text']
                title = web_24h_com_vn['urls'][i]['sub-category'][j]['content'][t]['title']
                published_date = web_24h_com_vn['urls'][i]['sub-category'][j]['content'][t]['published_date']
                cate_id = web_24h_com_vn['urls'][i]['cate_id']
                print("title: ", title, "\n")
                print("date: ", published_date, "\n")
                print("id: ", cate_id, "\n")
                try:
                    text_len = len(text.text)
                    if text_len <500:
                        print(text.text)
                        continue
                    if "Clip:" in title:
                        print(title)
                        continue
                    else:
                         send_post_to_5goals(title,str(text),cate_id,published_date)
                except (AttributeError,TypeError):
                    continue

if __name__ == '__main__':
    main()

                