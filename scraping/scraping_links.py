"""
Gather and output data into a CSV file, in this case: export image URLs.
Then, store the content of the URL into a variable, convert it into an image object,
and then save it to a specified location.

"""

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from concurrent.futures import ThreadPoolExecutor
import requests
import io
from PIL import Image
from pathlib import Path
import hashlib
import base64
import os
import time


query = "dog"
images_dir = os.path.join(os.getcwd(), f"images/{query}")
os.makedirs(images_dir, exist_ok=True)


def browser_setup():
    options = ChromeOptions()
    options.add_argument("--headless=new") # to run without GUI
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")


    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(f"https://www.google.com/search?site=&tbm=isch&source=hp&q={query}")


    # Simulate scrolling to load more images
    for _ in range(5):  # Adjust the number based on the number of images wanted
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # Wait for images to load
        
        
    content = driver.page_source
    soup = BeautifulSoup(content, "html.parser")
    soup_selected = soup.select('div.F0uyec div.H8Rx8c img')
    driver.quit()
    
    return soup, soup_selected


def fetch_image_urls(limit_count):
    soup, soup_selected = browser_setup()
    count = 0
    results= set()
    # PARSE HTML AND ADD IMAGES SOURCE TO LIST
    for parent_div in soup.find_all("div", class_="F0uyec"):
        image_div = parent_div.find("div", class_="H8Rx8c")
        if image_div:
            img_tag = image_div.find("img")
            if img_tag and "src" in img_tag.attrs:
                results.add(img_tag["src"])
                count += 1
                if count == limit_count:
                    break
                
    # PARSE HTML AND ADD IMAGES SOURCE TO LIST
    # for image_div in soup_selected:
    #     if image_div:
    #         img_tag = image_div.find("img")
    #         if img_tag and "src" in img_tag.attrs:
    #             results.add(img_tag["src"])
    #             count += 1
    #             if count == 50:
    #                 break

    print(count)
    return list(results)

# #CREATE DATASET AND CSV WITH IMAGES SOURCE FROM LIST
# df = pd.DataFrame({"links:":list(results)})
# df.to_csv("links.csv", index=False, encoding="utf-8")

# SAVE IMAGE URLS INTO IMAGES LOCALLY.

def save_image(img_src_url, idx):
    # for i,img_src_url in enumerate(results):
    try:
        if img_src_url.startswith('http'):
            image_content = requests.get(img_src_url).content
            if image_content:
                image_file = io.BytesIO(image_content)
                
                image = Image.open(image_file).convert("RGB")
                file_path = Path(images_dir, f"{hashlib.sha1(image_content).hexdigest()[:10]}.png")
                image.save(file_path, "PNG", quality=80)  
        elif img_src_url.startswith('data:image/jpeg;base64'):
            #Decode base64 image data and save
            img_data = img_src_url.split('base64,')[1]
            img_content = base64.b64decode(img_data)
            if img_content:
                img = Image.open(io.BytesIO(img_content))
                img_name = f"{hashlib.sha1(img_content).hexdigest()[:10]}.png"
                img_path = os.path.join(images_dir, img_name)
                img.save(img_path, "PNG")
        return True
    except Exception as e:
        print(f"Erro ao salvar a imagem {idx+1} É base64?{img_src_url.startswith('data:image/jpeg;base64')==True}: {e}")
        return False

if __name__ == "__main__":
    
    print("Selecionando os images urls...")
    
    results = fetch_image_urls(50)
    
    print("Criando dataset...")
    
    df = pd.DataFrame({"links:":list(results)})
    df.to_csv("links.csv", index=False, encoding="utf-8")
    
    print("Salvando imagens...")
    with ThreadPoolExecutor() as executor:
        results_status = list(executor.map(save_image, results, range(len(results))))
        
        saved_count = sum(results_status)
        total_count = len(results)
    
    print(f"{saved_count} de {total_count} imagens foram salvas com sucesso.")

