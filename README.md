# QMT chanlun 回测系统
    ##一、功能介绍：
        1.主要分析缠论中的顶、底、笔、线段、中枢、背驰、三类买点、三类卖点、macd, web可视化
        2.后续会在此基础上增加静态缠论选股、盘中动态分时选股、买入、卖出、持仓策略、调试信息、数据库等
![Snipaste_2025-05-24_04-25-16](https://github.com/user-attachments/assets/eef2d3b9-5832-4ba7-8fad-ac85a13c509a)


    ##二、环境搭建
        1.环境主要是在电脑本地进行开发，交易软件为QMT(相对于鼠标模拟点击更稳定)

        ### 安装python
        项目开发使用的是python 3.8运行程序
        ~~~
        （1）在官网 https://www.python.org/downloads/ 下载安装包，一键安装即可，安装切记勾选自动设置环境变量。
        （2）配置永久全局国内镜像库（因为有墙，无法正常安装库文件），执行如下dos命令：
            python pip config --global set  global.index-url https://mirrors.aliyun.com/pypi/simple/
            # 如果你只想为当前用户设置，你也可以去掉下面的"--global"选项
        ~~~

        ### 安装[pycharm](https://blog.csdn.net/zhang120529/article/details/147020818)教程网上很详细不赘述
        ~~~
        编辑代码的工具
        ~~~


        ###安装依赖库
        ~~~
        切换到本系统的根目录，执行下面命令：
        python pip install -r requirements.txt 
        ~~~

        ###主代码如下图
        
![Snipaste_2025-05-24_04-25-17](https://github.com/user-attachments/assets/71043e24-1025-40e2-8abe-4f16b2d638e2)

