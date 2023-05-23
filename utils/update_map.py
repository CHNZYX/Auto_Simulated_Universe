import os
import shutil
import requests
import zipfile

root_path = os.getcwd()


def download_and_extract_zip(url, root_path):
    response = requests.get(url)
    zip_file_path = os.path.join(root_path, 'repository.zip')
    with open(zip_file_path, 'wb') as file:
        file.write(response.content)

    # 解压ZIP文件
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(root_path)

    os.remove(zip_file_path)  # 删除ZIP文件


def sync_github_repo(repo_url, root_path):
    # 构建API URL
    api_url = f"https://api.github.com/repos/{repo_url}/zipball/main"

    # 检查保存路径是否存在，如果不存在则创建
    os.makedirs(root_path, exist_ok=True)

    # 下载并解压ZIP文件
    download_and_extract_zip(api_url, root_path)


def get_latest_branch_sha(repo_url):
    url = f"https://api.github.com/repos/{repo_url}/branches"
    headers = {
        "Accept": "application/vnd.github.v3+json"
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        branches = response.json()
        if branches:
            latest_branch = branches[0]
            return latest_branch['commit']['sha']
    else:
        print("Failed to fetch branch information.")


def get_local_sha():
    # 读取
    with open(root_path + '//info.txt', 'r') as file:
        lines = file.readlines()
    # 判断是否有sha信息,没有则填补空行
    if len(lines) < 4:
        lines.extend(['\n'] * (4 - len(lines)))
        with open('../info.txt', 'w') as file:
            file.writelines(lines)
    return lines[3].strip()


def set_local_sha(sha):
    # 读取
    with open(root_path + '//info.txt', 'r') as file:
        lines = file.readlines()
    # 判断是否有sha信息,没有则填补空行
    if len(lines) < 4:
        lines.extend(['\n'] * (4 - len(lines)))
        with open(root_path + '//info.txt', 'w') as file:
            file.writelines(lines)
    lines[3] = sha + '\n'
    with open(root_path + '//info.txt', 'w') as file:
        file.writelines(lines)


def update_map():
    repo_url = 'CHNZYX/maps'
    # 获取远端sha
    remote_sha = get_latest_branch_sha(repo_url)
    print("远端sha: " + remote_sha)
    # 获取本地sha
    local_sha = get_local_sha()
    print("本地sha: " + local_sha)
    # 判断是否需要更新
    if remote_sha == local_sha:
        print("map无需更新")
        return
    map_path = root_path + '\\imgs\\maps'
    # 下载map仓库并解压
    sync_github_repo(repo_url, root_path)
    print("下载完成")
    # 找出下载的map文件夹
    chn_folders = [item for item in os.listdir(root_path) if os.path.isdir(item) and item.startswith("CHNZYX-maps")]
    downloaded_map_path = root_path + '\\' + chn_folders[0] + '\\maps'
    # 删除原有map文件夹，复制新的map文件夹
    shutil.rmtree(map_path)
    shutil.copytree(downloaded_map_path, map_path)
    shutil.rmtree(root_path + '\\' + chn_folders[0])
    print("更新完成")
    # 更新sha
    set_local_sha(remote_sha)

# 测试用
if __name__ == '__main__':
    root_path = os.getcwd()[:-5]
    update_map()
