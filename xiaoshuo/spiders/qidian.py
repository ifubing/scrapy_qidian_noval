# -*- coding: utf-8 -*-
import scrapy


class QidianSpider(scrapy.Spider):
    name = 'qidian'
    allowed_domains = ['www.qidian.com']
    start_urls = ['http://www.qidian.com/']
    base_url = "https://www.qidian.com"

    def parse(self, response):
        print('>>>>>>>>>>>>>>>>')
        # 获取分类盒子
        dd_list = response.xpath("//div[@id='classify-list']//dd")

        for dd in dd_list:
            print(dd)
            big_type_dict = self.get_big_type(dd)
            if big_type_dict['type1_name'] == "女生网":
                continue
            print(big_type_dict)
            # 代码到这里，就都是有用的代码
            print('>>>>>>>>>>>>>>>>>>>')
            yield scrapy.Request(big_type_dict['type1_url'],
                                 callback=self.parse_type1,
                                 meta={"book_info": big_type_dict}
                                 )

    def parse_type1(self, response):
        """
        解析大分类页面的方法
        :param response: 大分类页面的响应
        https://www.qidian.com/xuanhuan
        :return:
        """
        # print(response.meta)
        big_type_dict = response.meta['book_info']
        print(big_type_dict)
        print('!!!!!!!!!!!!!!!!')
        print(response.url)

        # 获取二级分类的容器盒子 a标签
        a_list = response.xpath("//div[@class='sub-type-wrap']/div/a")
        # 从a标签中提取内容
        for a in a_list:
            small_type_dict = self.get_small_type(a)
            # 把名称中带有排行的数据过滤掉
            if '排行' in small_type_dict['type2_name']:
                continue
            print(small_type_dict)
            book_info_dict = {}
            book_info_dict.update(big_type_dict)
            book_info_dict.update(small_type_dict)
            print(book_info_dict)
            yield scrapy.Request(
                book_info_dict['type2_url'],
                callback=self.parse_noval_list,
                meta={'book_info': book_info_dict}
            )
            print('@@@@@@@@@@@@@@@@@@@@')

    def parse_noval_list(self, response):
        """
        小分类列表解函方法
        :param response:
        :return:
        """
        # 获取所有的li容器
        li_list = response.xpath("//ul[@class='all-img-list cf']/li")
        # 依次提取内容
        for li in li_list:
            noval_dict = self.get_noval_list(li)
            print(noval_dict)
            print('^^^^^^^^^^^^^^^^^^^^^^^^')
            book_info = dict()
            print('$$$$$$$$$$$$$$$$')
            print(response.meta)
            print('$$$$$$$$$$$$$$$$')
            book_info.update(response.meta['book_info'])
            book_info.update(noval_dict)
            print(book_info)
            yield book_info

        # 翻下一页的操作
        # javascript:;
        next_url = response.xpath("//li[@class='lbf-pagination-item'][last()]/a/@href").get()
        if next_url != "javascript:;":
            next_url = "https:" + response.xpath("//li[@class='lbf-pagination-item'][last()]/a/@href").get()
            print('下一页&&&&&&&&&&&&&&&&&&&&&&&&')
            print(next_url)
            yield scrapy.Request(next_url, callback=self.parse_noval_list, meta={'book_info': response.meta['book_info']})

    def get_noval_list(self, li):
        """
        从li对象中提取小说的数据
        :param li:
        :return noval_dict:
        {'book_img': '//bookcover.yuewen.com/qdbimg/349573/1016296064/150', 'book_title': '第一宗师', 'book_url': 'https://book.qidian.com/info/1016296064', 'book_author': '零度流浪', 'book_desc': '\r                        灵力复苏，魔窟入侵。林小度嘶声呐喊：为守护而战，为光明而战。这是一个小人物身怀大情怀，逐渐蜕变成一个大人物的故事。\r                    '}

        """
        # 图片地址
        book_img = "http:" + li.xpath(".//div[@class='book-img-box']//img/@src").get()
        # 书名称
        book_title = li.xpath("./div[last()]/h4/a/text()").get()
        # 链接
        book_url = "https:" + li.xpath("./div[last()]/h4/a/@href").get()
        # 作者
        book_author = li.xpath("./div[last()]/p/a[1]/text()").get()
        # 简介
        book_desc = li.xpath("./div[last()]/p[2]/text()").get().strip()
        # 构建返回的数据
        noval_dict = {
            'book_img': book_img,
            'book_title': book_title,
            'book_url': book_url,
            'book_author': book_author,
            'book_desc': book_desc
        }
        return noval_dict

    def get_small_type(self, a):
        """
        获取小分类的数据
        :param a:
        :return small_type_dict:
        {'type2_name': '异世大陆', 'type2_url': 'https://www.qidian.com/all?chanId=21&subCateId=73'}

        """
        small_type_dict = dict()
        name = a.xpath("./text()").get()
        url = a.xpath("./@href").get()
        small_type_dict['type2_name'] = name
        small_type_dict['type2_url'] = "https:" + url
        return small_type_dict

    def get_big_type(self, dd):
        """
        获取大分类的数据
        :return big_type_dict: 大分类字典
        {'type1_name': '科幻', 'type1_url': 'https://www.qidian.com/kehuan'}
        """
        big_type_dict = {}

        name = dd.xpath(".//i/text()").get()
        url = dd.xpath("./a/@href").get()
        big_type_dict["type1_name"] = name
        big_type_dict["type1_url"] = self.base_url + url
        return big_type_dict
