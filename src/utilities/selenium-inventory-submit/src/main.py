import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
import os
import time
import pyotp
from webdriver_manager.chrome import ChromeDriverManager

# Load environment variables at the top level
load_dotenv()
JW_USERNAME = os.getenv("JW_USERNAME")
JW_PASSWORD = os.getenv("JW_PASSWORD")
JW_TOTP_SECRET = os.getenv("JW_TOTP_SECRET")

def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--window-size=1920,1080")
    # Uncomment the next line for headless mode, or leave commented for visible browser
    # options.add_argument("--headless=new")

    from selenium.webdriver.chrome.service import Service
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

def navigate_to_website(driver, url):
    driver.get(url)

def enter_username(driver, username):
    username_input = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "username"))
    )
    username_input.clear()
    username_input.send_keys(username)
    # Wait for overlays to disappear before clicking
    try:
        WebDriverWait(driver, 3).until(
            EC.invisibility_of_element_located((By.CSS_SELECTOR, ".lnc-acceptCookiesButton"))
        )
    except Exception:
        pass
    next_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "submit-button"))
    )
    driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
    next_button.click()

def enter_password(driver, password):
    password_input = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "password"))
    )
    password_input.clear()
    password_input.send_keys(password)
    next_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "submit-button"))
    )
    next_button.click()

def enter_2fa_code(driver, totp_secret):
    totp = pyotp.TOTP(totp_secret)
    code = totp.now()
    code_input = WebDriverWait(driver, 20).until(
        EC.visibility_of_element_located((By.ID, "form.code"))
    )
    code_input.clear()
    code_input.send_keys(code)
    # Wait for and click the "Next" button after entering the code
    next_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[.//ptrn-translate[text()='Next']]"))
    )
    driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
    next_button.click()

def select_category(driver, category):
    category_dropdown = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "selector_for_category_dropdown"))
    )
    category_dropdown.click()
    
    category_option = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, f"//option[text()='{category}']"))
    )
    category_option.click()

def match_jw_id_and_enter_quantity(driver, jw_id, quantity):
    publication_element = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, f"//div[@data-jw-id='{jw_id}']"))
    )
    
    quantity_input = publication_element.find_element(By.CSS_SELECTOR, "selector_for_quantity_input")
    quantity_input.clear()
    quantity_input.send_keys(str(quantity))

def submit_form(driver):
    submit_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "selector_for_submit_button"))
    )
    submit_button.click()

def handle_stay_logged_in_prompt(driver):
    yes_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Yes']"))
    )
    yes_button.click()

def handle_privacy_banner(driver):
    try:
        accept_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".lnc-acceptCookiesButton"))
        )
        accept_button.click()
        # Optional: wait for the banner to disappear
        WebDriverWait(driver, 5).until(
            EC.invisibility_of_element_located((By.CSS_SELECTOR, ".lnc-acceptCookiesButton"))
        )
    except Exception:
        # If the banner doesn't appear, just continue
        pass

def go_to_inventory_page(driver):
    # Wait for the "Literature" link to be visible and clickable, then click it
    literature_link = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//a[contains(@class, 'home-link') and contains(text(), 'Literature')]"))
    )
    driver.execute_script("arguments[0].scrollIntoView(true);", literature_link)
    literature_link.click()

def go_to_inventory_reports(driver):
    # Wait for the "Inventory Reports" link to be visible and clickable, then click it
    reports_link = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//a[contains(@class, 'side-nav__link') and contains(text(), 'Inventory Reports')]"))
    )
    driver.execute_script("arguments[0].scrollIntoView(true);", reports_link)
    reports_link.click()

def click_inventory_report_for_language(driver, language):
    # Read all expected languages from file
    with open(get_languages_file_path(), "r", encoding="utf-8") as f:
        expected_languages = [line.strip().split(",")[-1] for line in f if line.strip()]

    # Wait until at least one language link is present (not all, just any)
    def any_language_loaded(driver):
        links = driver.find_elements(By.XPATH, "//a[contains(@class, 'card__header-link')]")
        return len(links) > 0

    print(f"Waiting for language links to load...")
    WebDriverWait(driver, 20).until(any_language_loaded)
    print(f"Language links loaded, checking for missing/extra languages...")

    # Now check all languages after they are loaded
    links = driver.find_elements(By.XPATH, "//a[contains(@class, 'card__header-link')]")
    found = [link.text.strip() for link in links]
    found_langs = [text.split("|")[-1].strip() for text in found if "|" in text]
    missing = [lang for lang in expected_languages if lang not in found_langs]
    extra = [lang for lang in found_langs if lang not in expected_languages]

    for lang in missing:
        print(f"[WARNING] Language missing on page: '{lang}'. Please add it to the site or check your languages.txt.")
    for lang in extra:
        print(f"[WARNING] Language found on page but not in languages.txt: '{lang}'. Please add it to languages.txt if needed.")

    # If the selected language is missing, abort
    if language not in found_langs:
        raise Exception(f"Selected language '{language}' is missing from the page. Please add it or check your languages.txt.")

    print(f"[DEBUG] Found links on page: {found}")
    print(f"[DEBUG] Number of expected languages found: {len(found_langs)}/{len(expected_languages)}")

    # Now, find and click the correct language link
    headers = driver.find_elements(By.CSS_SELECTOR, "h2.card__header-text > a.card__header-link")
    for link in headers:
        link_text = link.text.strip()
        print(f"[DEBUG] Checking link text: {link_text}")
        if link_text.endswith(language):
            driver.execute_script("arguments[0].scrollIntoView(true);", link)
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable(link))
            link.click()
            print(f"Clicked on inventory report for language: {language}")
            return
    raise Exception(f"No inventory report found for language: {language}")

def parse_args():
    parser = argparse.ArgumentParser(description="JW Inventory Automation")
    parser.add_argument("--language", "-l", default="en", help="Language code (e.g., en, es, fr)")
    return parser.parse_args()

def get_language_from_file():
    with open(get_languages_file_path(), "r", encoding="utf-8") as f:
        languages = [line.strip().split(",")[-1] for line in f if line.strip()]
    print("Available languages:")
    for idx, lang in enumerate(languages, 1):
        print(f"{idx}. {lang}")
    while True:
        choice = input("Select a language by number: ")
        if choice.isdigit() and 1 <= int(choice) <= len(languages):
            return languages[int(choice) - 1]
        print("Invalid selection. Try again.")

def get_languages_file_path():
    # This gets the directory where main.py is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, "languages.txt")

def load_languages():
    """Load languages from file. Returns a dict: code -> name, and name -> code."""
    lang_path = get_languages_file_path()
    code_to_name = {}
    name_to_code = {}
    with open(lang_path, "r", encoding="utf-8") as f:
        for line in f:
            parts = [p.strip() for p in line.strip().split(",") if p.strip()]
            if len(parts) == 2:
                code, name = parts
                code_to_name[code.lower()] = name
                name_to_code[name.lower()] = code
    return code_to_name, name_to_code

def select_language_interactively(code_to_name):
    codes = list(code_to_name.keys())
    print("\nAvailable languages:")
    print("------------------------------")
    for idx, code in enumerate(codes, 1):
        print(f"{idx}. {code} - {code_to_name[code]}")
    while True:
        choice = input("\nSelect a language by number, code, or name: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(codes):
            return codes[int(choice) - 1], code_to_name[codes[int(choice) - 1]]
        choice_lc = choice.lower()
        if choice_lc in code_to_name:
            return choice_lc, code_to_name[choice_lc]
        # Try matching by full name
        for code, name in code_to_name.items():
            if choice_lc == name.lower():
                return code, name
        print("Invalid selection. Try again.")

def resolve_language(language_arg, code_to_name, name_to_code):
    if not language_arg:
        return None, None
    arg = language_arg.strip().lower()
    if arg in code_to_name:
        return arg, code_to_name[arg]
    if arg in name_to_code:
        return name_to_code[arg], code_to_name[name_to_code[arg]]
    # Try partial match
    for code, name in code_to_name.items():
        if arg == name.lower():
            return code, name
    return None, None

def main():
    print(f"################### JW Inventory Automation Script ###################")
    code_to_name, name_to_code = load_languages()

    # Use CLI flag or prompt
    parser = argparse.ArgumentParser(description="JW Inventory Automation")
    parser.add_argument("--language", "-l", help="Language code or full name (e.g., en, English)")
    args = parser.parse_args()

    lang_code, lang_name = resolve_language(args.language, code_to_name, name_to_code)
    if not lang_code:
        lang_code, lang_name = select_language_interactively(code_to_name)

    print(f"###################################################################################")
    print(f"Selected language: {lang_name} ({lang_code})")
    print(f"###################################################################################")

    driver = setup_driver()
    try:
        print("\nNavigating to JW Login page...\n")
        # Use lang_code for URL, lang_name for UI selection
        url = f"https://login.jw.org/username?PostLoginUri=%2Fconnect%2Fauthorize%2Fcallback%3Fclient_id%3Dhub.jw.org%252Fhome%26redirect_uri%3Dhttps%253A%252F%252Fhub.jw.org%252Fhome%252Fsignin-oidc%26response_type%3Did_token%26scope%3Dopenid%2520profile%26response_mode%3Dform_post%26nonce%3D638833780679689374.NTI4NjM5M2EtNTFiNC00YjBhLWE5NjYtZDQ0MjUyM2JiODQ2MDNmNzg4NjItMzcwMi00OWU3LWEzMTItYThiNTVjNTEyY2Yw%26client-request-id%3D3b9b2b8f-05ed-4e3e-967e-d1d3b6ca5567%26original_params%3D%253FpostLoginUri%253D%25252Fen%26state%3DCfDJ8IIUqNGiUidGnmYicll1Oc8Nm3K86FVChNW8-pxPxDwub7VH6HIPKFPfbbGtADss0rnJsvZtqXICHOO51nPe15_7Z8W_coeGnvBtf0EMuBRaZ69KXUSPLd7EuNkAybQD8WaOsxk6NHft9L4r6A2HoMIs-vouhWpIuc2jMvtbx3UAv20qpGKKYTCajlPbKWgrFdP3cNuBonmip4supA4eSBuJmhjpfFAuAxQ9i4_RDhrR1xjglXIOOyKvrGqTS0GRi3_2Kb1GHNYvtUy8-Fg5SMqRl6zf7CwaVrVCwvBy1-ueOxjnV8iPqLNH06fJaMDLk3cvmNzJMCQyt_P1-aJhU8_pJYQCComk3UE-JiyvLCK2GOv3U7yhvvZEDCFcei_fhNNtnNW5BmoqWG4EWA3nLSfn20NOCXWSW_1BW3wAXfelkINvcx_0VoQL-pJnQAHfzBJWIoPMlTsjGE4K9i2k-HQZOEXDFubqUnjTB2UYrt1n8UXFX5aMGcJa8njGA_iewvVFQPwdFoEbD6livtnPnNOTuHcXlTCXIcFXQH_GPPGl%26x-client-SKU%3DID_NET9_0%26x-client-ver%3D8.7.0.0"
        navigate_to_website(driver, url)
        print("Entering username...")
        enter_username(driver, JW_USERNAME)
        print("Handling privacy banner...")
        handle_privacy_banner(driver)
        print("Entering password...")
        enter_password(driver, JW_PASSWORD)
        print("Handling 'Stay Logged In' prompt...")
        handle_stay_logged_in_prompt(driver)
        print("Entering 2FA code...")
        enter_2fa_code(driver, JW_TOTP_SECRET)
        print("Navigating to Inventory page...")
        go_to_inventory_page(driver)
        print("Navigating to Inventory Reports...")
        go_to_inventory_reports(driver)
        print("Clicking on Inventory Report for selected language...")
        click_inventory_report_for_language(driver, lang_name)
        # Continue with inventory actions...
        time.sleep(5)
    finally:
        driver.quit()

if __name__ == "__main__":
    main()