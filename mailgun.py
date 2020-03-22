import requests

apikey = "key-8439b6fada7f7dde0652d5564cff0fde"
url = "account.motracker.com"

def send_confirmation_email(data):
    message  = 'Tesing confirmation email'
    requests.post(url, 
        auth = ("api", apikey), 
        data = {
            "from": 'flavoursoft@devporte.com',
            "to": ["flavoursoft@yhaoo.com", "flavoursoft@gmail.com"], 
            "subject": "Email confirmation", 
            "text":message
        }
    )

    return "true"



