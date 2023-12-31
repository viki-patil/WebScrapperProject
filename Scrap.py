from flask import Flask, render_template, request,jsonify
from flask_cors import CORS, cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import logging
logging.basicConfig(filename="scrapper.log" , level=logging.INFO)
import math

app = Flask(__name__)

@app.route("/", methods = ['GET'])
def homepage():
    return render_template("index.html")

@app.route("/review", methods = ['POST'])
def index():
    if request.method == 'POST':
        try:
            searchString = request.form['content'].replace(" ","")
            flipkart_url = "https://www.flipkart.com/search?q=" + searchString
            uClient = uReq(flipkart_url)
            flipkartPage = uClient.read()
            uClient.close()
            flipkart_html = bs(flipkartPage, "html.parser")
            bigboxes = flipkart_html.findAll("div", {"class": "_1AtVbE col-12-12"})
            del bigboxes[0:3]
            del bigboxes[-3]
            print(len(bigboxes))

            box = bigboxes[0]
            productLink = "https://www.flipkart.com" + box.div.div.div.a['href']
            prodRes = requests.get(productLink)
            prodRes.encoding='utf-8'
            prod_html = bs(prodRes.text, "html.parser")
            
            # find total number of pages we need to scroll
            page_num = findNumberOfPages(prod_html)

            # find the flipkarts page links to scroll
            pages_link = getPageLinks(prod_html)
            
            rev_text=[]
            for i in range(1,int(page_num)+1):
                # Navigate to each pagelink to capture data
                flipcart_url_i = pages_link+f"{i}"
                # print(flipcart_url_i)
                req=requests.get(flipcart_url_i)
                
                # Capture each review individually
                # review=content.find_all('p',{"class":'_2sc7ZR _2V5EHH'})
                content=bs(req.content,'html.parser')
                reviewBoxes = content.select('div._1AtVbE.col-12-12 div._27M-vq')
                for reviewBox in reviewBoxes:
                    # print('reviewBox')
                    try:
                        name = reviewBox.select('div.row p._2sc7ZR._2V5EHH')[0].text
                        rating = reviewBox.select('div._3LWZlK._1BLPMq')[0].text
                        commentHead = reviewBox.select('p._2-N8zT')[0].text
                        custComment = reviewBox.select('div.t-ZTKy div div')[0].text
                    except:
                        logging.info(e)
                        print(e)
                        return 'Something wrong while fetching review details'
                    reviewDict = {
                        "Product": searchString, 
                        "Name": name, 
                        "Rating": rating, 
                        "CommentHead": commentHead,
                        "Comment": custComment
                        }
                    #print('reviewDict')
                    #print(reviewDict)
                    rev_text.append(reviewDict)

            return render_template('results.html', reviews=rev_text)
        except Exception as e:
            logging.info(e)
            print(e)
            return 'something is wrong'
    else:
        return render_template("index.html")


def findNumberOfPages(html):
    total_review_text = (html.find('div', {'class': "_3UAT2v _16PBlm"})).text
    print(total_review_text)
    total_review=int(total_review_text.split(" ")[1])
    print(total_review)
    review_per_page = 10
    total_pages= math.ceil(total_review/review_per_page)
    print(total_pages)
    return total_pages

def getPageLinks(html):
    uniqueChild= html.find('div', {'class': "_3UAT2v _16PBlm"})
    a_tag = uniqueChild.find_parent('a')
    href_value = a_tag.get('href')
    return "https://www.flipkart.com" +href_value +"&page="

if __name__=="__main__":
    # app.run(debug=True)
    app.run(host="0.0.0.0")




    
# flipcart_url = "https://www.flipkart.com/search?q=" + "iphone12pro"
# urlclient = urlopen(flipcart_url)
# flipcart_page = urlclient.read()
# flipcart_html = bs(flipcart_page, 'html.parser')
# bigboxes = flipcart_html.findAll("div", {"class": "_1AtVbE col-12-12"})
# print(len(bigboxes))
# del bigboxes[0:2]
# del bigboxes[-3:]
# print(len(bigboxes))
# box = bigboxes[len(bigboxes)-1]
# product_link = "https://flipkart.com" + bigboxes[1].div.div.div.a['href']
# print(product_link)
# product_req = requests.get(product_link)
# product_html = bs(product_req.text, 'html.parser')
# product_boxes = product_html.findAll("div", {"class": "_16PBlm"})
# print(len(product_boxes))
# del(product_boxes[-1])
# allReviews =[]
# for i in product_boxes:
#     print("Reviewer Name :")
#     print(i.div.div.find('p',{"class":"_2sc7ZR"}).text)
#     print("Reviewer Rating :")
#     print(i.div.div.div.div.text)
#     print("Reviewer Comment :")
#     print(i.div.div.div.p.text)
#     print("Reviewer Description :")
#     print(i.div.div.find_all('div', {"class":""}))
#     print("==================")
#     review = {
#         "name" : i.div.div.find('p',{"class":"_2sc7ZR"}).text,
#         "rating" : i.div.div.div.div.text,
#         "comment" : i.div.div.div.p.text,
#         "description" : i.div.div.find_all('div', {"class":""})
#     }
#     allReviews.append(review)
# print(allReviews)