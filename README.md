# FuckJLC

将其他EDA软件的gerber转换为傻逼立创EDA格式的脚本

立创EDA狗都不用

# Usage

``` python
python modify.py
```

请手动替换脚本中header和工作目录为你自己的

header获取方法：立创EDA导出gerber→随意打开一个gerber文件

## Noitce

目前仅对Kicad与Altium Designer所导出的gerber做适配，其他软件请发Issue并附带目录结构或者自力更生PR

对于Altium Designer所导出的gerber，请自行删除与下单无关的文件，避免影响脚本运行

请一定不要漏掉钻孔文件，可能包括金属化和非金属化孔两个文件

导出gerber时注意一些细节
* 使用`Protel格式文件扩展名`导出，此格式与LCEDA相同
* 钻孔文件最好也为gerber格式


**低调使用**

**嘉立创舔狗什么时候死啊**
