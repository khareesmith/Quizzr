# web_search.py
import time
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from urllib.parse import quote_plus
import logging
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_argument("--log-level=3")
    options.add_argument('--disable-dev-shm-usage')
    return webdriver.Chrome('C:\Program Files\Google\Chrome\chromedriver.exe', options=options)

def search_microsoft_docs(query, topic, sub_objective=None, num_results=3):
    # Enhance the search query with MS-900 specific terms
    ms900_terms = ["MS-900", "Microsoft 365 Fundamentals"]
    enhanced_query = f"{query} {' '.join(ms900_terms)}"
    
    if topic:
        enhanced_query += f" {topic}"
    if sub_objective:
        enhanced_query += f" {sub_objective}"
    
    encoded_query = quote_plus(f"site:microsoft.com {enhanced_query}")
    url = f"https://www.bing.com/search?q={encoded_query}"
    
    driver = setup_driver()
    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "b_algo")))
        
        results = []
        for result in driver.find_elements(By.CLASS_NAME, "b_algo"):
            try:
                title_element = WebDriverWait(result, 5).until(
                    EC.presence_of_element_located((By.TAG_NAME, "h2"))
                ).find_element(By.TAG_NAME, "a")
                
                link = title_element.get_attribute("href")
                title = title_element.text
                
                snippet = extract_snippet(result)
                
                if link and 'microsoft.com' in link:
                    relevance_score = calculate_relevance(title, snippet, query, topic, sub_objective)
                    results.append({
                        'title': title,
                        'link': link,
                        'snippet': snippet,
                        'relevance': relevance_score
                    })
            except (TimeoutException, NoSuchElementException) as e:
                logging.warning(f"Error processing a search result: {e}")
                continue
        
        # Sort results by relevance and return top matches
        sorted_results = sorted(results, key=lambda x: x['relevance'], reverse=True)
        return sorted_results[:num_results]
    
    except Exception as e:
        logging.error(f"Error during Microsoft Docs search: {e}")
        return []
    finally:
        driver.quit()

def extract_snippet(result):
    snippet_classes = ["b_caption", "b_snippet", "b_richSnippet"]
    for class_name in snippet_classes:
        try:
            return result.find_element(By.CLASS_NAME, class_name).text
        except NoSuchElementException:
            continue
    return "No snippet available"

def calculate_relevance(title, snippet, query, topic, sub_objective):
    relevance_score = 0
    
    # Check for MS-900 or Microsoft 365 Fundamentals in title or snippet
    if re.search(r'MS-900|Microsoft 365 Fundamentals', title + snippet, re.IGNORECASE):
        relevance_score += 2
    
    # Check for query terms in title and snippet
    query_terms = query.lower().split()
    for term in query_terms:
        if term in title.lower():
            relevance_score += 1
        if term in snippet.lower():
            relevance_score += 0.5
    
    # Check for topic and sub-objective terms
    if topic:
        topic_terms = topic.lower().split()
        for term in topic_terms:
            if term in title.lower():
                relevance_score += 1
            if term in snippet.lower():
                relevance_score += 0.5
    
    if sub_objective:
        sub_obj_terms = sub_objective.lower().split()
        for term in sub_obj_terms:
            if term in title.lower():
                relevance_score += 1
            if term in snippet.lower():
                relevance_score += 0.5
    
    return relevance_score

def get_official_documentation(topic, sub_objective=None):
    docs_results = search_microsoft_docs(topic, topic, sub_objective)
    if docs_results:
        return docs_results[0]['link'], docs_results[0]['snippet']
    logging.warning("No official documentation found")
    return None, None