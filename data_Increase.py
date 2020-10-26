import sys
import numpy as np
import glob

# 랜덤시드 고정시키기
np.random.seed(5)

from keras.preprocessing.image import ImageDataGenerator, array_to_img, img_to_array, load_img

# 데이터셋 불러오기
def increase(face_dir_id):
    data_aug_gen = ImageDataGenerator(rescale=1. / 255,
                                      rotation_range=15,
                                      width_shift_range=0.1,
                                      height_shift_range=0.1,
                                      shear_range=0.05,
                                      zoom_range=0,
                                      horizontal_flip=True,
                                      vertical_flip=False,
                                      fill_mode='nearest')

    face_id = face_dir_id
    # face_id = input('\n enter user id end press <return> ==>  ')
    dir = './Train/' + face_id
    pathList = glob.glob("%s/*.png" % (dir))

    count = 0

    for dir in pathList:
        img = load_img(dir)
        x = img_to_array(img)
        x = x.reshape((1,) + x.shape)

        i = 0
        count += 1

        # 이 for는 무한으로 반복되기 때문에 우리가 원하는 반복횟수를 지정하여, 지정된 반복횟수가 되면 빠져나오도록 해야합니다.
        for batch in data_aug_gen.flow(x, batch_size=1, save_to_dir='./Train/' + face_id,
                                       save_prefix=face_id + ' INC' + str(count), save_format='png'):
            i += 1
            if i > 20:
                break
