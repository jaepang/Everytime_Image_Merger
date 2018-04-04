# -*- coding: utf-8 -*-
__author__ = "shinjawkwang@naver.com"
# 이 프로그램은 악의 꽃 시간표 조정을 위해 제작한 프로그램입니다.
# 에브리타임 앱 내의 시간표 "이미지로 저장" 기능으로 저장한 시간표 이미지를 요합니다.
# 배경색이 흰색 계열인 (회색도 안됨) 테마의 시간표 이미지만 사용 가능합니다.


import glob

import cv2
import numpy as np
from PIL import Image


# (세로 길이, 칸 사이 거리, 칸 수)로 구성된 list를 return
# 칸 수의 case는 9칸, 14칸이므로, 두 가지 case만을 고려한 코드임을 알려드립니다.
def CalcRowLevel(files):
    matrix = []
    for file in files:

        # matrix에 넣을 list
        list = []

        # 흰 계열 공간을 확실히 흰색으로, 아닌 부분을 회색으로 하기 위해
        # cv2.IMREAD_GRAYSCALE을 사용
        img = cv2.imread(file, cv2.IMREAD_GRAYSCALE)

        # img.shape는 [height, width, channel(그레이스케일의 경우 존재하지 않는다)]로 구성
        height = img.shape[0]

        # 높이 list에 추가
        list.append(height)
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

        # 각 원소들 사이값의 평균으로 하는게 가장 정확하겠지만
        # 최초값으로 해도 큰 차이는 없기에
        # 편의상 최초 두 원소의 차로 칸 사이 거리를 계산함
        list.append(rows[0] - rows[1])

        # 회색 선이 시간표 맨 밑 칸에 있기도 하고, 없기도 하다
        # 그래서 rows 원소들이 칸 수 보다 하나 더 많이 생기는 경우가 있다
        # 이 경우를 고려하기 위함 (참고로, 맨 위에 줄이 있는 시간표는 내가 본 시간표 중엔 없었다)
        # 맨 밑에 회색줄이 있는 경우
        # ===== 시간표 칸수가 다른 경우, 여기서 9나 14를 수정(혹은 다른 수를 추가)해야 합니다 =====
        if len(rows) == 9 or len(rows) == 14:
            # =======================================================================
            list.append(len(rows))

        # 맨 밑에 회색줄이 없는 경우
        else:
            list.append(len(rows) - 1)

        # return할 matrix에 list 추가
        matrix.append(list)

    return matrix


# 가장 큰 칸 사이 거리를 return
def CalcMaxRowLv(matrix, col):
    maxRow = 0
    for i in range(len(matrix)):
        maxRow = max(maxRow, matrix[i][col])
    return maxRow


# 시간표들 중 가장 큰 column 값을 return
def CalcMax(files, case):
    Max = 0
    for file in files:
        img = cv2.imread(file, cv2.IMREAD_GRAYSCALE)
        Max = max(Max, img.shape[case])
    return Max


# 시간표 이미지에서 "월화수목금", "9시, 10시, 11시 ..." 부분을 삭제한다.
def deleteMax(files, target_dir):
    sv = []
    i = 0
    for file in files:
        img = cv2.imread(file, cv2.IMREAD_GRAYSCALE)

        # idx=0 : 세로 자르기
        # idx=1 : 가로 자르기
        idx = 0
        lev = 0
        while lev < img.shape[idx]:
            
            if idx==0:
                px = img[lev, 0]
            else:
                px = img[0, lev]

            # 회색 픽셀이 발견되었을 때
            if px<255:

                # 위치를 저장
                sv.append(lev)
                if len(sv)>1:

                    # 칸 사이 거리가 30 이상이면 칸이 떨어졌다고 간주
                    # 잘라서 저장하고 반복문을 종료한다.
                    if sv[len(sv)-1] - sv[len(sv)-2] > 30:
                        if idx==0:
                            delImg = img[sv[len(sv)-2]:img.shape[0], 0:img.shape[1]]

                            # parameter들 초기값으로 돌리고, 가로 모드로 전환
                            idx += 1
                            lev = 0
                            sv.clear()
                            # continue가 없으면 lev+=1이 수행되버림
                            continue

                        elif idx==1:
                            delImg = delImg[0:delImg.shape[0], sv[len(sv)-2]:img.shape[1]]
                            cv2.imwrite(target_dir + '/Resize/' + str(i) + '_rs.jpg', delImg)
                            break

            lev += 1

        # 리스트를 초기화한다.
        sv.clear()
        i += 1


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

    deleteMax(files, target_dir)
    rs_files = glob.glob(target_dir + '/Resize/' + '*.jpg')

    matrixRow = CalcRowLevel(files)
    maxCol = CalcMax(rs_files, 1)
    print(matrixRow)
    print(matrixCol)
    print(maxCol)
    # maxRowlv = CalcMaxRowLv(matrix, 1)
    # maxRow = CalcMax(rs_files, 0)

if __name__ == "__main__":
    main()
