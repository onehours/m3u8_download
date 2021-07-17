
# key的长度必须是16的倍数
key = 'Z3Ms6OQG0XBqtfrd'
from Crypto.Cipher import AES

cryptor = AES.new(key.encode('utf-8'), AES.MODE_CBC,key.encode('utf-8'))
print(len(key))

# res = cryptor.encrypt('dasfsfew2333333f'.encode('utf-8'))
# print(res)

# 加密过的数据
rs = b'G\x80\xd9 l\xe2\xc4\x18\x9bn\xa5.xo{Y'
print(cryptor.decrypt(rs))  # 解密
