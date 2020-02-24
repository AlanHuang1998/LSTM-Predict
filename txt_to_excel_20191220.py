''' 電話會省略0是因為excel設定問題 '''
''' 池國隆，吳瑛蘭的地址，電話處理有問題 '''
''' 地址中有空格會影響到生日處理的部分，可以透過227行來快速尋找錯誤點 '''
''' Single_Files function適用單一檔案(網站UI)，Multi_Files function可以用來測試多個檔案及資料夾(test) '''

import csv
import pandas as pd
from os import listdir
from os.path import join
from datetime import datetime

path = './問題檔案'
header = ['姓名', '回診日期', '地址', '電話', '身分證字號', '性別', '外籍人士', '生日', '診斷', '資料格式錯誤']
place = ['大同', '三星', '冬山', '蘇澳', '五結', '壯圍', '羅東', '員山', '礁溪', '頭城', '宜蘭市']

"""把字串全形轉半形"""
def strQ2B(string_in):
    strlist = []
    for s in string_in:
        string_out = ""
        for uchar in s:
            inside_code = ord(uchar)
            if inside_code == 12288:  # 全形空格直接轉換
                inside_code = 32
            elif (inside_code >= 65281 and inside_code <= 65374):  # 全形字元（除空格）根據關係轉化
                inside_code -= 65248
            string_out += chr(inside_code)
        strlist.append(string_out)
    return ''.join(strlist)

""" 把民國轉西元 """
def str2time(string_in):
    Year = string_in[0:3]
    Month = string_in[3:5]
    Day = string_in[5:7]
    VidDate = str(int(Year)+1911) + '/' + Month + '/' + Day
    #VidDate = datetime.strptime(VidDate, '%Y/%m/%d').date()
    return VidDate

""" 判斷地址 """
def addr(string_in):
    Addr = string_in
    for i in place:
        if i in string_in:
            if '宜蘭縣' not in string_in:
                Addr = '宜蘭縣'+ string_in
        else:
            pass

    if "台北縣" in string_in:
        Addr = '新北市' + string_in[3:]
    if "台南縣" in string_in:
        Addr = '台南市' + string_in[3:]#5] + '區' + string_in[6:]
    if "台中縣" in string_in:
        Addr = '台中市' + string_in[3:]#5] + '區' + string_in[6:]
    if "高雄縣" in string_in:
        Addr = '高雄市' + string_in[3:]#5] + '區' + string_in[6:]
    if "桃園縣" in string_in:
        Addr = '桃園市' + string_in[3:]#5] + '區' + string_in[6:]
    #if "台北市" in string_in:
    #    Addr = string_in[0:5] + '區' + string_in[6:]
    return Addr

""" 判斷電話 """
def phone(string_in):
    phone = ''
    line = string_in
    if len(line.split(',')) == 1: # 因為有的有電話有的沒有, 沒有的填空
        # 用char判斷是身分證字號還是電話
        if 91 > int(ord(line[0])) > 64: # 判斷是身份證字號的話電話填空
            phone = " "
            line = line.strip()
        else:
            phone = line[0:10]
            line = line[10:]
            while ord(line[0]) > 90 and ord(line[0]) < 65: # 如果身分證字號那邊開頭不是A-Z,電話就再往後取
                #print(ord(line[0]),line)
                phone += line[0]
                line = line[1:].strip()
    else:
        phone = line.split(',')[0]
        line = line.split(',')[-1]
    phone = phone.strip('*')
    #phone = phone.split('-')[-1]
    #phone = phone.strip()
    return phone, line

""" 用身份證字號轉性別及是否外籍人士 """
def IN2Gender(string_in):
    gender = ''
    foreigner = ' '
    if string_in[1] == 'A' or string_in[1] == 'C':
        gender = '1'
        foreigner = '外籍人士'
    elif string_in[1] == 'B' or string_in[1] == 'D':
        gender = '2'
        foreigner = '外籍人士'
    else:
        if string_in[1] == '1':
            gender = '1'
        elif string_in[1] == '2':
            gender = '2'
        else:
            gender = ''
    return gender, foreigner

""" 判斷診斷內容 """
def diagnosis(string_in):
    Diagnosis = ''
    if '1' in string_in or '一' in string_in:
        Diagnosis = '1'
    elif '2' in string_in or '二' in string_in:
        Diagnosis = '2'
    elif '葡萄糖' in string_in:
        Diagnosis = '3'
    else:
        Diagnosis = '0'
    return Diagnosis

""" 多數檔案(資料夾) """
def Multi_Files(folderpath):
    List_File = []
    List_Line = []
    files = listdir(folderpath)
    for file_ in files:
        if file_.split('.')[-1] == 'TXT':
            print("正在轉換:", file_)
            readpath = join(folderpath, file_) # 讀取txt檔 
            with open(readpath, 'r', encoding='ansi', errors='ignore') as filer:
                for line in filer.readlines():        
                    err = ' '
                    line = strQ2B(line).strip().replace(' ',',', 0) # 轉半形後去除頭尾空白
                    #line = line.strip().replace(' ',',', 0) # 轉半形後去除頭尾空白
                    #print(line)
                    if line[4] != ',':
                        line = line[0:4] + ',' + line[4:]
                    #else:
                        #line = line.replace(',', ' ', 1)

                    Name = line.split(',')[0] # 姓名
                    line = line.split(',')[1].strip()
                    #print(line)
                    try:
                        RVDate = str2time(line[:7]) # 取回診日期後進到str2time()這個function
                    except:
                        Name = Name + line[:4]
                        line = line[4:].strip()
                        RVDate = str2time(line[:7]) # 外國人名字長度會大於4 所以用try catch來做例外處理

                    line = line[7:].replace(' ',',', 1) # 因為日期統一為7位數可以直接分
                    #if '張財來' in Name:
                    #    print(line)
                    #print(line.replace(' ',',', 1))
                    try:
                        if len(line.split(',')) == 1: # 如果用","分不出來的話，改用長度判斷
                            Addr = addr(line[:20])
                            Addr = Addr.strip()
                            line = line[20:].strip().replace(' ', ',', 1)
                            while ord(line[0]) != 48 and ord(line[0]) != 57: # 如果電話那邊開頭不是0or9,地址就再往後取
                                #print(ord(line[0]),line)
                                Addr += line[0]
                                line = line[1:].strip()
                            
                        else:
                            #if '吳瑛蘭' in Name:
                            #    print(line)
                            Addr = addr(line.split(',')[0])
                            Addr = Addr.strip()
                            line = line.split(',')[1].strip().replace(' ', ',', 1)
                            
                            if (47 > ord(line[2]) or ord(line[2]) > 58) or (47 > ord(line[6]) or ord(line[6]) > 58) : # 有的地址中間會有空格
                                #if 47 > ord(line[5]) or ord(line[5]) > 58 :
                                #print(line)
                                line = line.replace(' ',',',1)
                                Addr = Addr + line.split(',')[0]
                                line = line.split(',')[-1].strip().replace(' ', ',', 1)
                            #if '張財來' in Name:
                            #    print(line)
                            if (47 < ord(Addr[-5]) < 58) and (47 < ord(Addr[-4]) < 58) and (47 < ord(Addr[-3]) < 58) and (47 < ord(Addr[-2]) < 58) and (47 < ord(Addr[-1]) < 58) : # 有的地址中間會有空格
                                line = Addr[-7:] + ',' + line
                                Addr = Addr[:-7]
                            #if '張財來' in Name:
                            #    print(line)
                            #if ord(Addr[-7]) == 57 and 47 < ord(Addr[-1]) < 58 and 47 < ord(Addr[-6]) < 58: # 有時電話後會有',',所以要把電話放回去line
                            #    line = Addr[-7:] + ',' + line 
                            #    Addr = Addr[:-7]
                            #if '張元福' in Name:
                            #    print(line)
                            #    print(ord(line[2]),ord(line[6]))
                            #if '陳天德' in Name:
                            #    print(line)
                    except:
                        err = '地址欄位空白'

                    #if '池國隆' in Name:
                    #    print(line)
                    line = line.strip()
                    try:
                        #if '鍾邵秀菊' in Name:
                            #print(line)
                        Phone, line = phone(line) # 進phone() function
                        line = line.split(',')[-1].strip()
                    except:
                        err = '電話欄位空白'
                    #print(line)
                    

                    Identity_Number = line[:10] # 身分證字號
                    line = line[10:]
                    try:
                        if ord(Identity_Number[0]) > 91 or ord(Identity_Number[0]) < 65: # 個案
                            line = Identity_Number[-1] + line
                            Identity_Number = Phone[-1] + Identity_Number
                            Identity_Number = Identity_Number[:-2]
                        Gender, Foreigner = IN2Gender(Identity_Number) # 性別, 外籍人士
                        #if '鍾邵秀菊' in Name:
                        #    print(ord(Identity_Number[0]), Identity_Number)
                    except:
                        err = '身份證字號欄位錯誤或空白'    
                    
                    #print(line)
                    try:
                        Birthday = str2time(line[:7]) # 生日(西元)
                    
                    except:
                        
                        #print(Name, line)
                        pass
                        line = line.split(',')[-1].replace(' ', ',', 1)
                        try:
                            Phone,line = phone(line)
                            line = line.strip()
                            Identity_Number = line[:10] # 身分證字號
                            Gender, Foreigner = IN2Gender(Identity_Number) # 性別, 外籍人士
                        except:
                            err = '未知欄位格式錯誤'
                        try:
                            Birthday = str2time(line[10:17])
                        except:
                            pass
                    
                    Diagnosis = diagnosis(line[7:]) # 診斷

                    if 48 > ord(Phone[0]) or ord(Phone[0]) > 57:
                        err = '電話欄位錯誤或空白'

                    List_Line.append(Name)
                    List_Line.append(RVDate)
                    List_Line.append(Addr)
                    List_Line.append(Phone)
                    List_Line.append(Identity_Number)
                    List_Line.append(Gender)
                    List_Line.append(Foreigner)
                    List_Line.append(Birthday)
                    List_Line.append(Diagnosis)
                    List_Line.append(err)
                    List_File.append(List_Line)
                    List_Line = []

                    #print('Name:', Name, 'RVDate:', RVDate, 'Addr:', Addr, 'Phone:', Phone, 'Identity_Number:', Identity_Number,
                    #        'Gender:', Gender, 'Foreigner:', Foreigner, 'Birthday:', Birthday, 'Diagnosis:', Diagnosis)

                df = pd.DataFrame(List_File, columns=header)
                writefile = join(path, file_.split('.')[0] + '.csv') # 轉出csv檔
                df.to_csv(writefile, index=None, header=True, encoding='utf_8_sig') # 使用utf-8-sig不然會亂碼
                print('轉換成功！')
                List_File = []
        else:
            print('檔案格式錯誤,非.txt檔')

""" 單一檔案(網頁UI) """
def Single_Files(filepath):
    List_File = []
    List_Line = []
    #filepath = './問題檔案/94-100.TXT' # user input
    if filepath.split('.')[-1] == 'TXT':
        print("正在轉換:", filepath)
        with open(filepath, 'r', encoding='ansi', errors='ignore') as filer:
            for line in filer.readlines():        
                err = ' '
                line = strQ2B(line).strip().replace(' ',',', 0) # 轉半形後去除頭尾空白
                if line[4] != ',':
                    line = line[0:4] + ',' + line[4:]

                Name = line.split(',')[0] # 姓名
                line = line.split(',')[1].strip()
                
                try:
                    RVDate = str2time(line[:7]) # 取回診日期後進到str2time()這個function
                except:
                    Name = Name + line[:4]
                    line = line[4:].strip()
                    RVDate = str2time(line[:7]) # 外國人名字長度會大於4 所以用try catch來做例外處理

                line = line[7:].replace(' ',',', 1) # 因為日期統一為7位數可以直接分
                
                try:
                    if len(line.split(',')) == 1: # 如果用","分不出來的話，改用長度判斷
                        Addr = addr(line[:20])
                        Addr = Addr.strip()
                        line = line[20:].strip().replace(' ', ',', 1)
                        while ord(line[0]) != 48 and ord(line[0]) != 57: # 如果電話那邊開頭不是0or9,地址就再往後取
                            #print(ord(line[0]),line)
                            Addr += line[0]
                            line = line[1:].strip()
                        
                    else:
                        Addr = addr(line.split(',')[0])
                        Addr = Addr.strip()
                        line = line.split(',')[1].strip().replace(' ', ',', 1)
                        
                        if (47 > ord(line[2]) or ord(line[2]) > 58) or (47 > ord(line[6]) or ord(line[6]) > 58) : # 有的地址中間會有空格
                            line = line.replace(' ',',',1)
                            Addr = Addr + line.split(',')[0]
                            line = line.split(',')[-1].strip().replace(' ', ',', 1)
                        if (47 < ord(Addr[-5]) < 58) and (47 < ord(Addr[-4]) < 58) and (47 < ord(Addr[-3]) < 58) and (47 < ord(Addr[-2]) < 58) and (47 < ord(Addr[-1]) < 58) : # 有的地址中間會有空格
                            line = Addr[-7:] + ',' + line
                            Addr = Addr[:-7]
                except:
                    err = '地址欄位空白'

                line = line.strip()
                try:
                    Phone, line = phone(line) # 進phone() function
                    line = line.split(',')[-1].strip()
                except:
                    err = '電話欄位空白'

                Identity_Number = line[:10] # 身分證字號
                line = line[10:]
                
                try:
                    if ord(Identity_Number[0]) > 91 or ord(Identity_Number[0]) < 65: # 個案
                        line = Identity_Number[-1] + line
                        Identity_Number = Phone[-1] + Identity_Number
                        Identity_Number = Identity_Number[:-2]
                    Gender, Foreigner = IN2Gender(Identity_Number) # 性別, 外籍人士
                except:
                    err = '身份證字號欄位錯誤或空白'    
                
                try:
                    Birthday = str2time(line[:7]) # 生日(西元)
                except:
                    pass
                    line = line.split(',')[-1].replace(' ', ',', 1)
                    try:
                        Phone,line = phone(line)
                        line = line.strip()
                        Identity_Number = line[:10] # 身分證字號
                        Gender, Foreigner = IN2Gender(Identity_Number) # 性別, 外籍人士
                    except:
                        err = '未知欄位格式錯誤'
                    try:
                        Birthday = str2time(line[10:17])
                    except:
                        pass
                
                Diagnosis = diagnosis(line[7:]) # 診斷

                if 48 > ord(Phone[0]) or ord(Phone[0]) > 57:
                    err = '電話欄位錯誤或空白'

                List_Line.append(Name)
                List_Line.append(RVDate)
                List_Line.append(Addr)
                List_Line.append(Phone)
                List_Line.append(Identity_Number)
                List_Line.append(Gender)
                List_Line.append(Foreigner)
                List_Line.append(Birthday)
                List_Line.append(Diagnosis)
                List_Line.append(err)
                List_File.append(List_Line)
                List_Line = []

            df = pd.DataFrame(List_File, columns=header)
            writefile = filepath.replace('TXT', 'csv', 1) # 轉出csv檔
            df.to_csv(writefile, index=None, header=True, encoding='utf_8_sig') # 使用utf-8-sig不然會亂碼
            print('轉換成功！')
            List_File = []
    else:
        print('檔案格式錯誤,非.txt檔')


if __name__ == "__main__":
    Multi_Files(path)
    #Single_Files('./問題檔案/94-100.TXT')