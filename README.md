# 使用Selenium爬取淘宝网想要搜索的商品信息

**本项目借鉴以下两位前辈的博文，特此感谢！**

- [[python3网络爬虫开发实战]7.4-使用Selenium爬取淘宝商品](https://cuiqingcai.com/5657.html)
- [scrapy+selenium爬取淘宝商品信息](https://www.cnblogs.com/triangle959/p/12024362.html)

## 需求分析

爬取[淘宝网](https://www.taobao.com)中想要搜索的商品信息, 并将爬取的数据保存到MongoDB数据库中。

## 项目总览

1. 利用Selenium驱动Chrome浏览器模拟打开[淘宝网登录界面](https://login.taobao.com/member/login.jhtml)，利用微博账号登录[淘宝网](https://www.taobao.com)
2. 模拟搜索关键字，得到查询后的商品列表。
3. 分析商品页码总数，模拟翻页，得到后续页面的商品列表
4. 利用PyQuery分析源码，解析得到每页列出商品的具体信息
5. 将爬取的商品列表信息存储至MongoDB数据库中

## 遇到的问题

1. 之所以选择先登录账号再进行搜索是因为如果在[淘宝网](https://www.taobao.com)直接搜索关键字搜索的话还是会弹出登录界面，所以索性先登录了，也可以在输入关键字之后做一下跳转判断，看是跳转到登录界面还是商品列表界面。
2. 爬取的少部分商品的image url会变成“'image': '//g.alicdn.com/s.gif'”， 不知为什么…可能是爬取过快网页未加载完全…
3. Selenium模拟出的页面源码与正常用Chrome浏览器打开的源码有一点不一样，有的地方用CSS Selector选不到，希望大神能给予一些解答~
4. 每次商品列表页面翻页之后要主动等待一段时间，如果不设置等待时间会报错并中断，不知道是不是因为淘宝的反爬机制，希望大神能给予解答~

## 文件列表

config.py: 配置MongoDB数据库，微博账号信息，要搜索的KEYWORD，chromedriver的本地位置

taobao_spider: 爬取文件，直接运行即可