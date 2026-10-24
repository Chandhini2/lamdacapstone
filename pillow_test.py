from PIL import Image
import io

def lambda_handler(event, context):
    image = Image.new("RGB", (100, 100), color="red")
    output = io.BytesIO()
    image.save(output, format="PNG")

    return {
        "statusCode": 200,
        "message": "Pillow layer works",
        "image_size": list(image.size),
        "png_bytes": len(output.getvalue())
    }
