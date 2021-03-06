from sys import argv
import math

from BitmapFile import BitmapFile
from SectionRaster import SectionRaster

script, path, image = argv

with open(path + image, "rb") as f:
    bmp = BitmapFile(bytearray(f.read()))

mapa = SectionRaster(bmp, 8)
print("map.width:", mapa.width, "map.height:", mapa.height)

mapa.calculateMinima()

print("map.minimum:", mapa.minimum, "map.maximum:", mapa.maximum)

mapa.calculateThreshold()

print("map.threshold:", mapa.threshold)

mapa.findForeground()

mapa.erodeForeground()
mapa.erodeForeground()
mapa.erodeForeground()

mapa.findCenterOfMass()

print("centerOfMass:", mapa.centerOfMass)

#-------------------------------------------------------------------------------
comX, comY = mapa.centerOfMass

def findOffsetX(offset, map, comX, comY, sign, limit, bottom, top):
    edge = False
    while not edge:
        offset += 1
        x = comX + offset * sign
        for i in range(offset + 1):
            yBottom = bottom if comY - i < bottom else comY - i
            yTop = top if comY + i > top else comY + i
            if (map.foreground[x][yBottom] or map.foreground[x][yTop]):
                break
            elif i == offset:
                offset -= 1
                edge = True
            elif x == limit:
                edge = True
    return offset
def findOffsetY(offset, map, comX, comY, sign, limit, left, right):
    edge = False
    while not edge:
        offset += 1
        y = comY + offset * sign
        for j in range(offset + 1):
            xLeft = left if comX - j < comX - j else comX - j
            xRight = right if comX + j > right else comX + j
            if (map.foreground[xLeft][y] or
                map.foreground[xRight][y]):
                break
            elif j == offset:
                offset -= 1
                edge = True
            elif y == limit:
                edge = True
    return offset

offsetW = findOffsetX(10, mapa, comX, comY, -1, 0, 0, mapa.height - 1)
offsetE = findOffsetX(10, mapa, comX, comY, 1, mapa.width - 1, 0, mapa.height - 1)
offsetS = findOffsetY(2, mapa, comX, comY, -1, 0, 0, mapa.width - 1)
offsetN = findOffsetY(10, mapa, comX, comY, 1, mapa.height - 1, 0, mapa.width - 1)

print("offsetW:", offsetW, "offsetE:", offsetE, "offsetS:", offsetS, "offsetN:", offsetN)

left = 0 if comX < offsetW else comX - offsetW
right = mapa.width - 1 if comX + offsetE >= mapa.width else comX + offsetE
bottom = 0 if comY < offsetS else comY - offsetS
top = mapa.height - 1 if comY + offsetN >= mapa.height else comY + offsetN

print("left:", left, "bottom:", bottom, "right:", right, "top:", top)

for x in range(mapa.width):
    for y in range(mapa.height):
        if (x < left or  x > right) or (y < bottom or y > top):
            mapa.foreground[x][y] = False

for y in range(bottom, top + 1):
    xl = right
    xr = left
    xlf = False
    xrf = False
    for x in range(right - left):
        if xlf and xrf:
            break
        if mapa.foreground[left + x][y] and not xlf:
            xl = left + x
            xlf = True
        if mapa.foreground[right - x][y] and not xrf:
            xr = right - x
            xrf = True
    for x in range(xl, xr + 1):
        mapa.foreground[x][y] = True

for x in range(left, right + 1):
    yb = bottom
    yt = top
    ybf = False
    ytf = False
    for y in range(top - bottom):
        if ybf and ytf:
            break
        if mapa.foreground[x][bottom + y] and not ybf:
            yb = bottom + y
            ybf = True
        if mapa.foreground[x][top - y] and not ytf:
            yt = top - y
            ytf = True
    for y in range(yb, yt + 1):
        mapa.foreground[x][y] = True
#-------------------------------------------------------------------------------

mapa.findCenterOfMass()
comX, comY = mapa.centerOfMass

print("centerOfMass:", mapa.centerOfMass)

centerOffsetX = mapa.width // 2 - comX
centerOffsetY = mapa.height // 2 - comY

print("centerOffsetX:", centerOffsetX, "centerOffsetY:", centerOffsetY)

#-------------------------------------------------------------------------------

bmp.makeFile(path + image + ".procesada.bmp")

with open(path + image + ".procesada.bmp", "rb") as f:
    bmpCopy = BitmapFile(bytearray(f.read()))

mapCopy = SectionRaster(bmpCopy, 8)

for x in range(mapa.width):
    for y in range(mapa.height):
        if mapa.foreground[x][y]:
            mapCopy.foreground[x+centerOffsetX][y+centerOffsetY] = True
            blockStart = (mapCopy.bmp.start +
                x * mapCopy.pixelSize * mapCopy.bmp.bpp +
                y * mapCopy.bmp.width * mapCopy.pixelSize * mapCopy.bmp.bpp)
            for i in range(mapCopy.pixelSize):
                for j in range(mapCopy.pixelSize):
                    idx = (blockStart +
                        i * mapCopy.bmp.bpp +
                        j * mapCopy.bmp.width * mapCopy.bmp.bpp)
                    idxCopy = (idx +
                        centerOffsetX * mapCopy.pixelSize * mapCopy.bmp.bpp +
                        centerOffsetY * mapCopy.pixelSize * mapCopy.bmp.width * mapCopy.bmp.bpp)
                    mapCopy.bmp.data[idxCopy:idxCopy+3] = mapa.bmp.data[idx:idx+3]
        if not mapCopy.foreground[x][y]:
            mapCopy.paintBlock(x, y, (255, 255, 255))

mapa = mapCopy
bmp = bmpCopy
mapa.centerOfMass = (mapa.width // 2, mapa.height // 2)
comX, comY = mapa.centerOfMass

#-------------------------------------------------------------------------------

middleLeftmost = comX
while mapa.foreground[middleLeftmost-1][comY]:
    middleLeftmost -= 1

print("middleLeftmost:", middleLeftmost)

leftEdge = [(middleLeftmost, comY)]

initX, initY = (middleLeftmost, comY)
while True:
    initY += 1
    initValue = mapa.foreground[initX][initY]
    
    x, y = (initX, initY)
    while initValue == mapa.foreground[x][y] and not abs(initX - x) > 1:
        if not mapa.foreground[x][y]:
            x += 1
        elif mapa.foreground[x-1][y]:
            x -= 1
        else:
            break
    if abs(initX - x) > 1:
        break
    else:
        leftEdge.append((x, y))
        initX, initY = (x, y)
#
initX, initY = (middleLeftmost, comY)
while True:
    initY -= 1
    initValue = mapa.foreground[initX][initY]
    
    x, y = (initX, initY)
    while initValue == mapa.foreground[x][y] and not abs(initX - x) > 1:
        if not mapa.foreground[x][y]:
            x += 1
        elif mapa.foreground[x-1][y]:
            x -= 1
        else:
            break
    if abs(initX - x) > 1:
        break
    else:
        leftEdge.append((x, y))
        initX, initY = (x, y)
#
#
middleRightmost = comX
while mapa.foreground[middleRightmost+1][comY]:
    middleRightmost += 1

print("middleRightmost:", middleRightmost)

rightEdge = [(middleRightmost, comY)]

initX, initY = (middleRightmost, comY)
while True:
    initY += 1
    initValue = mapa.foreground[initX][initY]
    
    x, y = (initX, initY)
    while initValue == mapa.foreground[x][y] and not abs(initX - x) > 1:
        if not mapa.foreground[x][y]:
            x -= 1
        elif mapa.foreground[x+1][y]:
            x += 1
        else:
            break
    if abs(initX - x) > 1:
        break
    else:
        rightEdge.append((x, y))
        initX, initY = (x, y)
#
initX, initY = (middleRightmost, comY)
while True:
    initY -= 1
    initValue = mapa.foreground[initX][initY]
    
    x, y = (initX, initY)
    while initValue == mapa.foreground[x][y] and not abs(initX - x) > 1:
        if not mapa.foreground[x][y]:
            x -= 1
        elif mapa.foreground[x+1][y]:
            x += 1
        else:
            break
    if abs(initX - x) > 1:
        break
    else:
        rightEdge.append((x, y))
        initX, initY = (x, y)
#
#
middleTopmost = comY
while mapa.foreground[comX][middleTopmost+1]:
    middleTopmost += 1

print("middleTopmost:", middleTopmost)

topEdge = [(comX, middleTopmost)]

initX, initY = (comX, middleTopmost)
while True:
    initX += 1
    initValue = mapa.foreground[initX][initY]

    x, y = (initX, initY)
    while initValue == mapa.foreground[x][y] and not abs(initY - y) > 1:
        if not mapa.foreground[x][y]:
            y -= 1
        elif mapa.foreground[x][y+1]:
            y += 1
        else:
            break
    if abs(initY - y) > 1:
        break
    else:
        topEdge.append((x, y))
        initX, initY = (x, y)
#
initX, initY = (comX, middleTopmost)
while True:
    initX -= 1
    initValue = mapa.foreground[initX][initY]

    x, y = (initX, initY)
    while initValue == mapa.foreground[x][y] and not abs(initY - y) > 1:
        if not mapa.foreground[x][y]:
            y -= 1
        elif mapa.foreground[x][y+1]:
            y += 1
        else:
            break
    if abs(initY - y) > 1:
        break
    else:
        topEdge.append((x, y))
        initX, initY = (x, y)

#-------------------------------------------------------------------------------

def horizontalLineSlope(pointList):
    x, y, xy, x2 = (0, 0, 0, 0)
    n = len(pointList)

    for i in range(n):
        xi, yi = pointList[i]
        x2 += xi ** 2
        y += yi
        x += xi
        xy += xi * yi

    a = (xy * n - x * y) / (x2 * n - x * x)
    b = (x2 * y - xy * x) / (x2 * n - x * x)
    return (a, b)

def verticalLineSlope(pointList):
    x, y, xy, x2 = (0, 0, 0, 0)
    n = len(pointList)

    for i in range(n):
        yi, xi = pointList[i]
        x2 += xi ** 2
        y += yi
        x += xi
        xy += xi * yi

    a = (xy * n - x * y) / (x2 * n - x * x)
    b = (x2 * y - xy * x) / (x2 * n - x * x)
    return (a, b)

mAverage = 0

m, b = horizontalLineSlope(topEdge)
mAverage += -m / 3

m, b = verticalLineSlope(leftEdge)
mAverage += m / 3

m, b = verticalLineSlope(rightEdge)
mAverage += m / 3

print("mAverage:", mAverage)

#-------------------------------------------------------------------------------

bmp.makeFile(path + image + ".procesada.bmp")
bmpWhiteData = bmp.data.copy()
#mapCopy = SectionRaster(bmpCopy, 8)

for i in range(bmp.start, bmp.start + bmp.width * bmp.height * bmp.bpp, bmp.bpp):
    bmpWhiteData[i:i+3] = (255, 255, 255)

bmpRotatedData = bmpWhiteData.copy()
angle = math.atan2(mAverage, 1)

for i in range(bmp.start, bmp.start + bmp.width * bmp.height * bmp.bpp, bmp.bpp):
    if bmp.data[i] != 255:
        pixelX = (i - bmp.start) // bmp.bpp % bmp.width
        pixelY = (i - bmp.start) // bmp.bpp // bmp.width

        newX = round(
            round(pixelX - math.tan(angle/2) * pixelY) - math.tan(angle/2) *
            round(round(pixelX - math.tan(angle/2) * pixelY) * math.sin(angle) + pixelY)
        )
        newY = round(
            round(pixelX - math.tan(angle/2) * pixelY) * math.sin(angle) + pixelY
        )

        idx = bmp.start + newX * bmp.bpp + newY * bmp.width * bmp.bpp
        if 0 <= newX < bmp.width and 0 <= newY < bmp.height:
            bmpRotatedData[idx:idx+3] = bmp.data[i:i+3]

bmp.data = bmpRotatedData

#-------------------------------------------------------------------------------

mapaBinarizacion = SectionRaster(bmp, 16)

mapaBinarizacion.calculateAverages()

for x in range(mapaBinarizacion.width):
    for y in range(mapaBinarizacion.height):
        if mapaBinarizacion.averages[x][y] < 255:
            blockStart = (mapaBinarizacion.bmp.start +
                          x * mapaBinarizacion.pixelSize * mapaBinarizacion.bmp.bpp +
                          y * mapaBinarizacion.bmp.width * mapaBinarizacion.pixelSize * mapaBinarizacion.bmp.bpp)
            for i in range(mapaBinarizacion.pixelSize):
                for j in range(mapaBinarizacion.pixelSize):
                    idx = (blockStart +
                           i * mapaBinarizacion.bmp.bpp +
                           j * mapaBinarizacion.bmp.width * mapaBinarizacion.bmp.bpp)
                    mapaBinarizacion.bmp.data[idx:idx+3] = (
                        (0, 0, 0) if (mapaBinarizacion.bmp.data[idx] <= mapaBinarizacion.averages[x][y]) else (255, 255, 255)
                        # (0, 0, 0) if (mapaBinarizacion.bmp.data[idx] <= mapaBinarizacion.average) else (255, 255, 255)
                    )

#-------------------------------------------------------------------------------

thinning = True
counter = 0

while thinning:
    counter = 1 - counter
    thinning = False
    whiteIndexes = []

    for i in range(
                    mapaBinarizacion.bmp.start + mapaBinarizacion.bmp.bpp,
                    mapaBinarizacion.bmp.start + mapaBinarizacion.bmp.width * mapaBinarizacion.bmp.height * mapaBinarizacion.bmp.bpp - mapaBinarizacion.bmp.bpp,
                    mapaBinarizacion.bmp.bpp
    ):
        if mapaBinarizacion.bmp.data[i] == 0:
            pixelX = (i - mapaBinarizacion.bmp.start) // mapaBinarizacion.bmp.bpp % mapaBinarizacion.bmp.width
            pixelY = (i - mapaBinarizacion.bmp.start) // mapaBinarizacion.bmp.bpp // mapaBinarizacion.bmp.width

            pixels = [0,
                      mapaBinarizacion.bmp.data[mapaBinarizacion.bmp.findPixelIndex(pixelX, pixelY + 1)],
                      mapaBinarizacion.bmp.data[mapaBinarizacion.bmp.findPixelIndex(pixelX + 1, pixelY + 1)],
                      mapaBinarizacion.bmp.data[mapaBinarizacion.bmp.findPixelIndex(pixelX + 1, pixelY)],
                      mapaBinarizacion.bmp.data[mapaBinarizacion.bmp.findPixelIndex(pixelX + 1, pixelY - 1)],
                      mapaBinarizacion.bmp.data[mapaBinarizacion.bmp.findPixelIndex(pixelX, pixelY - 1)],
                      mapaBinarizacion.bmp.data[mapaBinarizacion.bmp.findPixelIndex(pixelX - 1, pixelY - 1)],
                      mapaBinarizacion.bmp.data[mapaBinarizacion.bmp.findPixelIndex(pixelX - 1, pixelY)],
                      mapaBinarizacion.bmp.data[mapaBinarizacion.bmp.findPixelIndex(pixelX - 1, pixelY + 1)]]
            pixels = [k/255 for k in pixels]
            ti = [1, 2, 3, 4, 5, 6, 7, 8, 1]
            transitions = sum([1 for k in range(len(ti)-1) if pixels[ti[k]] - pixels[ti[k+1]] == 1])
            blackPixels = 8 - sum(pixels)

            if (
                2 <= blackPixels <= 6 and transitions == 1 and (
                    counter == 1 and pixels[1] + pixels[3] + pixels[5] > 0 and pixels[3] + pixels[5] + pixels[7] > 0 or
                    counter == 0 and pixels[1] + pixels[3] + pixels[7] > 0 and pixels[1] + pixels[5] + pixels[7] > 0
                )
            ):
                whiteIndexes.append(i)
                thinning = True

    for k in whiteIndexes:
        mapaBinarizacion.bmp.data[k:k+3] = (255, 255, 255)

#-------------------------------------------------------------------------------

mapaBinarizacion.bmp.makeFile(path + image + ".procesada.bmp")
print(path + image + ".procesada.bmp")
print("")
