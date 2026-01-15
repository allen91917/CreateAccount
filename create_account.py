import os
import subprocess
import time
import platform
import random
import threading
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
            print("無法判斷系統")
            return None

        # 取主版本號
        version = "".join([c for c in output if c.isdigit() or c == '.']).split('.')[0]
        return version

    except Exception as e:
        print("無法取得 Chrome 版本：", e)
        return None


# ============================
# 建立 Chrome Driver（含 manager）
# ============================
def create_driver():
    """建立 Selenium ChromeDriver（使用 ChromeDriverManager 自動下載）"""

    chrome_version = get_chrome_version()
    if not chrome_version:
        raise Exception("無法取得 Chrome 版本，請確認 Chrome 是否存在")

    # print(f"偵測到 Chrome 主版號：{chrome_version}")

    # 直接使用 ChromeDriverManager 下載
    print("使用 ChromeDriverManager 自動下載 chromedriver...")
    driver_path = ChromeDriverManager().install()
    # print(f"chromedriver 路徑：{driver_path}")

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
    if random.random() < 0.1:  # 10% 使用雙姓
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
#  讀取用戶資訊
# ============================

def read_user_info():
    """從專案資料夾的用戶資訊.txt讀取帳號、密碼、創建數量"""
    # 取得專案資料夾路徑
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    info_file = os.path.join(BASE_DIR, "用戶資訊.txt")
    
    if not os.path.exists(info_file):
        print(f"找不到檔案：{info_file}")
        print("請在專案資料夾建立 用戶資訊.txt，格式如下：")
        print("帳號,密碼,創建數量")
        print("user1,pass1,5")
        print("user2,pass2,10")
        return []
    
    users = []
    with open(info_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
        for i, line in enumerate(lines):
            line = line.strip()
            if not line or line.startswith("#") or i == 0:  # 跳過空行、註解和標題行
                continue
            
            parts = line.split(",")
            if len(parts) >= 3:
                account = parts[0].strip()
                password = parts[1].strip()
                try:
                    create_count = int(parts[2].strip())
                    if create_count <= 0:
                        print(f"警告：{account} 的創建數量 {create_count} 必須大於 0，跳過此帳號")
                        continue
                    users.append({
                        "account": account,
                        "password": password,
                        "create_count": create_count
                    })
                except ValueError:
                    print(f"警告：{account} 的創建數量格式錯誤，跳過此帳號")
    
    return users


# ============================
#  ⭐ 新增：帳號紀錄 TXT
# ============================

def init_agent_txt(agent_account, agent_password, txt_path):
    """第一次登入代理就建立 TXT 並寫入代理帳密（含中文標題）"""
    if not os.path.exists(txt_path):
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write("代理帳號,代理密碼\n")
            f.write(f"{agent_account},{agent_password}\n")
            f.write("遊戲帳號,遊戲密碼\n")   # 先寫標題，內容等最後 append


def append_random_account(created_account, txt_path):
    """封控後把隨機生成的遊戲帳號寫入 TXT"""
    with open(txt_path, "a", encoding="utf-8") as f:
        f.write(f"{created_account['account']},{created_account['password']}\n")


# ============================
#  登入代理帳號
# ============================

def login(driver, account, password):
    """使用提供的帳號密碼自動登入，並導向個人頁面"""

    # print(f"[{account}] 準備登入...")

    # === 2️⃣ 定位 XPath ===
    account_xpath = "//input[@placeholder='請輸入帳號']"
    password_xpath = "//input[@placeholder='請輸入密碼']"
    login_button_xpath = "//button[contains(@class, 'login-btn')]"

    wait = WebDriverWait(driver, 15)

    try:
        # 等待頁面完全載入
        # print(f"[{account}] 等待登入頁面載入...")
        time.sleep(3)

        # === 3️⃣ 輸入帳號 ===
        print(f"[{account}] 尋找帳號輸入欄位...")
        acc_el = wait.until(EC.presence_of_element_located((By.XPATH, account_xpath)))
        acc_el.clear()
        acc_el.send_keys(account)
        print(f"[{account}] ✔ 已輸入帳號")

        # === 4️⃣ 輸入密碼 ===
        pwd_el = wait.until(EC.presence_of_element_located((By.XPATH, password_xpath)))
        pwd_el.clear()
        pwd_el.send_keys(password)
        print(f"[{account}] ✔ 已輸入密碼")

        print(f"[{account}] 帳密輸入完成！")

        # === 5️⃣ 點擊登入按鈕 ===
        login_btn = wait.until(EC.element_to_be_clickable((By.XPATH, login_button_xpath)))
        login_btn.click()

        # 等待跳轉完成
        time.sleep(4)

        # ⭐ 不再點擊返回首頁，直接導向個人頁面
        target_url = "https://agent.jfw-win.com/#/personal/page"
        print(f"[{account}] 導向個人頁面：{target_url}")
        driver.get(target_url)

    except Exception as e:
        print(f"[{account}] 登入時發生錯誤：{e}")
        print(f"[{account}] 提示：請檢查網頁是否正常載入，或 XPath 是否已變更")


# ============================
#  代理控制 → 進入創帳號畫面
# ============================

def agent_control(driver, account):
    """登入完成後，依照順序點擊 代理控制 相關按鈕"""

    wait = WebDriverWait(driver, 15)

    time.sleep(10)  # 等待頁面加載

    try:
        # === 1️⃣ 點擊「agent_button」 ===
        agent_button_xpath = "/html/body/div/div[2]/div/div/div/div[2]/a"
        agent_btn = wait.until(EC.element_to_be_clickable((By.XPATH, agent_button_xpath)))
        agent_btn.click()
        print(f"[{account}] ✔ 已點擊 agent_button")
        time.sleep(5)  # 等待頁面加載

        # === 2️⃣ 點擊「direct_member」 ===
        direct_member_xpath = "/html/body/div/div[2]/div/section/main/div[3]/div[2]"
        dm_btn = wait.until(EC.element_to_be_clickable((By.XPATH, direct_member_xpath)))
        dm_btn.click()
        print(f"[{account}] ✔ 已點擊 direct_member")
        time.sleep(2)  # 等待頁面加載

        # === 3️⃣ 點擊「create_button」 ===
        create_button_xpath = "/html/body/div/div[2]/div/section/main/div[2]/div[2]/button"
        create_btn = wait.until(EC.element_to_be_clickable((By.XPATH, create_button_xpath)))
        create_btn.click()
        print(f"[{account}] ✔ 已點擊 create_button")
        time.sleep(2)  # 等待頁面加載

        # === 4️⃣ 點擊「cash_member」 ===
        cash_member_xpath = "/html/body/div/div[2]/div/section/main/div[6]/div/div[1]/div[2]/div[2]/div/div[1]"
        cash_btn = wait.until(EC.element_to_be_clickable((By.XPATH, cash_member_xpath)))
        cash_btn.click()
        print(f"[{account}] ✔ 已點擊 cash_member")
        time.sleep(2)  # 等待頁面加載

        # === 5️⃣ 點擊「confirm_button」 ===
        confirm_button_xpath = "/html/body/div/div[2]/div/section/main/div[6]/div/div[2]/button[2]"
        confirm_btn = wait.until(EC.element_to_be_clickable((By.XPATH, confirm_button_xpath)))
        confirm_btn.click()
        print(f"[{account}] ✔ 已點擊 confirm_button")
        time.sleep(5)  # 等待頁面加載

    except Exception as e:
        print(f"[{account}] agent_control 發生錯誤：{e}")


# ============================
#  ✅ 這裡是你原本的 create_account（含下滑）
# ============================

def create_account(driver, account):
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

    print(f"[{account}] 準備生成隨機帳號...")

    # === 0️⃣ 若有彈窗，先按 OK 關閉 ===
    try:
        ok_btn = driver.find_element(By.XPATH, ok_button_xpath)
        if ok_btn.is_displayed():
            print(f"[{account}] 偵測到彈窗 → 點擊 OK")
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
    print(f"[{account}] 已點擊隨機按鈕")
    time.sleep(3)  # 等待帳號生成

    # === 3️⃣ 讀取生成帳號 ===
    account_input = wait.until(
        EC.presence_of_element_located((By.XPATH, account_input_xpath))
    )
    account_value = account_input.get_attribute("value")

    if not account_value:
        time.sleep(1)
        account_value = account_input.get_attribute("value")

    print(f"[{account}] 生成帳號：{account_value}")

    # === 4️⃣ 填入密碼 ===
    password_input = wait.until(
        EC.presence_of_element_located((By.XPATH, password_input_xpath))
    )
    password_input.clear()
    password_input.send_keys(default_password)
    print(f"[{account}] 已輸入密碼：{default_password}")

    comfirm_password_input = wait.until(
        EC.presence_of_element_located((By.XPATH, comfirm_password_input_xpath))
    )
    comfirm_password_input.clear()
    comfirm_password_input.send_keys(default_password)
    print(f"[{account}] 已輸入確認密碼：{default_password}")

    # === 5️⃣ 填入暱稱 ===
    nickname_xpath = "/html/body/div/div[2]/div/section/main/div[3]/form/div[6]/div[2]/div/div/input"

    nickname_input = wait.until(
        EC.presence_of_element_located((By.XPATH, nickname_xpath))
    )

    nickname = generate_random_name()
    nickname_input.clear()
    nickname_input.send_keys(nickname)

    print(f"[{account}] 已輸入暱稱：{nickname}")
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

def set_credit_limit(driver, account):
    """設定額度為固定 5000，並按下下一步"""

    wait = WebDriverWait(driver, 10)

    credit_input_xpath = "/html/body/div/div[2]/div/section/main/div[3]/div/div[2]/div[2]/div/div/input"
    next2_button_xpath = "/html/body/div/div[2]/div/section/main/div[4]/button[3]"

    limit_value = "5000"  # 固定額度

    print(f"[{account}] 開始設定額度為 5000 ...")

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
    print(f"[{account}] 已輸入額度：{limit_value}")

    time.sleep(0.3)

    # === 3️⃣ 按下下一步 ===
    next_button = wait.until(
        EC.element_to_be_clickable((By.XPATH, next2_button_xpath))
    )
    next_button.click()

    print(f"[{account}] 已按下下一步（Next）")
    time.sleep(3)  # 等待下一頁加載


# ============================
#  hold_position
# ============================

def hold_position(driver, account):
    """按下一步 下滑到確認按鈕 按確認 每次動作 sleep 2 秒"""

    wait = WebDriverWait(driver, 10)

    next_btn_xpath = "/html/body/div/div[2]/div/section/main/div[4]/button[3]"
    confirm_btn_xpath = "/html/body/div/div[2]/div/section/main/div[6]/div[2]/button[2]"

    print(f"[{account}] 進入佔水階段（hold_position）...")

    # === 1️⃣ 按 下一步 ===
    next_btn = wait.until(EC.element_to_be_clickable((By.XPATH, next_btn_xpath)))
    next_btn.click()
    print(f"[{account}] 已按下『下一步』")
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
    print(f"[{account}] 已自動捲動到『確認』按鈕位置")
    time.sleep(2)  # 給頁面捲動動畫

    # === 4️⃣ 再次確認按鈕變成可點擊 ===
    confirm_btn = wait.until(
        EC.element_to_be_clickable((By.XPATH, confirm_btn_xpath))
    )

    # === 5️⃣ 點擊確認 ===
    confirm_btn.click()
    print(f"[{account}] 已按下『確認』")
    time.sleep(2)


# ============================
#  risk_control
# ============================

def risk_control(driver, account):
    """
    封控（risk control）點擊下一步 → 等待彈窗 → 點擊創建 → 點擊 Close
    返回值：True 表示成功，False 表示失敗（不應寫入 txt）
    """

    wait = WebDriverWait(driver, 15)

    print(f"[{account}] 進入封控流程...")

    # 多等一下，確保頁面完全載入
    time.sleep(3)

    # === 第一步：找出並點擊「下一步」按鈕 ===
    # print(f"[{account}] 搜尋所有按鈕...")
    try:
        buttons = driver.find_elements(By.TAG_NAME, "button")
        # print(f"[{account}] 找到 {len(buttons)} 個按鈕")
        
        next_btn = None
        
        for idx, btn in enumerate(buttons):
            try:
                btn_text = btn.text.strip()
                btn_class = btn.get_attribute("class") or ""
                btn_visible = btn.is_displayed()
                
                # print(f"[{account}] 按鈕 {idx}: text='{btn_text}' | class='{btn_class}' | visible={btn_visible}")
                
                # 找「下一步」按鈕
                if btn_visible and btn_text == "下一步":
                    next_btn = btn
                    # print(f"[{account}] ✓ 找到『下一步』按鈕 (索引 {idx})")
                    break
                    
            except Exception as e:
                print(f"[{account}] 檢查按鈕 {idx} 時出錯: {e}")
                continue
        
        # 點擊下一步
        if next_btn:
            # print(f"[{account}] 準備點擊『下一步』...")
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'auto', block: 'center'});", next_btn)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", next_btn)
            # print(f"[{account}] ✓ 已點擊『下一步』")
            time.sleep(3)  # 等待彈窗出現
        else:
            print(f"[{account}] ✗ 找不到『下一步』按鈕")
            return False
        
        # === 第二步：等待並點擊彈窗中的「創建」按鈕 ===
        # print(f"[{account}] 等待彈窗出現，搜尋『創建』按鈕...")
        time.sleep(2)
        
        buttons = driver.find_elements(By.TAG_NAME, "button")
        # print(f"[{account}] 重新掃描，找到 {len(buttons)} 個按鈕")
        
        create_btn = None
        
        for idx, btn in enumerate(buttons):
            try:
                btn_text = btn.text.strip()
                btn_class = btn.get_attribute("class") or ""
                btn_visible = btn.is_displayed()
                
                # print(f"[{account}] 按鈕 {idx}: text='{btn_text}' | class='{btn_class}' | visible={btn_visible}")
                
                # 找「創建」按鈕（文字是「創建」且可見）
                if btn_visible and btn_text == "創建":
                    create_btn = btn
                    # print(f"[{account}] ✓ 找到『創建』按鈕 (索引 {idx})")
                    break
                    
            except Exception as e:
                print(f"[{account}] 檢查按鈕 {idx} 時出錯: {e}")
                continue
        
        # 點擊創建
        if create_btn:
            # print(f"[{account}] 準備點擊『創建』...")
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'auto', block: 'center'});", create_btn)
            time.sleep(1)
            
            if create_btn.is_displayed() and create_btn.is_enabled():
                driver.execute_script("arguments[0].click();", create_btn)
                print(f"[{account}] ✓ 已點擊『創建』")
                time.sleep(3)
            else:
                print(f"[{account}] ✗ 創建按鈕不可點擊")
                return False
        else:
            print(f"[{account}] ✗ 找不到『創建』按鈕")
            return False
        
        # === 第三步：點擊 Close 按鈕 ===
        # print(f"[{account}] 搜尋『Close』按鈕...")
        
        close_btn_xpath = "/html/body/div/div[2]/div/section/main/div[6]/div[2]/button[3]"
        
        try:
            close_btn = wait.until(EC.presence_of_element_located((By.XPATH, close_btn_xpath)))
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'auto', block: 'center'});", close_btn)
            time.sleep(1)
            
            if close_btn.is_displayed() and close_btn.is_enabled():
                driver.execute_script("arguments[0].click();", close_btn)
                print(f"[{account}] ✓ 已點擊 Close")
                time.sleep(2)
                return True  # 成功完成
            else:
                print(f"[{account}] ✗ Close 按鈕不可點擊，可能帳號已滿或是改版，如改版請聯絡工程師")
                return False
        except Exception as e:
            print(f"[{account}] ✗ 點擊 Close 失敗（可能帳號已滿或是改版，如改版請聯絡工程師）: {e}")
            return False
                
    except Exception as e:
        print(f"[{account}] ✗ 封控流程發生錯誤: {e}")
        return False

    print(f"[{account}] 封控流程完成！")
    return True


# =======================================
#  單一用戶的工作流程
# =======================================

def process_user(user_info):
    """處理單一用戶的帳號創建流程"""
    account = user_info["account"]
    password = user_info["password"]
    create_count = user_info["create_count"]
    
    print(f"\n[{account}] ========== 開始處理 ==========")
    print(f"[{account}] 將創建 {create_count} 隻帳號")
    
    try:
        # 建立專屬的 driver
        driver = create_driver()
        
        # 前往登入頁面
        url = "https://agent.jfw-win.com/#/agent-login"
        print(f"[{account}] 前往網站：{url}")
        driver.get(url)
        
        # 登入
        login(driver, account, password)
        
        # 建立 TXT 檔案
        DESKTOP = os.path.join(os.path.expanduser("~"), "Desktop")
        txt_path = os.path.join(DESKTOP, f"{account}.txt")
        init_agent_txt(account, password, txt_path)
        
        # 循環創建帳號
        for i in range(1, create_count + 1):
            print(f"\n[{account}] ===== 開始創建第 {i}/{create_count} 隻帳號 =====")
            
            agent_control(driver, account)
            created_account = create_account(driver, account)
            print(f"[{account}] 本次創建的帳號：{created_account}")
            
            set_credit_limit(driver, account)
            hold_position(driver, account)
            
            # 執行封控並檢查是否成功
            success = risk_control(driver, account)
            
            if success:
                # 只有成功才寫入 txt
                append_random_account(created_account, txt_path)
                print(f"[{account}] ✓ 已寫入：{created_account} → {txt_path}")
            else:
                # 失敗則不寫入，可能帳號已滿
                print(f"[{account}] ✗ 創建失敗（可能帳號已滿），本次帳號不寫入 txt")
                print(f"[{account}] ⚠️ 建議檢查代理帳號是否已達上限")
        
        print(f"\n[{account}] 全部 {create_count} 隻帳號創建完畢！")
        print(f"[{account}] 5 秒後關閉瀏覽器...")
        time.sleep(5)
        
        driver.quit()
        print(f"[{account}] ========== 處理完成 ==========\n")
        
    except Exception as e:
        print(f"[{account}] 發生錯誤：{e}")
        try:
            driver.quit()
        except:
            pass


# =======================================
#  主程式 - 使用多線程處理多個用戶
# =======================================

def main():
    print("=" * 50)
    print("自動創建帳號系統 (多線程版本)")
    print("=" * 50)
    
    # 讀取用戶資訊
    users = read_user_info()
    
    if not users:
        print("\n沒有找到有效的用戶資訊，程式結束。")
        return
    
    print(f"\n共找到 {len(users)} 個用戶：")
    for user in users:
        print(f"  - {user['account']} (創建 {user['create_count']} 個帳號)")
    
    # print(f"\n將使用 {len(users)} 個線程同時處理...")

    
    # 建立線程列表
    threads = []
    
    # 為每個用戶建立一個線程
    for user in users:
        thread = threading.Thread(target=process_user, args=(user,))
        threads.append(thread)
        thread.start()
        time.sleep(2)  # 錯開啟動時間，避免同時啟動太多瀏覽器
    
    # 等待所有線程完成
    for thread in threads:
        thread.join()
    
    print("\n" + "=" * 50)
    print("所有用戶處理完成！")
    print("=" * 50)


if __name__ == "__main__":
    main()
