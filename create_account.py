import os
import subprocess
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def get_chrome_version() -> str:
    """取得系統 Chrome 主版號（例如 131）。"""
    try:
        output = subprocess.check_output(
            ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "--version"],
            stderr=subprocess.STDOUT
        ).decode("utf-8")
        version = output.replace("Google Chrome", "").strip().split(".")[0]
        return version
    except Exception as e:
        print("❌ 無法取得 Chrome 版本：", e)
        return None


def create_driver():
    """建立 Selenium ChromeDriver（使用本地 chromedriver + 關閉自動化控制提示）"""

    chrome_version = get_chrome_version()
    if not chrome_version:
        raise Exception("無法取得 Chrome 版本，請確認 Google Chrome 是否存在")

    print(f"🌐 偵測到 Chrome 版本：{chrome_version}")

    # 專案內 chromedriver 的路徑
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    driver_path = os.path.join(BASE_DIR, "chromedriver")

    if not os.path.exists(driver_path):
        raise FileNotFoundError(f"❌ 找不到 chromedriver：{driver_path}")

    # 設定 Chrome Options
    chrome_options = Options()

    # 關閉「Chrome 正受自動化控制」提示
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    # 關閉自動化控制 blink 特徵
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")

    # 防止 WebDriver 被偵測
    chrome_options.add_argument("--disable-blink-features")

    # 視窗大小（可調整）
    chrome_options.add_argument("--window-size=1280,800")

    service = Service(driver_path)

    driver = webdriver.Chrome(service=service, options=chrome_options)

    # 再次移除 webdriver 痕跡（最強 anti-detection）
    driver.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {
            "source": """
                Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            """
        },
    )

    return driver

def login(driver):
    """讓使用者輸入帳號密碼後，自動填入登入頁面"""
    
    # === 1️⃣ 使用者輸入帳密 ===
    account = input("請輸入帳號：").strip()
    password = input("請輸入密碼：").strip()

    print(f"📝 已儲存帳號密碼，準備登入...")

    # === 2️⃣ 定位 XPath（你給的）===
    account_xpath = "/html/body/div/div[2]/main/div[2]/div[2]/div[1]/div[2]/div/div/input"
    password_xpath = "/html/body/div/div[2]/main/div[2]/div[2]/div[2]/div[2]/div/div/input"
    login_button_xpath = "/html/body/div/div[2]/main/div[2]/button"
    back_button_xpath = "/html/body/div/div[2]/div/div"

    try:
        # === 3️⃣ 輸入帳號 ===
        acc_el = driver.find_element("xpath", account_xpath)
        acc_el.clear()
        acc_el.send_keys(account)
        print("✔ 已輸入帳號")

        # === 4️⃣ 輸入密碼 ===
        pwd_el = driver.find_element("xpath", password_xpath)
        pwd_el.clear()
        pwd_el.send_keys(password)
        print("✔ 已輸入密碼")

        print("🎯 帳密輸入完成！")

        # === 5️⃣ 點擊登入按鈕 ===
        login_btn = driver.find_element("xpath", login_button_xpath)
        login_btn.click()

        time.sleep(2)  # 等待頁面加載

        # === 網頁返回按鈕 ===
        back_btn = driver.find_element("xpath", back_button_xpath)
        back_btn.click()

    except Exception as e:
        print("❌ 登入時發生錯誤：", e)

def wait_loading_finished(driver, timeout=30):
    """等待 pk-loading-box 消失"""

    try:
        WebDriverWait(driver, timeout).until_not(
            EC.presence_of_element_located((By.CLASS_NAME, "pk-loading-box"))
        )
        print("⏳ loading 結束")
    except:
        print("⚠️ 警告：loading 遮罩可能仍存在，但已超時。")

def agent_control(driver):
    """登入完成後，依照順序點擊 代理控制 相關按鈕"""

    wait = WebDriverWait(driver, 15)

    time.sleep(10)  # 等待頁面加載

    try:
        # === 1️⃣ 點擊「agent_button」 ===
        agent_button_xpath = "/html/body/div/div[2]/div/div/div/div[2]/a"
        agent_btn = wait.until(EC.element_to_be_clickable((By.XPATH, agent_button_xpath)))
        agent_btn.click()
        print("✔ 已點擊 agent_button")
        time.sleep(5)  # 等待頁面加載

        # === 2️⃣ 點擊「direct_member」 ===
        direct_member_xpath = "/html/body/div/div[2]/div/section/main/div[3]/div[2]"
        dm_btn = wait.until(EC.element_to_be_clickable((By.XPATH, direct_member_xpath)))
        dm_btn.click()
        print("✔ 已點擊 direct_member")
        time.sleep(2)  # 等待頁面加載

        # === 3️⃣ 點擊「create_button」 ===
        create_button_xpath = "/html/body/div/div[2]/div/section/main/div[2]/div[2]/button"
        create_btn = wait.until(EC.element_to_be_clickable((By.XPATH, create_button_xpath)))
        create_btn.click()
        print("✔ 已點擊 create_button")
        time.sleep(2)  # 等待頁面加載

        # === 4️⃣ 點擊「cash_member」 ===
        cash_member_xpath = "/html/body/div/div[2]/div/section/main/div[6]/div/div[1]/div[2]/div[2]/div/div[1]"
        cash_btn = wait.until(EC.element_to_be_clickable((By.XPATH, cash_member_xpath)))
        cash_btn.click()
        print("✔ 已點擊 cash_member")
        time.sleep(2)  # 等待頁面加載

        # === 5️⃣ 點擊「confirm_button」 ===
        confirm_button_xpath = "/html/body/div/div[2]/div/section/main/div[6]/div/div[2]/button[2]"
        confirm_btn = wait.until(EC.element_to_be_clickable((By.XPATH, confirm_button_xpath)))
        confirm_btn.click()
        print("✔ 已點擊 confirm_button")
        time.sleep(2)  # 等待頁面加載

        print("🎉 agent_control 全流程完成！")
        input("請按下 Enter 鍵以結束程式...")

    except Exception as e:
        print("❌ agent_control 發生錯誤：", e)


def main():
    driver = create_driver()

    url = "https://agent.jfw-win.com/#/agent-login"
    print(f"🌏 前往網站：{url}")
    driver.get(url)

    print("✔ 已成功導向網站！")

    # ⭐ 呼叫登入流程
    login(driver)
    agent_control(driver)

if __name__ == "__main__":
    main()
