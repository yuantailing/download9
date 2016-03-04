import urllib.request
def getDownloadFilename(url):
    req = urllib.request.Request(url)
    req.add_header('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko')
    response = urllib.request.urlopen(req)
    dlurl = response.geturl()     # 跳转后的真实下载链接
    return dlurl, dlurl.split('/')[-1];
