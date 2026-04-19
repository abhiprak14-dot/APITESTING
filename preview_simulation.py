from PIL import Image
import io

# Load the full screenshot
img = Image.open("api_report.png")
width, height = img.size
print(f"Full image size: {width}x{height}")

# WhatsApp crops to 1.91:1 ratio from the top
preview_height = int(width / 1.91)
print(f"WhatsApp preview will show top: {width}x{preview_height}")

# Crop to simulate WhatsApp preview
preview = img.crop((0, 0, width, preview_height))
preview.save("whatsapp_preview_simulation.png")
print("Preview simulation saved!")
