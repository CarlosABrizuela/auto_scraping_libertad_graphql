import requests, base64, json
import time
from requests.exceptions import ProxyError
# import concurrent.futures
from datetime import datetime
import csv
import pandas as pd
from utility_functions import CONSOLE

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

    def fetch(self, url, params):
        """
        Realiza una solicitud HTTP a la URL especificada y devuelve la respuesta en formato json.
        """
        max_attempts = self.config['max_attempts'] 
        delay_attempts = self.config['delay_attempts']
        attempts = 0

        while attempts < max_attempts:
            try:
                response = self.session.get(url, params=params)
                if response.ok:
                    return response.json()
                else:
                    CONSOLE.info(f"Request not ok. Status code: {response.status_code}.")

            except ProxyError as e:
                CONSOLE.error('Proxy error:', e)
                return None
            except requests.RequestException as e:
                CONSOLE.error(f"Request error: {e}.")

            attempts += 1
            CONSOLE.info(f"Retrying. >{max_attempts-attempts} attempts lefts'")
            time.sleep(delay_attempts)

        CONSOLE.info(f"The request could not be made: {url}. No more attempts")
        return None
    
    def run(self):
        """ main method. 
        """
        all_categories = self.get_categories()
        if not all_categories: return

        self.process_department(all_categories[0])
        # with concurrent.futures.ThreadPoolExecutor(max_workers=self.config['thread_number']) as executor:
        #     executor.map(self.process_department, all_categories)

        self.close()
    
    def process_department(self, department):
        """Obtain the products for each category or department (level 1 category)
        """
        for category in department['sub_categorias']:
            self.process_subcategory(category)
        
        self.crear_csv(department['nombre'])

    def process_subcategory(self, category):
        """get all products for every category in the current deparment
        sub={
        }
        """
        _from = 1
        _to = self.config['pagination']
        while True:
            variables= {
                "hideUnavailableItems":False,
                "skusFilter":"ALL",
                "simulationBehavior":"skip",
                "installmentCriteria":"MAX_WITHOUT_INTEREST",
                "productOriginVtex":True,
                "map":"c,c",
                "query":category['query'],#
                "orderBy":"OrderByScoreDESC",
                "from":_from,#
                "to":_to,#
                "selectedFacets":
                    [{"key":"c","value":category['sup']},{"key":"c","value":category['sub']}], #
                    "facetsBehavior":"Static",
                    "categoryTreeBehavior":"default",
                    "withFacets":False,
                    "variant":""
                }
            variables_64 = base64.b64encode(json.dumps(variables).encode('utf-8')).decode()
            querystring = {
                "workspace":"master",
                "maxAge":"short",
                "appsEtag":"remove",
                "domain":"store",
                "locale":"es-AR",
                "operationName":"productSearchV3",
                "variables":"{}",
                "extensions":"{\"persistedQuery\":{\"version\":1,\"sha256Hash\":\""+self.config['sha256']+"\",\"sender\":\"vtex.store-resources@0.x\",\"provider\":\"vtex.search-graphql@0.x\"},\"variables\":\""+variables_64+"\"}"
                }

            products_queried= self.fetch(self.search_url, querystring)
            products= products_queried['data']['productSearch']['products']
            if not products: break
            for product in products:
                self.process_product(product)

            _from+= _to
            _to+= _to

    def process_product(self, product):
        """ extract the product information """
        try:
            dict_prod= {
            'nombre': product['productName'],
            'precio_publicado': product['priceRange']['sellingPrice']['highPrice'],
            'precio_regular': product['priceRange']['listPrice']['highPrice'], #precio tachado
            'categoria': product['categories'][0],
            'SKU': product['items'][0]['itemId'],
            'url_producto': product['link'],
            'stock': product['items'][0]['sellers'][0]['commertialOffer']['AvailableQuantity'],
            'descripcion': str(product['description']).replace('\n', ' ').replace('\r', '') # quitamos los espacios
            }
            self.data.append(dict_prod)
        except Exception as e:
            CONSOLE.info(f'(Process product): {e}')

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
        categories_json = self.fetch(self.config['categories_url'], {})
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
        CONSOLE.info(f"* A new output file was generated: {ouput}")

    def close(self):
        """
        Close the session
        """
        self.session.close()