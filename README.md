# douban_book
获取douban（老）中，某个分类下的书目信息，结果如下： 

  ![image](https://github.com/vermouth1994/douban_book/blob/master/images/redis.png)
  ![image](https://github.com/vermouth1994/douban_book/blob/master/images/content.png)

  次数超过限制，则只返回图书id，再通过豆瓣api2.0中图书接口获取,拼接url为：https://api.douban.com/v2/book/3421275

  官方api2.0接口只能获取200条，当前使用为老版豆瓣的url,可以最大数量获取书目列表，每次请求后随机１－５ｓ暂停,只用了一次，写的很粗糙
