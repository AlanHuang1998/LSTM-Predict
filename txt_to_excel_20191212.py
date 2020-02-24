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
    return Addr

""" 判斷電話 """
def phone(string_in):
    phone = ''
    line = string_in
    if len(line.split(',')) == 1: # 因為有的有電話有的沒有, 沒有的填空
        # 用char判斷是身分證字號還是電話
        if 91 > int(ord(line[0])) > 64: # 判斷是身份證字號的話電話填空
            phone = " "
        else:
            phone = line[0:10]
            line = line[10:]
    else:
        phone = line.split(',')[0]
        line = line.split(',')[-1]
    return phone, line

""" 用身份證字號轉性別及是否外籍人士 """
def IN2Gender(string_in):
    gender = ''
    foreigner = ' '
    if string_in[1] == 'A' or string_in[1] == 'C':
        gender = '男'
        foreigner = '外籍人士'
    elif string_in[1] == 'B' or string_in[1] == 'D':
        gender = '女'
        foreigner = '外籍人士'
    else:
        if string_in[1] == '1':
            gender = '男'
        else:
            gender = '女'
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

if __name__ == "__main__":
    List_File = []
    List_Line = []
    testfile = './問題檔案/94-100.TXT' # user input
    files = listdir(path)
    for file_ in files:
        if file_.split('.')[-1] == 'TXT':
            print(file_)
            readpath = join(path, file_) # 讀取txt檔 
            with open(readpath, 'r', encoding='ansi', errors='ignore') as filer:
                for line in filer.readlines():        
                    err = ' '
                    line = strQ2B(line).strip().replace(' ',',', 0) # 轉半形後去除頭尾空白
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

                    line = line[7:]#.replace(' ',',', 1) # 因為日期統一為7位數可以直接分
                    try:
                        Addr = addr(line[:24]) 
                        line = line[24:].strip().replace(' ', ',', 1)
                    except:
                        err = '地址欄位錯誤'
                    
                    #print(line)
                    try:
                        Phone, line = phone(line) # 進phone() function
                        line = line.split(',')[-1].strip()
                    except:
                        err = '電話格式錯誤'

                    Identity_Number = line[:10] # 身分證字號
                    try:
                        Gender, Foreigner = IN2Gender(Identity_Number) # 性別, 外籍人士
                    except:
                        err = '未知欄位格式錯誤'
                        pass
                    #print(line)
                    try:
                        Birthday = str2time(line[10:17]) # 生日(西元)
                    except:
                        err = '生日欄位格式錯誤'
                        #print(line)
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
                            err = '生日欄位格式錯誤'
                    Diagnosis = diagnosis(line[17:]) # 診斷
                    #print('Name:', Name, 'RVDate:', RVDate, 'Addr:', Addr, 'Phone:', Phone, 'Identity_Number:', Identity_Number,
                    #        'Gender:', Gender, 'Foreigner:', Foreigner, 'Birthday:', Birthday, 'Diagnosis:', Diagnosis)
                    
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

                #print(len(List_File))
                df = pd.DataFrame(List_File, columns=header)
                List_File = []
                #print(df.head())
                writefile = join(path, file_.split('.')[0] + '.csv') # 轉出csv檔
                df.to_csv(writefile, index=None, header=True, encoding='utf_8_sig') # 使用utf-8-sig不然會亂碼
        
        else:
            print('檔案格式錯誤,非.txt檔')
    '''
    files = listdir(path)
    for file_ in files:
        if file_.split('.')[-1] == 'TXT':
            print(file_)
            readpath = join(path, file_) # 讀取txt檔 
            writefile = join(path, file_.split('.')[0] + '.csv') # 轉出csv檔
            with open(readpath, 'r', encoding='ansi', errors='ignore') as filer:
                for line in filer.readlines():
                    line = line.strip()
                    print(line.lower())
                    break'''

    '''
                    if len(line.split(',')) == 1: # 因為有的有電話有的沒有, 沒有的填空
                        Addr = line[:24]
                        line = line[24:] 
                    else:
                        Addr = line.split(',')[0] # 用split分割,地址跟其他資料
                        line = line.split(',')[-1].strip().replace(' ', ',', 1)
                    '''