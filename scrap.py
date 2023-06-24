from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import csv
import re
import pandas as pd
from selenium.common.exceptions import TimeoutException
import time

# Create a WebDriver instance (assuming you have the appropriate driver executable in your PATH)
driver = webdriver.Chrome()

# Define the base URL
base_url = 'https://www.amazon.in/GRECIILOOKS-Western-Dresses-Perfect-XX-Large/dp/B0BRJ11C1J/ref=sxin_20_trfobq2av2_0_B0BRJ11C1J?content-id=amzn1.sym.c1eb4b2a-b703-404b-a097-61cb8a5ee3cb%3Aamzn1.sym.c1eb4b2a-b703-404b-a097-61cb8a5ee3cb&crid=1MDKQVKH6V0ZM&cv_ct_cx=dress&keywords=dress&pd_rd_i=B0BRJ11C1J&pd_rd_r=3bda1fdd-cfb9-4146-b8fe-7cf2be223ac8&pd_rd_w=sDeuo&pd_rd_wg=6UflU&pf_rd_p=c1eb4b2a-b703-404b-a097-61cb8a5ee3cb&pf_rd_r=246ZZ6P3NTTR6WP0HM9Q&qid=1687487995&sprefix=dres%2Caps%2C283&sr=1-1-973fd8bd-28ce-479e-8be4-fbaf1193947a'

# Open the CSV file for writing
with open('test.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Title','ASIN','Status','MRP','Price', 'Percent off','Is Lightning Deal','Sale Price', 'Is DOTD','DOTD Price','Is Limited time deal','Deal Price','Brand','Sold By','Shipping Fee','Rating', 'Date First Available', 'Review Data'])  # Write the header row
    processed_items = set()  # Set to store processed items

    # Navigate to the webpage
    driver.get(base_url)
    new_html = driver.page_source
    soup_new = BeautifulSoup(new_html, 'html.parser')
    div_new = soup_new.find_all('div', class_='a-section review-views celwidget')
    
    title = ''
    Asin=None
    Status=''
    rating = ''
    price = ''
    percent_off=''
    mrp_price = ''
    brand = ''
    sold_by=''
    discount = ''
    shippingfee=''
    first_available = ''
    is_LD=''
    is_L_D=''
    is_DOTD=''
    Sale_price=''
    DOTD_price=''
    Deal_price=''
    
    span_title = soup_new.find('span', class_='a-size-large product-title-word-break')
    if span_title:
        title = span_title.text.strip()
    else:
        span_check = soup_new.find('span', class_='a-size-large a-color-secondary')
        if span_check:
            check = span_check.text.strip()
            if check == 'Kindle Edition':
                span_title = soup_new.find('span', class_='a-size-extra-large')
                if span_title:
                    title = span_title.text.strip()
                else:
                    title = None
        else:
            title = None

    span_asin_table = soup_new.find('div', class_='a-section table-padding')
    if span_asin_table:
        span_asin = span_asin_table.find('table', id='productDetails_detailBullets_sections1')
        th_element = None  # Initialize th_element as None
        if span_asin:
            th_element = span_asin.find('th', class_='a-color-secondary a-size-base prodDetSectionEntry')
        if th_element and th_element.text.strip() == 'ASIN':
            td_element = th_element.find_next('td', class_='a-size-base prodDetAttrValue')
            if td_element:
                Asin = td_element.text.strip()
            else:
                Asin = None
        else:
            Asin = None
    else:
        Asin = None

    if Asin is None:
        detail_bullets_div = soup_new.find('div', id='detailBullets_feature_div')
        if detail_bullets_div:
            ul_element = detail_bullets_div.find('ul', class_='a-unordered-list a-nostyle a-vertical a-spacing-none detail-bullet-list')
            if ul_element:
                li_elements = ul_element.find_all('li')

                asin_value = ""
                for li_element in li_elements:
                    span_elements = li_element.find_all('span')
                    for span_element in span_elements:
                        if 'ASIN' in span_element.text:
                            asin_value = span_elements[-1].text.strip()
                            Asin = asin_value
                            break
            else:
                Asin = None
        else:
            Asin = None

    availability_div = soup_new.find('div', id='availability')
    if availability_div:
        in_stock_span = availability_div.find('span', class_='a-size-medium a-color-success')
        if in_stock_span:
            Status = in_stock_span.text.strip()
        else:
            in_stock_span = availability_div.find('span', class_="a-size-base a-color-price a-text-bold")
            if in_stock_span:
                Status = in_stock_span.text.strip()
            else:
                Status = None
    else:
        Status = None


    span_rating = soup_new.find('span', class_='a-icon-alt')
    if span_rating:
        rating = span_rating.text.strip()
    if not rating or not re.match(r'^\d+\.\d+ out of 5 stars$', rating):
        rating = "No customer reviews"

    span_price = soup_new.find('span', class_='a-price-whole')
    if span_price:
        price_str = span_price.text.strip().replace('.', '').replace(',', '')
        price=int(price_str)
    else:
        price=None

    span_percent_off = soup_new.find('span', class_='a-size-large a-color-price savingPriceOverride aok-align-center reinventPriceSavingsPercentageMargin savingsPercentage')
    if span_percent_off:
        percent_off= span_percent_off.text.strip()

    div_mrp = soup_new.find('div', class_='a-section a-spacing-small aok-align-center')
    if div_mrp:
        mrp_span = div_mrp.find('span', class_='aok-relative')
        if mrp_span:
            mrp_price_str = mrp_span.find('span', class_='a-offscreen').text.strip().replace('₹', '').replace(',', '')
            mrp_price = int(mrp_price_str)
        else:
            mrp_price = None

    div_elements = soup_new.find_all('div', class_='a-section a-spacing-none')
    for div in div_elements:
        anchor_tag = div.find('a', id='bylineInfo')
        if anchor_tag:
            brand = anchor_tag.text.strip().replace('Visit the', '')

    merchant_info = soup_new.find('div', id='merchant-info')
    if merchant_info:
        sold_by_span = merchant_info.find('a', class_='a-link-normal')
        if sold_by_span:
            sold_by = sold_by_span.find('span').text.strip()
        else:
            sold_by = ''
    else:
        sold_by = ''

    
    span_first_available = soup_new.find('div', id='mir-layout-DELIVERY_BLOCK')
    if span_first_available:
        shippingfee = span_first_available.find('a', class_='a-link-normal').text.strip()
        first_available = span_first_available.find('span', class_='a-text-bold').text.strip()
    
    lightning_deal_span = soup_new.find('span', class_='a-size-base gb-accordion-active a-text-bold')
    if lightning_deal_span and lightning_deal_span.text.strip() == 'Lightning Deal':
        is_LD = 'yes'
    else:
        is_LD = 'no'

    deal_badge_span = soup_new.find('span', class_='dealBadge')
    if deal_badge_span and deal_badge_span.text.strip() == 'Deal':
        is_L_D = 'yes'
    else:
        is_L_D = 'no'

    deal_badge_span = soup_new.find('span', class_='dealBadge')
    if deal_badge_span and deal_badge_span.text.strip() == 'Deal of the Day':
        is_DOTD = 'yes'
    else:
        is_DOTD = 'no'

    review_data = {}

    for div_review in div_new:
        span_reviews = div_review.find_all('span', class_='a-size-base a-color-secondary review-date')
        div_review_texts = div_review.find_all('div', class_='a-expander-content reviewText review-text-content a-expander-partial-collapse-content')

        for span_review, div_review_text in zip(span_reviews, div_review_texts):
            review_date = span_review.text.strip() if span_review else ""
            review_text = div_review_text.get_text(separator=" ").strip() if div_review_text else ""

            # Add the review data to the dictionary
            review_data[review_date] = review_text
    
    if(is_LD)=='yes':
        Sale_price=price
    if(is_DOTD)=='yes':
        DOTD_price=price
    if(is_L_D)=='yes':
        Deal_price=price

    writer.writerow([title, Asin,Status,mrp_price,price,percent_off,is_LD,Sale_price,is_DOTD,DOTD_price,is_L_D,Deal_price, brand,sold_by, shippingfee,rating, first_available, review_data])
    time.sleep(5)

# Close the WebDriver
driver.quit()