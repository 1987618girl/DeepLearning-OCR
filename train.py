import os
import time
from datetime import datetime
from keras.callbacks import ModelCheckpoint
from util import one_hot_decoder, plot_loss_figure, load_data, get_char_set, get_maxnb_char
from util import get_sample_weight, list2str
from post_correction import get_label_set, correction
from architecture.shallow import build_shallow


# @profile
def pred(model, X, char_set, label_set, post_correction):
	pred_res = model.predict(X)
	pred_res = [one_hot_decoder(i, char_set) for i in pred_res]
	pred_res = [list2str(i) for i in pred_res]
	# post correction
	if post_correction:
		pred_res = correction(pred_res, label_set)
	return pred_res

# @profile
def test(model, test_data, char_set, label_set, post_correction):
	test_X, test_y = test_data[0], test_data[1]
	test_y = [one_hot_decoder(i, char_set) for i in test_y]
	test_y = [list2str(i) for i in test_y]
	pred_res = pred(model, test_X, char_set, label_set, post_correction)
	# for i in pred_res:
	# 	print i
	nb_correct = sum(pred_res[i]==test_y[i] for i in range(len(pred_res)))
	for i in range(len(pred_res)):
		if test_y[i] != pred_res[i]:
			print 'test:', test_y[i]
			print 'pred:', pred_res[i]
			pass
	print 'nb_correct: ', nb_correct
	print 'Acurracy: ', float(nb_correct) / len(pred_res)


def train(model, batch_size, nb_epoch, save_dir, train_data, val_data, char_set):
	X_train, y_train = train_data[0], train_data[1]
	sample_weight = get_sample_weight(y_train, char_set)
	print 'X_train shape:', X_train.shape
	print X_train.shape[0], 'train samples'
	if os.path.exists(save_dir) == False:
		os.mkdir(save_dir)

	start_time = time.time()
	save_path = save_dir + 'weights.{epoch:02d}-{val_loss:.2f}.hdf5'
	check_pointer = ModelCheckpoint(save_path, 
		save_best_only=True)
	history = model.fit(X_train, y_train, batch_size=batch_size, nb_epoch=nb_epoch, 
		validation_data=val_data,
		validation_split=0.1, 
		callbacks=[check_pointer],
		sample_weight=sample_weight
		)

	plot_loss_figure(history, save_dir + str(datetime.now()).split('.')[0].split()[1]+'.jpg')
	print 'Training time(h):', (time.time()-start_time) / 3600


def main():
	# img_width, img_height = 48, 48
	img_width, img_height = 200, 60
	img_channels = 1 
	# batch_size = 1024
	batch_size = 32
	nb_epoch = 1000
	post_correction = False

	save_dir = 'save_model/' + str(datetime.now()).split('.')[0].split()[0] + '/' # model is saved corresponding to the datetime
	train_data_dir = 'train_data/ip_train/'
	# train_data_dir = 'train_data/single_1000000/'
	val_data_dir = 'train_data/ip_val/'
	test_data_dir = 'test_data//'
	weights_file_path = 'save_model/2016-10-27/weights.11-1.58.hdf5'
	char_set, char2idx = get_char_set(train_data_dir)
	nb_classes = len(char_set)
	max_nb_char = get_maxnb_char(train_data_dir)
	label_set = get_label_set(train_data_dir)
	# val 'char_set:', char_set
	print 'nb_classes:', nb_classes
	print 'max_nb_char:', max_nb_char
	print 'size_label_set:', len(label_set)
	model = build_shallow(img_channels, img_width, img_height, max_nb_char, nb_classes) # build CNN architecture
	# model.load_weights(weights_file_path) # load trained model

	val_data = load_data(val_data_dir, max_nb_char, img_width, img_height, img_channels, char_set, char2idx)
	# val_data = None 
	train_data = load_data(train_data_dir, max_nb_char, img_width, img_height, img_channels, char_set, char2idx) 
	train(model, batch_size, nb_epoch, save_dir, train_data, val_data, char_set)

	# train_data = load_data(train_data_dir, max_nb_char, img_width, img_height, img_channels, char_set, char2idx)
	# test(model, train_data, char_set, label_set, post_correction)
	# val_data = load_data(val_data_dir, max_nb_char, img_width, img_height, img_channels, char_set, char2idx)
	# test(model, val_data, char_set, label_set, post_correction)
	# test_data = load_data(test_data_dir, max_nb_char, img_width, img_height, img_channels, char_set, char2idx)
	# test(model, test_data, char_set, label_set, post_correction)


if __name__ == '__main__':
	main()