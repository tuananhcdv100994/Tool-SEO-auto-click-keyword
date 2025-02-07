import time
import requests
import random
from urllib.parse import quote

def format_proxy(proxy):
    proxy = proxy.strip()
    if not proxy.startswith("http"):
        proxy = "http://" + proxy  # Tự động thêm http nếu thiếu
    return proxy

def get_proxy(proxies):
    valid_proxies = [format_proxy(p) for p in proxies if ":" in p]
    if not valid_proxies:
        print("[ERROR] Không có proxy hợp lệ, sử dụng kết nối trực tiếp.")
        return None
    
    return valid_proxies

def user_interaction(real_url, proxy, action):
    stay_time = random.randint(15, 20)
    print(f"[INFO] Ở lại trang {stay_time} giây...")
    for i in range(stay_time, 0, -1):
        print(f"[INFO] {i} giây còn lại...", end="\r")
        time.sleep(1)
    print("\n[INFO] Hoàn thành thời gian ở lại trang.")
    
    if action == "scroll":
        print("[INFO] Cuộn xuống cuối trang...")
    elif action == "click_link":
        print("[INFO] Click vào một link ngẫu nhiên trên trang...")
        try:
            requests.get(real_url, proxies=proxy, timeout=10) if proxy else requests.get(real_url, timeout=10)
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Không thể thực hiện click ngẫu nhiên: {e}")

def google_search(keyword, target_url, api_key, proxies, action):
    found = False
    available_proxies = get_proxy(proxies)
    
    for start in range(0, 50, 10):  # Duyệt từ trang 1 đến trang 5 (50 kết quả)
        search_url = f"https://serpapi.com/search.json?q={quote(keyword)}&engine=google&start={start}&api_key={api_key}"
        proxy = None
        
        for attempt in range(len(available_proxies) + 1):  # Thử tất cả proxy nếu cần
            if available_proxies:
                selected_proxy = random.choice(available_proxies)
                proxy = {"http": selected_proxy, "https": selected_proxy}
                print(f"[INFO] Đang sử dụng proxy: {selected_proxy}")
            
            try:
                response = requests.get(search_url, proxies=proxy, timeout=10) if proxy else requests.get(search_url, timeout=10)
                if response.status_code == 200:
                    break
            except requests.exceptions.RequestException as e:
                print(f"[ERROR] Proxy lỗi: {selected_proxy}, thử proxy khác... ({e})")
                if selected_proxy in available_proxies:
                    available_proxies.remove(selected_proxy)  # Xóa proxy lỗi khỏi danh sách
                proxy = None  # Sử dụng kết nối trực tiếp
        
        if not response or response.status_code != 200:
            print(f"[ERROR] Không thể truy cập SerpAPI (Status Code: {response.status_code if response else 'N/A'})")
            continue
        
        data = response.json()
        results = data.get("organic_results", [])
        
        rank = start
        for result in results:
            rank += 1
            real_url = result.get("link", "")
            print(f"[INFO] Rank {rank}: {real_url}")
            if target_url in real_url:
                print(f"[SUCCESS] Tìm thấy {target_url} ở vị trí {rank}, đang truy cập...")
                try:
                    requests.get(real_url, proxies=proxy, timeout=10) if proxy else requests.get(real_url, timeout=10)
                    print(f"[DONE] Đã click vào {real_url}")
                    user_interaction(real_url, proxy, action)
                    found = True
                    break
                except requests.exceptions.RequestException as e:
                    print(f"[ERROR] Không thể truy cập {real_url}: {e}")
                    continue
        if found:
            break
    
    if not found:
        print(f"[FAIL] Không tìm thấy {target_url} trong kết quả.")
    return found

def main():
    api_key = input("Nhập API Key của SerpAPI: ").strip()
    keywords = input("Nhập danh sách từ khóa (cách nhau bằng dấu phẩy): ").split(",")
    target_url = input("Nhập URL mục tiêu: ").strip()
    proxies = input("Nhập danh sách proxy (cách nhau bằng dấu phẩy): ").split(",")
    
    print("Chọn hành động sau khi click vào trang:")
    print("1: Chỉ click vào website.")
    print("2: Click vào web + cuộn xuống cuối trang.")
    print("3: Click vào web + click vào một link ngẫu nhiên.")
    choice = input("Nhập lựa chọn (1/2/3): ").strip()
    
    action_map = {"1": "none", "2": "scroll", "3": "click_link"}
    action = action_map.get(choice, "none")
    
    while True:
        for keyword in keywords:
            keyword = keyword.strip()
            print(f"\n[INFO] Đang tìm kiếm từ khóa: {keyword}")
            google_search(keyword, target_url, api_key, proxies, action)
            print("[INFO] Chờ 21 giây trước lần tìm kiếm tiếp theo...")
            time.sleep(21)  # Delay 1 phút

if __name__ == "__main__":
    main()
