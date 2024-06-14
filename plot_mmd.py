import codecs
from os import environ
import struct
import binascii
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from numpy.lib import math
import re


class BoneData:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0
        self.parent = 0
        self.child = 0
        self.name = ""

class X_Direction:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0

class Z_Direction:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0

class FrameData:
    def __init__(self):
        self.name = ""
        self.num = 0

        self.x = 0.0
        self.y = 0.0
        self.z = 0.0

        self.qx = 0.0
        self.qy = 0.0
        self.qz = 0.0
        self.qw = 0.0

        self.parameta = ""

class Frame_DanceRota:
    def __init__(self):
        self.name = ""
        self.num = 0

        self.posi = [0.0, 0.0, 0.0]

        self.rota = [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]



#読み込むデータのバイト数
def return_byte(num, f):
    text = int.from_bytes(f.read(num), byteorder='little')
    return text

#読み込んで文字列で返す
def read_str(num, f, uni):
    text = f.read(num)
    if uni == 8 :
        text = text.decode(encoding='utf-8')
    elif uni == 16 :
        text = text.decode(encoding='utf-16')
    elif uni == 932 :
        text = text.decode(encoding='cp932')
    elif uni == 'jis' :
        text = text.decode(encoding='shift_jis')
    return text

#読み込んで文字列で表す
def print_str(num, f, uni):
    print(str(read_str(num, f, uni)))

#読み込んでintで返す
def read_int(num, f):
    text = int.from_bytes(f.read(num), byteorder='little')
    return text

#読み込んでintで表す
def print_int(num, f):
    print(str(read_int(num, f)))

#読み込んでfloatで返す
def read_float(num, f):
    text = struct.unpack('<f', f.read(num))[0]
    return text

#読み込んでfloatで表す
def print_float(num, f):
    print(str(read_float(num, f)))

#何バイトかわかっている時スキップする
def skip(num, f):
    text = f.read(num)

#skipのテスト、中身を表示する
def test_skip(num, f):
    text = f.read(num)

#スキップするバイト数を読み込んでからスキップ
def read_skip(f):
    num = return_byte(4, f)
    skip(num, f)

#read_skipのテスト、文字列で確認する
def test_read_skip(f):
    num = return_byte(4, f)
    print(num)
    #text = f.read(num)
    print_str(num, f, 16)
    #read_int(num, f)

#頂点の読み込み
def skip_vertex(BoneIndexSize, f):
    #position(3), normal(3), uv(2)
    for i in range(8):
        skip(4, f)

    #頂点のウェイト変換方式
    weight = read_int(1, f)
    #weightの値で読み込み方が変わる
    if weight == 0:
        skip(BoneIndexSize, f)

    elif weight == 1:
        skip(BoneIndexSize, f)
        skip(BoneIndexSize, f)
        skip(4, f)

    elif weight == 2:
        for i in range(4):
            skip(BoneIndexSize, f)
        for i in range(4):
            skip(4, f)

    elif weight == 3:
        skip(BoneIndexSize, f)
        skip(BoneIndexSize, f)
        skip(4, f)
        for i in range(9):
            skip(4, f)
    
    else :
        print("Error in skip_vertex")
    
    skip(4, f) #エッジ倍率

#面の読み込み
def skip_face(VertexIndexSize, f):
    for i in range(3): #頂点三個で一面
        skip(VertexIndexSize, f) #頂点インデックス

#テクスチャの読み込み
def skip_texture(f):
    read_skip(f) #バイト数を読んでから名前を読み込み

#マテリアルの読み込み
def skip_material(TextureIndexSize, f):
    read_skip(f)
    read_skip(f) #マテリアルの名前

    for i in range(11):
        skip(4, f) #拡散反射光(4), 鏡面反射(係数)(4), 環境光(3)
    skip(1, f) #bitflag

    for i in range(5):
        skip(4, f) #エッジ色(4), エッジサイズ(1)

    skip(TextureIndexSize, f)
    skip(TextureIndexSize, f) #テクスチャのインデックス
    skip(1, f) #スフィアモード
    toonflag = read_int(1, f)

    if toonflag == 0:
        skip(TextureIndexSize, f) #toonテクスチャのインデックス
    elif toonflag == 1:
        skip(1, f) #共有toonテクスチャ
    else :
        print("Error in skip_material")
    
    read_skip(f) #メモ
    skip(4, f) #対応している面(頂点の数), 3の倍数になるはず
    
#ボーンの読み込み
def read_bone(BoneIndexSize, f, bone, x_dir, z_dir, bone_nameindex_dict):
    #read_skip(f)
    bone.name = read_str(return_byte(4, f), f, 16)
    read_skip(f) #boneの名前
    #print(bone.name)

    bone_nameindex_dict[bone.name] = 0
    

    x = read_float(4, f)
    y = read_float(4, f)
    z = read_float(4, f)
    #boneClassに追加
    bone.x = x
    bone.y = y
    bone.z = z
    #print("position = (" + str(x) + ", " + str(y) + ", " + str(z) + ")")

    parentbone = read_int(BoneIndexSize, f)
    bone.parent = parentbone
    #print("親ボーンのインデックス: " + str(parentbone))
    #print("/変形階層/")
    #print_int(4, f) #変形階層
    skip(4, f)

    text = read_int(2, f)
    #16進数の数字表示が出る
    #print("bitflag")
    #print('{:#06x}'.format(text))
    flag = [0x0001, 0x0002, 0x0004, 0x0008, 0x0010, 0x0020, 0x0080, 0x0100, 0x0200, 0x0400, 0x0800, 0x1000, 0x2000]
    sample = list(range(13))
    for i in range(len(flag)):
        if(text & flag[i] == 0):
            sample[i] = 0
        else:
            sample[i] = 1
   
    #bitflag
    flag_test(sample, BoneIndexSize, f, x_dir, z_dir)
    #print("\n-----------------------\n")

    if(sample[0] == 0):
        return 0
    else:
        return 1
    
    
def flag_test(sample, BoneIndexSize, f, x_dir, z_dir):
    
    if(sample[0] == 0):
        x = read_float(4, f)
        y = read_float(4, f)
        z = read_float(4, f)
        #print("接続先座標オフセット = (" + str(x) + ", " + str(y) + ", " + str(z) + ")")
    else:
        text = read_int(BoneIndexSize, f)
        #print("接続先ボーンインデックス: " + str(text))
         #接続先ボーンのインデックス
    
    if(sample[7] == 1 or sample[8] == 1):
        text = read_int(BoneIndexSize, f)
        #print("付与親ボーンのボーンインデックス: " + str(text))
        #print_int(BoneIndexSize, f) #付与親ボーンのボーンインデックス
        text = read_float(4, f)
        #print("付与率: " + str(text))
        #print_float(4, f) #付与率

    if(sample[9] == 1):
        x = read_float(4, f)
        y = read_float(4, f)
        z = read_float(4, f)
        #print("軸の方向ベクトル = (" + str(x) + ", " + str(y) + ", " + str(z) + ")")
    
    if(sample[10] == 1):
        x = read_float(4, f)
        y = read_float(4, f)
        z = read_float(4, f)
        x_dir.x = x
        x_dir.y = y
        x_dir.z = z
        #print("x軸の方向ベクトル = (" + str(x) + ", " + str(y) + ", " + str(z) + ")")
        x = read_float(4, f)
        y = read_float(4, f)
        z = read_float(4, f)
        z_dir.x = x
        z_dir.y = y
        z_dir.z = z
        #print("z軸の方向ベクトル = (" + str(x) + ", " + str(y) + ", " + str(z) + ")")

    if(sample[12] == 1):
        text = read_int(4, f)
        #print("key値: " + str(text))
    
    if(sample[5] == 1):
        text = read_int(BoneIndexSize, f)
        #print("IKターゲットのボーンインデックス: " + str(text))
        #print_int(BoneIndexSize, f) #IKターゲットのボーンインデックス
        text = read_int(4, f)
        #print("IKループ回数: " + str(text))
        #print_int(4, f) #IKループ回数
        text = read_float(4, f)
        #print("制限角度: " + str(text))
        #print_float(4, f)
        
        IKlink = read_int(4, f) #IKリンク数
        #print("IKリンク数: " + str(IKlink)) 
        for i in range(IKlink):
            text = read_int(BoneIndexSize, f)
            #print("リンクのボーンインデックス: " + str(text))
            #print_int(BoneIndexSize, f) #IKターゲットのボーンインデックス
            
            rad = read_int(1, f)
            #print("角度制限" + str(rad))
            #print(str(rad))

            if(rad == 1):
                x = read_float(4, f)
                y = read_float(4, f)
                z = read_float(4, f)
                #print("下限ラジアン角 = (" + str(x) + ", " + str(y) + ", " + str(z) + ")")
                x = read_float(4, f)
                y = read_float(4, f)
                z = read_float(4, f)
                #print("上限ラジアン角 = (" + str(x) + ", " + str(y) + ", " + str(z) + ")")

def quart(qx, qy, qz, qw):
    m = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]

    m[0][0] = 1.0 - 2 * qy * qy - 2.0 * qz * qz
    m[0][1] = 2.0 * qx * qy + 2.0 * qw * qz
    m[0][2] = 2.0 * qx * qz - 2.0 * qw * qy

    m[1][0] = 2.0 * qx * qy - 2.0 * qw * qz
    m[1][1] = 1.0 - 2.0 * qx * qx - 2.0 * qz * qz
    m[1][2] = 2.0 * qy * qz + 2.0 * qw * qx

    m[2][0] = 2.0 * qx * qz + 2.0 * qw * qy
    m[2][1] = 2.0 * qy * qz - 2.0 * qw * qx
    m[2][2] = 1.0 - 2.0 * qx * qx - 2.0 * qy * qy
    #m[0][0] = qw * qw +qx * qx - qy * qy - qz * qz
    #m[0][1] = 2.0 * (qx * qy +  qw * qz)
    #m[0][2] = 2.0 * (qw * qz - 2.0 * qw * qy)

    #m[1][0] = 2.0 * qx * qy - 2.0 * qw * qz
    #m[1][1] = 1.0 - 2.0 * qx * qx - 2.0 * qz * qz
    #m[1][2] = 2.0 * qy * qz + 2.0 * qw * qx

    #m[2][0] = 2.0 * qx * qz + 2.0 * qw * qy
    #m[2][1] = 2.0 * qy * qz - 2.0 * qw * qx
    #m[2][2] = 1.0 - 2.0 * qx * qx - 2.0 * qy * qy


    return m

#行列計算のメソッド
#自分の位置、親の位置、回転行列、方向ベクトル、親の今フレームの位置
def calculate_position(my_vector, parent_vector, rotation_matrix, move_vector, parent_position):
    direction_vector = np.subtract(my_vector, parent_vector)
    answer = np.matmul(direction_vector, rotation_matrix) #回転行列 * 方向ベクトル
    answer = np.add(answer, move_vector) # + 移動ベクトル
    answer = np.add(answer, parent_position) # + 親の位置
    #answer[2] = -answer[2]

    return answer

#行列計算のメソッド
#自分の位置、親の位置、自分の回転行列、親の回転行列、方向ベクトル、親の今フレームの位置
def mul_calculate_position(my_vector, parent_vector, myrotation_matrix, parentrotation_matrix, move_vector, parent_position):
    myrotation_matrix = np.matmul(myrotation_matrix, parentrotation_matrix) #親　* 自分

    answer = calculate_position(my_vector, parent_vector, parentrotation_matrix, move_vector, parent_position)
    """direction_vector = np.subtract(my_vector, parent_vector)
    answer = np.matmul(direction_vector, myrotation_matrix) #回転行列 * 方向ベクトル
    answer = np.add(answer, move_vector) # + 移動ベクトル
    answer = np.add(answer, parent_position) # + 親の位置"""

    return answer

####################################################################################################################

bone_nameindex_dict = {}

#pmx読み込み
f = open('Tda式初音ミク・アペンド_Ver1.10.pmx', 'rb')

#headerの読み込み
skip(4, f) #PMX
skip(4, f) #2.0
skip(1, f) #8

EncodeType        = read_int(1, f) #0
UVNum             = read_int(1, f) #0
VertexIndexSize   = read_int(1, f) #2
TextureIndexSize  = read_int(1, f) #1
MaterialIndexSize = read_int(1, f) #1
BoneIndexSize     = read_int(1, f) #2
MorphIndexSize    = read_int(1, f) #1
RigidIndexSize    = read_int(1, f) #1

read_skip(f) #モデル名
read_skip(f) #モデル名英語
read_skip(f) #コメント
read_skip(f) #コメント英語

#頂点の読み込み
VertexNum = read_int(4, f) #頂点数 25164
for i in range(VertexNum):
    skip_vertex(BoneIndexSize, f) #頂点の個数分skip

#面の読み込み
FaceNum = int(read_int(4, f) / 3) #面の数 100233
for i in range(FaceNum):
    skip_face(VertexIndexSize, f) #面の数分skip


#テクスチャの読み込み
TextureNum = read_int(4, f) #テクスチャの数 13
for i in range(TextureNum):
    skip_texture(f) #テクスチャの数分skip


#材質の読み込み
MaterialNum = read_int(4, f) #マテリアルの数 17
for i in range(MaterialNum):
    skip_material(TextureIndexSize, f) #マテリアルの数だけskip


#ボーンの読み込み
BoneNum = read_int(4, f)
print(BoneNum)

#boneを保存
bone = list(range(BoneNum))
x_dir = list(range(BoneNum))
z_dir = list(range(BoneNum))

bone_indexname_dict = dict()
access = list(range(BoneNum))

for i in range(BoneNum):
    #print("boneindex: " , i)
    
    #print()
    bone[i] = BoneData()
    x_dir[i] = X_Direction()
    z_dir[i] = Z_Direction()
    access[i] = read_bone(BoneIndexSize, f, bone[i], x_dir[i], z_dir[i], bone_nameindex_dict)
    #print("position = (" + str(bone[i].x) + ", " + str(bone[i].y) + ", " + str(bone[i].z) + ")")
    #print("親ボーンのインデックス: " + str(bone[i].parent))
    bone_nameindex_dict[bone[i].name] = i #bone名とindexを対応
    #print("[", i, "]", bone[i].name)
    bone_indexname_dict[i] = bone[i].name
    

#boneの子と親の連想配列
child_parent_dict = {}

for i in range(BoneNum):
    child_parent_dict[i] = bone[i].parent

#for i in child_parent_dict.keys():
#    if(bone[i].parent != 65535):
#        bone[bone[i].parent].child = i

#for i in range(BoneNum):
#    print("parent: ", i, ": child: ", bone[i].child)



####################################################################################################################

all_frames = [[0] * 206 for i in range(3701)]
rotation_matrix = [[0] * 206 for i in range(3701)]
"""for i in range(len(rotation_matrix)):
    for j in range(len(rotation_matrix[i])):
        rotation_matrix = np.identity(3)"""

                
#vmd読み込み
fv = open('HIASOBI_motion_Light.vmd', 'rb')

skip(30, fv) #モーションデータ名前

skip(20, fv) #モデル名

FrameNum = read_int(4, fv) #フレーム数 140958
print(FrameNum)
print("\n")

dance = list(range(FrameNum))
count = 0
tmp_m = list()
bone_m = list()


for i in range(FrameNum):
    dance[i] = FrameData()

    dance[i].name = read_str(15, fv, 932).rstrip('\x00') #ボーン名

    #if(i < 266):
       # print("dance[", i, "]", dance[i].name)


    dance[i].num = read_int(4, fv) #フレーム番号

    dance[i].x = read_float(4, fv)
    dance[i].y = read_float(4, fv)
    dance[i].z = read_float(4, fv) #position

    dance[i].qx = read_float(4, fv)
    dance[i].qy = read_float(4, fv)
    dance[i].qz = read_float(4, fv)
    dance[i].qw = read_float(4, fv) #クオータニオン

    tmp_m.append(quart(dance[i].qx, dance[i].qy, dance[i].qz, dance[i].qw)) #クオータニオンの行列化
    bone_m.append(tmp_m[i])

    skip(64, fv) #補完パラメータ
    if(dance[i].num == 0):
        count += 1  #0フレームは265個

    #if(dance[i].num == 0):
        #bone_nameindex_dict[dance[i].name] = i #bone名とindexを紐付ける(最初のみ)

    num = int(dance[i].num / 2) #フレームは2の倍数なので
    #all_frames[フレーム数/2(~3701)][ボーン数(~265)] にそれぞれのpositionと回転行列を保存
    if(dance[i].name not in bone_nameindex_dict.keys()):
        #print("ないよ")
        a = 1
    else:
        
        all_frames[num][bone_nameindex_dict[dance[i].name]] = Frame_DanceRota() 
        all_frames[num][bone_nameindex_dict[dance[i].name]].posi = [dance[i].x, dance[i].y, dance[i].z]
        all_frames[num][bone_nameindex_dict[dance[i].name]].rota = bone_m[i]

    
    if(dance[i].name not in bone_nameindex_dict.keys()):
        a = 1
    elif(bone_nameindex_dict[dance[i].name] == 2 or bone_nameindex_dict[dance[i].name] == 4 or bone_nameindex_dict[dance[i].name] == 11 ):
        #print(dance[i].name, ": (", dance[i].x, dance[i].y, dance[i].z, ")")
        #print(bone_m[i])
        count += 1


####################################################################################################################
#フレーム0の再現
#npbone = list()
#npdance_posi = list()
#npdance_rota = list()
npbone = {} #pmxの骨の位置
npdance_posi = {} #vmdの方向ベクトル
npdance_rota = {} #vmdの回転行列
npafter = {} #移動後の骨の位置
npold = {} #移動後の骨の位置
after = list() #移動後の骨の位置
m = list()
bone_dict = {}
dance_dict = {}
rota_dict = {}
count = -1
miku_animation = list() #plotする用のlist, 前がフレーム数で後ろは点
dance_tmp = list()
rota_tmp = list()

#print(all_frames)


#dance時のboneのポジションと回転行列
for i in range(FrameNum): 
    dance_dict[dance[i].name] = [dance[i].x, dance[i].y, dance[i].z]
    rota_dict[dance[i].name] = [bone_m[i]]
    #print("フレーム数 : ", dance[i].num)
    #print(dance[i].name, " : (", dance_dict[dance[i].name], "), ", rota_dict[dance[i].name.rstrip('\x00')])



#フレームは0~7400までの偶数 -> 3501
print()
#for i in range (BoneNum):
#    for j in range(265):
#        if(bone[i].name == dance[j].name): #bone名が同じ時
#            count += 1
#            npbone.append([bone[i].x, bone[i].y, bone[i].z]) #boneのpositionを計算用listに保存
#            npdance_posi.append([dance[j].x, dance[j].y, dance[j].z]) #danceのpositionを計算用listに保存
#            npdance_rota.append([[dance[j].qx, 0, 0, 0], 
#                                 [0, dance[j].qy, 0, 0], 
#                                 [0, 0, dance[j].qz, 0], 
#                                 [0, 0, 0, dance[j].qw]]) #danceのrotationを計算用listに保存
#            if(bone[i].parent != 65535):
#                print("親あり")
#            else:
#                ans.append(np.add(np.matmul(npdance_rota[count], npbone[count]), npdance_posi[count]))
#                print(ans[count])

#print(count)

#boneの子は手打ち
for i in range(BoneNum):
    bone[i].child = 65535

bone[1].child = 2
bone[2].child = 3
bone[3].child = 4
bone[4].child = 11
bone[11].child = 12
bone[12].child = 18
bone[13].child = 145
bone[18].child = 19
bone[19].child = 65535
bone[32].child = 33
bone[33].child = 34
bone[34].child = 35
bone[35].child = 36
bone[36].child = 42
bone[42].child = 43
bone[43].child = 47
bone[70].child = 71
bone[71].child = 72
bone[72].child = 73
bone[73].child = 74
bone[74].child = 80
bone[80].child = 81
bone[81].child = 85
bone[145].child = 146
bone[146].child = 147
bone[147].child = 148
bone[149].child = 150
bone[150].child = 151
bone[151].child = 152
#計算

for i in range(BoneNum):
    if(bone[i].child != 65535 and access[i] == 0 and (bone[i].name != "操作中心" and bone[i].name != "全ての親" 
    and bone[i].name != "センター" and bone[i].name != "グルーブ" and bone[i].name != "腰" and 
    bone[i].name != "下半身" and bone[i].name != "腰キャンセル右" and bone[i].name != "腰キャンセル左")):
        #print("bone[", i, "]")
        #print(bone[i].name)
        #print("bone[", bone[i].child, "].parent = ")
        bone[bone[i].child].parent = bone[i].parent

    #if(access[i] == 0 and bone[i].child != 65535):
    #    bone[bone[i].child].parent = bone[i].parent

#boneのポジションと名前
for i in range(BoneNum):
    bone_dict[bone[i].name] = [bone[i].x, bone[i].y, bone[i].z]
    if(bone[i].parent != 65535):
        print("bone[", i, "]", bone[i].name, " -> 親", "bone[", bone[i].parent, "]", bone[bone[i].parent].name )
    else: 
        print("bone[", i, "]", bone[i].name, " -> 親なし")

    if(bone[i].name not in dance_dict.keys()):
        print("↑boneにあるがdanceに無い")
    print()


#for i in range(BoneNum):
#    print(i, bone[i].name)
##    print("parent: ", bone[i].parent)
#    print("child: ", bone[i].child)


bone_loop = 71

#腰：４、上半身：11
#フレーム0
#方向ベクトル
answer = list(range(BoneNum))
direction = 0
for i in range(BoneNum):
    answer[i] = list()


#表示するフレーム数
frame_loop = 800

center_dir = list()


for i in range(frame_loop):
    for j in range(BoneNum):
        #今のボーンの名前を保存
        bone_name = bone_indexname_dict[j]
        if(bone[j].parent != 65535):
            parent_name = bone_indexname_dict[bone[j].parent]

        #全ての親の時は処理が特別
        if(j == bone_nameindex_dict["全ての親"]):
            #初期位置を代入
            npbone[bone_name] = bone_dict[bone_name]
            #初期位置を計算用に代入
            npafter[bone_name] = npbone[bone_name]
            #i=0の時にはもう保存できている
            if(i != 0):
                all_frames[i][j] = Frame_DanceRota() 
                all_frames[i][j].rota = all_frames[0][j].rota
                all_frames[i][j].posi = all_frames[0][j].posi

            #方向ベクトル*回転行列+移動の位置
            #npafter[bone_name] = np.matmul(all_frames[i][j].rota, npafter[bone_name])
            #npafter[bone_name] = np.matmul(npafter[bone_name], all_frames[i][j].rota)
            #npafter[bone_name] = np.add(npafter[bone_name], all_frames[i][j].posi)
            npafter[bone_name] = calculate_position(npbone[bone_name], [0, 0, 0], all_frames[i][j].rota, 
                                        all_frames[i][j].posi, [0, 0, 0])

            answer[j].append(npafter[bone_name])

        
        elif(bone_name == "センター" or bone_name == "グルーブ" or bone_name == "腰" or bone_name == "上半身" or 
        bone_name == "上半身2" or bone_name == "下半身" or bone_name == "首" or bone_name == "頭"
         or bone_name == "右肩" or bone_name == "右腕" or bone_name == "右腕捩" or bone_name == "右ひじ"
         or bone_name == "右手捩" or bone_name == "右手首" 
         or bone_name == "左肩" or bone_name == "左腕" or bone_name == "左腕捩" or bone_name == "左ひじ"
         or bone_name == "左手捩" or bone_name == "左手首" 
         or bone_name == "腰キャンセル右" or bone_name == "右足" or bone_name == "右ひざ" or bone_name == "右足首"
         or bone_name == "腰キャンセル左" or bone_name == "左足D" or bone_name == "左足" or bone_name == "左ひざD" or bone_name == "左ひざ" or bone_name == "左足首"):
            
            if(all_frames[i][j] == 0): #フレームが0しかない時
                all_frames[i][j] = Frame_DanceRota() 
                all_frames[i][j].posi = all_frames[0][j].posi
                all_frames[i][j].rota = all_frames[0][j].rota
            
            if(i == 0):
                print("[ ", j, " ]", bone_name)
                print("親 -> [ ", bone[j].parent, " ]", parent_name)
                print("自分の回転行列: \n", all_frames[i][j].rota)
                print("親の回転行列: \n", all_frames[i][bone[j].parent].rota)

                
                #初期位置の保存
                npbone[bone_name] = bone_dict[bone_name]
                #計算用に保存
                npafter[bone_name] = npbone[bone_name]

                if(bone[j].parent != 65535): #親がある時に親の回転行列もかける
                    all_frames[i][j].rota = np.matmul(all_frames[i][j].rota, all_frames[i][bone[j].parent].rota)
                    #npafter[bone_name] = mul_calculate_position(npbone[bone_name], npbone[parent_name], all_frames[i][j].rota, 
                    #                            all_frames[i][bone[j].parent].rota, all_frames[i][j].posi, npafter[parent_name])
                
                #else:
                #    npafter[bone_name] = calculate_position(npbone[bone_name], npbone[parent_name], all_frames[i][j].rota, 
                #                       all_frames[i][j].posi, npafter[parent_name])



                #方向ベクトル = 自分の初期位置 - 親の初期位置
                direction = np.subtract(npbone[bone_name], npbone[parent_name])
                
                #位置ベクトル = 回転行列 * 方向ベクトル + 移動ベクトル + 親の位置
                #npafter[bone_name] = np.matmul(direction, all_frames[i][j].rota)
                #npafter[bone_name] = np.add(npafter[bone_name], all_frames[i][j].posi)
                #npafter[bone_name] = np.add(npafter[bone_name], npafter[parent_name])
                npafter[bone_name] = calculate_position(npbone[bone_name], npbone[parent_name], all_frames[i][bone[j].parent].rota, 
                                        all_frames[i][j].posi, npafter[parent_name])
                
                #print("[", j, "] ", bone_name, "\n", "[", bone[j].parent, "] ", parent_name, "\n")

                
                
                print("回転行列: \n", all_frames[i][j].rota)
                print("初期位置: ", bone_dict[bone_name])
                print("親の初期位置: ", bone_dict[parent_name])
                print("方向ベクトル: ", direction)
                print("移動ベクトル: \n", all_frames[i][j].posi)
                print("計算後位置: ", npafter[bone_name])
                print()

                #if(bone_name == "腰キャンセル右" or bone_name == "腰キャンセル左"):
                #    print(i, "frame, ", bone_name, ", ", parent_name, "の座標: \n", npafter[parent_name])


                answer[j].append(npafter[bone_name])
                #[ 0.11986237 12.05423243 -2.53934672]
                 #[ 0.11348504 11.27998638 -1.71524689]
                # [ 0.11986237 12.05423243 -2.53934672]

            
            
            else: #i != 0の時
                if(bone[j].parent != 65535): #親がある時に親の回転行列もかける
                    all_frames[i][j].rota = np.matmul(all_frames[i][j].rota, all_frames[i][bone[j].parent].rota)
                    #npafter[bone_name] = mul_calculate_position(npbone[bone_name], npbone[parent_name], all_frames[i][j].rota, 
                    #                            all_frames[i][bone[j].parent].rota, all_frames[i][j].posi, npafter[parent_name])
                
                """else:
                    npafter[bone_name] = calculate_position(npbone[bone_name], npbone[parent_name], all_frames[i][j].rota, 
                                       all_frames[i][j].posi, npafter[parent_name])"""
 
                  
                    #方向ベクトルは初期位置の自分のposition - 親のposition
                #if(bone[j].parent != 65535):
                #    direction = np.subtract(npbone[bone_name], npbone[parent_name])
                #else:                        
                #    direction = 0
                   
                #位置ベクトル = 回転行列 * 方向ベクトル + 移動ベクトル + 親の位置
                #npafter[bone_name] = np.matmul(direction, all_frames[i][j].rota)
                #npafter[bone_name] = np.add(npafter[bone_name], all_frames[i][j].posi)
                #npafter[bone_name] = np.add(npafter[bone_name], npafter[parent_name])
                npafter[bone_name] = calculate_position(npbone[bone_name], npbone[parent_name], all_frames[i][bone[j].parent].rota, 
                                        all_frames[i][j].posi, npafter[parent_name])

                answer[j].append(npafter[bone_name])  

    #print("フレーム", i)
    #print("上半身 = ", npafter["上半身"])
    #print("上半身2 = ", npafter["上半身2"])
    #print("下半身 = ", npafter["下半身"])
    #print("首 = ", npafter["首"])


x = list(range(2))
y = list(range(2))
z = list(range(2))
# 3Dでプロット
fig = plt.figure(figsize=(6, 6))
ax = fig.add_subplot(111, projection='3d')

sleepTime = 0.005  # １フレーム表示する時間[s]
bone_loop = BoneNum

show = 0 #1フレームのみを見たい時

#frame_loop = 300
for i in range(frame_loop):
    for j in range(bone_loop):
        if(j == 11 or j == 12 or j == 13 or j == 18 or j == 19 or j == 33 or j == 35 
        or j == 36 or j == 42 or  j== 43 or j == 47 or j == 71 or j == 73 or j == 74
        or j == 80 or j == 81 or j == 85 or j == 145 or j == 146 or j == 147 or j == 148
        or j == 149 or j == 150 or j == 151 or j == 152): #頭、首、上半身*2、腰、下半身だけでやる

            show = i
            print(i, "frame, ", j, "bone")  
            if(bone[j].parent != 65535):
                """x = [answer[j][i][0], answer[bone[j].parent][i][0]]
                y = [answer[j][i][1], answer[bone[j].parent][i][1]]
                z = [answer[j][i][2], answer[bone[j].parent][i][2]]"""
                x = [answer[j][show][0], answer[bone[j].parent][show][0]]
                y = [answer[j][show][1], answer[bone[j].parent][show][1]]
                z = [answer[j][show][2], answer[bone[j].parent][show][2]]

                if(j == 147):
                    ax.plot(x, z, y, "o-", color="#000000", ms=4, mew=0.1)
                elif(33 <= j and j <= 47):
                    ax.plot(x, z, y, "o-", color="#aa0000", ms=4, mew=0.1)
                elif(71 <= j and j <= 85):
                    ax.plot(x, z, y, "o-", color="#0000aa", ms=4, mew=0.1)

                else:
                    ax.plot(x, z, y, "o-", color="#00aa00", ms=4, mew=0.1)
                    
            else: 
                """x = [answer[j][i][0], answer[j][i][0]]
                y = [answer[j][i][1], answer[j][i][1]]
                z = [answer[j][i][2], answer[j][i][2]]"""
                x = [answer[j][show][0], answer[j][show][0]]
                y = [answer[j][show][1], answer[j][show][1]]
                z = [answer[j][show][2], answer[j][show][2]]

                ax.plot(x, z, y, "o-", color="#00aa00", ms=4, mew=0.1)
            
        
        
            #xの方向ベクトルのプロット
            #if(x_dir[i].x != 0 and x_dir[i].y != 0 and x_dir[i].z != 0):
            #    x = [bone[i].x, bone[i].x + x_dir[i].x]
            #    y = [bone[i].y, bone[i].y + x_dir[i].y]
            #    z = [bone[i].z, bone[i].z + x_dir[i].z]
            #    ax.plot(x, y, z, "o-", color="#ff0000", ms=4, mew=0.1) 

            #zの方向ベクトルのプロット
            #if(z_dir[i].x != 0 and z_dir[i].y != 0 and z_dir[i].z != 0):
            #    x = [bone[i].x, bone[i].x + z_dir[i].x]
            #    y = [bone[i].y, bone[i].y + z_dir[i].y]
            #    z = [bone[i].z, bone[i].z + z_dir[i].z]
            #    ax.plot(x, y, z, "o-", color="#0000ff", ms=4, mew=0.1)

    # 軸ラベル
    ax.set_xlabel('x')
    ax.set_ylabel('z')
    ax.set_zlabel('y')

    #軸の範囲
    ax.set_xlim(-10, 10)
    ax.set_ylim(-10, 10)
    ax.set_zlim(0, 20)

    ax.set_box_aspect((5, 5, 5))

    # 表示
    ax.plot(x, y, z)
    #plt.show()
    plt.draw()
    plt.pause(sleepTime)
    plt.cla()
    
for i in range(266):
    print("dance[", i, "]", dance[i].name)

#boneのポジションと名前
for i in range(BoneNum):
    bone_dict[bone[i].name] = [bone[i].x, bone[i].y, bone[i].z]
    if(bone[i].parent != 65535):
        print("bone[", i, "]", bone[i].name, " -> 親", "bone[", bone[i].parent, "]", bone[bone[i].parent].name )
    else: 
        print("bone[", i, "]", bone[i].name, " -> 親なし")

    if(bone[i].name not in dance_dict.keys()):
        print("↑boneにあるがdanceに無い")
    print()