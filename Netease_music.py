# -*- coding: utf-8 -*-
import base64
import json
import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad


class Encrypt:

    def __init__(self, word):
        self.key = "0CoJUm6Qyw8W8jud"
        self.iv = "0102030405060708"
        self.i = "eX2qyei8Ntt3qhN2"
        self.word = word
        self._data = {}

    def get_encSecKey(self):
        # 由于 i 固定了，encSecKey加密也固定
        encSecKey = "a01eac5ddb2f5bfb9eba52e2280ec1d4a5df6033500a4033f1f9bdfd47e8547481c3216fb20ab40f7ccf9bb015ddd8d32f43f3304ca330198d506fb2397d54ddcfecb49fed54b3fa24226b04a1667bf94b09a6c4a311edc207f9d90d0bd1307a6259e21dd1af16b36bffacbb0f85f0c10dde097d15ebb92f22ce0f78aa6fbb3b"
        return encSecKey

    def encrypt_params(self, word, key):
        '''
        :param word:
        传入的格式：
            播放指定ID音乐："{"ids":"[65312]","level":"standard","encodeType":"aac","csrf_token":""}"
            搜索音乐：'{"s":"遥远的她","limit":"8","csrf_token":""}'
        :param key: "0CoJUm6Qyw8W8jud"  固定不变
        :param iv: "0102030405060708" 	偏移量固定不变
        :return: 加密后的串
        '''
        key = key.encode('utf8')
        iv = self.iv.encode('utf8')
        word = word.encode('utf-8')
        #  加密串必须为16的倍数
        #  补全方案   pkcs7 补全
        pad_pkcs7 = pad(word, AES.block_size, style='pkcs7')
        mode = AES.MODE_CBC  # 加密方式 AES，CBC，对称加密
        aes = AES.new(key, mode, iv)
        res = aes.encrypt(pad_pkcs7)
        encryptd_word = str(base64.encodebytes(res), encoding="utf-8")
        encryptd_word = encryptd_word.replace('\n', '')
        return encryptd_word

    def get_params(self):
        # 两次加密
        params = self.encrypt_params(self.word, self.key)
        params = self.encrypt_params(params, self.i)
        return params

    @property
    def request_data(self):
        self._data["params"] = self.get_params()
        self._data["encSecKey"] = self.get_encSecKey()
        return self._data


class Music():

    def __init__(self):
        self.headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Referer': 'https://music.163.com/',
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
        }
        self.get_url_api = "https://music.163.com/weapi/song/enhance/player/url/v1?csrf_token="
        self.search_api = "https://music.163.com/weapi/cloudsearch/get/web?csrf_token="
        self.session = requests.session()
        self.session.headers.update(self.headers)
        self.music_dic = {}

    def get_music_url(self, api_url, data=None):
        for m_id, m_name in self.music_dic.items():
            data = '{"ids":"[%s]","level":"standard","encodeType":"aac","csrf_token":""}' % m_id
            data = Encrypt(data).request_data
            res = self.session.post(url=api_url, headers=self.headers, data=data)
            if res.status_code != 200 and res.content == "":
                continue
            else:
                try:
                    content = json.loads(res.content.decode("utf-8"))
                except Exception as e:
                    print(res.content)
                    print(e)
                self.music_dic.get(m_id)['url'] = content.get("data")[0].get("url", None)
        return self.music_dic

    def search_music(self, name):
        # s_api_url: https://music.163.com/weapi/cloudsearch/get/web?csrf_token=
        # 搜索数据格式 "{'s': '%s', 'type': 1, 'limit': 8}"
        # search_dict = "{'s': '%s', 'type': 1, 'offset': 0, 'sub': 'false', 'limit': 8}" % name
        search_dict = "{'s': '%s', 'type': 1, 'limit': 9}" % name
        # 加密 表单数据
        data = Encrypt(search_dict).request_data
        # print("data", data)

        res = self.session.post(url=self.search_api, headers=self.headers, data=data)
        content = json.loads(res.content.decode("utf-8"))
        if res.status_code != 200 and content == "":
            print("请求有错误")
            return
        # 解析数据
        temp_dic = content.get("result", None).get("songs")
        for music in temp_dic:
            m_id = music.get("id")
            m_name = music.get("name")
            star_id = music.get("ar")[0].get("id", None)
            star_name = music.get("ar")[0].get("name", None)

            temp = {"name": m_name + "-" + star_name}
            self.music_dic[m_id] = temp
        return self.get_music_url(self.get_url_api)

    def music_url(self):
        return

    def download_music(self, url):
        pass


if __name__ == '__main__':

    s = {188230:
             {'name': '遥远的她 (Live)-张学友',
              'url': 'http://m10.music.126.net/20210922191151/256aad236286839c55d0e4becc8b0ab6/yyaac/obj/wonDkMOGw6XDiTHCmMOi/3070783573/d031/0522/f2ce/2d38c663ae6d834afbaef9d57ee8e55e.m4a'},
         401722037:
             {'name': '遥远的她 (Live)-李克勤',
              'url': 'http://m801.music.126.net/20210922191151/08f94ef8351677cb09d699c5fba33771/jdyyaac/050c/0152/550c/2f0abd300b68a7db5135bfcbfa2f1194.m4a'}
         }

    for music in s.values():
        print(music.get("name"))
        print(music.get("url"))
