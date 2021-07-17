import asyncio
import aiohttp
import aiofiles
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
                    if res.status_code == 200:
                        self.key_value = res.content
                    print('key',self.key_value)
                if ".ts" in line:
                    self.ts_list.append(line)
            return self.base_url, self.ts_list, self.key_value
            # self.get_ts_file(ts_list)

    def decryptAES(self, key_value):
        # 创建加解密对象
        return AES.new(key_value, AES.MODE_CBC, key_value)

    # 下载ts文件
    async def sync_down(self, day_path, base_url, name, cryptor=None):
        try:
            async with self.semaphore: # 并发限制
                async with aiohttp.ClientSession() as session:
                    print('下载',f"{base_url}/{name}")
                    async with session.get(f"{base_url}/{name}") as response:
                        # 普通方式打开文件
                        # with open(name,mode='wb') as f:
                        #     f.write(await response.read())
                        # 携程方式打开文件
                        async with aiofiles.open(os.path.join(day_path, name), 'wb') as f:
                            # 一次读取数据,写入文件,数据会加载在内存中
                            if cryptor:  # 判断是否有加密,
                                await f.write(cryptor.decrypt(await response.read()))
                            else:
                                await f.write(await response.read())

                            # while True:
                            #     # 流式传输到文件中的内容,大文件时用
                            #     chunk = await response.content.read(1024)
                            #     if not chunk:
                            #         break
                            #     await f.write(chunk)
                    print(f"{name}下载完成")
        except Exception as E:
            print("error: ", E)

    def run(self):
        self.get_index_m3u8()
        cryptor = None
        if self.key_value:
            cryptor = self.decryptAES(self.key_value)
        # 不然将报错：ValueError: too many file descriptors in select()
        self.semaphore = asyncio.Semaphore(100)  # 限制并发量为500,这里windows需要进行并发限制，
        loop = asyncio.get_event_loop()
        tasks = [self.sync_down(self.save_path,self.base_url,i,cryptor) for i in self.ts_list]
        loop.run_until_complete(asyncio.wait(tasks))


    # 合并文件,指定目录
    def merge_file(self):
        os.chdir(self.save_path)
        print(self.save_path)
        print(os.getcwd())
        os.system("copy /b * new.mp4")
        os.system('del /Q *.ts')
        # os.system('del /Q *.mp4')
        # os.rename("new.tmp", "new.mp4")



if __name__ == '__main__':
        base_dir = r'D:\baidudownload'

        url = 'https://www.ziboshishen.com/20191216/FkJYnXLV/index.m3u8'
        url33 = 'http://mudan.iii-kuyunzy.com/20191217/5961_270bf954/1000k/hls/index.m3u8'
        day_path = input('这个多少集:')
        save_path = os.path.join(base_dir,day_path)
        if not os.path.isdir(save_path): os.mkdir(save_path)


        m = M3u8(url,save_path)
        m.run()
        # 合并文件
        # m.merge_file()





