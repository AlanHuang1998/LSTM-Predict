''' 電話會省略0是因為excel設定問題 '''
''' 池國隆，吳瑛蘭的地址，電話處理有問題 '''
''' 地址中有空格會影響到生日處理的部分，可以透過227行來快速尋找錯誤點 '''
''' Single_Files function適用單一檔案(網站UI)，Multi_Files function可以用來測試多個檔案及資料夾(test) '''
''' 將多數檔案改成寫入mysql '''

import csv
import pandas as pd
import numpy as np
from os import listdir
from os.path import join
from datetime import datetime
nowtime = datetime.now()

import mysql.connector
Clientdb = mysql.connector.connect(
    host = "127.0.0.1",
    user = "root",
    password = "qaz05698",
    #database = "ClientServer",
)
cursor = Clientdb.cursor()
cursor.execute("CREATE DATABASE ClientDB")

path = './問題檔案'
header = ['姓名', '回診日期', '地址', '電話', '身分證字號', '性別', '外籍人士', '生日', '年齡', '診斷', '初次就醫日期', 
            '初次診斷DM日期', '初次IG日期', '姓名欄位錯誤', '回診日期欄位錯誤', '地址欄位空白', '電話欄位錯誤', 
            '電話欄位空白', '身分證字號欄位錯誤', '生日欄位空白']
place = ['大同', '三星', '冬山', '蘇澳', '五結', '壯圍', '羅東', '員山', '礁溪', '頭城', '宜蘭市']

class WordTransfer:
    
    def __init__(self, string_in):
        self.string_in = string_in

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


class FileTransfer:
    
    def __init__(self, folderpath, filepath):
        self.folderpath = folderpath
        self.filepath = filepath
            
    """ 多數檔案(資料夾) """
    def Multi_Files(folderpath):
        List_Name = []
        List_Line = []
        List_Files = []
        files = listdir(folderpath)
        for file_ in files:
            if file_.split('.')[-1] == 'TXT':
                print("正在轉換:", file_)
                filepath = join(folderpath, file_) # 讀取txt檔
                with open(filepath, 'r', encoding='ansi', errors='ignore') as filer:
                    for line in filer.readlines(): 
                        line = WordTransfer.strQ2B(line).strip().replace(' ',',', 0) # 轉半形後去除頭尾空白
                        if line[4] != ',':
                            line = line[0:4] + ',' + line[4:]

                        Name = line.split(',')[0] # 姓名
                        line = line.split(',')[1].strip()
                        if Name == 'SITI': # 個案
                            Name = Name + line[:3]
                            line = line[3:]
                        
                        try:
                            RVDate = WordTransfer.str2time(line[:7]) # 取回診日期後進到str2time()這個function
                        except:
                            Name = Name + line[:4]
                            line = line[4:].strip()
                            RVDate = WordTransfer.str2time(line[:7]) # 外國人名字長度會大於4 所以用try catch來做例外處理

                        line = line[7:].replace(' ',',', 1) # 因為日期統一為7位數可以直接分
                        
                        try:
                            if len(line.split(',')) == 1: # 如果用","分不出來的話，改用長度判斷
                                Addr = WordTransfer.addr(line[:20])
                                Addr = Addr.strip()
                                line = line[20:].strip().replace(' ', ',', 1)
                                while ord(line[0]) != 48 and ord(line[0]) != 57: # 如果電話那邊開頭不是0or9,地址就再往後取
                                    #print(ord(line[0]),line)
                                    Addr += line[0]
                                    line = line[1:].strip()
                                
                            else:
                                Addr = WordTransfer.addr(line.split(',')[0])
                                Addr = Addr.strip()
                                line = line.split(',')[1].strip().replace(' ', ',', 1)
                                
                                if (47 > ord(line[2]) or ord(line[2]) > 58) or (47 > ord(line[6]) or ord(line[6]) > 58) : # 有的地址中間會有空格(個案)
                                    line = line.replace(' ',',',1)
                                    Addr = Addr + line.split(',')[0]
                                    line = line.split(',')[-1].strip().replace(' ', ',', 1)
                                if (47 < ord(Addr[-5]) < 58) and (47 < ord(Addr[-4]) < 58) and (47 < ord(Addr[-3]) < 58) and (47 < ord(Addr[-2]) < 58) and (47 < ord(Addr[-1]) < 58) : # 有的地址中間會有空格
                                    line = Addr[-7:] + ',' + line
                                    Addr = Addr[:-7]
                        except:
                            if Name != '歐   ':
                                Addr = ''
                            pass
                            

                        line = line.strip()
                        try:
                            Phone, line = WordTransfer.phone(line) # 進phone() function
                            line = line.split(',')[-1].strip()
                        except:
                            Phone = ''
                            pass

                        err_IN = ''
                        Identity_Number = line[:10] # 身分證字號
                        line = line[10:]
                        
                        try:
                            if ord(Identity_Number[0]) > 91 or ord(Identity_Number[0]) < 65: # 個案
                                line = Identity_Number[-1] + line
                                Identity_Number = Phone[-1] + Identity_Number
                                Identity_Number = Identity_Number[:-2]
                            Gender, Foreigner = WordTransfer.IN2Gender(Identity_Number) # 性別, 外籍人士
                        except:
                            Identity_Number = ''
                            Gender = ''
                            Foreigner = ''
                            err_IN = '身份證字號欄位錯誤'    
                        
                        blank_Birt = ''
                        try:
                            Birthday = WordTransfer.str2time(line[:7]) # 生日(西元)
                        except:
                            pass
                            line = line.split(',')[-1].replace(' ', ',', 1)
                            try:
                                Phone,line = WordTransfer.phone(line)
                                line = line.strip()
                                Identity_Number = line[:10] # 身分證字號
                                Gender, Foreigner = WordTransfer.IN2Gender(Identity_Number) # 性別, 外籍人士
                            except:
                                pass
                            try:
                                Birthday = WordTransfer.str2time(line[10:17])
                            except:
                                Birthday = ''
                                blank_Birt = '生日欄位空白'
                                pass

                        if Name == '歐   ':
                            line = Addr + line
                            Addr = ''
                        Diagnosis = WordTransfer.diagnosis(line[7:]) # 診斷
                        if Name == '歐   ':
                            Diagnosis = '2'

                        if len(Addr) == 0:
                            err_Addr = '地址欄位空白'
                        else:
                            err_Addr = ''

                        if ord(RVDate[-1]) == 32:
                            err_RVDate = '回診日期欄位錯誤'
                        else:
                            err_RVDate = ''

                        blank_Phone = ''
                        err_Phone = ''
                        try:
                            if 48 > ord(Phone[0]) or ord(Phone[0]) > 57:
                                if 1 >= len(Phone) >= 0:
                                    blank_Phone = '電話欄位空白'
                                else:
                                    err_Phone = '電話欄位錯誤'
                        except:
                            blank_Phone = '電話欄位空白'

                        try:
                            Age = str(int(nowtime.year) - int(Birthday[:4]))
                        except:
                            Age = ''

                        err_Name = ''
                        Phone = Phone + " "
                        List_Line.append(Name)
                        List_Line.append(RVDate)
                        List_Line.append(Addr)
                        List_Line.append(Phone)
                        List_Line.append(Identity_Number)
                        List_Line.append(Gender)
                        List_Line.append(Foreigner)
                        List_Line.append(Birthday)
                        List_Line.append(Age)
                        List_Line.append(Diagnosis)
                        List_Line.append(RVDate) # 初次就診日期
                        first_DM = ''
                        List_Line.append(first_DM) # 初次診斷DM
                        first_IG = ''
                        List_Line.append(first_IG) # 初次IG日期
                        List_Line.append(err_Name)
                        List_Line.append(err_RVDate)
                        List_Line.append(err_Addr)
                        List_Line.append(err_Phone)
                        List_Line.append(blank_Phone)
                        List_Line.append(err_IN)
                        List_Line.append(blank_Birt)
                        List_Name.append(Name) # 收集全部檔案的名稱欄位
                        List_Files.append(List_Line) # 收集全部檔案全部的欄位
                        List_Line = []
                    # 如果改成先排好順序再找呢?
                    Sort_Files = sorted(List_Files, key = lambda x: datetime.strptime(x[1], '%Y/%m/%d'), reverse = False)
                    
                    df = pd.DataFrame(Sort_Files, columns=header)
                    print(df)
                    #writefile = join(path, file_.split('.')[0] + '.csv') # 轉出csv檔
                    df.to_csv('94-10810.csv', index=None, header=True, encoding='utf_8_sig') # 使用utf-8-sig不然會亂碼
                    #df.to_csv(writefile, index=None, header=True, encoding='utf_8_sig') # 使用utf-8-sig不然會亂碼
                    #print('轉換成功！')
            else:
                print('檔案格式錯誤,非txt檔')

    """ 單一檔案(網頁UI) """
    def Single_File(filepath):
        List_File = []
        List_Line = []
        #filepath = './問題檔案/94-100.TXT' # user input
        if filepath.split('.')[-1] == 'TXT':
            print("正在轉換:", filepath)
            with open(filepath, 'r', encoding='ansi', errors='ignore') as filer:
                for line in filer.readlines(): 
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
                        if Name != '歐   ':
                            Addr = ''
                        pass
                        

                    line = line.strip()
                    try:
                        Phone, line = phone(line) # 進phone() function
                        line = line.split(',')[-1].strip()
                    except:
                        Phone = ''
                        pass
                        #blank_Phone = '電話欄位空白'

                    err_IN = ''
                    Identity_Number = line[:10] # 身分證字號
                    line = line[10:]
                    
                    try:
                        if ord(Identity_Number[0]) > 91 or ord(Identity_Number[0]) < 65: # 個案
                            line = Identity_Number[-1] + line
                            Identity_Number = Phone[-1] + Identity_Number
                            Identity_Number = Identity_Number[:-2]
                        Gender, Foreigner = IN2Gender(Identity_Number) # 性別, 外籍人士
                    except:
                        Identity_Number = ''
                        Gender = ''
                        Foreigner = ''
                        err_IN = '身份證字號欄位錯誤'    
                    
                    blank_Birt = ''
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
                            #err_Fore = ''
                        except:
                            pass
                        try:
                            Birthday = str2time(line[10:17])
                        except:
                            Birthday = ''
                            blank_Birt = '生日欄位空白'
                            pass

                    if Name == '歐   ':
                        line = Addr + line
                        Addr = ''
                    Diagnosis = diagnosis(line[7:]) # 診斷
                    if Name == '歐   ':
                        Diagnosis = '2'

                    if len(Addr) == 0:
                        err_Addr = '地址欄位空白'
                    else:
                        err_Addr = ''

                    if ord(RVDate[-1]) == 32:
                        err_RVDate = '回診日期欄位錯誤'
                    else:
                        err_RVDate = ''

                    blank_Phone = ''
                    err_Phone = ''
                    try:
                        if 48 > ord(Phone[0]) or ord(Phone[0]) > 57:
                            if 1 >= len(Phone) >= 0:
                                blank_Phone = '電話欄位空白'
                            else:
                                err_Phone = '電話欄位錯誤'
                    except:
                        blank_Phone = '電話欄位空白'

                    try:
                        Age = str(int(nowtime.year) - int(Birthday[:4]))
                    except:
                        Age = ''
                    
                    #blank_Birt = ''
                    #if 1 >= len(Birthday) >= 0:
                    #    blank_Birt = '生日欄位空白'

                    err_Name = ''
                    Phone = Phone + " "
                    List_Line.append(Name)
                    List_Line.append(RVDate)
                    List_Line.append(Addr)
                    List_Line.append(Phone)
                    List_Line.append(Identity_Number)
                    List_Line.append(Gender)
                    List_Line.append(Foreigner)
                    List_Line.append(Birthday)
                    List_Line.append(Age)
                    List_Line.append(Diagnosis)
                    List_Line.append(err_Name)
                    List_Line.append(err_RVDate)
                    List_Line.append(err_Addr)
                    List_Line.append(err_Phone)
                    List_Line.append(blank_Phone)
                    List_Line.append(err_IN)
                    #List_Line.append(err_Fore)
                    #List_Line.append(err_Birt)
                    List_Line.append(blank_Birt)
                    #List_Line.append(err_Diag)
                    List_File.append(List_Line) # 收齊全部的欄位
                    List_Line = []
                    #header = ['姓名', '回診日期', '地址', '電話', '身分證字號', '性別', '外籍人士', '生日', '診斷', '姓名欄位錯誤', 
                        #'回診日期欄位錯誤', '地址欄位錯誤', '電話欄位錯誤', '電話欄位空白', '身分證字號欄位錯誤', '生日欄位錯誤']

                df = pd.DataFrame(List_File, columns=header)
                writefile = filepath.replace('TXT', 'csv', 1) # 轉出csv檔
                df.to_csv(writefile, index=None, header=True, encoding='utf_8_sig') # 使用utf-8-sig不然會亂碼
                print('轉換成功！')
                List_File = []
        else:
            print('檔案格式錯誤,非.txt檔')
            pass


if __name__ == "__main__":
    FileTransfer.Multi_Files(path)
    #FileTransfer.Single_File('./問題檔案/94-100.TXT')