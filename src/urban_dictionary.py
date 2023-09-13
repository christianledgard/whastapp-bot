from requests import get

class UrbanDictionary:

    def __init__(self):
        pass

    def get_word(self, word):
        response = get(f"https://api.urbandictionary.com/v0/define?term={word}")
        print(response.text)
        return response.json()