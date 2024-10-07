import os
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image, ImageFilter
import time

# Setup the Chrome driver
driver = webdriver.Chrome()

# Navigate to the Goodreads page
driver.get("https://www.goodreads.com/book/popular_by_date/2024/6")

# Define folders for downloading and editing images
download_folder = "C:\\Users\\Abdul\\Desktop\\downloaded_book_images"
edit_folder = "C:\\Users\\Abdul\\Desktop\\edited_book_images"

if not os.path.exists(download_folder):
    os.makedirs(download_folder)
if not os.path.exists(edit_folder):
    os.makedirs(edit_folder)

# Clean filename function to create valid filenames
def clean_filename(filename):
    return "".join([c for c in filename if c.isalpha() or c.isdigit() or c == ' ']).rstrip()

# Function to download images
def download_images(image_elements, book_title_elements, download_folder):
    try:
        for i in range(min(len(image_elements), len(book_title_elements))):
            image_url = image_elements[i].get_attribute('src')
            book_title = book_title_elements[i].text

            # Clean the book title to use as filename
            clean_title = clean_filename(book_title) + ".jpg"

            # Download the image and save it
            image_response = requests.get(image_url)
            if image_response.status_code == 200:
                image_path = os.path.join(download_folder, clean_title)
                with open(image_path, 'wb') as img_file:
                    img_file.write(image_response.content)
                print(f"Downloaded: {book_title} -> {clean_title}")
            else:
                print(f"Failed to download image for: {book_title}")

        print(f"Successfully downloaded {min(len(image_elements), len(book_title_elements))} images.")
    except Exception as e:
        print(f"Error downloading images: {e}")

# Function to process each downloaded image
def process_image(image_path, output_path):
    try:
        print("Opening the image...")
        original_image = Image.open(image_path)
        print("Image opened successfully.")

        landscape_width = original_image.width * 2
        landscape_height = original_image.height

        background_image = original_image.resize((landscape_width, landscape_height))
        blurred_background = background_image.filter(ImageFilter.GaussianBlur(radius=10))
        print("Blur applied to background.")

        output_image = blurred_background.copy()
        position = (
            (landscape_width - original_image.width) // 2,
            (landscape_height - original_image.height) // 2
        )

        output_image.paste(original_image, position, original_image.convert('RGBA'))
        print("Pasted book cover on blurred background.")

        output_image.save(output_path, format="PNG")
        print(f"Image saved at: {output_path}")
    except Exception as e:
        print(f"Error occurred during image processing: {e}")

# Function to click "Show more books" button multiple times
def load_all_books(driver, clicks=10):
    current_count = 0
    promo_closed = False  # Flag to track if promo has been closed

    for _ in range(clicks):
        try:
            # Check if promo prompt is open and close it if it is (only need to do this once)
            if not promo_closed:
                try:
                    promo_close_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, "/html/body/div[3]/div/div[1]/div/div/button"))
                    )
                    promo_close_button.click()
                    print("Promo prompt closed.")
                    promo_closed = True  # Set flag to true after closing the promo
                    time.sleep(2)  # Small delay after closing the promo
                except Exception as e:
                    print("No promo prompt detected or error closing promo: ", e)

            # Scroll to the button using JavaScript to make sure it's in view
            show_more_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//*[@id='__next']/div[2]/main/div[2]/div[1]/div[3]/div/div/button"))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", show_more_button)
            time.sleep(2)  # Give some time for scrolling
            show_more_button.click()
            print("Clicked 'Show more books' button.")

            # Wait for the books to load after clicking
            time.sleep(5)

            # Update the count of books loaded
            image_elements = driver.find_elements(By.XPATH, "//img[@class='ResponsiveImage']")
            current_count = len(image_elements)
            print(f"Books loaded so far: {current_count}")
        except Exception as e:
            print(f"Error clicking 'Show more books': {e}")


if __name__ == "__main__":
    try:
        # Click "Show more books" button 10 times
        load_all_books(driver, clicks=15)

        # After loading all books, scrape the image elements and titles again
        image_elements = driver.find_elements(By.XPATH, "//img[@class='ResponsiveImage']")
        book_title_elements = driver.find_elements(By.XPATH, "//h3[@class='Text Text__title3 Text__umber']/strong/a")

        # Download the images
        download_images(image_elements, book_title_elements, download_folder)

        # Process each downloaded image
        for root, _, files in os.walk(download_folder):
            for file in files:
                if file.endswith(".jpg"):
                    image_path = os.path.join(root, file)
                    output_path = os.path.join(edit_folder, file.replace(".jpg", "_edited.png"))

                    process_image(image_path, output_path)

    except Exception as e:
        print(f"Error occurred: {e}")

    finally:
        # Close the browser
        driver.quit()
