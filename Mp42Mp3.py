#!/usr/bin/python3
# -*-coding:utf-8-*-

"""
一些命令：
    pip3 config list
    pip3 config set global.index-url http://mirrors.aliyun.com/pypi/simple/
    sudo pip3 install moviepy  地址：https://zulko.github.io/moviepy/install.html
    may error(fix): sudo pip3 install --upgrade pip setuptools wheel
                    sudo python3 -m pip install Pillow

"""

from moviepy.editor import *
import os


def findAllFile(dir):
    for root, ds, fs in os.walk(dir):
        for f in fs:
            if f.endswith('.mp4'):
                fullname = os.path.join(root, f)
                yield fullname


def Mp4ToMp3(inDir, outPath, pre):
    print("输入的目录为：" + inDir)
    n = 0  # 计数用于文件名字编号
    for f in findAllFile(inDir):
        n = n + 1
        print("转换中：" + f)
        tran(f, outPath, n, pre)


def tran(filePath, fileOut, index, pre):
    video = VideoFileClip(filePath)
    audio = video.audio
    # 转成mp3文件，重命名并保存到指定文件夹
    name = fileOut + pre + '【' + str(index) + '】' + '.mp3'
    audio.write_audiofile(name)
    print("转换成功：" + name)


if __name__ == '__main__':
    inPath = "/xxx/xxx/"
    out = "/xxx/xxx/"
    preName = "aaa"
    Mp4ToMp3(inPath, out, preName)
