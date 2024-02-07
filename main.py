from PIL import Image
import numpy as np

class KutterJordanBossen:
    NUM_OF_REPEATS = 15

    def __init__(self):
        self.x_pos = self.y_pos = 3

    def encode(self, text, input_file, output_file):
        image = Image.open(input_file)
        message = self.prepare_text_to_encode(text)
        result = image.copy()

        if (len(message) * 8 * self.NUM_OF_REPEATS >
                (image.width // 4 - 1) * (image.height // 4 - 1)):
            raise Exception("Image is too small for the given text.")

        for i in range(len(message)):
            self.write_byte(result, message[i])

        result.save(output_file, compression_level=0)
        return output_file

    def decode(self, input_file):
        image = Image.open(input_file)
        self.x_pos = self.y_pos = 3

        len_byte_0 = self.read_byte(image)
        len_byte_1 = self.read_byte(image)
        len_byte_2 = self.read_byte(image)
        len_byte_3 = self.read_byte(image)

        msg_len = ((len_byte_0 & 0xff) << 24) | ((len_byte_1 & 0xff) << 16) | \
                  ((len_byte_2 & 0xff) << 8) | (len_byte_3 & 0xff)

        if msg_len <= 0 or (msg_len * 8 * self.NUM_OF_REPEATS >
                            (image.width // 4 - 1) * (image.height // 4 - 1)):
            raise Exception("Error decoding. Make sure the image contains text.")

        msg_bytes = [self.read_byte(image) for _ in range(msg_len)]
        msg = bytes(msg_bytes).decode('utf-8')
        return msg

    def prepare_text_to_encode(self, text):
        msg_bytes = text.encode('utf-8')
        len_bytes = len(msg_bytes).to_bytes(4, byteorder='big')

        message = bytearray(len_bytes + msg_bytes)
        message[len(len_bytes):] = msg_bytes

        return message

    def write_byte(self, img, byte_val):
        for j in range(7, -1, -1):
            bit_val = (byte_val >> j) & 1
            self.write_bit(img, bit_val)

    def read_byte(self, img):
        byte_val = 0

        for _ in range(8):
            byte_val = (byte_val << 1) | (self.read_bit(img) & 1)

        return byte_val

    def write_bit(self, img, bit):
        for _ in range(self.NUM_OF_REPEATS):
            if self.x_pos + 4 > img.width:
                self.x_pos = 3
                self.y_pos += 4

            self.write_into_pixel(img, self.x_pos, self.y_pos, bit, 0.25)
            self.x_pos += 4

    def read_bit(self, img):
        bit_estimate = 0

        for _ in range(self.NUM_OF_REPEATS):
            if self.x_pos + 4 > img.width:
                self.x_pos = 3
                self.y_pos += 4

            bit_estimate += self.read_from_pixel(img, self.x_pos, self.y_pos)
            self.x_pos += 4

        bit_estimate /= self.NUM_OF_REPEATS

        return 1 if bit_estimate > 0.5 else 0

    @staticmethod
    def write_into_pixel(image, x, y, bit, energy):
        red, green, blue = image.getpixel((x, y))

        # Сохраняем исходные значения пикселей
        original_pixel = (red, green, blue)

        # Применяем изменения к пикселям
        pixel_brightness = int(0.29890 * red + 0.58662 * green + 0.11448 * blue)

        modified_blue_component = int(blue + energy * pixel_brightness) if bit > 0 \
            else int(blue - energy * pixel_brightness)

        # Коррекция значений компонентов пикселя, если они выходят за пределы 0-255
        modified_blue_component = max(0, min(255, modified_blue_component))
        modified_red = max(0, min(255, red))
        modified_green = max(0, min(255, green))

        # Обновляем значения пикселей с учетом изменений
        pixel_modified = (modified_red, modified_green, modified_blue_component)
        image.putpixel((x, y), pixel_modified)

        # Возвращаем исходные значения пикселей
        return original_pixel

    def read_from_pixel(self, image, x, y):
        estimate = 0

        for i1 in range(1, 4):
            pixel = image.getpixel((x + i1, y))
            estimate += pixel[2]

        for i1 in range(1, 4):
            pixel = image.getpixel((x - i1, y))
            estimate += pixel[2]

        for i1 in range(1, 4):
            pixel = image.getpixel((x, y + i1))
            estimate += pixel[2]

        for i1 in range(1, 4):
            pixel = image.getpixel((x, y - i1))
            estimate += pixel[2]

        estimate //= 12

        pixel = image.getpixel((x, y))
        blue = pixel[2]

        return 1 if blue > estimate else 0
    
def calculate_psnr(image_path):
    img = np.array(Image.open(image_path))

    if img is None:
        raise ValueError("Unable to load image")

    black_img = np.zeros_like(img, dtype=np.uint8)

    psnr_values = {}
    for channel in range(3):
        mse = np.mean((img[:, :, channel] - black_img[:, :, channel]) ** 2)
        if mse == 0:
            psnr_values[channel] = float('inf')
        else:
            max_pixel = 255.0
            psnr_values[channel] = 20 * np.log10(max_pixel / np.sqrt(mse))

    return psnr_values

kjb = KutterJordanBossen()
input_image_path = "Images2/out.bmp"
output_image_path = input_image_path[0:-4] + "_encoded" + input_image_path[-4:]

with open("message.txt", "r") as message_file:
    message = message_file.readline()

encoded_image_path = kjb.encode(message, input_image_path, output_image_path)
decoded_text = kjb.decode(encoded_image_path)
print("Decoded text: " + decoded_text)

psnr_components = calculate_psnr(input_image_path)
print("PSNR for Red channel:", psnr_components[0])
print("PSNR for Green channel:", psnr_components[1])
print("PSNR for Blue channel:", psnr_components[2])


print("\n")
psnr_components = calculate_psnr(output_image_path)
print("PSNR for Red channel:", psnr_components[0])
print("PSNR for Green channel:", psnr_components[1])
print("PSNR for Blue channel:", psnr_components[2])
