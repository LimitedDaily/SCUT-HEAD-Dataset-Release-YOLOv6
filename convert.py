import os
import shutil
import random
import xml.etree.ElementTree as elemTree
from PIL import Image
import cv2

def testConvertedData(fname, img_dst, label_dst):
    img_fname = img_dst + fname + ".jpg"
    label_fname = label_dst + fname + ".txt"
    img_width = 0
    img_height = 0
    class_id = -1
    if os.path.exists(img_fname):
        image = Image.open(img_fname)
        img_width, img_height = image.size

    img = cv2.imread(img_fname)
    with open(label_fname, 'r') as f:
        for line in f:
            items = line.split()

            class_id = float(items[0])
            x_center = float(items[1]) * img_width
            y_center = float(items[2]) * img_height
            width = float(items[3]) * img_width
            height = float(items[4]) * img_height

            cv2.rectangle(img, (int(x_center - (width / 2)), int(y_center - (height / 2))),
                          (int(x_center + (width / 2)), int(y_center + (height / 2))), (0, 255, 0), 2)

        f.close()


    cv2.imshow("test", img)
    cv2.waitKey(0)

def copyfile(flist, dst):
    print("copying image files(:"+dst+")...")
    for fpath in flist:
        fname = os.path.splitext(os.path.basename(fpath))
        shutil.copy2(fpath, dst+fname[0]+fname[1])
    print("copy complete")

def convert(label_dst_path, image_dst_path, fnames_list):
    print("converting annotation files(:"+label_dst_path+")...")
    annotation_path = "./data/annotations/"

    # ---convert data ---
    for fname in fnames_list:
        with open(label_dst_path + fname + ".txt", "w") as f:
            annotation_fpath = annotation_path + fname + ".xml"
            tree = elemTree.parse(annotation_fpath)
            root = tree.getroot()

            size = root.find('size')
            width = int(size.find('width').text)
            height = int(size.find('height').text)
            if width <= 0 or height <= 0:
                print(fname)
                img_fname = image_dst_path + fname +".jpg"
                if os.path.exists(img_fname):
                    image = Image.open(img_fname)
                    width, height = image.size
                    print("width or height is zero.. read from img file (width : " + str(width) + ", " + str(height)+")")

            for obj in root.findall('object'):
                xmin = int(obj.find('bndbox/xmin').text)
                ymin = int(obj.find('bndbox/ymin').text)
                xmax = int(obj.find('bndbox/xmax').text)
                ymax = int(obj.find('bndbox/ymax').text)

                class_id = 0
                center_x = (xmin + ((xmax - xmin) / 2)) / width
                center_y = (ymin + ((ymax - ymin) / 2)) / height
                bbox_width = (xmax - xmin) / width
                bbox_height = (ymax - ymin) / height

                f.write(str(class_id) + " " + str(center_x) + " " + str(center_y) + " " + str(bbox_width) + " " + str(bbox_height) + "\n")
            f.close()
    print("convert complete")

f_test = open('./data/imagesets/main/test.txt', 'r')
f_train = open('./data/imagesets/main/train.txt', 'r')
f_val = open('./data/imagesets/main/val.txt', 'r')

fnames_test = f_test.readlines()
fnames_test = list(map(lambda s: s.strip(), fnames_test))

fnames_train = f_train.readlines()
fnames_train = list(map(lambda s: s.strip(), fnames_train))

fnames_val = f_val.readlines()
fnames_val = list(map(lambda s: s.strip(), fnames_val))

print('train dataset count : ' + str(len(fnames_train)))
print('val dataset count : ' + str(len(fnames_val)))
print('test dataset count : ' + str(len(fnames_test)))

dir_path = './data/jpegimages/'

train_res = []
val_res = []
test_res = []

# Iterate org_directory
for fname in os.listdir(dir_path):
    file_path = os.path.join(dir_path, fname)
    fname_noext = os.path.basename(fname).split('.')[0]
    if os.path.isfile(file_path):
        if fname_noext in fnames_train:
            train_res.append(file_path)
        if fname_noext in fnames_val:
            val_res.append(file_path)
        if fname_noext in fnames_test:
            test_res.append(file_path)

#copy files to custom_dataset
train_image_dst_path = './custom_dataset/images/train/'
test_image_dst_path = './custom_dataset/images/test/'
val_image_dst_path = './custom_dataset/images/val/'

copyfile(train_res, train_image_dst_path)
copyfile(val_res, val_image_dst_path)
copyfile(test_res, test_image_dst_path)

#convert annotation to txt
annotation_path = "./data/annotations/"

train_label_dst_path = "./custom_dataset/labels/train/"
test_label_dst_path = "./custom_dataset/labels/test/"
val_label_dst_path = "./custom_dataset/labels/val/"

convert(train_label_dst_path, train_image_dst_path, fnames_train)
convert(test_label_dst_path, test_image_dst_path, fnames_test)
convert(val_label_dst_path, val_image_dst_path, fnames_val)

#testConvertedData(random.choice(fnames_train), train_image_dst_path, train_label_dst_path)
#testConvertedData("PartB_00000", train_image_dst_path, train_label_dst_path)