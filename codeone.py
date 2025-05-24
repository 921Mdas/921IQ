import requests # type: ignore
import json
import os
from bs4 import BeautifulSoup
from flask import Flask


#scraping
url = 'http://books.toscrape.com'
headers = {"User-Agent": "Mozilla/5.0"} 
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')


#save data in file
def createFile(books:list):
    try:
            with open('books.json', 'w') as file:
                 json.dump(books, file, indent=4)
    except Exception as e:
         print(f"An error occurred: {e}")

def collector()-> None:
    try:
           articles = soup.find_all('article', class_='product_pod')
           scrap = []
           if articles:
            for article in articles:
                    dictdata = {}
                    dictdata['imglink'] = article.select_one('div.image_container > a').select_one('img')['src'] if article else None
                    dictdata['rating'] = len(article.select_one('p.star-rating').find_all('i'))
                    dictdata['title'] = article.select_one('h3 > a')['title']
                    dictdata['price'] = article.select_one('.price_color').text.replace('Â£', '')
                    scrap.append(dictdata)      
            
            createFile(scrap)
    except Exception as e:
           print('something went wrong',jsonify(e))

collector()

# # create api endpoint from flask
# app = Flask(__name__)

# @app.route('/astro', methods=['GET'])

# def callAPI()->None:
#     try:
#         response = requests.get('http://api.open-notify.org/astros.json')
#         response.raise_for_status()
#         data = response.json()

#         if data:
#             people = data['people']
#             ISS_People = [p['name'] for p in people if p['craft'] == 'ISS']
            
#             file_path = input('Where do you want to save the file? (e.g., ./ISS_astro.txt): ').strip()
#             os.makedirs(os.path.dirname(file_path), exist_ok=True)

#             for person in ISS_People:
#                 with open(file_path, 'a') as file:
#                     file.write(f'{person}\n')
#         else:
#             print('no data')
    
#     except requests.exceptions as e:
#         print('something went wrong', e)
#     finally:
#         return data.json()

# callAPI()
    

# if __name__ == '__main__':
#     app.run(debug=True)

#pulling data from the an api and return it as my own api data
#maybe some data we pull online, scrape or parse from excel docs that we can return online

from flask import Flask, jsonify
import requests  # type: ignore
import os

# app = Flask(__name__)

# @app.route('/astro', methods=['GET'])
# def callAPI():
#     try:
#         response = requests.get('http://api.open-notify.org/astros.json')
#         response.raise_for_status()
#         data = response.json()

#         if data:
#             people = data['people']
#             ISS_People = [p['name'] for p in people if p['craft'] == 'ISS']
            
#             file_path = './ISS_astro.txt'  # removed input() for Flask safety
#             os.makedirs(os.path.dirname(file_path), exist_ok=True)

#             with open(file_path, 'a') as file:
#                 for person in ISS_People:
#                     file.write(f'{person}\n')

#         return jsonify(data)  # ✅ safe Flask response

#     except requests.exceptions.RequestException as e:
#         print('Something went wrong:', e)
#         return jsonify({'error': str(e)}), 500


# if __name__ == '__main__':
#     app.run(debug=True, port=8080)





















# # # def callAPI(url:str) -> list:
# # #     try:
# # #        response = requests.get(url)
# # #        response.raise_for_status()
# # #        data = response.json()

# # #        print(json.dumps(data, indent=4))


# # #        return data
# # #     except requests.RequestException as e:
# # #        print('something went wrong', e)

# # #        return []

# # # callAPI('http://api.open-notify.org/astros.json')


# # # class Car():
# # #    def __init__(self, make, model):
# # #        self.make = make
# # #        self.model = model

# # #    def start_engine(self,days):
# # #        print(f'the car make {self.make}, model {self.model}, is due for maintenance in {days} days')


# # # Mazda = Car('CX5','SUV')

# # # print(Mazda.start_engine(10))



# # # class ElectricCar(Car):
# # #     def __init__(self, make, model, battery_size):
# # #         super().__init__(make, model)
# # #         self.battery_size = battery_size

# # #     def start_engine(self, days, motor):
# # #         super().start_engine(days)
# # #         print(f'The electric {self.make} {self.model} with a {self.battery_size}kWh battery starts silently... with a {motor} motor')

# # #     def describe_batter():
# # #         print("This car has a {battery_size}kWh battery.")


# # # Tesla = ElectricCar('Tesla S', 'Zed', 100)
# # # Tesla.start_engine(20, 'hydrogen')


# # class STSUSER():
# #    def __init__(self, name, email):
# #       self.tickets = []
# #       self.name = name
# #       self.email = email

# #    def __str__(self):
# #        return f'Hi Im {self.name}, email f{self.email}'

# #    def create_ticket(self, description, priority):
# #        ticket = STSTicket(description, priority)
# #        self.tickets.append(ticket)
# #        return ticket

# #    def view_tickets(self):
# #        return self.tickets

# # class STSTicket():
# #    __id = 1
# #    def __init__(self, description, priority, created_by):
# #       self.id = STSTicket.__id + 1
# #       self.description = description
# #       self.priority = priority
# #       self.status = 'Open'
# #       self.created_by = created_by
# #       self.assigned_to = None
# #       self.response = None
    
# #    def assign(self, agent):
# #        agent_name = STSSupportAgent(agent)
# #        return agent_name

# #    def add_response(self,message):
# #        print(f' Hi  here is your id {self.id}, {message} ')
# #        return ''
   
# # class STSSupportAgent():
# #       def __init__(self, name):
# #           return name

# #       def respond_to_ticket(message):
# #           STSTicket
      

# # # user created
# # Nathalie = STSUSER("Nathalie Rochette", 'nr@gmail.com')

# # # user creates a ticket
# # ticket_one = STSTicket('Nathalie Rochette', 'nr@gmail.com', 1, 'cannot login', 'urgent', 'open', 'Nathalie', 'unkown', 'we have received your message' )

# # ticket_one.assign('Peter John')
# # ticket_one.add_response('I am reviewing your ticket and will get back shortly')


# def fileWriter(txt:str, mode:str) -> None:
#     try:
#             if mode == 'r':
#                 with open('data.txt', mode) as file:
#                    content =  file.read()
#                    print(content)
#                     # line by line read
#                     # for line in file:
#                     #     print('new line', line.strip())
#             else:
#                 with open('data.txt',mode) as file:
#                     file.write(txt)
#     except Exception as e:
#         print('something went wrong', e)
    



# fileWriter('Hello World\n', 'w')
# fileWriter('bye world\n', 'a')
# fileWriter('bye world\n', 'r')
        
         
         