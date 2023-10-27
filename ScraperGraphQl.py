import requests
import time
from requests.exceptions import ProxyError
# import concurrent.futures
from datetime import datetime
import csv
import pandas as pd

class ScraperHLibertad:
    def __init__(self, config):
        """Start the Scraper

        Args:
            config (dict): it has the configurations: proxy, proxy_ip_port, output
        """
        self.config = config
        self.search_url = self.config['search_url']
        self.data = []
        self.actual_register = None
        self.session = requests.Session()
        if self.config['proxy']:
            self.session.proxies = config['proxy_ip_port']

    def fetch(self, url):
        """
        Realiza una solicitud HTTP a la URL especificada y devuelve la respuesta en formato json.
        """
        max_attempts = self.config['max_attempts'] 
        delay_attempts = self.config['delay_attempts']
        attempts = 0

        while attempts < max_attempts:
            try:
                response = self.session.get(url)
                if response.ok:
                    return response.json()
                else:
                    print(f"Request not ok. Status code: {response.status_code}.")

            except ProxyError as e:
                print('Proxy error:', e)
                return None
            except requests.RequestException as e:
                print(f"Request error: {e}.")

            attempts += 1
            print(f"Retrying. >{max_attempts-attempts} attempts lefts'")
            time.sleep(delay_attempts)

        print(f"The request could not be made: {url}. No more attempts")
        return None
    
    def run(self):
        """ main method. 
        """
        all_categories = self.get_categories()
        if all_categories:
            print(all_categories)

        # with concurrent.futures.ThreadPoolExecutor(max_workers=self.config['thread_number']) as executor:
        #     executor.map(self.process_department, all_categories)

        self.close()
    
    def process_department(self):
        """Obtain the products for each category or department (level 1 category)
        """
        pass

    def process_subcategory(self, sub_category):
        """get all products for every category in the current deparment
        sub={
        }
        """
        pass

    def process_product(self, product):
        """ extract the product information """
        pass

    def get_categories(self):
        """Get the list of categories and format them for processing
        format:
        {
            "nombre": "Tecnologia",
            "sub_categorias": [
                {
                    "sup": "Tecnologia",
                    "sub": "TV Y VIDEO",
                    "query": "Tecnologia/TV Y VIDEO"
                }, ...
        }
        """
        categories_json = self.fetch(self.config['categories_url'])
        if categories_json:
            return self.process_list_categories(categories_json)

    def process_list_categories(self, categories_json):
        """ accumulates the second level categories in a list, for each first level category. """
        supcategories_list= []
        for category in categories_json:
            if category["hasChildren"]:
                sub_categories = self.process_list_subcategories(category["children"], category["name"])
                categoria_dict_sup ={
                        "nombre": category['name'],
                        "sub_categorias": sub_categories
                    }
                supcategories_list.append(categoria_dict_sup)
            
        return supcategories_list

    def process_list_subcategories(self, categories_json, sup_name):
        """ Returns the leaf categories, or those that do not have child categories. """
        subcategories_list = []
        for category in categories_json:
            category_dict = {
                "sup": sup_name,
                "sub": category["name"],
                "query": sup_name +"/"+ category["name"]
            }
            subcategories_list.append(category_dict)
        return subcategories_list

    def crear_csv(self, category_name):
        """
            To create the csv file with the products.
        """
        date = (datetime.today()).strftime('%d-%m-%Y')
        df = pd.DataFrame(self.data)
        ouput= f'{date}__{category_name}.csv'
        df.to_csv(f'{self.config['output_dir']}/{ouput}',  quoting=csv.QUOTE_MINIMAL)
        print(f"* A new output file was generated: {ouput}")

    def close(self):
        """
        Close the session
        """
        self.session.close()