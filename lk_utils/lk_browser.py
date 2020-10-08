"""
@Author  : Likianta <likianta@foxmail.com>
@Module  : lk_browser.py
@Created : 2018-00-00
@Updated : 2020-09-06
@Version : 1.7.1
@Desc    :
"""
from os.path import exists
from random import randint
from time import sleep

from requests import Response, Session

from .read_and_write import loads as loads_file


def _analyse_plain_form(form: str, sep='\n', assign=': ') -> dict:
    """
    ARGS:
        form: 纯文本表单
        sep: 分割符
        assign: 赋值符
    
    IN: form. copied from chrome browser. e.g. '''
            searchParamStr: 作者:(小明)
            classType: degree-degree_artical
            chineseEnglishExpand: false
            topicExpand: false
            singleFacetFieldFlag: false
            singleFacetField:
            singleFacetFieldLimit: 0
            corePerio: false
        '''
    OT: data (dict). e.g. {
            "searchParamStr"       : "作者:(小明)",
            "classType"            : "degree-degree_artical",
            "chineseEnglishExpand" : "false",
            "topicExpand"          : "false",
            "singleFacetFieldFlag" : "false",
            "singleFacetField"     : "",
            "singleFacetFieldLimit": "0",  # 暂不支持转为 int
            "corePerio"            : "false",
        }
    """
    # reg = re.compile(r'[^\d]+')
    data = {}
    for t in form.strip().split(sep):
        # -> ['searchParamStr: 作者:(小明)', ...]
        k, v = t.split(assign, 1)
        # -> 'searchParamStr', '作者:(小明)'
        data[k] = v.strip('"')
        # -> {"searchParamStr": "作者:(小明)", ...}
    return data


# ------------------------------------------------------------------------------

class LKBrowser:
    _url = ''  # 临时保留的请求时 url, 仅用于检查重定向
    response = None
    session: Session
    sleepy = None  # Union[None, Tuple[int, int]]
    
    def __init__(self, cookies=None, header=None, sleepy=None):
        self.session = Session()
        
        if cookies:
            self.set_cookies(cookies)
        
        self.set_header(header or {
            # updated 2019-11-08, derived from chrome
            "Accept"         : "*/*",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Connection"     : "keep-alive",
            "User-Agent"     : " ".join((
                "Mozilla/5.0 (Windows NT 10.0; WOW64)",
                "AppleWebKit/537.36 (KHTML, like Gecko)",
                "Chrome/74.0.3729.169",
                "Safari/537.36"
            )),
        })
        
        self.sleepy = sleepy
    
    # --------------------------------------------------------------------------
    # cookies
    
    @property
    def header(self):
        return self.session.headers
    
    def get_header(self):
        return self.session.headers
    
    def set_header(self, header: (str, dict)):
        if isinstance(header, str):
            if header.endswith('.txt'):
                header = _analyse_plain_form(
                    loads_file(header, -1), '\n', ': '
                )
            elif header.endswith('.json'):
                header = loads_file(header)
            else:
                raise AttributeError
            # NOTE: 去除错误的头部信息, 常见的有 Content-Length
            if 'Content-Length' in header:
                header.pop('Content-Length')
        elif not isinstance(header, dict):
            raise TypeError
        self.session.headers.update(header)
    
    @property
    def cookies(self):
        return self.session.cookies
    
    def get_cookies(self) -> dict:
        return self.session.cookies.get_dict()
    
    def set_cookies(self, cookies: (str, dict)):
        """
        IN: cookies
                str: 表示一个 cookies 文件的路径. 如果该路径以 '.txt' 结尾, 则使
                    用 cook_cookies() 方法读取; 如果是以 '.json' 结尾, 则使用
                    read_json() 方法. 最终目的是将其转化为 dict 类型.
                dict: 可直接使用.
        OT: self.session.cookies (updated)
        """
        if isinstance(cookies, str):
            if cookies.endswith('.txt'):
                cookies = _analyse_plain_form(
                    loads_file(cookies, -1), '; ', '='
                )
            elif cookies.endswith('.json'):
                cookies = loads_file(cookies)
            else:
                raise AttributeError
        elif not isinstance(cookies, dict):
            raise TypeError
        self.session.cookies.update(cookies)
    
    # ------------------------------------------------ sleeping
    
    def be_server_friendly(self, *sleepy):
        """
        sleepy: 传入睡眠范围值.
            单位是秒.
            暂不支持浮点数 (意味着最小的睡眠区间是 0 ~ 1).
            传入小于0的值, 报错;
            传入一个大于0的值, 则表示 0 ~ n 区间;
            传入两个大于0的值, 则表示 m ~ n 区间;
            传入三个及以上的值, 报错;
            不传入值, 则使用缺省值 0 ~ 3.
        注: 如果您需要睡眠毫秒级的时间, 请自己设计函数实现. LKBrowser 自带的睡眠
            相关的方法不具备此功能.
            提示:
                from random import random
                from time import sleep
                
                def _doze(m: float, n: float):
                    # e.g. m = 1.0, n = 1.5
                    sleep(round(m + random() * (n - m), 3))
        """
        if len(sleepy) == 0:  # use default value
            self.sleepy = (0, 3)
        elif len(sleepy) == 1:  # assert sleepy[0] > 0
            self.sleepy = (0, sleepy[0])
        elif len(sleepy) == 2:
            self.sleepy = sleepy
        else:
            raise Exception
    
    def _doze(self):
        if self.sleepy:
            r = randint(*self.sleepy)
            sleep(r)
    
    # --------------------------------------------------------------------------
    # requests
    
    def get(self, url, params=None, max_retry=1) -> str:
        """ request of GET method. """
        self._url = url
        self._doze()
        
        _retry_times = 0
        while _retry_times < max_retry:
            _retry_times += 1
            self.response = self.session.get(url, params=params)
            if self.response.status_code == 200:
                break
            else:
                # lk.logt('[W2912]', _retry_times, h='parent')
                continue
        
        self._check_status_code(additional_info=(url, params))
        return self.response.text
    
    def post(self, url, data, req_fmt='form-data', max_retry=1) -> str:
        """ request of POST method. """
        self._url = url
        self._doze()
        
        if req_fmt == 'form-data':
            data = {'data': data}
        else:  # fmt == 'request-payload'
            data = {'json': data}
        
        _retry_times = 0
        while _retry_times < max_retry:
            _retry_times += 1
            self.response = self.session.post(url, **data)
            if self.response.status_code == 200:
                break
            else:
                # lk.logt('[W2913]', _retry_times, h='parent')
                continue
        
        self._check_status_code(additional_info=(url, data))
        return self.response.text
    
    def postfile(self, url: str, filedata: dict, data=None) -> Response:
        """
        FIXME: maybe we should return response.text
        
        Example:
            1. smfile 图床:
                filedata = {'smfile': open('123.png', 'rb)}
                data = {'ssl': False, 'format': 'json'}
            2. chrome 浏览器:
                假设我们在某网页提交时, xhr 链接如下:
                    url: https://example.com/submit
                    method: POST
                    form (点击 view parsed 按钮):
                        authorFile: (binary)
                    form (点击 view source 按钮):
                        ------WebKitFormBoundaryXt7PiZRFs1qj9b46
                        Content-Disposition: form-data; name="authorFile";
                        filename="test.json"
                        Content-Type: application/json
                        
                        
                        ------WebKitFormBoundaryXt7PiZRFs1qj9b46--
                那么这样使用 postfile:
                    browser.postfile(
                        'https://example.com/submit',
                        {'authorFile': open('test.json', 'rb')}
                    )
        参考:
            [崔庆才] Python 3 网络爬虫开发实战.pdf - p142
            https://blog.csdn.net/qq_32502511/article/details/80924090
        """
        self._url = url
        self.response = self.session.post(url, files=filedata, data=data)
        self._check_status_code(additional_info=(url, data))
        return self.response
    
    def download(self, url, ofile):
        """
        注: 此方法不检查下载文件的编码格式, 适用于下载图片, 音频, 视频, 资源文件
            类数据. 如需下载离线网页, 请改用 self.save_page().
        参考:
            python 爬虫 requests 下载图片 - 稀里糊涂林老冷 - 博客园
            https://www.cnblogs.com/Lin-Yi/p/7640155.html
        """
        self._url = url
        self.response = self.session.get(url)
        with open(ofile, 'wb') as f:
            f.write(self.response.content)
    
    def save_page(self, url, ofile, jump_exists=False,
                  source_encoding=None, target_encoding='utf-8'):
        """
        这是 self.download() 方法的特化版, 专门用于下载并调节下载文件的格式以
            utf-8 (默认) 保存.
        ARGS:
            url: 要请求的网页 (只支持 GET 请求)
            ofile: 生成文件
            jump_exists: 如果目标文件已存在, 是否覆盖
            source_encoding (None|str): 源网页编码, None 表示自动检测; str 表示
                强制指定. str 不区分大小写
            target_encoding (str): 目标网页编码, 默认是 'utf-8', 您也可以自己指
                定. 不区分大小写
        """
        if jump_exists and exists(ofile):
            return
        
        self._url = url
        self.response = self.session.get(url)
        
        if source_encoding is None:
            if ofile.endswith((  # 常见的二进制文件
                    '.exe', '.flv', '.ico', '.jpeg', '.jpg', '.mp3', '.mp4',
                    '.mpeg', '.pdf', '.png', '.rar', '.xls', '.xlsx', '.zip'
            )):
                source_encoding = None
            else:
                """ 注意: 本方法对获取编码的方法进行了调整:
                1. 优先使用 chardet 预测的 encoding, 其次是 http headers 提供的
                   encoding 信息. 这样做的原因在于, 经发现国内的一些网站的 http
                   headers 提供的是错误的 encoding. 比如 http://www.most.gov.cn/
                   cxfw/kjjlcx/kjjl2000/200802/t20080214_59023.htm, 明明含有中
                   文, 但却提供了纯西文字符的 "ISO-8859-1" 编码集, 如果按照 "ISO
                   -8859-1" 来解码, 会出现乱码. 而用 chardet 预测的编码 (GB2312)
                   来解码则不会出现乱码
                2. 若 chardet 预测编码为 GB2312, 则使用 GBK 代替. 因为 GBK 是
                   GB2312 的超集, 且国内网站以 GBK 编码的要远多于 GB2312, 使用
                   GBK 替代不会有任何副作用, 相反能避免部分中字符无法解析的情况
                   (参考: http://ioqq.com/python-chardet-gbk%E8%BD%ACutf8-%E4
                   %B8%AD%E6%96%87%E4%B9%B1%E7%A0%81.html)
                """
                source_encoding = self.response.apparent_encoding \
                                  or self.response.encoding
        
        if source_encoding is None:
            # 出现这种情况, 说明网页没有给出编码信息, chardet 也无法预测. 通常意
            # 味着此文件是 pdf, jpg, png 等类型的文件. 那么我们采用二进制写入.
            with open(ofile, 'wb') as f:
                f.write(self.response.content)
        else:
            if source_encoding == 'GB2312':
                source_encoding = 'GBK'
            content = self.response.content.decode(
                source_encoding, errors='ignore'
            )
            with open(ofile, 'w', encoding=target_encoding) as f:
                f.write(content)
    
    # --------------------------------------------------------------------------
    # inner methods
    
    def _check_status_code(self, additional_info=None):
        """
        some serious status code:
            403 permission denied
            429 too frequent requests
        """
        status_code = self.response.status_code
        
        if status_code == 200:
            return
        
        # the following case is assert status_code != 200
        
        info = {
            'error_msg'  : '',
            'status_code': status_code,
            'url'        : self.response.url,
            'redirected' : self.response.is_redirect,
            'extra'      : additional_info
        }
        
        if status_code >= 400:
            if status_code == 403:
                info['error_msg'] = 'permission denied (forbidden)'
            elif status_code == 429:
                info['error_msg'] = 'too frequent requests'
            else:
                info['error_msg'] = 'error 400+'
            raise CriticalException(info)
        else:
            info['error_msg'] = 'unexpected status code'
            raise Exception(info)
    
    # --------------------------------------------------------------------------
    # status
    
    @property
    def status_code(self) -> int:
        return self.response.status_code
    
    @property
    def is_redirect(self) -> bool:
        if self.response.is_redirect:
            return True
        if self.response.is_permanent_redirect:
            return True
        if self._url == '':
            raise Exception
        if self.response.url != self._url:
            return True
        else:
            return False


class CriticalException(Exception):
    pass


browser = LKBrowser()
