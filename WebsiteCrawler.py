# -*- coding: UTF-8 -*-

import re
import selenium
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver
import mysql.connector
import datetime

# 連線MYSQL
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="1234",
    database="aceinfohub"
)

def main():
    time = find()
    for i in range(time):
        root=get_root(i+1)
        crawler = Crawler()
        refresh()
        crawler.crawl(types='Daily', url=root, ti_df=1)
        refresh()
        crawler.crawl(types='Weekly', url= root, ti_df=2)
        refresh()
        crawler.crawl(types='Monthly', url= root, ti_df=3)
    
    crawler.handle_window()

def find():
    mycursor = mydb.cursor()
    mycursor.execute("SELECT sid FROM scraping_investing")
    sid = mycursor.fetchall()
    return len(sid)

def get_root(time):
    mycursor = mydb.cursor()
    sql = "SELECT c_url FROM scraping_investing WHERE sid = %s"
    val = (time,)
    mycursor.execute(sql, val)
    root = mycursor.fetchone()
    root = ''.join(root)
    print(root)
    return root

class Crawler:
    
    # path 路徑要修改成 chromedriver.exe 的路徑
    path = 'C:/Users/USER/Downloads/chromedriver_win32/chromedriver.exe'
    driver = webdriver.Chrome(path)
    
    executor_url = driver.command_executor._url
    session_id = driver.session_id
    
    def __init__(self):
        self.Without_Charge = 6

    def driver_session(self, session_id, url):
        org_command_execute = RemoteWebDriver.execute

        def new_command_execute(self, command, params=None):
            if command == "newSession":
                return {'success': 0, 'value': None, 'sessionId': session_id}
            else:
                return org_command_execute(self, command, params)

        RemoteWebDriver.execute = new_command_execute

        new_driver = webdriver.Remote(command_executor=executor_url, desired_capabilities={})
        new_driver.session_id = session_id

        RemoteWebDriver.execute = org_command_execute

        return new_driver    

    def excepts(self, col, string, ti_df):
        Str = []
        num = []
        if ti_df==3:
            if col == 0:
                for index in range(len(string)):
                    if string[index] == ',':
                        break

                    if string[index].isalpha():
                        Str.append(string[index])

                    if string[index].isdigit():
                        num.append(string[index])

                return ''.join(num) + '-' + ''.join(Str)

        if col == self.Without_Charge - 1:
            if string == '-':
                return ''.join('-1'),''.join('-')
            else:
                return ''.join(re.findall(r'-?\d+\.?\d*e?-?\d*?', string)[0]),''.join(
                                      re.findall(r'[a-zA-Z]', string)[0])
        else:
            return string
    
    def articles(self, types, url, sleep_time=0.2):
        if self.driver.get(url):
            self.driver = self.driver_session(self.session_id, self.executor_url)
    
        select = Select(self.driver.find_element_by_id('data_interval'))
        select.select_by_value(types)

        time.sleep(sleep_time)
        
        soup = BeautifulSoup(self.driver.page_source, 'lxml')
        
        return soup

    def handle_window(self):
        return self.driver.close()
    
    def crawl(self, types='Daily', url=None, ti_df=None, sleep_time=0.1):
        if ti_df==1:
            print("Daily")
        elif ti_df==2:
            print('Weekly')
        elif ti_df==3:
            print('monthly')
        else:
            print('Crawling in error.')
        group = []
        lst2 = []
        mycursor = mydb.cursor()
        sql = "SELECT group1, group2, c_name FROM scraping_investing WHERE c_url = %s"
        val = (url,)
        mycursor.execute(sql, val)
        group = mycursor.fetchall()
        
        try:
            start_row = self.articles(types, url).findAll('div', {'id': 'results_box'})[0].findAll('tbody')[0].findAll('tr')
            for row in range(len(start_row)):
                lst2.clear()
                for col in range(self.Without_Charge):
                    lst2.append(self.excepts(col, start_row[row].findAll('td')[col].text,ti_df))
                    
                    time.sleep(sleep_time)
                vol = list(lst2[5])
                
                mycursor = mydb.cursor()
                if ti_df==1:
                    c_date = time_change(lst2[0])
                    print(c_date)
                    sql = "INSERT INTO commodity_daily (group1,group2,c_name,c_date,c_price,                    c_open,c_high,c_low,c_vol,c_vol_unit,c_price_unit) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                    val = (group[0][0], group[0][1], group[0][2], c_date, lst2[1], lst2[2]                      , lst2[3], lst2[4], vol[0], vol[1], "USD")
                elif ti_df==2:
                    c_date = time_change(lst2[0])
                    print(c_date)
                    sql = "INSERT INTO commodity_weekly (group1,group2,c_name,c_date,c_price,                    c_open,c_high,c_low,c_vol,c_vol_unit,c_price_unit) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                    val = (group[0][0], group[0][1], group[0][2], c_date, lst2[1], lst2[2]                      , lst2[3], lst2[4], vol[0], vol[1], "USD")
                elif ti_df==3:
                    print(lst2[0])
                    sql = "INSERT INTO commodity_monthly (group1,group2,c_name,c_date,c_price,                    c_open,c_high,c_low,c_vol,c_vol_unit,c_price_unit) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                    val = (group[0][0], group[0][1], group[0][2], lst2[0], lst2[1], lst2[2]                      , lst2[3], lst2[4], vol[0], vol[1], "USD")
                else:
                    print('Crawling in error.')
                
                mycursor.execute(sql, val)
                mydb.commit()
                #print("1 record affected")
            
            mycursor = mydb.cursor()
            sql = "UPDATE scraping_investing SET toscrap_done = '1' WHERE c_url = %s"
            val = (url,)
            mycursor.execute(sql, val)
            mydb.commit()
            print(mycursor.rowcount, "record(s) affected where toscrap_done=1")
        except:
            print('Crawling in error.')
    
    

def refresh():
    mycursor = mydb.cursor()
    mycursor.execute("UPDATE scraping_investing SET toscrap_done = '0'")
    mydb.commit()
    
def time_change(y1):
    y2 = y1.replace(",",'')
    y3 = y2.replace(" ",'-')
    y4 = datetime.datetime.strptime(y3, "%b-%d-%Y")
    c_date = datetime.datetime.strftime(y4,"%Y-%m-%d %H:%M:%S")
    return c_date

if __name__ == '__main__':
    main()
