import numpy
import pandas
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import MinMaxScaler
from get_balance import *
from attempt_4 import *
from keras.models import load_model

dataframe = get_balance('../../sample_data.csv')
dataset = dataframe['Cost'].values
dataset = dataset.astype('float32')

# hack
dataset = numpy.expand_dims(dataset, axis=1)

scaler = MinMaxScaler(feature_range=(0, 1))

dataset = scaler.fit_transform(dataset)

# split into train and test sets
look_back = int(len(dataset) * 0.20)
train_size = int(len(dataset) * 0.70)
train, test = split_dataset(dataset, train_size, look_back)

batch_size = 1
model = load_model('../saved_model_short.h5')

# reshape into X=t and Y=t+1
train_x, train_y = create_dataset(train, look_back)
test_x, test_y = create_dataset(test, look_back)

# reshape input to be [samples, time steps, features]
train_x = numpy.reshape(train_x, (train_x.shape[0], train_x.shape[1], 1))
test_x = numpy.reshape(test_x, (test_x.shape[0], test_x.shape[1], 1))

# generate predictions for training
train_predict = model.predict(train_x, batch_size)
test_predict = model.predict(test_x, batch_size)

# generate forecast predictions
forecast_predict = make_forecast(model, test_x[-1::], timesteps=100, batch_size=batch_size)

# invert dataset and predictions
dataset = scaler.inverse_transform(dataset)
train_predict = scaler.inverse_transform(train_predict)
train_y = scaler.inverse_transform([train_y])
test_predict = scaler.inverse_transform(test_predict)
test_y = scaler.inverse_transform([test_y])
forecast_predict = scaler.inverse_transform(forecast_predict)

# calculate root mean squared error
train_score = numpy.sqrt(mean_squared_error(train_y[0], train_predict[:, 0]))
print('Train Score: %.2f RMSE' % train_score)
test_score = numpy.sqrt(mean_squared_error(test_y[0], test_predict[:, 0]))
print('Test Score: %.2f RMSE' % test_score)

plot_data(dataset, look_back, train_predict, test_predict, forecast_predict)