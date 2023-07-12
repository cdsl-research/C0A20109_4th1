from machine import Pin, I2C, RTC
import utime
import urequests
import ujson
import time

class AE_BMX055:
    def __init__(self, i2c, *, addr_accel=25, addr_mag=19, debug=False):
        self.__i2c_wait_time = 200
        self.__i2c = i2c
        self.__addr_accel = addr_accel
        self.__addr_mag = addr_mag
        self.__debug = debug

        self.__init_accel()
        self.__init_mag()

    

    @property
    def accel(self):
        data = [None] * 6
        for i in range(6):
            # Read 6 bytes of data
            # xAccl lsb, xAccl msb, yAccl lsb, yAccl msb, zAccl lsb, zAccl msb
            data[i] = self.__read_1byte(addr=self.__addr_accel, register=(2 + i))

        if self.__debug:
            print('AE_BMX055.accel raw i2c data:', [hex(x) for x in data])

        # Convert the data to 12-bits
        xAccl = ((data[1] * 256) + (data[0] & 0xF0)) / 16
        if xAccl > 2047:
            xAccl -= 4096
        yAccl = ((data[3] * 256) + (data[2] & 0xF0)) / 16
        if yAccl > 2047:
            yAccl -= 4096
        zAccl = ((data[5] * 256) + (data[4] & 0xF0)) / 16
        if zAccl > 2047:
            zAccl -= 4096

        xAccl = xAccl * 0.0098  # renge +-2g
        yAccl = yAccl * 0.0098  # renge +-2g
        zAccl = zAccl * 0.0098  # renge +-2g

        return xAccl, yAccl, zAccl

    @property
    def mag(self):
        data = [None] * 8
        for i in range(8):
            # Read 6 bytes of data
            # xMag lsb, xMag msb, yMag lsb, yMag msb, zMag lsb, zMag msb
            data[i] = self.__read_1byte(addr=self.__addr_mag, register=(0x42 + i))

        if self.__debug:
            print('AE_BMX055.mag raw i2c data:', [hex(x) for x in data])

        # Convert the data
        xMag = ((data[1]<<8) | (data[0]>>3))
        if xMag > 4095:
            xMag -= 8192
        yMag = ((data[3]<<8) | (data[2]>>3))
        if yMag > 4095:
            yMag -= 8192
        zMag = ((data[5]<<8) | (data[4]>>3))
        if zMag > 16383:
          zMag -= 32768

        return xMag, yMag, zMag


    def __init_accel(self):
        print("init_accel")
        time.sleep_ms(self.__i2c_wait_time)

        self.__i2c.writeto_mem(self.__addr_accel, 0x0F, b'\x03')
        time.sleep_ms(self.__i2c_wait_time)

        self.__i2c.writeto_mem(self.__addr_accel, 0x10, b'\x08')
        time.sleep_ms(self.__i2c_wait_time)

        self.__i2c.writeto_mem(self.__addr_accel, 0x11, b'\x00')
        time.sleep_ms(self.__i2c_wait_time)

    def __init_gyro(self):
        print("init_gyro")
        time.sleep_ms(self.__i2c_wait_time)

        self.__i2c.writeto_mem(self.__addr_gyro, 0x0F, b'\x04')
        time.sleep_ms(self.__i2c_wait_time)

        self.__i2c.writeto_mem(self.__addr_gyro, 0x10, b'\x07')
        time.sleep_ms(self.__i2c_wait_time)

        self.__i2c.writeto_mem(self.__addr_gyro, 0x11, b'\x00')
        time.sleep_ms(self.__i2c_wait_time)


    def __init_mag(self):
        print("init_mag")
        time.sleep_ms(self.__i2c_wait_time)

        self.__i2c.writeto_mem(self.__addr_gyro, 0x4B, b'\x83')
        time.sleep_ms(self.__i2c_wait_time)

        self.__i2c.writeto_mem(self.__addr_gyro, 0x4B, b'\x01')
        time.sleep_ms(self.__i2c_wait_time)

        self.__i2c.writeto_mem(self.__addr_gyro, 0x4C, b'\x00')
        time.sleep_ms(self.__i2c_wait_time)

        self.__i2c.writeto_mem(self.__addr_gyro, 0x4E, b'\x84')
        time.sleep_ms(self.__i2c_wait_time)

        self.__i2c.writeto_mem(self.__addr_gyro, 0x51, b'\x04')
        time.sleep_ms(self.__i2c_wait_time)

        self.__i2c.writeto_mem(self.__addr_gyro, 0x52, b'\x16')
        time.sleep_ms(self.__i2c_wait_time) 

    def __read_1byte(self, *, addr, register):
        return int.from_bytes(self.__i2c.readfrom_mem(addr, register, 1), 'big')

# ----- ----- ----- ----- ----- #
def write_data(file_path,time,x,y,z):
    # データを追記
    data_string = '{},{:>+13.4f},{:>+13.4f},{:>+13.4f}\n'.format(time,x, y, z)
    f = open(file_path, 'a')
    f.write(str(data_string))
    f.close()

def write_line(file_path):
    # ラインを追記
    f = open(file_path, 'a')
    f.write("--------------------\n")
    f.close()

I2C_SCL_PIN = 22
I2C_SDA_PIN = 21

p_scl = Pin(I2C_SCL_PIN, Pin.IN, Pin.PULL_UP)
p_sda = Pin(I2C_SDA_PIN, Pin.IN, Pin.PULL_UP)
i2c = I2C(scl=Pin(I2C_SCL_PIN), sda=Pin(I2C_SDA_PIN))

bmx055 = AE_BMX055(i2c)

accl_path = "accl.csv"
gyaro_path = "mag.csv"
write_line(accl_path)
write_line(mag_path)

while True:
    time_data = utime.ticks_ms() / 1000
    # BMX055 加速度の読み取り
    xAccl, yAccl, zAccl = bmx055.accel
    # BMX055 磁気の読み取り
    xMag, yMag, zMag = bmx055.mag
    print('Accl= ({:>+13.4f}, {:>+13.4f}, {:>+13.4f})'.format(xAccl, yAccl, zAccl))
    print('Mag=  ({:>+13.4f}, {:>+13.4f}, {:>+13.4f})'.format(xMag, yMag, zMag))
    write_data(accl_path,time_data,xAccl,yAccl,zAccl)
    write_data(gyaro_path,time_data,xMag,yMag,zMag)
    time.sleep_ms(100)

