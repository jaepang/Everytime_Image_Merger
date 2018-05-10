# -*- coding: utf-8 -*-
__author__ = "shinjawkwang@naver.com"
# 이 프로그램은 성균관대학교 정보통신대학 밴드동아리 악의 꽃 시간표 조정을 위해 제작한 프로그램입니다.
# 에브리타임 앱 내의 시간표 "이미지로 저장" 기능으로 저장한 시간표 이미지를 요합니다.
# "화이트(기본)" 테마의 시간표 이미지만 사용 가능합니다. (추후 업데이트 예정)
# 월~금요일까지 기록된 시간표만 지원합니다 (동아리에 토욜시간표도 추가하는 사람이 생기면 그 때 수정 예정)


import glob

import cv2
import numpy as np


# 칸수의 case를 고려하기 위해, 아래 method의 rows 리스트를 이용해 칸 수를 조정하고자 한다
# 맨 밑에 회색줄의 위치가 기록된 경우, 그 부분을 삭제하는 method이다
def deleteBottom(rows, height):
    if height - rows[0] < 10:
        del rows[0]
    return rows


# (칸 사이 거리, 칸의 수)로 구성된 list를 return
# 칸 수의 case를 고려하는 method : deleteBottom
def CalcRows(files):
    matrix = []
    for file in files:
        print("==== ", file, " ====")
        # matrix에 넣을 list
        list = []

        # 흰 계열 공간을 확실히 흰색으로, 아닌 부분을 회색으로 하기 위해
        # cv2.IMREAD_GRAYSCALE을 사용
        img = cv2.imread(file, cv2.IMREAD_GRAYSCALE)

        # img.shape는 [height, width, channel(그레이스케일의 경우 존재하지 않는다)]로 구성
        height = img.shape[0]
        
        # 높이 list에 추가
        rows = []

        # 최초 sv는 필터링 되지 않기 위함
        sv = height + 100
        while height > 0:

            # 픽셀은 0~height-1 로 구성된 듯 하다. height로 하니 오류 출력
            px = img[height-1, 1]

            # 흰색보다 살짝이라도 어두운 케이스
            # 이하 '회색'으로 지칭, 선을 이루는 픽셀로 간주함
            if px < 255:

                # 마지막으로 발견한 회색 픽셀과 가까운 (거리가 20픽셀 미만)
                # 픽셀에서 다시 회색 픽셀을 발견한 경우
                if sv - height < 20:

                    # 같은 선을 이루고 있는 픽셀이므로 리스트에 넣을 필요가 없음
                    # rows 리스트에서 pop하고 새롭게 발견한 픽셀을 저장
                    # 선을 이루는 마지막 픽셀을 저장하기 위함
                    rows.pop()
                rows.append(height)

                # 저장값 갱신
                sv = height
            height -= 1

        # 회색 선이 시간표 맨 밑 칸에 있기도 하고, 없기도 하다
        # 그래서 rows 원소들이 칸 수 보다 하나 더 많이 생기는 경우가 있다
        # 이 경우를 고려하기 위함 (참고로, 맨 위에 줄이 있는 시간표는 내가 본 시간표 중엔 없었다)
        rows = deleteBottom(rows, img.shape[0])

        # 각 원소들 사이값의 평균으로 하는게 가장 정확하겠지만
        # 최초값으로 해도 큰 차이는 없기에
        # 편의상 최초 두 원소의 차로 칸 사이 거리를 계산함
        list.append(rows[0] - rows[1])
        list.append(len(rows))
        
        # return할 matrix에 list 추가
        matrix.append(list)
    
    return matrix


# 시간표 이미지에서 "월화수목금", "9시, 10시, 11시 ..." 부분을 삭제한다.
def deleteTop(files, target_dir):
    sv = []
    i = 0
    for file in files:
        img = cv2.imread(file, cv2.IMREAD_COLOR)
        imgG = cv2.imread(file, cv2.IMREAD_GRAYSCALE)

        # idx=0 : 세로 자르기
        # idx=1 : 가로 자르기
        idx = 0
        lev = 0
        while lev < img.shape[idx]:

            if idx == 0:
                px = imgG[lev, 0]
            else:
                px = imgG[0, lev]

            # 회색 픽셀이 발견되었을 때
            if px < 255:

                # 위치를 저장
                sv.append(lev)
                if len(sv) > 1:

                    # 칸 사이 거리가 30 이상이면 칸이 떨어졌다고 간주
                    # 잘라서 저장하고 반복문을 종료한다.
                    if sv[len(sv)-1] - sv[len(sv)-2] > 30:
                        if idx == 0:
                            delImg = img[sv[len(sv)-2]:img.shape[0], 0:img.shape[1]]

                            # parameter들 초기값으로 돌리고, 가로 모드로 전환
                            idx += 1
                            lev = 0
                            sv.clear()
                            # continue가 없으면 lev+=1이 수행되버림
                            continue

                        elif idx == 1:
                            delImg = delImg[0:delImg.shape[0],
                                            sv[len(sv)-2]:img.shape[1]]
                            cv2.imwrite(target_dir + '/Resize/' +
                                        str(i) + '_rs.jpg', delImg)
                            break

            lev += 1

        # 리스트를 초기화한다.
        sv.clear()
        i += 1


# 시간표에서 line을 삭제한다
# issue : 현재 프로세싱 과정이 상당히 느리다. 
def deleteLine(files, target_dir):
    i = 0
    for file in files:
        img = cv2.imread(file)
        imgray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        height, width, _ = img.shape
        for row in range(0, height-1):
            for col in range(0, width-1):
                pixel = img[row, col]
                if 185 < pixel[0] < 255 and 185 < pixel[1] < 255 and 185 < pixel[2] < 255:
                    imgray[row, col] = 255
        cv2.imwrite(target_dir + '/Complete/' + str(i) + '.jpg', imgray)
        i += 1


def delete(files, target_dir):
    deleteTop(files, target_dir)
    rs_files = glob.glob(target_dir + '/Resize/' + '*.jpg')
    deleteLine(rs_files, target_dir)


# delete로 변환한 이미지와, CalcRows로 구한 (칸 사이 거리, 칸의 수)를 이용해
# 비는 시간대를 계산한다 (수업 사이 15분은 사실상 의미가 없으므로 무시한다)
# [0-15, 15-30, 30-45, 45-60]
def CalcTimeTable(files, matrix):
    busyTime = []
    pxList = []
    temp = []
    quarters = []
    i = 0
    for file in files:
        print("==== ", file, " ====\n")
        img = cv2.imread(file, cv2.IMREAD_GRAYSCALE)

        height, width = img.shape
        print(height, width)
        aQuarter = round((height // matrix[i][1]) / 4)
        print("a quarter : ", aQuarter)

        # 1~5 => range(1, 6)
        for days in range(1, 6):
            row = ((width // 5) * days) - 5
            print("Detecting day: ", days)
            lev = 0
            flag = True
            while lev < height and flag:
                flag = True
                px = img[lev, row]
                while px < 250:
                    pxList.append(lev)
                    lev += 1
                    if(lev < height):
                        px = img[lev, row]
                    else:
                        flag = False
                        break

                if len(pxList) > 0:

                    # 시간표에 글씨때문에 잘렸던 경우
                    if len(temp) > 0 and pxList[0] - temp[len(temp)-1] < 20 and len(temp) > 10 and len(pxList) > 10:
                        if len(quarters) > 0 and quarters[len(quarters)-1][1] == temp[0]:
                            quarters.pop()
                        classLV = pxList[len(pxList)-1] - temp[0]
                    else:
                        classLV = pxList[len(pxList)-1] - pxList[0]
                    print("====", classLV, "====")
                    quarters.append([round((classLV/aQuarter)), pxList[0]])
                    if quarters[len(quarters)-1][0] == 0:
                        quarters.pop()
                    print(pxList, quarters)
                    temp = pxList
                    print("\n==== temp ====")
                    print(temp)
                else:
                    lev += 1

                pxList.clear()
                # 이 경우가 아닐 경우, 기록된 픽셀은 칸을 나누는 선이다
            # for time in range(len(hours)):

            temp.clear()
            quarters.clear()
        i += 1

def RectangleDetector(files):
    for file in files:
        img = cv2.imread(file)
        imgray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        blur = cv2.GaussianBlur(imgray, (5,5), 0)
        ret, thr = cv2.threshold(imgray, 127, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        _, contours, _ = cv2.findContours(thr, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        cv2.drawContours(img, contours, -1, (0,0,255), 1)
        cv2.imshow('thresh', thr)
        cv2.imshow('contour', img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


def main():
    print("# Welcome to Everytime Schedule MAkEr")
    # Enter Your Path
    # target_dir = input("INPUT PATH : ")
    # == Default Path in BOOTY, Windows ============
    # target_dir = "C:\\Users\\Shinjaekwang\\Dropbox\\Code\\2018\\LFDM_PYthon\\Images\\"
    # == Default Path in shinjaekwang, Mac OS X ====
    target_dir = "/Users/shinjaekwang/Dropbox/Code/Everytime_Image_Merger/Images/"
    # target_dir = input("이미지 파일이 담긴 폴더 경로를 입력하십시오: ")
    # ==============================================
    files = glob.glob(target_dir + "*.jpg")

    matrixRow = CalcRows(files)
    delete(files, target_dir)
    files = glob.glob(target_dir + '/Complete/' + '*.jpg')
    
    # print(matrixRow)
    # calcEmpty(rs_files, matrixRow)
    RectangleDetector(files)
    

if __name__ == "__main__":
    main()
