import numpy
import pandas
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import MinMaxScaler
from get_balance import *
from attempt_4 import *
from keras.models import load_model

def plot_data(dataset: numpy.ndarray,
              look_back: int,
              train_predict: numpy.ndarray,
              test_predict: numpy.ndarray,
              forecast_predict: numpy.ndarray):
    """
    Plots baseline and predictions.
    blue: baseline
    green: prediction with training data
    red: prediction with test data
    cyan: prediction based on predictions
    :param dataset: dataset used for predictions
    :param look_back: number of previous time steps as int
    :param train_predict: predicted values based on training data
    :param test_predict: predicted values based on test data
    :param forecast_predict: predicted values based on previous predictions
    :return: None
    """
    plt.plot(dataset)
    plt.plot([None for _ in range(look_back)] +
             [None for _ in train_predict] +
             [x for x in test_predict])
    plt.plot([None for _ in range(look_back)] +
             [None for _ in train_predict])
    plt.plot([None for _ in range(look_back)] +
             [None for _ in train_predict] +
             [None for _ in test_predict] +
             [x for x in forecast_predict])
    plt.show()




dataframe = get_balance('../../sample_data.csv')
dataframe.to_csv('../../graph_data.csv')
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
model = load_model('../saved_model_short_4.h5')

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




forecast_predict = []

plot_data(dataset[:81,], look_back, train_predict, test_predict, forecast_predict)



