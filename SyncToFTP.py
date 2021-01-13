# -*- coding: utf-8 -*-

# Reference ############################################################
# ftplib — FTP protocol client:
# https://docs.python.org/3/library/ftplib.html
# How to Install Python PIP on Windows, Mac, and Linux
# https://www.makeuseof.com/tag/install-pip-for-python/
# Python入门七：安装支持WinXp运行的Python及环境配置
# https://blog.csdn.net/zjm12343/article/details/79738396
# Python PyInstaller安装和使用教程（详解版）
# http://c.biancheng.net/view/2690.html

import os, sys, time, shutil
from ftplib import FTP
import configparser

def _GetApplicationPath():
    application_path = ''
    if getattr(sys, 'frozen', False):
        # If the application is run as a bundle, the PyInstaller bootloader
        # extends the sys module by a flag frozen=True and sets the app
        # path into variable _MEIPASS'.
        application_path = sys._MEIPASS
    else:
        application_path = os.path.dirname(os.path.abspath(__file__))

    return application_path


def _GetFullIniFilepath(filepath):

    if os.path.isabs(filepath) == False:
        #filepath = os.path.join(sys.path[0], filepath)
        filepath = os.path.join(_GetApplicationPath(), filepath)

    # print(filepath)

    return filepath


def _loadConf(filepath, session, fieldsWithDefaultValue):

    filepath = _GetFullIniFilepath(filepath)

    config = configparser.ConfigParser()
    if os.path.exists(filepath) == False:
        config.add_section(session)
        for key, value in fieldsWithDefaultValue.items():
            config.set(session, key, value)
        with open(filepath, "w", encoding="utf-8") as file:
            config.write(file)  # 值写入配置文件

    config.read(filepath, encoding="UTF-8")

    conf = dict()
    for key, value in fieldsWithDefaultValue.items():
        conf[key] = config[session][key]

    return conf


def loadAppConf(filepath):
    return _loadConf(
        filepath,
        "app",
        {
            "Path": "D:/test.txt",
            "reconnectTimeout": "5",
            "fileCheckingTimeout": "5",
            "TransfterSuccessTimeout": "60",
        },
    )


def loadFTPConf(filepath):
    return _loadConf(
        filepath,
        "ftp",
        {
            "host": "10.144.41.49",
            "user": "admin",
            "passwd": "welcome",
            "acct": "",
            "timeout": "10",
            "source_address": "None",
            "encoding": "utf-8",
        },
    )


def check_file_exist(filePath):
    return os.path.isfile(filePath)


def thread():

    appConf = loadAppConf("syncToFTP.app.ini")
    print(appConf)
    filePath = appConf["Path"]
    print("Watching File: "+ filePath)

    # ftp 是否连接上
    ftpConnected = False
    # 是否需要上传
    needUploading = False
    # 上次修改时间
    lastModifyTime = ""
    # 本次检查的文件修改时间
    modifyTime = ""
    # FTP Obj
    ftp = FTP()

    #### Loop Start: 系统流程循环
    while True:

        # Step1: 连接 FTP,如果没有连接上, 则继续连接; 如果连接上, 则继续下一个步骤
        while not ftpConnected:
            try:
                ftpConf = loadFTPConf("syncToFTP.ftp.ini")
                print(ftpConf)
                ftp = FTP(
                    host=ftpConf["host"],
                    user=ftpConf["user"],
                    passwd=ftpConf["passwd"],
                    acct=ftpConf["acct"],
                    timeout=float(ftpConf["timeout"]),
                )
                ftp.cwd("/")
                ftpConnected = True
                pass
            except Exception as e:
                print(e)
                ftpConnected = False
                time.sleep(float(appConf["reconnectTimeout"]))  # default 5s
                pass

        # Step2: 判断是否需要上传(发生修改),如果没有发生修改,则继续检查
        # 获取文件的修改时间
        if check_file_exist(filePath):
            modifyTime = time.ctime(os.path.getmtime(filePath))

        needUploading = modifyTime != lastModifyTime

        if not needUploading:
            print("File not Changed!")
            time.sleep(float(appConf["fileCheckingTimeout"]))  # default 5s
            continue

        # Step3: 上传流程
        if lastModifyTime == "":
            print("First Run. Start uploading...")
            pass
        else:
            print("File is changed. Start uploading...")
            pass
        try:
            # Step3.1: 复制到一个临时文件中去
            fileFolder, fileName = os.path.split(filePath)
            destFilePath = os.path.join(fileFolder, fileName + ".upload")
            shutil.copyfile(filePath, destFilePath)

            # Step3.2: FTP 上传
            with open(destFilePath, "rb") as fp:
                print(ftp.storbinary("STOR " + fileName, fp))

            # Step3.3: 上传成功,修改上次修改时间
            lastModifyTime = modifyTime
            time.sleep(float(appConf["TransfterSuccessTimeout"]))  # default 60s
            pass

        except Exception as e:
            # Step3.Error 如果上传流程发生任何的错误,很可能是FTP发生连接错误,因此重置连接Flag ,重新连接
            print(e)
            ftp.quit()
            ftpConnected = False
            pass

        #### Loop End: 系统流程循环
        pass

    print(ftp.quit())


if __name__ == "__main__":

    # filePath = "D:/New Rich Text Document.rtf"
    # print(time.ctime(os.path.getmtime(filePath)))
    # print(time.ctime(os.path.getctime(filePath)))
    # print(check_file_exist(filePath))
    # folder, name = os.path.split(filePath)
    # print(folder)
    # shutil.copyfile(filePath, "D:/New Rich Text Document2.rtf")

    print("ApplicationDir: "+ _GetApplicationPath())
    thread()
