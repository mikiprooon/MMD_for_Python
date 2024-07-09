import codecs
import struct

header = list()
data = list(range(10))
#読み込み
f = open('HIASOBI_motion_Light.vmd', 'rb')


header.append(f.read(30))
header[0] = header[0].decode()
print(str(header[0]))

header.append(f.read(20))
header[1] = header[1].decode(encoding='cp932')
print(header[1])
#binary_str = codecs.decode(header[1], "utf-8")
#print(str(binary_str,'utf-8'

header.append(int.from_bytes(f.read(4), byteorder='little'))
print(str(header[2]))
print("\n")

for i in range(10000):
    data[0] = f.read(15)
    data[0] = data[0].decode(encoding='cp932')
    print("ボーン名: " + str(data[0]))

    data[1] = int.from_bytes(f.read(4), byteorder='little')
    print("フレーム番号: " + str(data[1]))

    data[2] = struct.unpack('<f', f.read(4))[0]
    data[3] = struct.unpack('<f', f.read(4))[0]
    data[4] = struct.unpack('<f', f.read(4))[0]
    
    print("position = " + "(" + str(data[2]) + ", "+ str(data[3]) + ", "+ str(data[4]) + ")")
    

    data[5] = struct.unpack('<f', f.read(4))[0]
    data[6] = struct.unpack('<f', f.read(4))[0]
    data[7] = struct.unpack('<f', f.read(4))[0]
    data[8] = struct.unpack('<f', f.read(4))[0]

    print("rotation = " + "(" + str(data[5]) + ", "+ str(data[6]) + ", "+ str(data[7]) + ", "+ str(data[8]) + ")")

    data[9] = f.read(64)
    #data[9] = data[9].decode(encoding='cp932')
    #print("補間パラ: " + str(data[9]))

    print("\n")

