![hiper libertad](https://hiperlibertad.vtexassets.com/assets/vtex/assets-builder/hiperlibertad.fizzmod-theme/1.17.1/img/retailStoreLogo___647637fa923edf985acb24aa6915109e.svg)
# auto_scraping_libertad
Scraping test challenge for AUTOscraping. Using Requests library.

Page: _hiperlibertad.com.ar_

The main goal is to get all products from the page and save them into csv files, one for every category.

# Process explanation
## 1
To achieve this, first we get the list of categories from the website, then format that as follows
```json
[
    {
        "nombre": "Tecnologia",
        "sub_categorias": [
            {
                "sup": "Tecnologia",
                "sub": "TV Y VIDEO",
                "query": "Tecnologia/TV Y VIDEO"
            }, "...", 
        ]
    }
    "..."
]
```
## 2
To requests the data we use the following url.
- Search url: https://www.hiperlibertad.com.ar/_v/segment/graphql/v1

Then use the requests library to do the request.
- get request: requests.get(url, params=querystring)

We need the querystring param:
- querystring: 
```python
querystring = {
            "workspace":"master",
            "maxAge":"short",
            "appsEtag":"remove",
            "domain":"store",
            "locale":"es-AR",
            "operationName":"productSearchV3",
            "variables":"{}",
            "extensions":"{\"persistedQuery\":{\"version\":1,\"sha256Hash\":\"HASH_STRING\",\"sender\":\"vtex.store-resources@0.x\",\"provider\":\"vtex.search-graphql@0.x\"},\"variables\":\"VARIABLE_BASE64_ENCODED_DECODED_STRING\"}"
            }
```
here we have two subparams to fill: sha256Hash and variables.

The first one, 'the Hash', we get from the webpage of hiper libertad, and store it in the config file in case we need to change it.

![where we take the hash from](https://github.com/CarlosABrizuela/auto_scraping_libertad_graphql/blob/main/files/hlibertad_graphql_exp1.jpg?raw=true)

For the second one, we create a dictionary, where we need to supply the following parameters: from, to, query, selectedFacets (these last two are why we gave that format to the categories json)
```python
variable = {
            "hideUnavailableItems":False,
            "skusFilter":"ALL",
            "simulationBehavior":"skip",
            "installmentCriteria":"MAX_WITHOUT_INTEREST",
            "productOriginVtex":True,
            "map":"c,c",
            "query":category['query'], # example Tecnologia/TV Y VIDEO
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
```

With that we do the query and it returns a json file with a list of products information that we paginate through this every number of page (configurable) products.

### Output format: **date**__**category-name****.csv**
>'31-10-2023__Tecnologia.csv'

# To config the script it was used a yaml file: 'config.yaml'
> [!NOTE]
> Change before run.
```yaml
search_url: https://www.hiperlibertad.com.ar/_v/segment/graphql/v1  #API search url
categories_url: https://www.hiperlibertad.com.ar/api/catalog_system/pub/category/tree/3 # url to categories json file.
proxy: False     # indicate if proxy will be use to connect.
proxy_ip_port:      # proxy port example: 35.236.207.242:33333
thread_number: 5    # number of threads
max_attempts: 2     # number of attempts if a connection could not be established.
delay_attempts: 3   # waiting seconds in every attempt
pagination: 30      # number of products for each page.
output_dir: C:\Users\salida  # folder dir where files will be saved (it must exist)
sha256: 40b843ca1f7934d20d05d334916220a0c2cae3833d9f17bcb79cdd2185adceac  # sha256hash. used to do the query
```
# Considerations:
Version of python: **Python 3.12.0**.

## Libraries
- [requests](https://requests.readthedocs.io/): to make http requets.
- [PyYAML](https://pyyaml.org/): To manage the configuration.
- [pandas](https://pandas.pydata.org/docs/index.html): To create the csv files.

# How to use:
- Clone the project
```
git clone https://github.com/CarlosABrizuela/auto_scraping_libertad_graphql.git
```
```
cd auto_scraping_libertad_graphql
```
- Install the libraries
```
pip install -r requirements.txt
```
- run the script
```
python main.py
```

## Licencia
- Sin Licencia
