"""
cancel_follow_requests.py
-------------------------
Automates cancelling *pending* Instagram follow requests for a list of usernames.

Setup
-----
1) pip install -r requirements.txt   (selenium, webdriver-manager, etc.)
2) put usernames in pending_follow_requests.csv (column: username)
3) python cancel_follow_requests.py
"""

import os
import time
import random
import sys
import csv

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options

CSV_IN = "pending_follow_requests.csv"
CSV_OUT = "results_cancel_follow_requests.csv"


def human_sleep(a=0.6, b=1.2):
    time.sleep(random.uniform(a, b))


def click_button_safely(btn, driver):
    try:
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
        btn.click()
        return True
    except ElementClickInterceptedException:
        try:
            driver.execute_script("arguments[0].click();", btn)
            return True
        except Exception:
            return False
    except Exception:
        return False


def maybe_confirm_unrequest(driver):
    """
    'Requested' tıklandıktan sonra açılan popup'ta onay butonunu tıkla.
    Önce bilinen metinlerle dener; olmazsa dialogdaki butonlardan
    'İptal/Cancel/Vazgeç/Şimdi Değil' OLMAYANI seçer.
    """
    texts = [
        "Cancel request", "Unsend request", "Remove request",
        "İsteği iptal et", "Takip isteğini iptal et", "İsteği geri çek",
        "İsteği kaldır", "İptal et"
    ]
    end_time = time.time() + 8
    while time.time() < end_time:
        # bilinen metinler
        for t in texts:
            for xp in (
                f"//div[@role='dialog']//button[contains(normalize-space(.), '{t}')]",
                f"//button[contains(normalize-space(.), '{t}')]",
            ):
                try:
                    btn = WebDriverWait(driver, 1.2).until(
                        EC.element_to_be_clickable((By.XPATH, xp))
                    )
                    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
                    btn.click()
                    human_sleep(0.25, 0.5)
                    return True
                except TimeoutException:
                    continue
                except Exception:
                    continue

        # fallback: dialogdaki butonlardan "iptal" olmayanı seç
        try:
            dialog = WebDriverWait(driver, 0.8).until(
                EC.presence_of_element_located((By.XPATH, "//div[@role='dialog']"))
            )
            buttons = dialog.find_elements(By.XPATH, ".//button")
            cancel_words = {"iptal", "vazgeç", "cancel", "not now", "şimdi değil", "kapat"}
            candidates = []
            for b in buttons:
                txt = (b.text or "").strip().lower()
                aria = (b.get_attribute("aria-label") or "").strip().lower()
                html = (b.get_attribute("innerHTML") or "").lower()
                label = txt or aria
                if not label:
                    if "svg" in html:
                        candidates.append(b)
                        continue
                if label and not any(w in label for w in cancel_words):
                    candidates.append(b)
            target = candidates[0] if candidates else (buttons[-1] if buttons else None)
            if target:
                try:
                    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", target)
                    target.click()
                except ElementClickInterceptedException:
                    driver.execute_script("arguments[0].click();", target)
                human_sleep(0.25, 0.5)
                return True
        except TimeoutException:
            pass
        except Exception:
            pass

    return False


def find_requested_button(driver):
    """
    'Requested' / 'İstek Gönderildi' durum butonunu yakala.
    Metin + aria-label + ikon fallback taraması yapar.
    """
    xpaths = [
        "//button[normalize-space()='Requested']",
        "//div[normalize-space()='Requested']/ancestor::button",
        "//button[contains(normalize-space(.), 'İstek Gönderildi')]",
        "//button[contains(normalize-space(.), 'İstek')]",
        "//*[@role='button' and contains(normalize-space(.), 'Requested')]",
        "//*[@role='button' and contains(normalize-space(.), 'İstek')]",
    ]
    for xp in xpaths:
        try:
            el = WebDriverWait(driver, 2).until(
                EC.presence_of_element_located((By.XPATH, xp))
            )
            if el and el.is_displayed():
                return el
        except TimeoutException:
            continue

    # Yazısız/ikonlu fallback
    buttons = driver.find_elements(By.XPATH, "//button")
    for b in buttons:
        txt = (b.text or "").lower()
        aria = (b.get_attribute("aria-label") or "").lower()
        html = (b.get_attribute("innerHTML") or "").lower()
        if any(k in txt for k in ["request", "istek", "gönderildi"]):
            return b
        if any(k in aria for k in ["request", "istek"]):
            return b
        if "svg" in html and any(k in html for k in ["request", "istek"]):
            return b
    return None


def login(driver):
    driver.get("https://www.instagram.com/")
    print("👉 Chrome profilinden login kullanılacak.")
    WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )
    human_sleep(2, 3)


def process_username(driver, uname):
    profile_url = f"https://www.instagram.com/{uname.strip().lstrip('@')}/"
    driver.get(profile_url)
    print(f"Visiting: {profile_url}")
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
    except TimeoutException:
        return "timeout"

    human_sleep()

    btn = find_requested_button(driver)
    if not btn:
        return "no-action"

    txt = (btn.text or "").lower()
    aria = (btn.get_attribute("aria-label") or "").lower()

    if "istek" in txt or "request" in txt or "gönderildi" in txt or "request" in aria:
        if click_button_safely(btn, driver):
            human_sleep()
            if maybe_confirm_unrequest(driver):
                return "request-cancelled"
            return "failed-request-cancel"
    elif "takip" in txt or "following" in txt or "takip" in aria or "following" in aria:
        if click_button_safely(btn, driver):
            human_sleep()
            if maybe_confirm_unrequest(driver):
                return "unfollowed"
            return "failed-unfollow"

    return "unknown"


def main():
    if not os.path.exists(CSV_IN):
        print(f"Input CSV not found: {CSV_IN}")
        sys.exit(1)

    usernames = []
    with open(CSV_IN, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            u = row.get("username")
            if u:
                usernames.append(u.strip())

    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument(r"--user-data-dir=C:\Users\mrtcl\selenium-profile")
    chrome_options.add_argument("--profile-directory=Default")

    driver = webdriver.Chrome(
        service=ChromeService(ChromeDriverManager().install()),
        options=chrome_options,
    )

    try:
        login(driver)
        results = []
        for i, uname in enumerate(usernames, 1):
            status = process_username(driver, uname)
            print(f"[{i}/{len(usernames)}] {uname}: {status}")
            results.append({"username": uname, "status": status})
            human_sleep()

        with open(CSV_OUT, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["username", "status"])
            writer.writeheader()
            writer.writerows(results)

        print(f"✅ Done. Results written to {CSV_OUT}")
    finally:
        try:
            driver.quit()
        except Exception:
            pass


if __name__ == "__main__":
    main()
