# 雨课堂代码开发过程中遇到的问题

- 其他学校的记得修改相关关键词
- 1. `https://bksycsu.yuketang.cn/` 中的`bksycsu`
- 2. `university_id` 改成自己学校的

1. university_id 有要求  中南大学为:2952
2. header里加上 `'referer': 'https://bksycsu.yuketang.cn/'` 因为他会检测发出源
3. [通过这个链接获得`userid`](https://bksycsu.yuketang.cn/edu_admin/check_user_session/)


4. 遇见了以下unicode代码，输出时候出现了乱码
    ``` json
    \u5927\u5b66\u751f\u5fc3\u7406\u5065\u5eb7\u6559\u80b2
    ```
    通过以下方法解决
    
    1. 右键`我的电脑`，点`属性`，`高级系统设置`，`环境变量`
    2. `新建`一个变量名称，变量名`PYTHONIOENCODING`，值设置为`UTF8`
    3. 重启VScode可以解决
