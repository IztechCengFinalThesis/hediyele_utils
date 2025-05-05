from PIL import Image
import io

class ImageProcessor:
    TARGET_SIZE = (150, 150)
    OUTPUT_FORMAT = 'PNG'

    @staticmethod
    def prepare_image_for_db(image_path: str) -> bytes | None:
        try:
            with Image.open(image_path) as img:
                if img.mode != 'RGB':
                     img = img.convert('RGB')

                img.thumbnail(ImageProcessor.TARGET_SIZE, Image.Resampling.LANCZOS)

                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format=ImageProcessor.OUTPUT_FORMAT)
                img_bytes = img_byte_arr.getvalue()
                return img_bytes
        except FileNotFoundError:
            print(f"Error: Image file not found at {image_path}")
            return None
        except Exception as e:
            print(f"Error processing image {image_path}: {e}")
            return None
