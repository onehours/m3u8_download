from concurrent.futures import ThreadPoolExecutor,as_completed
import requests
import os
from Crypto.Cipher import AES

"""
下载主文件
分析得到解密key
得到ts文件
下载文件
pip install Crypto 
解密后保存
合并文件成mp4
"""

class M3u8():
    def __init__(self,url,save_path):
        self.url = url
        self.save_path = save_path

    def get_index_m3u8(self):
        # 得到url目录
        self.base_url = self.url.rsplit('/', 1)[0]
        print('获得m3u8文件')
        indexfile = requests.get(self.url).text
        # 判断是否加密
        self.key_value = False
        self.ts_list = []
        print('判断是否是m3u8文件')
        if "#EXTM3U" in indexfile:
            content = indexfile.split('\n')  # 分割文件,
            print('遍历文件,获得key和ts列表')
            for line in content:
                if "EXT-X-KEY" in line:
                    print('取出密钥')
                    keyname = line.rsplit("=")[-1].replace('"', "")
                    res = requests.get(url=f"{self.base_url}/{keyname}")
                    print(res.status_code)
                    if res.status_code == 200:
                        self.key_value = res.content
                if ".ts" in line:  # ts文件 存放到列表中
                    self.ts_list.append(line)
            return self.base_url, self.ts_list, self.key_value
            # self.get_ts_file(ts_list)

    def decryptAES(self, key_value):
        # 创建加解密对象
        return AES.new(key_value, AES.MODE_CBC, key_value)


    def down(self, day_path, base_url, name, cryptor=None):
        with open(os.path.join(day_path, name), mode='wb') as f:
            print('下载开始', f"{base_url}/{name}")
            content = requests.get(url=f"{base_url}/{name}").content
            if cryptor:  # 判断是否有加密,
                f.write(cryptor.decrypt(content))
            else:
                f.write(content)
        return f'下载完成{name}'

    def run(self):
        self.get_index_m3u8()
        cryptor = None
        if self.key_value:
            cryptor = self.decryptAES(self.key_value)


        # 单独的submit 是非阻塞的,可以配合# result方法(阻塞获取)可以获取task的执行结果
        with ThreadPoolExecutor(20) as p:
            all_tasks = [p.submit(self.down, self.save_path, self.base_url, i, cryptor) for i in self.ts_list]

            # 非阻塞运行1,有序阻塞读取返回结果
            # for future in all_tasks:
            #     print(future.result())

            # 非阻塞运行2,无序阻塞读取返回结果,先完成的任务会先通知主线程
            # as_completed()方法是一个生成器，在没有任务完成的时候，会阻塞，
            # 在有某个任务完成的时候，会yield这个任务，就能执行for循环下面的语句，然后继续阻塞住，循环到所有的任务结束。从结果也可以看出，先完成的任务会先通知主线程。
            for future in as_completed(all_tasks):
                print(future.result())  # 打印返回结果


    # 合并文件,指定目录
    def merge_file(self):
        os.chdir(self.save_path)
        print(os.listdir(self.save_path))
        os.system("copy /b * new.mp4")
        os.system('del /Q *.ts')

if __name__ == '__main__':
        base_dir = r'D:\baidudownload'

        url = 'https://play.yljiankang365.com/upload/2019-12-25/253473434447a9c0d08728c07a476863/m3u8/index.m3u8'
        url33 = 'http://mudan.iii-kuyunzy.com/20191217/5961_270bf954/1000k/hls/index.m3u8'
        day_path = input('这个多少集:')
        save_path = os.path.join(base_dir,day_path)
        if not os.path.isdir(save_path): os.mkdir(save_path)

        m = M3u8(url,save_path)
        m.run()
        # 合并文件
        m.merge_file()

