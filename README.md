# ReadZhihu
A practice project of read all the people who vote up a Zhihu's answer

##本程序适用于知乎网站
* 通过使用者提供的答案编号，能够爬取所有对该答案点赞的用户的昵称，ID，点赞数，感谢数

* 答案编号目前还需要使用者自己通过抓包进行获取
* 方法：在答案界面按F12打开chrome浏览器内嵌的开发工具，点击上方的Network。之后点击知乎答案点赞者名单后面的“等人赞同”链
接，使得赞同名单跳出。之后在开发工具中选择name为voters_profile的一项连接，在request url中获取类似于 "https://www.zhihu.com/answer/xxxxxxxxx/voters_profile"  这样的url地址
xxxxxxxxx就是答案的编号，按照要求输入到程序中即可
该功能用户不友好，待改进
