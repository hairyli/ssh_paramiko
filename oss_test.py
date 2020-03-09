import oss2
import time
import cv2
import os
import RPi.GPIO as GPIO

class Camera(object):
    """摄像的初始化，配置"""
    def __init__(self, channel):
        self.capture = cv2.VideoCapture(channel)

        self.fps = int(self.capture.get(cv2.CAP_PROP_FPS))
        self.video_height = int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.video_width = int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))

        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.video_width)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.video_height)
        self.capture.set(cv2.CAP_PROP_FPS, self.fps)
        # 设置摄像头的缓存图片为1，为了能获取实时的图像
        self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    def get_pic(self, image_dir=None, image_name=None, is_show=False, is_write=False):
        """
        写入照片
        """
        if self.capture.isOpened():
            # 读取缓存中的图片，起到清空缓存的作用
            abandon_ret, abandon_frame = self.capture.read()
            # 用于处理/上传的图片
            ret, frame = self.capture.read()
            # 判断图片信息是否读取成功
            if ret is False:
                print('get picture failed')
                return None
            # 是否需要显示
            if is_show is True:
                cv2.imshow('image', frame)
                cv2.waitKey(200)
            # 是否需要写入到文件中
            if is_write is True:
                cv2.imwrite(image_dir + '/' + image_name, frame)
            print('get picture success')
            return frame

    def release_camera(self):
        """
        释放摄像机资源
        """
        self.capture.release()
        cv2.destroyAllWindows()


class oss(object):
    """对象存储类，将图片传至阿里云端"""
    def __init__(self):
        self.auth = oss2.Auth('LTAIkA49HkgVYUsW', '**********************')
        self.bucket = oss2.Bucket(self.auth, 'http://oss-cn-hangzhou.aliyuncs.com', '20190731')

    def put_image(self, image_dir, image_name):
        put_result = self.bucket.put_object_from_file(image_name, image_dir + '/' + image_name)
        # 状态为200表示成功的上传
        if put_result.status == 200:
            print('put success')

    def get_image(self):
        pass


class gpio(object):
    """触发信号的控制"""
    event_flag = False  # 判断是否有电平触发信号

    def __init__(self, pin):
        """GPIO初始化"""
        self.pin = pin
        # 设置引脚应用模式
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        # 设计引脚触发模式为：上升沿触发模式，防抖的时间为1000ms
        GPIO.add_event_detect(self.pin, GPIO.RISING, callback=gpio.callback, bouncetime=1000)

    @staticmethod
    def callback(flag):
        """回调函数"""
        gpio.event_flag = True

    def stop_event(self):
        GPIO.remove_event_detect(self.pin)

    def start_event(self):
        GPIO.add_event_detect(self.pin, GPIO.RISING, callback=gpio.callback, bouncetime=1000)

    @staticmethod
    def release():
        """GPIO释放引脚资源"""
        GPIO.cleanup()


if __name__ == "__main__":
    picture = None
    sleep_time = 0
    picture_path = './put'
    picture_name = '.jpg'
    gpio_pin = 18

    # oss配置
    oss_server = oss()
    # 开启摄像头
    camera = Camera(0)
    # GPIO初始化
    event = gpio(gpio_pin)

    while True:
        if gpio.event_flag is True:
            gpio.event_flag = False  # 标志位置位
            event.stop_event()  # 关闭事件触发
            picture_name = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time())) + '.jpg'
            # 获取图片
            picture = camera.get_pic(picture_path, picture_name, is_show=True, is_write=True)

            if picture is not None:
                pass
                # oss_server.put_image(picture_path, picture_name)
            else:
                camera.release_camera()
                camera = Camera(0)
            # 删除照片，防止内存爆炸
            os.remove(picture_path + '/' + picture_name)

            event.start_event()  # 开启事件触发
            # time.sleep(sleep_time)

        gpio.release()