from scrapy.item import Field, Item
from scrapy.spiders import Spider 
from scrapy.loader import ItemLoader   
from bs4 import BeautifulSoup   
# BeautifulSoup se utiliza para hacer parsing del HTML fuera del sistema nativo de Scrapy.

# ------------------------------
# Definición del modelo de datos
# ------------------------------

class New(Item):
    """Representa una noticia extraída del sitio El Universo."""
    id = Field()           # Identificador único para cada ítem
    headline = Field()     # Título de la noticia
    description = Field()  # Resumen o extracto de la noticia


# ------------------------------
# Definición del Spider
# ------------------------------

class ElUniversoSpider(Spider):
    """
    Spider que navega la sección de Deportes del sitio El Universo
    y extrae los títulos y descripciones de las noticias listadas.
    """
    
    name = "MySecondSpider"  # Nombre interno del spider
    
    # Configuración personalizada del agente de usuario para evitar bloqueos por scraping
    custom_settings = {
        "USER-AGENT" : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36", 
        "FEED_EXPORT_FIELDS": ["id", "headline", "description"],  # Orden de columnas en CSV
        "CONCURRENT_REQUESTS" : 1, # controla cuántas solicitudes HTTP al mismo tiempo puede hacer Scrapy (Por defecto esta en: 16, ponerlo en 1 hace que disminuya la prob de que detecte a nuestro scraper como bot )
        "FEED_EXPORT_ENCODING": "utf-8"
    }
    
    # URL desde donde se inicia el scraping
    start_urls = ["https://www.eluniverso.com/deportes/"]
    
    def parse(self, response):
        """
        Extrae el título y la descripción de las noticias desde la página de Deportes El Universo.

        Args:
            response (scrapy.http.Response): 
                Objeto que representa la respuesta HTTP recibida al acceder a una URL. 
                Contiene el contenido HTML que será parseado.

        Yields:
            New: 
                Ítem con los campos `headline` (título de la noticia), 
                `description` (extracto) e `id` (número secuencial).
        """
        
        # Se parsea el cuerpo HTML usando BeautifulSoup
        soup = BeautifulSoup(response.body, "html.parser")
        
        # Buscar <ul> que contenga "feed" como una de sus clases
        content_news = soup.find_all("ul", attrs={"class": lambda c: c and "feed" in c})
        
        id = 0  # Contador para asignar un ID único a cada noticia
        
        # Iteración sobre cada bloque de noticias
        for content in content_news:
            
            # Se seleccionan las noticias individuales (elementos <li>)
            news = content.find_all("li", class_="relative", recursive=False)
            
            for new in news:
                # Se crea el loader del ítem. 
                # Aunque estamos usando BeautifulSoup, se instancia con el response para compatibilidad.
                item = ItemLoader(New(), selector=new)
                
                # Extracción y limpieza del título
                headline = new.find("h2").text.strip()
                
                # Extracción del resumen de la noticia
                description = new.find("p")
                if (description):
                    item.add_value("description", description.text.replace('\n', '').replace('\r', ''))
                else:
                    item.add_value("description", "N/A")
                
                # Incremento correcto del ID
                id += 1
                
                # Se cargan los valores al ítem
                item.add_value("headline", headline)
                item.add_value("id", id)
                
                # Se devuelve el ítem cargado
                yield item.load_item()

#-------------------
#     E J E C U T A R
# scrapy runspider scraper.py -o  universo.csv -t csv