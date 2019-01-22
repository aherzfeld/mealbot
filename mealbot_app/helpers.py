""" Helper functions related to Spoonacular API requests """

import requests


class SpoonAPI():
    """ Interact with Spoonacular API via requests """

    endpoint = 'https://spoonacular-recipe-food-nutrition-v1.p.rapidapi.com/recipes/extract?url='

    def __init__(self, api_key):

        self.api_key = {'X-RapidAPI-Key': api_key}

    def extract_recipe_from_website(self, url):
        return requests.get(SpoonAPI.endpoint + url, headers=self.api_key)
