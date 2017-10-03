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
import thread

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

    # calculate diameter direction
    def calculateDiameterDirection(self, array):

        # input: array from ptsloader1
        # output: the diameter direction (if many, the last one)

        length = len(array)
        diameter = 0
        direction = [0,0,0]
        for i in range(length-1):
            for j in range(i+1, length):
                distance = math.sqrt((array[i][0]-array[j][0])**2 + (array[i][1]-array[j][1])**2 + (array[i][1]-array[j][1])**2)
                if distance > diameter:
                    diameter = distance
                    direction=[array[i][0]-array[j][0], array[i][1]-array[j][1],array[i][1]-array[j][1]]
        return direction

    # calculate the angle between two 3D arrow
    def calculateRadianBetweenDirections(self, direction1, direction2):

        # input: two direction array, with 3 dimension x y z
        # output: the radian between these two direction

        numerator = direction1[0]*direction2[0] + direction1[1]*direction2[1] + direction1[2]*direction2[2]
        denominator = math.sqrt(direction1[0]**2 + direction1[1]**2 + direction1[2]**2) * math.sqrt(direction2[0]**2 + direction2[1]**2 + direction2[2]**2)
        costheta = numerator / denominator
        theta = math.acos(costheta) # return radian, not angle

        return theta

    # calculate the normal vector of the two direction, passing through the gravity center
    def calculateNormalVector(self, direction1, direction2):

        # input: the two direction and gravity center
        # output: the normal vector passing through the gravity center

        # using cross product
        nx = direction1[1]*direction2[2] - direction1[2]*direction2[1]
        ny = -(direction1[0]*direction2[2] - direction1[2]*direction2[0])
        nz = direction1[0]*direction2[1] - direction1[1]*direction2[0]

        return [nx, ny, nz]

    # remember to move the point cloud to the origin before calling this function !!!
    def rotateAcrossNormalVector(self, normal, array, angle):

        # input: the normal vector of the two direction, the point cloud array, and the rotate angle
        # output: the rotated array according to the normal vector

        # first normalize the normal vector
        normallength = math.sqrt(normal[0]**2 + normal[1]**2 + normal[2]**2)
        normal[0] /= normallength
        normal[1] /= normallength
        normal[2] /= normallength

        # get the support value
        radian = math.radians(angle)
        c = math.cos(radian)
        s = math.sin(radian)
        x = normal[0]
        y = normal[1]
        z = normal[2]

        # calculate the rotated array.
        for coordinate in array:
            tempx = coordinate[0]
            tempy = coordinate[1]
            tempz = coordinate[2]
            coordinate[0] = (x**2 *(1-c) + c) * tempx + (x*y *(1-c)-z*s) * tempy + (x*z*(1-c) + y*s) * tempz
            coordinate[1] = (x*y*(1-c) + z*s) * tempx + (y**2*(1-c) + c) * tempy + (y*z*(1-c) - x*z) * tempz
            coordinate[2] = (x*z*(1-c) - y*s) * tempx + (y*z*(1-c) +x*s) * tempy + (z**2 *(1-c) + c) * tempz


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

    # calculate center of gravity (with equal gravity)
    def calculateCenter(self,array):

        # input: array for the two point cloud obtained from ptsloader1,
        # ouput: the center of gravity (with equal gravity)

        num = len(array)
        if num == 0:
            return 0, 0, 0
        Xsum, Ysum, Zsum = 0.0, 0.0, 0.0
        for coordinates in array:
            Xsum += coordinates[0]
            Ysum += coordinates[1]
            Zsum += coordinates[2]
        Xsum /= num
        Ysum /= num
        Zsum /= num

        return Xsum, Ysum, Zsum


    # put the two object to the origin, let the two gravity center overlap with the origin point
    def overlapCenterOfGravity(self, array1, array2):

        # input: array for the two point cloud obtained from ptsloader1, footstep(angle) for each rotation
        # output: modify array1 and array2 to make gravity center overlap with origin point

        Xcenter1, Ycenter1, Zcenter1 = self.calculateCenter(array1)
        Xcenter2, Ycenter2, Zcenter2 = self.calculateCenter(array2)

        for coordinates in array1:
            coordinates[0] -= Xcenter1
            coordinates[1] -= Ycenter1
            coordinates[2] -= Zcenter1

        for coordinates in array2:
            coordinates[0] -= Xcenter2
            coordinates[1] -= Ycenter2
            coordinates[2] -= Zcenter2

                # Xdiff = Xcenter1 - Xcenter2
        # Ydiff = Ycenter1 - Ycenter2
        # Zdiff = Zcenter1 - Zcenter2
        # for coordinates in array2:
        #     coordinates[0] += Xdiff
        #     coordinates[1] += Ydiff
        #     coordinates[2] += Zdiff
        #print(array2)

    # brute force
    def calculateGromovHausdorffDistance(self, footstep, array1, array2):

        # input: array for the two point cloud obtained from ptsloader1, footstep(angle) for each rotation
        # ouput: the discrete gromov-hausdorff distance

        # overlap their center of gravity
        self.overlapCenterOfGravity(array1,array2)

        # using rotation
        count = 0;
        ghdistance = self.calculateHausdorffDistance(array1, array2)
        for x in range(0,360,footstep):
            for y in range(0,360,footstep):
                for z in range(0,360,footstep):

                    #array1 = self.rotate(footstep,array1,'Z')
                    self.rotate(footstep, array1, 'Z')
                    distance = self.calculateHausdorffDistance(array1, array2)
                    count += 1;
                    #print(count / (360.0/footstep)**3)
                    #print(distance, ghdistance)

                    if distance < ghdistance:
                        ghdistance = distance

                    # if totally the same, break the loop and return
                    # if the difference is small enough, we treat it as equal
                    if ghdistance == 0 or ghdistance < 0.0000001:
                        #print(count)
                        return 0

                #array1 = self.rotate(footstep, array1, 'Y')
                self.rotate(footstep, array1, 'Y')
            #array1 = self.rotate(footstep, array1, 'X')
            self.rotate(footstep, array1, 'X')

        return ghdistance

    # rotate each point of a point cloud array by its footstep
    # remember to move the point cloud to the origin before calling this function !!!
    def rotate(self, footstep, array, direction='X'):

        # input: array for the two point cloud obtained from ptsloader1, footstep(angle) and direction('X','Y','Z')
        # ouput: the array after rotation

        # using radians instead of angle
        footstep = math.radians(footstep)

        # python use == to compare value, java use == to compare object
        if direction == 'X':
            for coordinate in array:
                tempx = coordinate[0]
                tempy = coordinate[1]
                tempz = coordinate[2]
                coordinate[0] = tempx
                coordinate[1] = math.cos(footstep)*tempy - math.sin(footstep)*tempz
                coordinate[2] = math.sin(footstep)*tempy + math.cos(footstep)*tempz
        elif direction == 'Y':
            for coordinate in array:
                tempx = coordinate[0]
                tempy = coordinate[1]
                tempz = coordinate[2]
                coordinate[0] = math.cos(footstep)*tempx + math.sin(footstep)*tempz
                coordinate[1] = tempy
                coordinate[2] = -math.sin(footstep)*tempx + math.cos(footstep)*tempz
        elif direction == 'Z':
            for coordinate in array:
                tempx = coordinate[0]
                tempy = coordinate[1]
                tempz = coordinate[2]
                coordinate[0] = math.cos(footstep)*tempx - math.sin(footstep)*tempy
                coordinate[1] = math.sin(footstep)*tempx + math.cos(footstep)*tempy
                coordinate[2] = tempz
        return array # do not need to return, already change the list

    # using GHDistance <= 1/2 max(diameter(x), diameter(y))
    def calculateUpperBoundofGHDistance(self, array1, array2):

        # input: array for the two point cloud obtained from ptsloader1
        # ouput: the upper bound of gromov-hausdorff distance

        len1, max1, min1 = self.getProperties(array1)
        len2, max2, min2 = self.getProperties(array2)
        upperbound = max(max1, max2) / 2

        return upperbound

    # using overlap diameter direction way
    def calculateIntuitiveUpperBound(self,array1,array2):

        # input: array for the two point cloud obtained from ptsloader1
        # ouput: the intuitive upper bound of gromov-hausdorff distance

        # first, move to origin
        self.overlapCenterOfGravity(array1,array2)

        # calculate the direction of the diameter
        direction1 = self.calculateDiameterDirection(array1)
        direction2 = self.calculateDiameterDirection(array2)

        # calculate normal vector of the two direction
        normalvector = self.calculateNormalVector(direction1, direction2)

        # calculate the radian of the two direction
        radian = self.calculateRadianBetweenDirections(direction1, direction2)

        # rotate the point cloud array
        self.rotateAcrossNormalVector(normalvector,array2,radian)

        # calculate hausdorrf distance at this position
        distance = self.calculateHausdorffDistance(array1, array2)

        # use this as the upper bound
        return distance

    def multiThreadCompute(self, threadsnum):
        pass

    def subThreadForGHDistance(self,):
        pass

# ======================= testing =========================

instance = MyPointCloudUtil()

array1 = instance.ptsloader1("test1.pts")
print(array1)
array2 = instance.ptsloader1("test2.pts")
print(array2)
instance.overlapCenterOfGravity(array1,array2)
print (array1)
print(array2)
instance.rotate(180,array1,'X')
print(array1)
print(instance.calculateGromovHausdorffDistance(1,array1,array2))
print(instance.calculateIntuitiveUpperBound(array1,array2))

# print(instance.calculateDiameterDirection(array2))

# X,Y,Z = instance.calculateCenter(array1)
# print(X,Y,Z)
#
# X2, Y2, Z2 = instance.calculateCenter(array2)
# print(X2,Y2,Z2)
#
# instance.overlapCenterOfGravity(array1,array2)
# print (array2)
#
# dis = instance.calculateGromovHausdorffDistance(1,array1,array2)
# print(dis)

# instance.rotate(1,array1,'X')
# array1 = instance.rotate(1,array1,'X')
#print(array1)



# import plyfile
# plydata = plyfile.PlyData.read('texturedknot.ply')
# print(plydata)
# print(plydata["vertex"][0])

# reload(sys)
# sys.setdefaultencoding('utf8')

#print(instance.plyloader("airplane.ply"))

# array = instance.offloader("m101.off")
# print(len(array))
#print(instance.offloader("000.off"))
#print(instance.plyloader("tr_scan_000.ply"))

#print(instance.plyloader("texturedknot.ply"))

# about ??? hours using i7-6920HQ processor
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