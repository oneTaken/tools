import os

def countDownedImgs(path):
    files = os.listdir(path)
    count = 0
    for file in files:
        filePath = path + os.sep + file
        if os.path.isdir(filePath):
            count += countDownedImgs(filePath)
        elif os.path.isfile(filePath):
            count += 1
        else:
            print(filePath)
    return count

if __name__ == "__main__":
    path = 'D:\Project\imgLabeling\首页\图片'
    print(countDownedImgs(path))