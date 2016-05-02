# -*- coding: utf-8 -*-
import LoginZhihu
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
import csv

#getUrl方法根据用户输入的答案编号生成点赞用户页面的url，编号目前只能通过chrome或者Fiddler抓包获得
#因为这个编号和每个回答本身的编号不同，我还没找到规律，所以只能让用户手动抓包后续希望能找到方法改进
def getUrl():
    id = input("请输入要查询的问题编号：")
    url = "https://www.zhihu.com/answer/"+id+"/voters_profile"
    return url

#获得点赞者的昵称，为了方便循环输出，利用generator
def getname(soup):
    res  = soup.findAll('a',{"class":"zm-item-link-avatar"})
    res1 = soup.findAll('img',{"class":"zm-item-img-avatar"})
    for x in res:
        #print("知乎昵称:",x["title"])
        yield(x["title"])

    for x in res1:
        try:
            yield(x["title"])
        except:
            continue
    return 'done'

#获得点赞者的ID
def getid(soup):
    res  = soup.findAll('a',{"class":"zm-item-link-avatar"})
    for x in res:
        #print("知乎id:",x["href"][8:])
        yield x["href"][8:]
    return 'done'

#获得点赞者自己的总点赞数和感谢数
def getvoteup(soup):
    res  = soup.findAll('ul',{"class":"status"})
    for x in res:
        voteup=x.findAll("li")[0].find("span").get_text()
        thanks = x.findAll("li")[1].find("span").get_text()
        #知乎对于赞同数和感谢数较多的数量表示方法是以K为单位，为了输出int类型的结果便于后续数据整理
        #需要在这里事先进行处理，为了简单起见，我们就直接把K替换为三个零
        if(voteup[-4] == "K"):
            voteup = voteup.replace("K","000")
        if(thanks[-4] == "K"):
            thanks = thanks.replace("K","000")
        voteup = int(voteup[:len(voteup)-3])
        thanks = int(thanks[:len(thanks)-3])

        #print("赞同数:",voteup," 感谢数:",thanks)
        yield voteup,thanks
    return 'none'

#获得下一页的偏移地址，因为点赞页面每次只能显示10个点赞者，如果要翻页则需要手动在url里面添加offset参数，每次增长10个
#getoffset方法输入总点赞人数和偏移量来生成偏移url
def getoffset(total,offset):
    return r"?total="+str(total)+"&offset="+str(offset)

#用来将点赞者的姓名，ID，被点赞数和被感谢数写入csvFile对应的csv文件中
def write2csv(name,id,vote,thanks,csvFile):
    #注意，这里为了避免csvwriter输出的csv文件每两个数据之间都有空行，需要按照下面的写法进行
    #大致的原因是writer以Windows风格的行分隔符\r\n作为每行的分割，而不是Unix下的\n
    writer = csv.writer(csvFile,delimiter=',', lineterminator='\n')
    writer.writerow((name,id,vote,thanks))

#主程序
def start():
    if LoginZhihu.isLogin():
        print('您已经登录')
    else:
        account = input('请输入你的用户名\n>  ')
        secret = input("请输入你的密码\n>  ")
        LoginZhihu.login(secret, account)

    session = LoginZhihu.session
    headers = LoginZhihu.headers


    #index_url = 'https://www.zhihu.com/answer/4803587/voters_profile'
    index_url = getUrl()
    #index_url = 'https://www.zhihu.com/answer/34744961/voters_profile'

    try:
        data = session.get(index_url,headers = headers)
    except:
        print("Network Error!")


    data =data.content
    #这里是属于一个很奇怪的问题，用unicode-escape来进行decode能强制转义
    #是一个很烦人的问题，只在知乎的这个点赞用户对应的页面上出现过，所以只要记住这个解决方法就好
    data = data.decode('unicode-escape')
    data = data.replace("\/","/")

    #经常由于网络不稳定导致读取失败，所以每次都判断一下是不是读取成功了，如果没有，那么就再读一遍，直到成功为止
    while(len(data) == 0):
        try:
            data = session.get(index_url,headers = headers)
            data = data.content.decode('unicode-escape')
            data = data.replace("\/","/")
        except:
            print("Network Error!")

    soup = BeautifulSoup(data,"html.parser")

    #在页面上找到总的点赞数
    regex = re.compile("paging\": {\"total\": ([0-9]+)")
    num_voteup = int(re.findall(regex,data)[0])
    print(num_voteup)

    loop_time = num_voteup // 10+1
    offset = 0
    csvFile = open("./test.csv",'w+',newline=None)

    while loop_time > 0:
        suffix = getoffset(num_voteup,offset)
        url = index_url + suffix
        content = session.get(url,headers = headers)
        content = content.content.decode("unicode-escape").replace("\/","/")
        while(len(content) == 0):
            content = session.get(url,headers = headers)
            content = content.content.decode("unicode-escape").replace("\/","/")
        soup = BeautifulSoup(content,"html.parser")

        #获得生成器
        get_name = getname(soup)
        get_id = getid(soup)
        get_voteup = getvoteup(soup)

        while True:
            try:
                name = next(get_name)
                if name == "匿名用户":
                    #print(name)
                    continue
                id = next(get_id)
                voteup = next(get_voteup)
                write2csv(name,id,voteup[0],voteup[1],csvFile)
                #print("昵称：", name,"  ID：",id,"  赞同数：",voteup[0],"  感谢数：",voteup[1])
            except StopIteration as e:
                #print(e)
                break
        offset += 10
        loop_time -= 1
        #print(loop_time)
        rate = offset * 100 // num_voteup
        #输出进度百分比
        print("进度：%s%s"%(str(rate),"%"),end='\r')
    csvFile.close()

if __name__ == "__main__":
    start()
    print('输出结束')