import json
import os
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.webdriver.remote.webelement import WebElement
from utils import handle_privacy_banner

def get_publication_data_path(language):
    # Normalize language for folder name (e.g., "English")
    language_folder = language.lower()
    print(f"Looking for publication data in folder: {language_folder}")
    # Capitalize first letter for folder (if needed)
    print(f"Using folder: {language_folder} for publication data")
    # Get current year and month
    now = datetime.now()
    year = str(now.year)
    month = now.strftime("%B")  # e.g., "June"
    # Example: .../english/2025/June2025.json
    filename = f"{month}{year}.json"
    print(f"Looking for file: {filename} in {language_folder}/{year} directory")
    # Only go up one directory to reach 'selenium-inventory-submit'
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(
        base_dir, "data", "inventory-data", language_folder, year, filename
    )
    return data_path

def load_publication_data(language):
    json_path = get_publication_data_path(language)
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)

def normalize_text(text):
    import re
    return re.sub(r"[^a-zA-Z0-9 ]", "", text or "").lower().strip()

def normalize_id(jwid):
    import re
    return re.sub(r"[^a-zA-Z0-9]", "", jwid or "").lower().strip()

def input_publications(driver, publication_data, language):
    category_ui_map = {
        "brochures": "Brochures and Booklets",
        "forms & supplies": "Forms and Supplies"
    }

    category_map = {}
    for pub in publication_data:
        category = pub.get("category", "Uncategorized")
        category_map.setdefault(category, []).append(pub)

    all_not_found = []

    for category, pubs in category_map.items():
        ui_category = category_ui_map.get(category.lower(), category)
        print(f"\nCategory: {ui_category}")

        # Privacy Banner Check at the start of each category
        try:
            privacy_banner = driver.find_element(By.ID, "privacy-banner")
            if privacy_banner.is_displayed():
                print("Privacy banner detected, dismissing...")
                handle_privacy_banner(driver)
        except Exception:
            pass

        found_count = 0
        not_found = []

        # Privacy Banner Check again right before clicking category
        try:
            privacy_banner = driver.find_element(By.ID, "privacy-banner")
            if privacy_banner.is_displayed():
                print("Privacy banner detected, dismissing...")
                handle_privacy_banner(driver)
        except Exception:
            pass

        if not click_category(driver, ui_category):
            print(f"[ERROR] Could not find category '{ui_category}' on the page.")
            all_not_found.extend([f"{pub.get('name')} (jwId: {pub.get('jwId')})" for pub in pubs])
            continue

        retried_labels = set()  # Track which labels have been retried

        for pub in pubs:
            name = pub.get("name")
            jwid = pub.get("jwId")
            qty = pub.get("quantity")
            normalized_name = normalize_text(name)
            normalized_jwid = normalize_id(jwid)
            try:
                buttons = driver.find_elements(By.XPATH, "//button[contains(@class, 'button--link')]")
                found = False
                for btn in buttons:
                    btn_text = normalize_text(btn.text)
                    print(f"    [DEBUG] Button text: '{btn.text}' (normalized: '{btn_text}')")
                    print(f"    [DEBUG] Looking for name: '{normalized_name}' and jwid: '{normalized_jwid}'")
                    # Use AND logic: both name and jwId must be present in the button text
                    if normalized_name in btn_text and (normalized_jwid and normalized_jwid in btn_text):
                        btn.click()
                        print(f"  Clicked: {name} (jwId: {jwid})")
                        found = True
                        break
                if not found:
                    raise Exception("Button not found")

                WebDriverWait(driver, 5).until(
                    EC.visibility_of_element_located((
                        By.XPATH,
                        "//h2[contains(@class, 'ptrn-modal-dialog__heading') and contains(text(), 'Update Quantity')]"
                    ))
                )
                time.sleep(1)

                qty_input = WebDriverWait(driver, 5).until(
                    EC.visibility_of_element_located((By.ID, "form.currentQuantity"))
                )
                qty_input.clear()
                qty_input.send_keys(str(qty))

                save_btn = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((
                        By.XPATH,
                        "//button[contains(@class, 'button--primary') and .//ptrn-translate[contains(text(), 'Save')]]"
                    ))
                )
                save_btn.click()
                time.sleep(1)

                try:
                    warning = WebDriverWait(driver, 2).until(
                        EC.visibility_of_element_located((
                            By.XPATH,
                            "//p[contains(@class, 'message--warning') and contains(., 'Amount higher than previous quantity. Confirm if received quantity needs to be updated.')]"
                        ))
                    )
                    if warning.is_displayed():
                        print(f"  Warning appeared for {name}, clicking Save again.")
                        save_btn = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((
                                By.XPATH,
                                "//button[contains(@class, 'button--primary') and .//ptrn-translate[contains(text(), 'Save')]]"
                            ))
                        )
                        save_btn.click()
                        time.sleep(1)
                except Exception:
                    pass

                # --- Wait for modal to close and card quantity to update ---
                try:
                    WebDriverWait(driver, 5).until(
                        EC.invisibility_of_element_located((By.XPATH, "//form[contains(@class, 'form--edit')]"))
                    )
                    # Find the card for this publication
                    card_elem = btn.find_element(By.XPATH, "ancestor::article[contains(@class, 'card')]")
                    # Wait for the <p> element to update to the expected quantity
                    def card_quantity_updated(driver):
                        try:
                            qty_elem = card_elem.find_element(By.XPATH, ".//p[contains(@class, 'ng-star-inserted')]")
                            card_qty = qty_elem.text.strip()
                            return str(card_qty) == str(qty)
                        except Exception:
                            return False
                    if WebDriverWait(driver, 5).until(card_quantity_updated):
                        print(f"[VERIFY] Card quantity for '{name}' (jwId: {jwid}) correctly set to '{qty}'")
                    else:
                        qty_elem = card_elem.find_element(By.XPATH, ".//p[contains(@class, 'ng-star-inserted')]")
                        card_qty = qty_elem.text.strip()
                        print(f"[WARNING] Card quantity for '{name}' (jwId: {jwid}) is '{card_qty}', expected '{qty}'")
                except Exception as e:
                    print(f"[WARNING] Could not verify card quantity for '{name}' (jwId: {jwid}): {e}")

                found_count += 1

            except Exception as e:
                print(f"  Not found or failed to submit: {name} (jwId: {jwid})")
                not_found.append(f"{name} (jwId: {jwid})")

        # --- Final check for unchecked checkboxes, retry only once ---
        try:
            checkboxes = driver.find_elements(By.XPATH, "//input[@type='checkbox' and not(@checked)]")
            if checkboxes:
                print("-" * 60)
                print(f"[RETRY] The following publications in '{ui_category}' were not checked as done:")
                for cb in checkboxes:
                    # Try to get the publication label from the card context
                    try:
                        card_elem = cb.find_element(By.XPATH, "ancestor::article[contains(@class, 'card')]")
                        btn_elem = card_elem.find_element(By.XPATH, ".//button[contains(@class, 'button--link')]")
                        label = btn_elem.text.strip()
                    except Exception:
                        label = "(label not found)"
                    print(f"    - {label}")

                    matched_pub = None
                    for pub in pubs:
                        pub_name_norm = normalize_text(pub.get("name"))
                        pub_jwid_norm = normalize_id(pub.get("jwId"))
                        label_norm = normalize_text(label)

                        # Special handling for "Others - Category" publications
                        if pub_name_norm.startswith("others -"):
                            # Only match if label is exactly "others"
                            if label_norm.strip() == "others":
                                matched_pub = pub
                                break
                        else:
                            # Normal AND logic for all other publications
                            if pub_name_norm in label_norm and (pub_jwid_norm and pub_jwid_norm in label_norm):
                                matched_pub = pub
                                break
                    if matched_pub and label not in retried_labels:
                        # --- Check if card quantity is already correct before retrying ---
                        try:
                            qty_elem = card_elem.find_element(By.XPATH, ".//p[contains(@class, 'ng-star-inserted')]")
                            card_qty = qty_elem.text.strip()
                            if str(card_qty) == str(matched_pub.get("quantity")):
                                print(f"[INFO] Card quantity for '{matched_pub.get('name')}' (jwId: {matched_pub.get('jwId')}) already matches expected value '{card_qty}'. Skipping retry.")
                                retried_labels.add(label)
                                continue  # Don't retry if already correct
                        except Exception as e:
                            print(f"[WARNING] Could not verify card quantity before retry for '{matched_pub.get('name')}' (jwId: {matched_pub.get('jwId')}): {e}")

                        print(f"      Retrying submission for: {matched_pub.get('name')} (jwId: {matched_pub.get('jwId')})")
                        retried_labels.add(label)
                        # --- Retry logic (same as above, but only once) ---
                        try:
                            buttons = driver.find_elements(By.XPATH, "//button[contains(@class, 'button--link')]")
                            found = False
                            normalized_name = normalize_text(matched_pub.get("name"))
                            jwid = matched_pub.get("jwId")
                            qty = matched_pub.get("quantity")
                            for btn in buttons:
                                btn_text = normalize_text(btn.text)
                                if normalized_name in btn_text and (jwid and jwid.lower() in btn_text):
                                    btn.click()
                                    print(f"  [RETRY] Clicked: {matched_pub.get('name')} (jwId: {jwid})")
                                    found = True
                                    break
                            if found:
                                WebDriverWait(driver, 5).until(
                                    EC.visibility_of_element_located((
                                        By.XPATH,
                                        "//h2[contains(@class, 'ptrn-modal-dialog__heading') and contains(text(), 'Update Quantity')]"
                                    ))
                                )
                                time.sleep(1)
                                qty_input = WebDriverWait(driver, 5).until(
                                    EC.visibility_of_element_located((By.ID, "form.currentQuantity"))
                                )
                                qty_input.clear()
                                qty_input.send_keys(str(qty))
                                save_btn = WebDriverWait(driver, 5).until(
                                    EC.element_to_be_clickable((
                                        By.XPATH,
                                        "//button[contains(@class, 'button--primary') and .//ptrn-translate[contains(text(), 'Save')]]"
                                    ))
                                )
                                save_btn.click()
                                time.sleep(1)
                                try:
                                    warning = WebDriverWait(driver, 2).until(
                                        EC.visibility_of_element_located((
                                            By.XPATH,
                                            "//p[contains(@class, 'message--warning') and contains(., 'Amount higher than previous quantity. Confirm if received quantity needs to be updated.')]"
                                        ))
                                    )
                                    if warning.is_displayed():
                                        print(f"  [RETRY] Warning appeared for {matched_pub.get('name')}, clicking Save again.")
                                        save_btn = WebDriverWait(driver, 5).until(
                                            EC.element_to_be_clickable((
                                                By.XPATH,
                                                "//button[contains(@class, 'button--primary') and .//ptrn-translate[contains(text(), 'Save')]]"
                                            ))
                                        )
                                        save_btn.click()
                                        time.sleep(1)
                                except Exception:
                                    pass
                        except Exception as e:
                            print(f"      [RETRY] Failed to resubmit: {matched_pub.get('name')} (jwId: {matched_pub.get('jwId')}) - {e}")
                    elif not matched_pub:
                        print(f"      No matching publication data found for: {label}")
                print("-" * 60)
        except Exception:
            pass

        # Handle "Others" category
        if category.lower() == "others":
            try:
                done_checkbox = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//input[@type='checkbox' and @name='done']"))
                )
                done_checkbox.click()
                print("  Checked 'done' for Others category.")
            except Exception:
                print("  Could not find 'done' checkbox for Others category.")

            try:
                prev_btn = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((
                        By.XPATH,
                        "//a[contains(@class, 'button') and .//ptrn-translate[text()='Previous']]"
                    ))
                )
                prev_btn.click()
                print("  Clicked 'Previous' to continue to next category.")
            except Exception:
                print("  Could not find 'Previous' button for Others category.")
        else:
            try:
                prev_btn = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((
                        By.XPATH,
                        "//a[contains(@class, 'button') and .//ptrn-translate[text()='Previous']]"
                    ))
                )
                prev_btn.click()
                print("  Clicked 'Previous' to continue to next category.")
            except Exception:
                print("  Could not find 'Previous' button after category.")

        if found_count > 0:
            print(f"[SUCCESS] Submitted {found_count} publications for category '{ui_category}'.")
        if not_found:
            print(f"[WARNING] Publications not found in category '{ui_category}':")
            for nf in not_found:
                print(f"    - {nf}")
            all_not_found.extend(not_found)

    print("\n=== Submission Complete ===")
    if all_not_found:
        print("-" * 60)
        print("The following publications could not be submitted:")
        for nf in all_not_found:
            print(f"    - {nf}")
        print("-" * 60)
    else:
        print("All publications were successfully submitted.")

def click_category(driver, category_name, timeout=10):
    """
    Clicks the category element matching the given category_name.
    """
    print(f"Looking for category: {category_name}")
    # Updated selector for the category link
    category_xpath = (
        f"//a[contains(@class, 'process-guide-section__title')]"
        f"[.//span[normalize-space(text())='{category_name}']]"
    )
    try:
        category_elem = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.XPATH, category_xpath))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", category_elem)
        category_elem.click()
        print(f"Clicked category: {category_name}")
        return True
    except Exception as e:
        print(f"[WARNING] Category '{category_name}' not found or not clickable: {e}")
        return False