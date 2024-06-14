import codecs
from os import environ
import struct
import binascii

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
def read_bone(BoneIndexSize, f):
    print_str(return_byte(4, f), f, 16)
    read_skip(f) #boneの名前

    x = read_float(4, f)
    y = read_float(4, f)
    z = read_float(4, f)
    print("position = (" + str(x) + ", " + str(y) + ", " + str(z) + ")")

    print("親ボーンのインデックス: " + str(read_int(BoneIndexSize, f)))
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
        
        print("フラグ; ", sample[i], ", ", flag[i])
    #bitflag
    flag_test(sample, BoneIndexSize, f)
    print("\n-----------------------\n")
    
    
    
def flag_test(sample, BoneIndexSize, f):
    
    if(sample[0] == 0):
        x = read_float(4, f)
        y = read_float(4, f)
        z = read_float(4, f)
        print("接続先座標オフセット = (" + str(x) + ", " + str(y) + ", " + str(z) + ")")
    else:
        print("接続先ボーンインデックス: " + str(read_int(BoneIndexSize, f)))
         #接続先ボーンのインデックス
    
    if(sample[7] == 1 or sample[8] == 1):
        print("付与親ボーンのボーンインデックス: " + str(read_int(BoneIndexSize, f)))
        #print_int(BoneIndexSize, f) #付与親ボーンのボーンインデックス
        print("付与率: " + str(read_float(4, f)))
        #print_float(4, f) #付与率

    if(sample[9] == 1):
        x = read_float(4, f)
        y = read_float(4, f)
        z = read_float(4, f)
        print("軸の方向ベクトル = (" + str(x) + ", " + str(y) + ", " + str(z) + ")")
    
    if(sample[10] == 1):
        x = read_float(4, f)
        y = read_float(4, f)
        z = read_float(4, f)
        print("x軸の方向ベクトル = (" + str(x) + ", " + str(y) + ", " + str(z) + ")")
        x = read_float(4, f)
        y = read_float(4, f)
        z = read_float(4, f)
        print("z軸の方向ベクトル = (" + str(x) + ", " + str(y) + ", " + str(z) + ")")

    if(sample[12] == 1):
        print("key値: " + str(read_int(4, f)))
    
    if(sample[5] == 1):
        print("IKターゲットのボーンインデックス: " + str(read_int(BoneIndexSize, f)))
        #print_int(BoneIndexSize, f) #IKターゲットのボーンインデックス
        print("IKループ回数: " + str(read_int(4, f)))
        #print_int(4, f) #IKループ回数
        print("制限角度: " + str(read_float(4, f)))
        #print_float(4, f)
        
        IKlink = read_int(4, f) #IKリンク数
        print("IKリンク数: " + str(IKlink)) 
        for i in range(IKlink):
            print("リンクのボーンインデックス: " + str(read_int(BoneIndexSize, f)))
            #print_int(BoneIndexSize, f) #IKターゲットのボーンインデックス
            
            rad = read_int(1, f)
            print("角度制限" + str(rad))
            #print(str(rad))

            if(rad == 1):
                x = read_float(4, f)
                y = read_float(4, f)
                z = read_float(4, f)
                print("下限ラジアン角 = (" + str(x) + ", " + str(y) + ", " + str(z) + ")")
                x = read_float(4, f)
                y = read_float(4, f)
                z = read_float(4, f)
                print("上限ラジアン角 = (" + str(x) + ", " + str(y) + ", " + str(z) + ")")
                


header = list()
#読み込み
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

for i in range(BoneNum):
    read_bone(BoneIndexSize, f)

