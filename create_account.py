import os
import subprocess
import time
import platform
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


# ============================
# 取得 Chrome 主版本（Mac / Windows）
# ============================
def get_chrome_version() -> str:
    """取得系統 Chrome 主版號（例如 131）"""
    try:
        system = platform.system()

        # macOS
        if system == "Darwin":
            output = subprocess.check_output(
                ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "--version"],
                stderr=subprocess.STDOUT
            ).decode()

        # Windows
        elif system == "Windows":
            output = subprocess.check_output(
                ['reg', 'query', r'HKEY_CURRENT_USER\Software\Google\Chrome\BLBeacon', '/v', 'version'],
                stderr=subprocess.STDOUT
            ).decode()
        else:
            print("❌ 無法判斷系統")
            return None

        # 取主版本號
        version = "".join([c for c in output if c.isdigit() or c == '.']).split('.')[0]
        return version

    except Exception as e:
        print("❌ 無法取得 Chrome 版本：", e)
        return None


# ============================
# 建立 Chrome Driver（含 manager）
# ============================
def create_driver():
    """建立 Selenium ChromeDriver（Mac / Windows 自動判斷 + manager 自動下載）"""

    chrome_version = get_chrome_version()
    if not chrome_version:
        raise Exception("❌ 無法取得 Chrome 版本，請確認 Chrome 是否存在")

    print(f"🌐 偵測到 Chrome 主版號：{chrome_version}")

    # 專案路徑 driver
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    mac_driver = os.path.join(BASE_DIR, "chromedriver")
    win_driver = os.path.join(BASE_DIR, "chromedriver.exe")

    # =====================================
    # 1️⃣ 優先使用「專案內」的 driver
    # =====================================
    if platform.system() == "Windows" and os.path.exists(win_driver):
        driver_path = win_driver
        print(f"🖥️ Windows 使用專案內 chromedriver.exe：{driver_path}")

    elif platform.system() == "Darwin" and os.path.exists(mac_driver):
        driver_path = mac_driver
        print(f"🍎 macOS 使用專案內 chromedriver：{driver_path}")

    else:
        # =====================================
        # 2️⃣ 專案內無 driver → manager 自動下載
        # =====================================
        print("📥 專案內無 chromedriver，自動使用 ChromeDriverManager 下載...")
        driver_path = ChromeDriverManager().install()

    # ============================
    # Chrome Options
    # ============================
    chrome_options = Options()
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-save-password-bubble")

    # 關閉 Chrome 密碼儲存提示
    prefs = {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False
    }
    chrome_options.add_experimental_option("prefs", prefs)

    # 設定視窗大小
    chrome_options.add_argument("--window-size=1280,800")

    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # ============================
    # 最強 anti-detection
    # ============================
    driver.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {
            "source": """
                Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            """
        },
    )

    return driver


# ============================
#  暱稱產生
# ============================

def generate_random_name():
    """隨機生成暱稱：可能單姓 or 雙姓 + 兩字名字"""

    # 單姓
    single_last_names = [
        "陳","林","黃","張","李","王","吳","劉","蔡","楊","許","鄭","謝","洪","郭",
        "邱","曾","廖","賴","徐","周","葉","蘇","莊","呂","江","何","蕭","羅","高",
        "潘","簡","朱","鍾","彭","游","翁","戴","范","宋","余","程","連","唐","馬",
        "董","石"
    ]

    # 新增：雙姓
    double_last_names = [
        "歐陽", "司馬", "諸葛", "上官", "司徒", "夏侯", "張簡", "范姜", "南宮", "西門",
        "東方", "皇甫", "慕容", "長孫", "宇文", "司空", "公孫", "令狐"
    ]

    # 讓雙姓比率稍微低一點（自然一點）
    if random.random() < 0.15:  # 15% 使用雙姓
        last_name = random.choice(double_last_names)
    else:
        last_name = random.choice(single_last_names)

    # 名字第一字
    first_char_list = [
        "家","冠","孟","志","承","柏","俊","冠","子","宇","怡","雅","淑","珮","品","欣",
        "嘉","彥","佳","宗","昇","美","詩","柔","芷","心","宥","睿","建","哲","廷","瑜",
        "郁","婉","雨","馨","明","偉","宏","諾","安","雲","語"
    ]
    
    # 名字第二字
    second_char_list = [
        "瑋","宇","軒","豪","翰","翰","宏","霖","傑","翔","叡","君","婷","芬","琪","萱",
        "婷","雯","萱","怡","蓉","慧","涵","婷","玲","琳","筑","芊","瑜","妤","平","晴",
        "哲","豪","明","偉","哲","成","達","潔","嫻","安","菲","菁"
    ]

    # 兩字名字組合
    name = last_name + random.choice(first_char_list) + random.choice(second_char_list)
    return name



# ============================
#  ⭐ 新增：帳號紀錄 TXT
# ============================

def init_agent_txt(agent_account, agent_password, txt_path):
    """第一次登入代理就建立 TXT 並寫入代理帳密（含中文標題）"""
    if not os.path.exists(txt_path):
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write("代理帳號;代理密碼\n")
            f.write(f"{agent_account};{agent_password}\n")
            f.write("遊戲帳號;遊戲密碼\n")   # 先寫標題，內容等最後 append


def append_random_account(created_account, txt_path):
    """封控後把隨機生成的遊戲帳號寫入 TXT"""
    with open(txt_path, "a", encoding="utf-8") as f:
        f.write(f"{created_account['account']};{created_account['password']}\n")


# ============================
#  登入代理帳號
# ============================

def login(driver):
    """讓使用者輸入帳號密碼後，自動登入，並導向個人頁面"""

    # === 1️⃣ 使用者輸入帳密 ===
    account = input("請輸入帳號：").strip()
    password = input("請輸入密碼：").strip()

    print(f"📝 已儲存帳號密碼，準備登入...")

    # === 2️⃣ 定位 XPath ===
    account_xpath = "/html/body/div/div[2]/main/div[2]/div[2]/div[1]/div[2]/div/div/input"
    password_xpath = "/html/body/div/div[2]/main/div[2]/div[2]/div[2]/div[2]/div/div/input"
    login_button_xpath = "/html/body/div/div[2]/main/div[2]/button"

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

        # 等待跳轉完成
        time.sleep(4)

        # ⭐ 不再點擊返回首頁，直接導向個人頁面
        target_url = "https://agent.jfw-win.com/#/personal/page"
        print(f"➡️ 導向個人頁面：{target_url}")
        driver.get(target_url)

    except Exception as e:
        print("❌ 登入時發生錯誤：", e)

    # 回傳登入帳密（寫 txt 用）
    return account, password



# ============================
#  代理控制 → 進入創帳號畫面
# ============================

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
        time.sleep(5)  # 等待頁面加載

    except Exception as e:
        print("❌ agent_control 發生錯誤：", e)


# ============================
#  ✅ 這裡是你原本的 create_account（含下滑）
# ============================

def create_account(driver):
    """
    創建會員帳號流程（不使用 safe_click）
    1. 下滑到隨機按鈕
    2. 點擊隨機
    3. 讀取帳號
    4. 填寫密碼（aaaa1111）
    """

    wait = WebDriverWait(driver, 10)

    random_btn_xpath = "/html/body/div/div[2]/div/section/main/div[3]/form/div[3]/button"
    account_input_xpath = "/html/body/div/div[2]/div/section/main/div[3]/form/div[3]/div/div[2]/div/div/input"
    ok_button_xpath = "//button[contains(@class,'pk-button-ok')]"
    next1_button_xpath = "/html/body/div/div[2]/div/section/main/div[4]/button[2]"

    # ⭐ 新增：密碼欄位 XPath
    password_input_xpath = "/html/body/div/div[2]/div/section/main/div[3]/form/div[4]/div[1]/div[2]/div/div/input"
    comfirm_password_input_xpath = "/html/body/div/div[2]/div/section/main/div[3]/form/div[5]/div[1]/div[2]/div/div/input"

    # ⭐ 固定密碼
    default_password = "aaaa1111"

    print("⏳ 準備生成隨機帳號...")

    # === 0️⃣ 若有彈窗，先按 OK 關閉 ===
    try:
        ok_btn = driver.find_element(By.XPATH, ok_button_xpath)
        if ok_btn.is_displayed():
            print("⚠️ 偵測到彈窗 → 點擊 OK")
            ok_btn.click()
            time.sleep(0.5)
    except:
        pass

    # === 1️⃣ 下滑到隨機按鈕 ===
    random_btn = wait.until(EC.presence_of_element_located((By.XPATH, random_btn_xpath)))
    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", random_btn)
    time.sleep(0.5)

    # === 2️⃣ 點擊隨機按鈕 ===
    random_btn = wait.until(EC.element_to_be_clickable((By.XPATH, random_btn_xpath)))
    random_btn.click()
    print("✔ 已點擊隨機按鈕")
    time.sleep(3)  # 等待帳號生成

    # === 3️⃣ 讀取生成帳號 ===
    account_input = wait.until(
        EC.presence_of_element_located((By.XPATH, account_input_xpath))
    )
    account_value = account_input.get_attribute("value")

    if not account_value:
        time.sleep(1)
        account_value = account_input.get_attribute("value")

    print(f"🎯 生成帳號：{account_value}")

    # === 4️⃣ 填入密碼 ===
    password_input = wait.until(
        EC.presence_of_element_located((By.XPATH, password_input_xpath))
    )
    password_input.clear()
    password_input.send_keys(default_password)
    print(f"🔐 已輸入密碼：{default_password}")

    comfirm_password_input = wait.until(
        EC.presence_of_element_located((By.XPATH, comfirm_password_input_xpath))
    )
    comfirm_password_input.clear()
    comfirm_password_input.send_keys(default_password)
    print(f"🔐 已輸入確認密碼：{default_password}")

    # === 5️⃣ 填入暱稱 ===
    nickname_xpath = "/html/body/div/div[2]/div/section/main/div[3]/form/div[6]/div[2]/div/div/input"

    nickname_input = wait.until(
        EC.presence_of_element_located((By.XPATH, nickname_xpath))
    )

    nickname = generate_random_name()
    nickname_input.clear()
    nickname_input.send_keys(nickname)

    print(f"🧩 已輸入暱稱：{nickname}")
    time.sleep(1)
    
    # === 6️⃣ 點擊下一步 === 
    next1_button = wait.until(EC.element_to_be_clickable((By.XPATH, next1_button_xpath)))
    next1_button.click()
    time.sleep(3)  # 等待下一頁加載

    # 若要回傳整組資訊，可以這樣：
    return {
        "account": account_value,
        "password": default_password
    }


# ============================
#  設定額度
# ============================

def set_credit_limit(driver):
    """
    設定額度為固定 5000，並按下下一步
    """

    wait = WebDriverWait(driver, 10)

    credit_input_xpath = "/html/body/div/div[2]/div/section/main/div[3]/div/div[2]/div[2]/div/div/input"
    next2_button_xpath = "/html/body/div/div[2]/div/section/main/div[4]/button[3]"

    limit_value = "5000"  # 固定額度

    print("⏳ 開始設定額度為 5000 ...")

    # === 1️⃣ 找到額度輸入框 ===
    credit_input = wait.until(
        EC.presence_of_element_located((By.XPATH, credit_input_xpath))
    )

    # 讓畫面自動捲到額度欄位
    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", credit_input)
    time.sleep(0.5)

    # === 2️⃣ 輸入額度 ===
    credit_input.clear()
    credit_input.send_keys(limit_value)
    print(f"💰 已輸入額度：{limit_value}")

    time.sleep(0.3)

    # === 3️⃣ 按下下一步 ===
    next_button = wait.until(
        EC.element_to_be_clickable((By.XPATH, next2_button_xpath))
    )
    next_button.click()

    print("➡️ 已按下下一步（Next）")
    time.sleep(3)  # 等待下一頁加載


# ============================
#  hold_position
# ============================

def hold_position(driver):
    """
    按下一步 → 下滑到確認按鈕 → 按確認
    每次動作 sleep 2 秒
    """

    wait = WebDriverWait(driver, 10)

    next_btn_xpath = "/html/body/div/div[2]/div/section/main/div[4]/button[3]"
    confirm_btn_xpath = "/html/body/div/div[2]/div/section/main/div[6]/div[2]/button[2]"

    print("⏳ 進入佔水階段（hold_position）...")

    # === 1️⃣ 按 下一步 ===
    next_btn = wait.until(EC.element_to_be_clickable((By.XPATH, next_btn_xpath)))
    next_btn.click()
    print("➡️ 已按下『下一步』")
    time.sleep(2)

    # === 2️⃣ 找到確認按鈕（但不點） ===
    confirm_btn = wait.until(
        EC.presence_of_element_located((By.XPATH, confirm_btn_xpath))
    )

    # === 3️⃣ 捲動到確認按鈕的位置 ===
    driver.execute_script(
        "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
        confirm_btn
    )
    print("⬇️ 已自動捲動到『確認』按鈕位置")
    time.sleep(2)  # 給頁面捲動動畫

    # === 4️⃣ 再次確認按鈕變成可點擊 ===
    confirm_btn = wait.until(
        EC.element_to_be_clickable((By.XPATH, confirm_btn_xpath))
    )

    # === 5️⃣ 點擊確認 ===
    confirm_btn.click()
    print("✔️ 已按下『確認』")
    time.sleep(2)


# ============================
#  risk_control
# ============================

def risk_control(driver):
    """
    封控（risk control）
    1. 檢查限紅 true/false
    2. 若未勾選 → 自動點擊
    3. 點擊 Create → sleep 2
    4. 點擊 Close → sleep 2
    """

    wait = WebDriverWait(driver, 10)

    toggle_xpath = "/html/body/div/div[2]/div/section/main/div[3]/div[3]/div[3]/div[2]/div"
    create_btn_xpath = "/html/body/div/div[2]/div/section/main/div[4]/button[3]"   # ← 正確
    close_btn_xpath = "/html/body/div/div[2]/div/section/main/div[6]/div[2]/button[3]"

    print("⏳ 檢查封控開關狀態...")

    # === 1️⃣ 找到開關 ===
    toggle = wait.until(
        EC.presence_of_element_located((By.XPATH, toggle_xpath))
    )

    # 下滑到開關位置
    driver.execute_script(
        "arguments[0].scrollIntoView({behavior:'smooth',block:'center'});", toggle
    )
    time.sleep(0.5)

    # === 2️⃣ 判斷 true / false 屬性 ===
    attrs = ["aria-checked", "data-checked", "checked", "value"]
    state = None
    for attr in attrs:
        val = toggle.get_attribute(attr)
        if val is not None:
            state = val.lower().strip()
            break

    print(f"🔍 封控屬性：{state}")

    # === 3️⃣ 如果是 false → 自動打勾 ===
    if state != "true":
        print("⚠ 限紅未勾選 → 自動勾選...")
        toggle.click()
        time.sleep(0.5)

    # === 4️⃣ 點擊 Create ===
    create_btn = wait.until(EC.element_to_be_clickable((By.XPATH, create_btn_xpath)))
    create_btn.click()
    print("📝 已按下 Create")
    time.sleep(2)

    # === 5️⃣ 點擊 Close ===
    close_btn = wait.until(EC.element_to_be_clickable((By.XPATH, close_btn_xpath)))
    close_btn.click()
    print("❎ 已按下 Close")
    time.sleep(2)

    print("🎉 封控流程（risk_control）完成！")


# =======================================
#  主程式 讓使用者選擇要創建 5 隻或 10 隻
# =======================================

def main():
    driver = create_driver()

    url = "https://agent.jfw-win.com/#/agent-login"
    print(f"🌏 前往網站：{url}")
    driver.get(url)

    print("✔ 已成功導向網站！")

    # ⭐ 使用者選擇要創建 5 隻或 10 隻
    while True:
        try:
            create_count = int(input("請選擇要創建帳號數量 (5 或 10)：").strip())
            if create_count in (5, 10):
                break
            else:
                print("❌ 請只能輸入 5 或 10")
        except:
            print("❌ 請輸入數字 5 或 10")

    print(f"👉 將創建 {create_count} 隻帳號\n")

    # ⭐ 先登入一次代理
    agent_account, agent_password = login(driver)
    
    # ⭐ TXT 建在桌面
    DESKTOP = os.path.join(os.path.expanduser("~"), "Desktop")
    txt_path = os.path.join(DESKTOP, f"{agent_account}.txt")

    init_agent_txt(agent_account, agent_password, txt_path)

    # ⭐ 跑 N 次
    for i in range(1, create_count + 1):
        print("\n=============================")
        print(f"👉 開始創建第 {i} 隻帳號")
        print("=============================\n")

        agent_control(driver)

        created_account = create_account(driver)
        print("🟢 本次創建的帳號：", created_account)

        set_credit_limit(driver)
        hold_position(driver)
        risk_control(driver)

        append_random_account(created_account, txt_path)
        print(f"📁 已寫入：{created_account} → {txt_path}")

    # ⭐ 全部創完 → 等 5 秒 → 關閉 → 結束程式
    print(f"\n🎉 全部 {create_count} 隻帳號創建完畢！")
    print("⏳ 5 秒後自動關閉瀏覽器並結束程式...")
    time.sleep(5)

    driver.quit()
    os._exit(0)



if __name__ == "__main__":
    main()
