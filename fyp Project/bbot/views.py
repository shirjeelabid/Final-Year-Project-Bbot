from django.shortcuts import render
from django.http import HttpResponse
from .models import Product, Customer, DealDone
# Create your views here.
import random


import nltk
# nltk.download('punkt')
# nltk.download('wordnet')
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()
import pickle
import numpy as np

from keras.models import load_model
model = load_model('chatbot_model.h5')
import json
import random
intents = json.loads(open('New_intents.json').read())
words = pickle.load(open('words.pkl','rb'))
classes = pickle.load(open('classes.pkl','rb'))

buyer_offers_list = []


def clean_up_sentence(sentence):
    
    # tokenize the pattern - splitting words into array
    sentence_words = nltk.word_tokenize(sentence)
    # stemming every word - reducing to base form
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words


# return bag of words array: 0 or 1 for words that exist in sentence
def bag_of_words(sentence, words, show_details=True):
    
    # tokenizing patterns
    sentence_words = clean_up_sentence(sentence)
    # bag of words - vocabulary matrix
    bag = [0]*len(words)  
    for s in sentence_words:
        for i,word in enumerate(words):
            if word == s: 
                # assign 1 if current word is in the vocabulary position
                bag[i] = 1
                if show_details:
                    print ("found in bag: %s" % word)
    return(np.array(bag))

def predict_class(sentence):
    
    # filter below  threshold predictions
    p = bag_of_words(sentence, words,show_details=False)
    res = model.predict(np.array([p]))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i,r] for i,r in enumerate(res) if r>ERROR_THRESHOLD]
    # sorting strength probability
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({"intent": classes[r[0]], "probability": str(r[1])})
    return return_list

def getResponse(ints, intents_json):
    
    tag = ints[0]['intent']
    list_of_intents = intents_json['intents']
    for i in list_of_intents:
        if(i['tag']== tag):
            result = random.choice(i['responses'])
            break
    return result






def new_amount_offer(buyer_offer, new_offer, actual_amount, thresh, buyer_offers_list):
    
    temp = 0
    iterator = len(buyer_offers_list)
    if iterator==1:
        price_cut = buyer_offer * 100/actual_amount
        temp = new_offer - price_cut
        temp = temp/10
        temp = temp * 0.10
    else:
        price_cut = buyer_offer * 100/actual_amount
        temp = new_offer - price_cut
        temp = (temp/10)
        temp = temp * 0.10 
        return (temp*100)-(iterator*10)
    
    return (temp*100)
        

def extract_amount(sentence):
    try:
        sentence = sentence.lower()
        if "rs." in sentence:
            price_start = str.find(sentence, "rs.")
            price_end = str.find(sentence, "/-")
            amount = sentence[price_start + 3:price_end]
            amount = amount.strip()  
            return float(amount)
    except:
        return 'invalid_amount'
    


def send(msg, actual_amt, thresh):
    
    new_offer = actual_amt 
    
    buyer_offer = extract_amount(msg)
    concat_msg = ""
    if(buyer_offer!=None):
        
        buyer_offers_list.append(buyer_offer)
        max_offer = max(buyer_offers_list)
        buyer_offers_list.index(max_offer)
        
        if len(buyer_offers_list)>1:
            
            if buyer_offers_list[-1]<max_offer:
                concat_msg += "Are you playing? You have offered more than a few seconds ago."
                if max_offer<thresh:
                    concat_msg += "All of your offers are rejected. You are offering less than no-loss/no-profit amount."
            else:

                new_offer = new_amount_offer(buyer_offer, new_offer, actual_amt, thresh, buyer_offers_list)
                if buyer_offer<new_offer:
                    concat_msg += "New Offer: Rs." + str(round(new_offer)) +"/- "
                else:
                    concat_msg += "Deal Done!"
        else:
            new_offer = new_amount_offer(buyer_offer, new_offer, actual_amt, thresh, buyer_offers_list)
            if buyer_offer<new_offer:
                concat_msg += "New Offer:" + str(round(new_offer))
            else:
                concat_msg += "Deal Done!"
    else:
        buyer_offers_list.append(0)
                

    if msg != '':
        # print("You: " + msg + '\n\n')
    
        ints = predict_class(msg)
        res = getResponse(ints, intents)
        if concat_msg == "Deal Done!":
            return "" +concat_msg +"\n\n"
        else:
            return "" +concat_msg +'\n'+ res + "\n\n"
    return "Wait for the seller to respond! B-Bot is busy."
            









    
def home(request):
    products = Product.objects.all()
    return render(request, 'home.html', {"products": products})

def productview(request):
    
    id = request.POST.get("product_id", "")
    product = Product.objects.get(id=id)
    return render(request, "productview.html", {"product": product})

def send_msg(request):
    x = request.POST['msg']
    actual_amt = int(request.POST['price'])
    thresh = int(request.POST['thresh'])
    
    y = send(x,actual_amt, thresh)
    if(y.strip()=="Deal Done!"):
        c = Customer()
        c.save()
        customer_id = Customer.objects.all().order_by("-id")[0]

        final_price = extract_amount(x)
        product = Product.objects.get(id=int(request.POST['productId']))
        dd = DealDone(price = final_price, product_id = product, customer_id = customer_id)
        dd.save()

    return HttpResponse(y)

def addproduct(request):
    products = Product.objects.all()
    return render(request, "addproduct.html", {"products": products})

def editproduct(request):
    id = request.POST.get("product_id", "")
    product = Product.objects.get(id=id)
    return render(request, "editproduct.html", {"product": product})

def productedited(request):
    id = request.POST.get("id", "")
    title = request.POST.get("title", "")
    deadline = request.POST.get("deadline", "")
    description = request.POST.get("description", "")
    price = request.POST.get("price", "")
    Product.objects.filter(id=id).update(title = title, description=description, deadline=deadline, price=price)
    return render(request, "productedited.html", {"title": title})

def addnewproduct(request):
    return render(request, "addnewproduct.html")

def productadded(request):
    p = Product(title = request.POST.get("title", ""), deadline = request.POST.get("deadline", ""), 
    description = request.POST.get("description", ""), price = request.POST.get("price", ""), 
    date = request.POST.get("date", ""), img = request.FILES.get("image", ""), thresh = request.POST.get("thresh", ""))
    p.save()
    return render(request, "productadded.html")