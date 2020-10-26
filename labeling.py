from PIL import Image
import os, glob, numpy as np
from sklearn.model_selection import train_test_split

Trian_dir = "./Train"

def labeling():
    categories = os.listdir(Trian_dir)
    print(categories)

    nb_classes = len(categories)

    image_w = 64
    image_h = 64

    pixels = image_h * image_w * 3

    X = []
    Y = []

    for idx, cat in enumerate(categories):

        # one-hot 돌리기. , 카테고리별로 돌면서 0으로 초기화
        label = [0 for i in range(nb_classes)]
        label[idx] = 1

        image_dir = Trian_dir + "/" + cat  # cat 아님 category의 cat
        files = glob.glob(image_dir + "/*.png")
        print(cat, " 파일 길이 : ", len(files))
        for i, f in enumerate(files):
            img = Image.open(f)
            img = img.convert("RGB")
            img = img.resize((image_w, image_h))
            data = np.asarray(img)

            print("X값: ", data)
            X.append(data)
            Y.append(label)

            if i % 700 == 0:
                print(cat, " : ", f)

    X = np.array(X)  # 데이터
    Y = np.array(Y)  # 라벨링
    # 1 0 0 0 이면 airplanes
    # 0 1 0 0 이면 buddha 이런식

    X_train, X_test, Y_train, Y_test = train_test_split(X, Y)
    xy = (X_train, X_test, Y_train, Y_test)
    np.save("model/increase_image_data.npy", xy)

    print("ok", len(Y))
