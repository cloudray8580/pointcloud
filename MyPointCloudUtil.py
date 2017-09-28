# MyPointCloudUtil provides methods to read data from .pts files
# plot these data to 3D scene and calculate some basic properties
# --------------------------------------------------------
# MyPointCloudUtil
# Licensed under The MIT License
# Copyright (C) 2017 Richie Li
# --------------------------------------------------------
# reference: https://github.com/albanie/pts_loader/blob/master/pts_loader.py
# reference: http://blog.csdn.net/eddy_zheng/article/details/48713449

import matplotlib.pyplot as plt
#from mpl_toolkits.mplot3d import Axes3D
import datetime
import chardet
import math
import os
import sys

class MyPointCloudUtil(object):

    # load all the point cloud file under one or many dirctory
    def batchloader(self, path):

        #input: the dictory contains all point cloud file
        #output: the 3 dimension array contains all point clouds

        allfiles = 	os.listdir(path)
        if not (path.endswith("/") or path.endswith("\\")): # linux:\ windows:/
            path = path + os.sep
        allPointClouds = []
        pointcloud = []
        for file in allfiles:
            if file.endswith(".pts"):
                pointcloud = self.ptsloader1(path+file)
            elif file.endswith(".ply"):
                pointcloud = self.plyloader(path+file)
            elif file.endswith(".off"):
                pointcloud = self.offloader(path+file)
            allPointClouds.append(pointcloud)
            pointcloud = []
        return  allPointClouds

    # load file in pts format
    def ptsloader1(self, path):

        #input: pts file path
        #output: 2D array in format like [[x,y,z],[x,y,z]...]

        rows = []
        ptsfile = open(path)
        for row in ptsfile:
            # strip remove /r/n at the end of a row; split dived them into array
            coordinates = [float(x) for x in row.strip().split(" ")]
            rows.append(coordinates)
        return rows

    # load file in pts format
    def ptsloader2(self, path):

        # input: pts file path
        # output: X Y Z array

        X = []
        Y = []
        Z = []
        ptsfile = open(path)
        for row in ptsfile:
            # strip remove /r/n at the end of a row; split dived them into array
            coordinates = [float(x) for x in row.strip().split(" ")]
            X.append(coordinates[0])
            Y.append(coordinates[1])
            Z.append(coordinates[2])
        return X, Y, Z

    # load file in ply format
    def plyloader(self,path):

        # input: ply file path
        # output: X Y Z array

        # plyfile = open(path, "rb")
        # buf = plyfile.readline()
        #print(chardet.detect(buf))

        rows = []
        plyfile = open(path, "rb")
        getheader = False
        count = 0
        for row in plyfile:
            #print(row.decode("ascii"))
            # strip remove /r/n at the end of a row; split dived them into array
            # the first row will be "ply\r\n"
            if row.__contains__("ply"):
                continue
            if row.startswith("#"):
                continue
            if not getheader:
                if row.__contains__("element vertex"):
                    numberOfPoints = int(row.strip().split(" ")[-1])
                    count = numberOfPoints
                    print(numberOfPoints)
                if row.__contains__("end_header"):
                    getheader = True
                    continue
            else:
                if count > 0:
                    coordinates = [float(x) for x in row.strip().split(" ")]
                    # only the vertex data, ignore other info
                    rows.append(coordinates[:3]) # take the first 3 elements
                    count -= 1
                elif count <= 0:
                    break
        return rows

    # load file in off format
    def offloader(self,path):

        #input: off file path
        # output: X Y Z array

        rows = []
        offfile = open(path)
        getheader = False
        for row in offfile:
            # strip remove /r/n at the end of a row; split dived them into array
            # the first row will be "OFF\r\n"
            if row.__contains__("OFF"):# row == "OFF":
                continue
            if row.startswith("#"):
                continue
            if not getheader:
                parameters = row.strip().split(" ")#[float(x) for x in row.strip().split(" ")]
                numberOfPoints = parameters[0]
                getheader = True
                continue

            coordinates = [float(x) for x in row.strip().split(" ")]
            # only the vertex data, ignore the face data
            if len(coordinates) == 3:
                rows.append(coordinates)
            else:
                break
        return rows

    def extractXYZ(self, array):

        #input: array return from myload
        #output: X Y Z array

        X = []
        Y = []
        Z = []
        for coordinates in array:
            X.append(coordinates[0])
            Y.append(coordinates[1])
            Z.append(coordinates[2])
        return X,Y,Z

    # plot data in 3D and show
    def myplot(self, path):

        #input: pts file path
        #output: the plot 3D scene

        fig = plt.figure()
        ax = fig.add_subplot(111,projection='3d')
        X, Y, Z = self.ptsloader2(path) # call the same class function ! using self.XXX !!!
        ax.scatter(X, Y, Z)
        plt.show()

    # extract number of points, diameter and separation
    def getProperties(self, array):

        #input: array from ptsloader1
        #output: some properties

        # the first dimension
        length = len(array)

        # longest point distance in this point cloud, initialize to 0
        diameter = 0

        # shortest point distance in this point cloud, initialize to be the infinity
        separation = float('inf')

        for i in range(length-1):
            for j in range(i+1, length):
                distance = math.sqrt((array[i][0]-array[j][0])**2 + (array[i][1]-array[j][1])**2 + (array[i][2]-array[j][2])**2)
                if distance > diameter:
                    diameter = distance
                if distance < separation:
                    separation = distance


        return length, diameter, separation

    # brute force
    def calculateHausdorffDistance(self, array1, array2):

        #input: array for the two point cloud obtained from ptsloader1
        #ouput: the hausdorff distance

        distance1to2outside = []
        distance1to2inside = []
        for coordinate1 in array1:
            for coordinate2 in array2:
                distance = math.sqrt((coordinate1[0]-coordinate2[0])**2 + (coordinate1[1]-coordinate2[1])**2 + (coordinate1[2]-coordinate2[2])**2)
                distance1to2inside.append(distance)
            inf = min(distance1to2inside)
            distance1to2outside.append(inf)
            distance1to2inside = []
        sup1 = max(distance1to2outside)

        distance2to1outside = []
        distance2to1inside = []
        for coordinate1 in array2:
            for coordinate2 in array1:
                distance = math.sqrt((coordinate2[0]-coordinate1[0])**2 + (coordinate2[1]-coordinate1[1])**2 + (coordinate2[2]-coordinate1[2])**2)
                distance2to1inside.append(distance)
            inf = min(distance2to1inside)
            distance2to1outside.append(inf)
            distance2to1inside = []
        sup2 = max(distance2to1outside)

        return max(sup1,sup2)

    # brute force
    def calculateGromovHausdorffDistance(self, footstep, array1, array2):

        # input: array for the two point cloud obtained from ptsloader1, footstep(angle) for each rotation
        # ouput: the discrete gromov-hausdorff distance

        count = 0;
        ghdistance = self.calculateHausdorffDistance(array1, array2)
        for x in range(0,360,footstep):
            for y in range(0,360,footstep):
                for z in range(0,360,footstep):
                    array1 = self.rotate(footstep,array1,'Z')
                    distance = self.calculateHausdorffDistance(array1, array2)
                    count += 1;
                    print((count / 360.0**3)*100)
                    if ghdistance < distance:
                        ghdistance = distance
                array1 = self.rotate(footstep, array1, 'Y')
            array1 = self.rotate(footstep, array1, 'X')

        return ghdistance

    # rotate each point of a point cloud array by its footstep
    def rotate(self, footstep, array, direction='X'):

        # input: array for the two point cloud obtained from ptsloader1, footstep(angle) and direction('X','Y','Z')
        # ouput: the array after rotation

        # python use == to compare value, java use == to compare object
        if direction == 'X':
            for coordinate in array:
                tempx = coordinate[0]
                tempy = coordinate[1]
                tempz = coordinate[2]
                coordinate[0] = tempx
                coordinate[1] = math.cos(math.radians(footstep))*tempy - math.sin(math.radians(footstep))*tempz
                coordinate[2] = math.sin(math.radians(footstep))*tempy + math.cos(math.radians(footstep))*tempz
        elif direction == 'Y':
            for coordinate in array:
                tempx = coordinate[0]
                tempy = coordinate[1]
                tempz = coordinate[2]
                coordinate[0] = math.cos(math.radians(footstep))*tempx + math.sin(math.radians(footstep))*tempz
                coordinate[1] = tempy
                coordinate[2] = -math.sin(math.radians(footstep))*tempx + math.cos(math.radians(footstep))*tempz
        elif direction == 'Z':
            for coordinate in array:
                tempx = coordinate[0]
                tempy = coordinate[1]
                tempz = coordinate[2]
                coordinate[0] = math.cos(math.radians(footstep))*tempx - math.sin(math.radians(footstep))*tempy
                coordinate[1] = math.sin(math.radians(footstep))*tempx + math.cos(math.radians(footstep))*tempy
                coordinate[2] = tempz
        return array

    # using GHDistance <= 1/2 max(diameter(x), diameter(y))
    def calculateUpperBoundofGHDistance(self, array1, array2):

        # input: array for the two point cloud obtained from ptsloader1
        # ouput: the upper bound of gromov-hausdorff distance

        len1, max1, min1 = self.getProperties(array1)
        len2, max2, min2 = self.getProperties(array2)
        upperbound = max(max1, max2) / 2

        return upperbound

# ======================= testing =========================

instance = MyPointCloudUtil()

# reload(sys)
# sys.setdefaultencoding('utf8')

print(instance.plyloader("airplane.ply"))

# array = instance.offloader("m101.off")
# print(len(array))
#print(instance.offloader("000.off"))
#print(instance.plyloader("tr_scan_000.ply"))

#print(instance.plyloader("texturedknot.ply"))

# about 3 hours using i7-6920HQ processor
# starttime = datetime.datetime.now()
# print(instance.calculateGromovHausdorffDistance(1,instance.ptsloader1("test1.pts"),instance.ptsloader1("000020.pts")))
# endtime = datetime.datetime.now()
# print (endtime - starttime)

# len,max,min = instance.getProperties(instance.ptsloader1("test1.pts"))
# print(len,max,min)


# X, Y, Z = instance.extractXYZ(instance.myload("test1.pts"))
# print(X)
# print(Y)
# print(Z)


#print(instance.myload("test1.pts"))
#print(instance.myload("000020.pts"))


# instance.myplot("test1.pts")
# instance.myplot("000020.pts")