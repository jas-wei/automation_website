from PIL import Image, ImageDraw, ImageFont
import time

def timeit(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()  # Record the start time
        result = func(*args, **kwargs)  # Call the actual function
        end_time = time.time()  # Record the end time
        elapsed_time = end_time - start_time  # Calculate the elapsed time
        print(f"\n\n\n\nFunction '{func.__name__}' executed in {elapsed_time:.4f} seconds\n\n\n\n")
        return result  # Return the result of the function
    return wrapper

def show_it(input_path):
    image = Image.open(input_path).convert("RGBA")
    image.show()

# @timeit
def add_AI_disturbance_overlay(input_path, output_path, opacity):
    """
    This function overlays an AI disturbance image on top of your original image
    so that AI would have a harder time training on it.

    Parameters:
        input_path: filepath to image you want to protect
        opacity: adjust opacity of overlay image in between 0.00 - 1.00 (0% to 100%)

    Returns:
        None
    """
    try:
        # Ensure opacity is a float
        opacity = float(opacity)
        if not (0.0 <= opacity <= 1.0):
            raise ValueError("Opacity must be between 0.00 and 1.00")

        # This path might need to change later
        
        overlay_path = r'.\website\automation_script\__pycache__\overlay.png'
        # output_path = r'.\website\downloads\output.png'

        # Open the input image and convert it to RGBA mode (includes alpha channel for transparency)
        input_image = Image.open(input_path).convert("RGBA")
        overlay_image = Image.open(overlay_path).convert("RGBA")

        # Resize overlay to match the size of the input image
        # input_image.size provides dimensions for overlay_image to resize into
        # Image.Resampling.LANCZOS uses math to make the newly sized image high quality
        overlay_image = overlay_image.resize(input_image.size, Image.Resampling.LANCZOS)

        # Adjust opacity of the overlay image
        overlay_image = overlay_image.copy()  # Creates a copy so that the original overlay is not altered
        alpha = overlay_image.split()[3]  # Extract the alpha channel from index 3 of RGBA collection
        alpha = alpha.point(lambda p: p * float(opacity))  # Modify the alpha channel based on the opacity
        overlay_image.putalpha(alpha)  # Apply the modified alpha channel back to the overlay

        # Paste the overlay image onto the input image
        input_image.paste(overlay_image, (0, 0), overlay_image)

        # Save the resulting image
        input_image.save(output_path, format="PNG", compress_level=1)
        # input_image.show()
    except Exception as e:
        print(f"An error occurred: {e}")

# @timeit
def add_watermark(input_path, output_path, watermark_text, opacity, size, style):
    try:
        # Ensure opacity is a float
        opacity = float(opacity)
        size = float(size)
        if not (0.0 <= opacity <= 1.0):
            raise ValueError("Opacity must be between 0.00 and 1.00")

        # Open the original image
        original = Image.open(input_path).convert("RGBA")

        # Create an image for the watermark with an alpha layer (RGBA)
        width, height = original.size
        watermark = Image.new("RGBA", original.size)

        # Load a font and specify the size (e.g., 50 for larger text)
        # font = ImageFont.truetype("calibri.ttf", size)  # Adjust the font size as needed
        # thing = "Newsreader-VariableFont_opsz,wght"
        font = ImageFont.truetype(fr".\website\automation_script\watermark_fonts\{style}.ttf", size)


        # Create a drawing context
        draw = ImageDraw.Draw(watermark)

        # Get the size of the watermark text
        bbox = draw.textbbox((0, 0), watermark_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # Position the text at the bottom right corner
        position = (width - text_width - size, height - text_height - size)

        # Draw the text onto the watermark image
        draw.text(position, watermark_text, font=font, fill=(255, 255, 255, int(255 * opacity)))

        # Combine the original image with the watermark
        combined = Image.alpha_composite(original, watermark)

        # Save the image
        # combined.show()  # Display the image (optional)
        combined.save(output_path, format="PNG", compress_level=1)
        

    except Exception as e:
        print(f"An error occurred: {e}")

def add_watermark_logo(input_path, output_path, opacity, logo_path):
    try:
        # Ensure opacity is a float
        opacity = float(opacity)
        if not (0.0 <= opacity <= 1.0):
            raise ValueError("Opacity must be between 0.00 and 1.00")

        # Open the input image and convert it to RGBA mode (includes alpha channel for transparency)
        input_image = Image.open(input_path).convert("RGBA")
        logo_image = Image.open(logo_path).convert("RGBA")

        # Resize the logo to be 1/5 of the input image's width while maintaining the aspect ratio
        input_width, input_height = input_image.size
        logo_width = input_width // 5  # Logo width is 1/5 of input image width
        logo_aspect_ratio = logo_image.height / logo_image.width
        logo_height = int(logo_width * logo_aspect_ratio)

        logo_image = logo_image.resize((logo_width, logo_height), Image.Resampling.LANCZOS)

        # Adjust the opacity of the logo image
        logo_image = logo_image.copy()  # Create a copy so that the original logo is not altered
        alpha = logo_image.split()[3]  # Extract the alpha channel from the RGBA image
        alpha = alpha.point(lambda p: p * opacity)  # Modify the alpha channel based on the opacity
        logo_image.putalpha(alpha)  # Apply the modified alpha channel back to the logo

        # Position the logo at the bottom-right corner of the input image
        position = (input_width - logo_width - 10, input_height - logo_height - 10)  # 10px padding from the edges

        # Paste the logo onto the input image using the alpha channel as the mask
        input_image.paste(logo_image, position, logo_image)

        # Save the resulting image
        input_image.save(output_path, format="PNG", compress_level=1)

    except Exception as e:
        print(f"An error occurred: {e}")