# yuketang

# 雨课堂网课视频脚本代码

## 上课看视频用的是 `https://school-id.yuketang.cn/`这些带学校id的网址，千万别用`https://www.yuketang.cn/`

#
1. 运行程序(也可通过Release中下载运行)
``` python
python .\yuke.py
```
2. 需要提供一个`url`链接以及`cookie`
   - 在网页登录后，随便打开一个视频，复制此时的网页`url`链接如`https://bksycsu.yuketang.cn/pro/***/7g****4s/1*****8/video/2******7`
   - 获得`url`链接
   - 如何获取`cookie`
     1. 在视频播放页面按下`F12`,选择`打开开发者工具`
     2. 在开发者工具最上一栏选择`网络`
     3. 等待一会，下方出现一个`heartbeat/`的文件
     4. `点击`后查找`请求标头`中的`cookie`，如
     ``` 
        cookie: csrftoken=y3O***************gl; sessionid=6****************icn; university_id=****; platform_id=3; user_role=3;JG_d65****************c1_PV=165***************4
     ```
    - `右键`选择`复制值`得到`cookie`

3. 课程观看完毕后程序会自动消失

# 
# 切记本项目仅供学习参考，本人对使用本工具造成的一切后果不负责任

# 写在最后
1. 感谢华南理工的老哥[@heyBlackC](https://github.com/heyblackC)提供的[基本方案](https://github.com/heyblackC/yuketangHelper)，为我省下了很多功夫
2. 我只是对代码进行了一次调整并对其易用性进行了改进，增加了一点注释(？
   
    ~~3. 其实有想法，要不要改成多线程开刷，一次性进行多个并发观看，大幅度提升效率。不过算了，因为已经够快的了~~
3. 一个课程一个线程，里面每个视频再加一个线程，加速！加速！
4. 还有个问题就是，老哥哪里找来的API，我都找不到


