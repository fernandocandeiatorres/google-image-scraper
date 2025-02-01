# **Google Image Scraper & Image Labeling for Dataset & Image Classification with CNN** 

A Python-based Google Image Scraper that automates the process of searching for images on Google, extracting image URLs, and downloading them locally. This tool uses **Selenium**, **Pandas**, **BeautifulSoup**, and **Concurrency** to efficiently handle scraping and downloading.

After scraping and saving the images, you can label the images and save it to a dataset in this format: id/img_name/label. Labeling it using ResNet50 pretrained model.

Also, a CNN for Image Classification.

---

## **Features**
- Extracts image URLs and saves them in a CSV file.
- Creates a dataset of the images URLs too.
- Downloads images locally with proper naming and format handling.
- Optimized for performance using concurrency.

---

## **Setup**
Follow these steps to get started:

1. Clone or download this repository.
2. Install the required Python packages by running:
   ```bash
   pip install -r requirements.txt
