from PIL import Image, ImageDraw

class KutterJordanBossen:
    NUM_OF_REPEATS = 15

    def __init__(self):
        self.x_pos = self.y_pos = 3

    def encode(self, text, bitmap):
        message = self.prepare_text_to_encode(text)
        result = bitmap.copy()

        if (len(message) * 8 * self.NUM_OF_REPEATS >
                (bitmap.width // 4 - 1) * (bitmap.height // 4 - 1)):
            raise Exception("Image is too small for the given text.")

        for i in range(len(message)):
            self.write_byte(result, message[i])

        return result

    def decode(self, bitmap):
        self.x_pos = self.y_pos = 3

        len_byte_0 = self.read_byte(bitmap)
        len_byte_1 = self.read_byte(bitmap)
        len_byte_2 = self.read_byte(bitmap)
        len_byte_3 = self.read_byte(bitmap)

        msg_len = ((len_byte_0 & 0xff) << 24) | ((len_byte_1 & 0xff) << 16) | \
                  ((len_byte_2 & 0xff) << 8) | (len_byte_3 & 0xff)

        if msg_len <= 0 or (msg_len * 8 * self.NUM_OF_REPEATS >
                            (bitmap.width // 4 - 1) * (bitmap.height // 4 - 1)):
            raise Exception("Error decoding. Make sure the image contains text.")

        msg_bytes = [self.read_byte(bitmap) for _ in range(msg_len)]
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

        pixel_brightness = int(0.29890 * red + 0.58662 * green + 0.11448 * blue)

        modified_blue_component = int(blue + energy * pixel_brightness) if bit > 0 \
            else int(blue - energy * pixel_brightness)

        modified_blue_component = max(0, min(255, modified_blue_component))

        pixel_modified = (red, green, modified_blue_component)
        image.putpixel((x, y), pixel_modified)

        return modified_blue_component

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

# Пример использования:
kjb = KutterJordanBossen()
image = Image.open("makima.png")
encoded_image = kjb.encode("Hello, world!", image)
decoded_text = kjb.decode(encoded_image)
print(decoded_text)
