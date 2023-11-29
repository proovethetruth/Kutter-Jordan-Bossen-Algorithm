from PIL import Image

def embed_watermark(image_path, watermark, output_path):
    # Открываем изображение
    image = Image.open(image_path)
    
    # Конвертируем изображение в режим RGB
    image = image.convert("RGB")
    
    # Получаем размеры изображения
    width, height = image.size
    
    # Преобразовываем водяной знак в бинарный формат
    watermark_bin = ''.join(format(ord(char), '08b') for char in watermark)
    
    # Индексы для бит водяного знака
    watermark_index = 0
    
    # Проходим по каждому пикселю изображения
    for y in range(height):
        for x in range(width):
            # Получаем значения RGB пикселя
            pixel = list(image.getpixel((x, y)))
            
            # Внедряем бит водяного знака в синий канал
            if watermark_index < len(watermark_bin):
                if watermark_bin[watermark_index] == '1':
                    pixel[2] |= 1  # Устанавливаем младший бит в 1
                else:
                    pixel[2] &= ~1  # Обнуляем младший бит
                watermark_index += 1
            
            # Обновляем пиксель в изображении
            image.putpixel((x, y), tuple(pixel))
    
    # Сохраняем результат
    image.save(output_path)

def extract_watermark(image_path, watermark_length):
    # Открываем изображение
    image = Image.open(image_path)
    
    # Конвертируем изображение в режим RGB
    image = image.convert("RGB")
    
    # Получаем размеры изображения
    width, height = image.size
    
    # Строка для хранения извлеченного водяного знака
    extracted_watermark = ""
    
    # Проходим по каждому пикселю изображения
    for y in range(height):
        for x in range(width):
            # Получаем значение синего канала пикселя
            blue_channel = image.getpixel((x, y))[2]
            
            # Извлекаем младший бит из синего канала и добавляем в строку
            extracted_watermark += str(blue_channel & 1)
            
            # Если достигнута длина водяного знака, завершаем извлечение
            if len(extracted_watermark) == watermark_length:
                return extracted_watermark

def binary_to_text(binary_str):
    text = ""
    for i in range(0, len(binary_str), 8):
        byte = binary_str[i:i+8]
        text += chr(int(byte, 2))
    return text

# Пример использования
image_path = "input_image.bmp"
watermark_text = "Hello, Watermark!"
output_path = "output_image_with_watermark.bmp"

# Внедрение водяного знака
embed_watermark(image_path, watermark_text, output_path)

# Извлечение водяного знака
extracted_watermark = extract_watermark(output_path, len(watermark_text) * 8)
print("Extracted Watermark:", extracted_watermark)

# Преобразование бинарной последовательности в текст
decoded_text = binary_to_text(extracted_watermark)
print("Decoded Text:", decoded_text)
