import time
import random
import threading
import requests
import re
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 使用fake_useragent庫生成隨機User-Agent
ua = UserAgent()

# 你的目標網址
url = "https://www.youtube.com/watch?v=rqLxQ1OKv9M"

# 在程式開始時讀取已經存在的 User-Agent 列表
def read_user_agents_from_file(file_name):
    try:
        with open(file_name, 'r') as f:
            return [line.strip() for line in f]
    except FileNotFoundError:
        # 當檔案不存在時，創建一個空檔案並返回空列表
        with open(file_name, 'w'):
            pass
        return []

# 在程式結束時將 User-Agent 列表寫入文件
def write_user_agents_to_file(file_name, user_agents):
    # 讀取文件中的 User-Agent，如果文件不存在，創建一個空文件
    existing_user_agents = read_user_agents_from_file(file_name)

    # 使用 'a' 模式（追加模式）打開文件，這樣即使文件不存在，也會自動創建
    with open(file_name, 'a') as f:
        for user_agent in user_agents:
            # 只有在 User-Agent 不存在於 existing_user_agents 中時，才將其寫入文件
            if user_agent not in existing_user_agents:
                f.write(user_agent + '\n')


def get_local_ip():
    # 定義常用的 IP 地址列表，用於模擬不同的 IP 位址
    ip_addresses = []

    for i in range(0, 256):
        ip_addresses.append('192.168.0.' + str(i))
    return ip_addresses

# 獲取代理IP列表
def get_proxy_ips():
    res = requests.get('https://free-proxy-list.net/')
    m = re.findall('\d+\.\d+\.\d+\.\d+:\d+', res.text)
    valid_ips = []

    for ip in m:
        try:
            res = requests.get('https://api.ipify.org?format=json', proxies={'http': ip, 'https': ip}, timeout=5)
            valid_ips.append(ip)
            print(f'有效代理IP: {ip}')
        except:
            print(f'無效代理IP: {ip}')
            pass
    return valid_ips

def refresh_website(url, proxy, user_agent):
    options = webdriver.ChromeOptions()
    options.add_argument(f'user-agent={user_agent}')
    options.add_argument(f"--proxy-server={proxy}")

    # 請將executable_path替換為你的ChromeDriver路徑
    driver = webdriver.Chrome(executable_path=r"C:\Users\HR\Desktop\Selenium\chromedriver", options=options)
    
    try:
        watch_time = random.randint(36, 61)
        print(f'觀看時間: {watch_time} 秒')
        driver.get(url)
        print(f'成功訪問: {url}  使用代理: {proxy} 和 User-Agent: {user_agent}')
        
        # 檢查頁面是否包含 "無法連上這個網站" 或 "需要升級版本"
        page_content = driver.page_source
        # if "無法連上這個網站" in page_content or "請更新你的瀏覽器" in page_content:
        if "請更新你的瀏覽器" in page_content:
            print("遇到錯誤，關閉瀏覽器並嘗試下一次執行")
            driver.quit()
            return False  # 失敗
        
        elif "無法連上這個網站" in page_content or "這個網頁無法正常運作" in page_content or "您的連線已中斷" in page_content or "為何顯示此頁" in page_content:
            print("網站沒有回應，關閉瀏覽器並嘗試下一次執行")
            driver.quit()
            return True  # 成功
        
        wait = WebDriverWait(driver, 120)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[aria-label="播放"]')))
        if "播放" in page_content:
            driver.find_element(By.CSS_SELECTOR, '[aria-label="播放"]').click()
            time.sleep(10)

            # 檢查頁面是否包含 "略過廣告"
            if "略過廣告" in page_content:
                # 等待元素出現
                wait = WebDriverWait(driver, 10) # 超時時間設為 10 秒
                skip_ad_element = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class='ytp-ad-text ytp-ad-skip-button-text' and contains(text(), '略過廣告')]")))
                # 點擊元素
                skip_ad_element.click()
                print("有廣告, 略過廣告")
            else:
                print("沒有廣告, 繼續觀看")
        time.sleep(watch_time)
    except Exception as e:
        print(f'錯誤: {e}')
    finally:
        driver.quit()
        print("觀看結束, 關閉瀏覽器")
    return True  # 成功

def execute_thread(thread_name, success_user_agents, error_user_agents):
    print(f"{thread_name} 開始執行")
    start_time = time.time()
    four_hours = 4 * 60 * 60

    # 使用get_proxy_ips()獲取有效的代理IP列表
    proxies = get_proxy_ips()
    # proxies = get_local_ip()

    # 模擬線程執行的任務
    while True:
        success_user_agents = read_user_agents_from_file(success_user_agents_file)
        error_user_agents = read_user_agents_from_file(error_user_agents_file)
        elapsed_time = time.time() - start_time

        if elapsed_time >= four_hours:
            print(f"{thread_name} 執行了 4 小時，關閉後重新運行")
            break

        # 選擇隨機的代理和User-Agent
        proxy = random.choice(proxies)
        user_agent = ua.random
        while user_agent in error_user_agents:  # 確保不選擇錯誤列表中的User-Agent
            user_agent = ua.random
            print("選擇了錯誤的 User-Agent, 重新選擇")

        # 如果成功，將 user_agent 添加到 success_user_agents 列表，如果失敗，將其添加到 error_user_agents 列表
        if refresh_website(url, proxy, user_agent) == True:
            success_user_agents.append(user_agent)
            write_user_agents_to_file("success_user_agents.txt", success_user_agents)
        else:
            error_user_agents.append(user_agent)
            write_user_agents_to_file("error_user_agents.txt", error_user_agents)

# 設定要創建的線程數量
num_threads = 1

# 在主程式中創建成功和錯誤 User-Agent 列表，並從文件中讀取已有的 User-Agent
success_user_agents_file = "success_user_agents.txt"
error_user_agents_file = "error_user_agents.txt"
success_user_agents = read_user_agents_from_file(success_user_agents_file)
error_user_agents = read_user_agents_from_file(error_user_agents_file)

while True:
    # 創建指定數量的線程，並啟動它們
    for i in range(num_threads):
        # 創建線程，傳入目標函數和參數
        thread_name = f"線程{i+1}"
        t = threading.Thread(target=execute_thread, args=(thread_name, success_user_agents, error_user_agents))
        t.start()

    # 主線程等待所有子線程執行完畢
    for t in threading.enumerate():
        if t != threading.current_thread():
            t.join()

    print("所有線程執行完畢，重新啟動")


