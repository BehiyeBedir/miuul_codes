from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup
import re


def setup_driver():
    """
    Tarayıcıyı başlatır ve döndürür.
    """
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=options)
    return driver


def get_category_urls(driver, url):
    """
    Verilen URL'den kategori bağlantılarını alır.

    :param driver: Selenium WebDriver nesnesi
    :param url: Ana sayfa URL'si
    :return: Kategori URL'lerinin listesi
    """
    driver.get(url)
    time.sleep(0.25)  # Sayfanın yüklenmesi için kısa bir bekleme
    category_elements_xpath = "//a[contains(text(),'Travel') or contains(text(),'Nonfiction')]"
    category_elements = driver.find_elements(By.XPATH, category_elements_xpath)
    return [element.get_attribute("href") for element in category_elements]


def get_book_urls(driver, category_url, max_pagination=3):
    """
    Belirli bir kategori URL'sinden kitap URL'lerini alır.

    :param driver: Selenium WebDriver nesnesi
    :param category_url: Kategori URL'si
    :param max_pagination: Maksimum sayfa sayısı
    :return: Kitap URL'lerinin listesi
    """
    driver.get(category_url)
    book_urls = []
    book_elements_xpath = "//div[@class='image_container']//a"

    for i in range(1, max_pagination + 1):
        update_url = category_url if i == 1 else category_url.replace("index", f"page-{i}")
        driver.get(update_url)
        book_elements = driver.find_elements(By.XPATH, book_elements_xpath)
        if not book_elements:
            break
        temp_urls = [element.get_attribute("href") for element in book_elements]
        book_urls.extend(temp_urls)

    return book_urls


def get_product_detail(driver, book_url):
    """
    Belirli bir kitap URL'sinden ürün detaylarını alır.

    :param driver: Selenium WebDriver nesnesi
    :param book_url: Kitap URL'si
    :return: Kitap detaylarını içeren sözlük
    """
    driver.get(book_url)
    time.sleep(2)  # Sayfanın yüklenmesi için kısa bir bekleme

    content_div = driver.find_element(By.XPATH, "//div[@class='content']")
    inner_html = content_div.get_attribute("innerHTML")
    soup = BeautifulSoup(inner_html, "html.parser")

    # Kitap adını al
    name_elem = soup.find("h1")
    book_name = name_elem.text if name_elem else "Kitap adı bulunamadı"

    # Kitap fiyatını al
    price_elem = soup.find("p", attrs={"class": "price_color"})
    book_price = price_elem.text if price_elem else "Fiyat öğesi bulunamadı"

    # Kitap yıldız sayısını al
    regrex = re.compile('^star-rating')
    star_elem = soup.find("p", attrs={"class": regrex})
    book_star_count = star_elem["class"][-1] if star_elem else "Yıldız sayısı bulunamadı"

    # Kitap açıklamasını al
    desc_elem = soup.find("div", attrs={"id": "product_description"}).find_next_sibling()
    book_desc = desc_elem.text if desc_elem else "Açıklama bulunamadı"

    # Kitap ürün bilgilerini al
    product_info = {}
    table_rows = soup.find("table").find_all("tr")
    for row in table_rows:
        key = row.find("th").text
        value = row.find("td").text
        product_info[key] = value

    return {
        "book_name": book_name,
        "book_price": book_price,
        "book_star_count": book_star_count,
        "book_desc": book_desc,
        "product_info": product_info
    }


def print_product_details(product_details):
    """
    Kitap detaylarını ekrana yazdırır.

    :param product_details: Kitap detaylarını içeren sözlük
    """
    print(f"Kitap Adı: {product_details['book_name']}")
    print(f"Fiyat: {product_details['book_price']}")
    print(f"Yıldız Sayısı: {product_details['book_star_count']}")
    print(f"Açıklama: {product_details['book_desc']}")
    print("Ürün Bilgileri:")
    for key, value in product_details['product_info'].items():
        print(f"  {key}: {value}")
    print("\n" + "=" * 50 + "\n")


def main():
    """
    Ana işlev: Tarayıcıyı başlatır, kategori ve kitap URL'lerini toplar,
    kitap detaylarını alır ve ekrana yazdırır.
    """
    driver = setup_driver()
    try:
        # Kategori URL'lerini al
        category_urls = get_category_urls(driver, "https://books.toscrape.com/")

        # Kitap URL'lerini toplar
        all_book_urls = []
        for category_url in category_urls:
            book_urls = get_book_urls(driver, category_url)
            all_book_urls.extend(book_urls)

        # Her kitap için detayları alır ve ekrana yazdırır
        for book_url in all_book_urls:
            product_details = get_product_detail(driver, book_url)
            print_product_details(product_details)

    finally:
        driver.quit()


if __name__ == "__main__":
    main()
