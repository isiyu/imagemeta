import os
import unittest
from pkg_resources import resource_filename

import imagemeta.imageMetaLib as imageMetaLib


IMG_3276_meta = {'image': 'mock_bucket/IMG_3276.JPG', 'exif_metadata': {'Image Make': 'Apple', 'Image Model': 'iPhone X', 'Image Orientation': 'Horizontal (normal)', 'Image XResolution': '72', 'Image YResolution': '72', 'Image ResolutionUnit': 'Pixels/Inch', 'Image Software': '12.1.4', 'Image DateTime': '2019:03:13 11:04:13', 'Image TileWidth': '512', 'Image TileLength': '512', 'Image ExifOffset': '218', 'GPS GPSLatitudeRef': 'N', 'GPS GPSLatitude': '[40, 42, 1567/50]', 'GPS GPSLongitudeRef': 'W', 'GPS GPSLongitude': '[73, 56, 129/4]', 'GPS GPSAltitudeRef': '0', 'GPS GPSAltitude': '11497/428', 'GPS GPSTimeStamp': '[15, 4, 11]', 'GPS GPSSpeedRef': 'K', 'GPS GPSSpeed': '13/50', 'GPS GPSImgDirectionRef': 'T', 'GPS GPSImgDirection': '57520/193', 'GPS GPSDestBearingRef': 'T', 'GPS GPSDestBearing': '57520/193', 'GPS GPSDate': '2019:03:13', 'GPS Tag 0x001F': '5', 'Image GPSInfo': '1832', 'EXIF ExposureTime': '1/2825', 'EXIF FNumber': '9/5', 'EXIF ExposureProgram': 'Program Normal', 'EXIF ISOSpeedRatings': '20', 'EXIF ExifVersion': '0221', 'EXIF DateTimeOriginal': '2019:03:13 11:04:13', 'EXIF DateTimeDigitized': '2019:03:13 11:04:13', 'EXIF ComponentsConfiguration': 'YCbCr', 'EXIF ShutterSpeedValue': '2545/222', 'EXIF ApertureValue': '2159/1273', 'EXIF BrightnessValue': '10084/913', 'EXIF ExposureBiasValue': '0', 'EXIF MeteringMode': 'Pattern', 'EXIF Flash': 'Flash did not fire, compulsory flash mode', 'EXIF FocalLength': '4', 'EXIF SubjectArea': '[2015, 1511, 2217, 1330]', 'EXIF SubSecTimeOriginal': '710', 'EXIF SubSecTimeDigitized': '710', 'EXIF FlashPixVersion': '0100', 'EXIF ExifImageWidth': '4032', 'EXIF ExifImageLength': '3024', 'EXIF SensingMethod': 'One-chip color area', 'EXIF SceneType': 'Directly Photographed', 'EXIF ExposureMode': 'Auto Exposure', 'EXIF WhiteBalance': 'Auto', 'EXIF FocalLengthIn35mmFilm': '28', 'EXIF SceneCaptureType': 'Standard', 'EXIF LensSpecification': '[4, 6, 9/5, 12/5]', 'EXIF LensMake': 'Apple', 'EXIF LensModel': 'iPhone X back dual camera 4mm f/1.8', 'MakerNote Tag 0x0001': '10', 'MakerNote Tag 0x0002': '[153, 0, 155, 0, 160, 0, 171, 0, 167, 0, 169, 0, 171, 0, 175, 0, 180, 0, 183, 0, ... ]', 'MakerNote Tag 0x0003': '[6, 7, 8, 85, 102, 108, 97, 103, 115, 85, 118, 97, 108, 117, 101, 89, 116, 105, 109, 101, ... ]', 'MakerNote Tag 0x0004': '1', 'MakerNote Tag 0x0005': '207', 'MakerNote Tag 0x0006': '214', 'MakerNote Tag 0x0007': '1', 'MakerNote Tag 0x0008': '[2933/262, 15937/5025, 128/51]', 'MakerNote Tag 0x000C': '[1065317/1397843283, 549813689/387783117]', 'MakerNote Tag 0x000D': '35', 'MakerNote Tag 0x000E': '4', 'MakerNote Tag 0x0010': '1', 'MakerNote Tag 0x0014': '1', 'MakerNote Tag 0x0016': 'M/Pg2m4ksUiFqQ', 'MakerNote Tag 0x0017': '8192', 'MakerNote Tag 0x0019': '0', 'MakerNote Tag 0x001A': '', 'MakerNote Tag 0x001F': '0', 'MakerNote Tag 0x0021': '1/0', 'MakerNote Tag 0x0023': '[65536, 262144]', 'MakerNote Tag 0x0025': '0', 'MakerNote Tag 0x0026': '0', 'MakerNote Tag 0x0027': '1/6'}}

def request_gc_api_image(url):
    img = url.split('/')[-1]
    bucket = url.split('/')[-2]
    img_path = resource_filename(__name__, '/%s/%s'%(bucket,img))
    return open(img_path, 'rb')

def request_gc_api_bucket(url):
    mock_file = resource_filename(__name__, 'mock_list_bucket_response')
    return open(mock_file, 'r')

class TestImageMetaLib(unittest.TestCase):

    def test_get_image_meta(self):
        imageMetaLib.request_gc_api = request_gc_api_image
        img_path = resource_filename(__name__, 'mock_bucket/IMG_3276.JPG')

        IMG_3276_meta_test = imageMetaLib.get_image_meta('mock_bucket', 'IMG_3276.JPG')
        self.assertEqual(IMG_3276_meta, IMG_3276_meta_test)

    def test_list_bucket(self):
        imageMetaLib.request_gc_api = request_gc_api_bucket
        files = ['IMG_3276.JPG', 'greece.jpg']

        bucket_objects = imageMetaLib.list_bucket('mock_bucket')
        self.assertEqual(files, bucket_objects)

if __name__ == '__main__':
    unittest.main()
