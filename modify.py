# Warn = """\033[0;31;40m
# =======警告=======
# 此脚本仅包含有限的“自动重命名”功能，它：
# - 不会对Gerber文件进行解析
# - 不会验证文件格式是否正确
# - 不会处理钻孔文件
# - 极有可能损坏你的文件或引起生产错误
# - 需要你根据实际情况进行修改
# 如果你不知道自己在干什么，请手动修改文件而不是使用脚本
# 请编辑此脚本以解除警告
# \033[0m"""
# print(Warn)
# raise Exception("READ THE WARNING")

import yaml, os, re

fconfig = open("config.yaml", "r", encoding="utf-8")
frule = open("rule.yaml", "r", encoding="utf-8")
Config = yaml.load(fconfig, Loader=yaml.FullLoader)
Rule = yaml.load(frule, Loader=yaml.FullLoader)

WorkDir = Config["WorkDir"]
DestDir = Config["DestDir"]
WorkDirFiles = os.listdir(WorkDir)

if not DestDir:
    DestDir=os.path.join(WorkDir,'output')
if not os.path.exists(DestDir):
    os.mkdir(DestDir)

#创建PCB下单必读文档
with open(os.path.join(DestDir, Config["TextFileName"]), "w") as textFile:
    textFile.write(Config["TextFileContent"])

#检验文件是否齐全/重复匹配
for key, value in Rule.items():
    matchFile = []
    rePattern = re.compile(pattern=value)

    for fileName in WorkDirFiles:
        if rePattern.search(fileName):
            matchFile.append(fileName)

    if len(matchFile) < 1:
        raise Exception(key + "匹配失败")
    elif len(matchFile) > 1:
        raise Exception(key + "重复匹配")
    else:
        print(key + " -> " + matchFile[0])

#改名和加头操作
for key, value in Rule.items():
    matchFile = ""
    rePattern = re.compile(pattern=value)

    for fileName in WorkDirFiles:
        if rePattern.search(fileName):
            matchFile = fileName

    with open(os.path.join(WorkDir, matchFile), "r") as file:
        fileData = file.read()
    with open(os.path.join(DestDir, Config["FileName"][key]), "w") as file:
        file.write(Config["Header"])
        file.write(fileData)

fconfig.close()
frule.close()
exit()