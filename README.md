# TrWebOCR-开源的离线OCR  

## 用于 ∞-type Café 暑期学校的会议室聊天记录识别
> 本项目只做了一层wrapper，用于支持批量对图片进行OCR，目前并未修改 [TrWebOCR](https://github.com/alisen39/TrWebOCR) 的源码。

## 介绍
TrWebOCR，基于开源项目 [Tr](https://github.com/myhub/tr) 构建。  
在其基础上提供了http调用的接口，便于你在其他的项目中调用。  
并且提供了易于使用的web页面，便于调试或日常使用。   

## 构建与运行

基于Python 3.6+， 经测试支持在以下平台运行:
- Ubuntu 16.04
- Ubuntu 18.04
- CentOS 7

或基于Docker:

使用 Dockerfile 构建 或者直接 Pull镜像  

- docker build
```shell script
docker build -t trwebocr:latest .
docker run -itd --rm -p 8089:8089 --name trwebocr trwebocr:latest 
```  

- docker pull
```shell script
docker pull mmmz/trwebocr:latest
docker run -itd --rm -p 8089:8089 --name trwebocr mmmz/trwebocr:latest 
``` 

## 文档
[接口文档](https://github.com/alisen39/TrWebOCR/wiki/%E6%8E%A5%E5%8F%A3%E6%96%87%E6%A1%A3)    

### 调用示例
这里以python为例：

``` python
import requests
url = 'http://localhost:8089/api/tr-run/'
img1_file = { 'file': open('img1.png', 'rb') }

res = requests.post(url=url, data={'compress': 1600}, files=img1_file)
```

- 也可使用Base64  
``` python
import requests
import base64

def img_to_base64(img_path):
    with open(img_path, 'rb')as read:
        b64 = base64.b64encode(read.read())
    return b64
    
url = 'http://localhost:8089/api/tr-run/'
img_b64 = img_to_base64('./img1.png')
res = requests.post(url=url, data={'img': img_b64, 'compress': 1600})
```
经过测试，`compress`的值最好设置为1600，否则可能出现无`raw_out`的问题

## 鸣谢
- [alisen39](https://github.com/alisen39) 和他的开源项目 [TrWebOCR](https://github.com/alisen39/TrWebOCR)
- [myhub](https://github.com/myhub) 和它的开源项目 [Tr](https://github.com/myhub/tr)

## License
[Apache 2.0](./LICENSE.txt)