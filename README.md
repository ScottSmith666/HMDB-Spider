# HMDB Spider

### ！！使用本程序前请仔细阅读

### HMDB Spider是专门用于爬取Human Metabolome Database（HMDB）中代谢物信息的程序，非常简单易用。不仅如此，本程序还非常贴心地将爬取的信息翻译成中文，有效缓解了非英语母语人士的痛苦。
![](https://github.com/ScottSmith666/HMDB-Spider/blob/master/imgs/hmdb.png)
### 以下是本程序的用法：

## 1. 下载本程序
鼠标点击右边“code”绿色按钮，展开菜单栏，点击“Download zip”下载压缩包，在你的PC上解压缩。
![image](https://github.com/user-attachments/assets/5649e1e2-0cfc-4153-8d68-80d6ff656834)

或者在终端用命令`git clone https://github.com/ScottSmith666/HMDB-Spider.git`直接克隆至你的PC上也可。

## 2. 安装Python
Python的安装方法网上一堆，可以自行去互联网上检索。Python版本大致在3.10至3.12即可，本人设备上的Python版本是3.12。

## 3. 安装本程序用到的依赖
这里仅演示针对Windows 11系统的方法，Linux用户和Mac用户视为默认掌握一定计算机技巧的人士，这里不再演示Linux和macOS上的安装方法。

进入本程序项目的根目录，能看到这些文件：
![image](https://github.com/user-attachments/assets/bd650ab8-bf25-4be8-b2b0-8f20b8ad7097)

在空白处右键，选择“在终端中打开”。
![image](https://github.com/user-attachments/assets/e8eba5f9-0e47-4d73-b70d-14bb284f5922)

### 这里注意，Windows 10需要先按住Shift键的同时再在空白处右键，选择“在PowerShell中打开”。

发现打开了终端（黑窗口），在其中输入`pip install -r requirements.txt`，然后回车，不报错（Error）即为安装成功。
![image](https://github.com/user-attachments/assets/cdce6d91-32e0-447c-860d-c836ad9422a1)

## 4. 准备好本程序需要的输入文件
本程序所需输入表格文件的格式为`csv`，分隔符为`逗号`而`不是其他符号`。表头必须包括`id`、`polar`、`mz`、`addt`、`tor`和`unit`这六个字段，允许包含其他字段，不用去除。

这六个字段分别代表“代谢峰的id”“质谱极性”“质荷比”“加合类别（Adduct Type）”“允许的误差”和“误差单位”

#### 表格数据注意点：
1. 在同一个csv表格文件内，`id`字段值不允许重复。
2. `polar`字段值只能为`positive`和`negative`。
3. `unit`字段值只能为`ppm`和`Da`。
4. 表格大致的样式如下：

| id | polar | mz | addt | tor | unit | ... |
| -------- | -------- | -------- | --------| --------| -------- | -------- |
| 54 | positive | 290.2683275 | M+H | 5 | ppm | ... |
| 104 | positive | 318.2998779 | M+H | 5 | ppm | ... |
| 8057 | negative | 487.322269 | M-H | 5 | ppm | ... |
| ... | ... | ... | ... | ... | ... | ... |

## 5. 运行本程序
将准备好的csv表格文件放入根目录中的`origin_read_data`文件夹中。

然后根据第3节的方法打开终端，输入`python query_metab_name.py`，回车。

然后耐心等待本程序运行完毕！enjoy it~

