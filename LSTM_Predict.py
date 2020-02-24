# 參考網址1: https://ithelp.ithome.com.tw/articles/10206312
# 參考網址2: https://www.finlab.tw/%E7%94%A8%E6%B7%B1%E5%BA%A6%E5%AD%B8%E7%BF%92%E5%B9%AB%E4%BD%A0%E8%A7%A3%E6%9E%90K%E7%B7%9A%E5%9C%96%EF%BC%81/
# IMPORTING LIBRARIES
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import Dense, Activation, Dropout
from keras.layers import LSTM

def LSTM_model(dataset_train, dataset_test):
    np.random.seed(7)
    
    dataset_train = dataset_train.reindex(index = dataset_train.index[::-1]) # 上下反置
    Train_set = np.reshape(dataset_train['Price'].values, (len(dataset_train['Price']), 1))
    
    # 正規化
    sc = MinMaxScaler(feature_range = (0, 1))
    Train_set_sc = sc.fit_transform(Train_set)

    # 建立training set
    Timesteps = 60
    X_train = []
    Y_train = []
    for i in range(Timesteps, len(Train_set_sc)):
        # Timesteps 設為 60 ，代表過去 60 天的資訊，嘗試過數值設置太少，將使 RNN 無法學習。同時Y = X的後一天
        X_train.append(Train_set_sc[i - Timesteps:i, 0])
        Y_train.append(Train_set_sc[i, 0])
    X_train, Y_train = np.array(X_train), np.array(Y_train) # 轉成np.array格式，方便輸入LSTM
    # reshape成 3 Dimension = [stock prices, timesteps, indicators] = (3748, 1, 1)
    X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))
    print(X_train.shape)
    
    # 搭建 LSTM layer:
    #   units: 神經元的數目
    #   第一層的 LSTM Layer 記得要設定input_shape參數 (60天, 1維)
    #   搭配使用dropout，這裡設為 0.2
    #   由於這邊的第四層 LSTM Layer 即將跟 Ouput Layer 做連接，因此注意這邊的 return_sequences 設為預設值 False （也就是不用寫上 return_sequences）
    input_dim = 1
    model = Sequential()
    model.add(LSTM(units = 256, return_sequences = True, input_shape = (X_train.shape[1], input_dim)))
    model.add(Dropout(0.2))
    model.add(LSTM(units = 256, return_sequences = True))
    model.add(Dropout(0.2))
    model.add(LSTM(units = 256, return_sequences = True))
    model.add(Dropout(0.2))
    model.add(LSTM(units = 128))
    model.add(Dropout(0.2))
    model.add(Dense(16, kernel_initializer="uniform", activation='relu'))
    model.add(Dense(1, activation='linear'))
    model.summary()

    model.compile(loss = 'mean_squared_error', optimizer='adam')
    model.fit(X_train, Y_train, batch_size = 128, epochs = 5)

    dataset_test = dataset_test.reindex(index = dataset_test.index[::-1])
    Real_Price = np.reshape(dataset_test['Price'].values, (len(dataset_test['Price']), 1))
    dataset_total = pd.concat((dataset_train['Price'], dataset_test['Price']), axis = 0)
    inputs = dataset_total[len(dataset_total) - len(dataset_test) - 60:].values
    inputs = inputs.reshape(-1, 1)
    inputs = sc.fit_transform(inputs) # Feature Scaling

    X_test = []
    for i in range(Timesteps, len(inputs)):
        X_test.append(inputs[i - Timesteps:i, 0])
    X_test = np.array(X_test)
    X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1)) # reshape to 3 Dimension
    Predicted_Price = model.predict(X_test)
    Predicted_Price = sc.inverse_transform(Predicted_Price) # get the original scale

    # Visualising the results
    plt.plot(Real_Price, color = 'red', label = 'Real Brent Oil Price')  # 紅線表示真實股價
    plt.plot(Predicted_Price, color = 'blue', label = 'Predicted Brent Oil Price')  # 藍線表示預測股價
    plt.title('Brent Oil Price Prediction')
    plt.xlabel('Time')
    plt.ylabel('Brent Oil Price')
    plt.legend()
    plt.show()

if __name__ == '__main__':
    dataset_train = pd.read_csv('./Brent Oil Futures Historical Data_Train.csv', usecols=[1,2,3,4])
    dataset_test = pd.read_csv('./Brent Oil Futures Historical Data_Test.csv', usecols=[1,2,3,4])
    LSTM_model(dataset_train, dataset_test)
