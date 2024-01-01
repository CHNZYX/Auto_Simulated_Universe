import psutil
import requests
import tkinter as tk
from tkinter import ttk
import time
import threading
import win32api
import zipfile
import os

def get_latest_release_info(repo_url):
    response = requests.get(repo_url)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return None

def kill_process_by_name(process_name):
    res = 0
    for process in psutil.process_iter(attrs=['pid', 'name']):
        if process.info['name'] == process_name:
            try:
                # Terminate the process
                psutil.Process(process.info['pid']).terminate()
                print(f"Killed process {process_name} with PID {process.info['pid']}")
                res = 1
            except:
                pass
    return res

def unzip_and_overwrite(zip_path, extract_path):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        for file_info in zip_ref.infolist():
            try:
                print(file_info)
                zip_ref.extract(file_info, extract_path)
            except Exception as e:
                pass

def download_file(url, save_path):
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    size = 0
    tm = time.time()
    size_ls = [0]
    tm_ls = [tm]
    cnt_ls = [0 for _ in range(5)]
    
    with open(save_path, 'wb') as file:
        for data in response.iter_content(chunk_size=1024):
            size += file.write(data)
            size_ls.append(size)
            tm_ls.append(time.time())
            progress_bar["value"]=size/total_size*100
            if time.time()>tm+1:
                tm = time.time()
                cnt_ls.append(len(tm_ls))
            if cnt_ls[-1] == len(tm_ls):
                operation_label.config(text="下载中... {:.0f}%\t{:.0f}KB/s".format(progress_bar["value"],(size-size_ls[cnt_ls[-5]])/(time.time()-tm_ls[cnt_ls[-5]])/1024))
            progress_bar.update()
    
    operation_label.config(text="下载完成，正在退出gui...")
    res = kill_process_by_name("flet.exe")
    res |= kill_process_by_name("gui.exe")
    if res:
        time.sleep(4)
    else:
        time.sleep(1.5)
    operation_label.config(text="解压文件中...")
    unzip_and_overwrite('./archive.zip','.')
    os.remove('./archive.zip')
    operation_label.config(text="更新完成")
    

def start_download():
    popup.destroy()
    operation_label.config(text="下载中...")
    download_url = f"https://github.moeyy.xyz/https://github.com/CHNZYX/Auto_Simulated_Universe/releases/download/{info['tag_name']}/Auto_Simulated_Universe_{info['tag_name']}.zip"
    save_path = "./archive.zip"
    t = threading.Thread(target=download_file, args=(download_url, save_path))
    t.start()

def main_operation():
    global info
    operation_label.config(text="获取版本信息...")
    repo_url = "https://api.github.com/repos/CHNZYX/Auto_Simulated_Universe/releases/latest"
    info = get_latest_release_info(repo_url)
    try:
        version_remote = info['tag_name'].strip('v').split(' ')[0]
    except:
        try:
            info = dict()
            info['tag_name']= 'v'+requests.get("https://chnzyx.github.io/asu_version_latest/").text.strip()
            version_remote = info['tag_name'].strip('v').split(' ')[0]
            operation_label.config(text=f"网络异常，当前可用最高版本：{info['tag_name']}")
        except:
            operation_label.config(text=f"网络异常")
            return
    
    strInfoPath = u'\\StringFileInfo\\000004B0\\FileVersion'
    try:
        version_local = win32api.GetFileVersionInfo('gui.exe', strInfoPath)
    except:
        version_local = "0.0"
    if float(version_remote) <= float(version_local):
        operation_label.config(text="当前已是最新版本")
        return
    
    if version_local == "0.0":
        version_local = "不存在"
    global popup
    popup = tk.Toplevel(root)
    popup.title("版本信息")
    version_label = tk.Label(popup, text=f"当前版本： {version_local} 最新版本： {version_remote}")
    version_label.pack(padx=20, pady=5)
    show_popup_button = tk.Button(popup, text="更新", command=start_download)
    show_popup_button.pack(padx=20, pady=5)
    
    

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Update")
    
    # 创建操作标签
    operation_label = tk.Label(root, text="Starting...")
    operation_label.pack(pady=10)

    # 创建进度条
    progress_bar = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
    progress_bar.pack(pady=10)

    # 执行操作
    t = threading.Thread(target=main_operation)
    t.start()

    # 运行主循环
    root.mainloop()