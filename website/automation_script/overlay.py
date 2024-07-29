from PIL import Image

def add_AI_disturbance_overlay(input_path, opacity, output_path):
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
        input_image.save(output_path)
        # input_image.show()
    except Exception as e:
        print(f"An error occurred: {e}")


# def add_watermark(input_path, output_path, watermark_path, opacity):


# def main():
#     input_path = 'Attack.png'
#     # overlay_path = 'overlay.png'
#     # output_path = 'output.png'
#     # watermark_text = 'klip_sk'
#     opacity = 0.05

#     # Call the function to add the watermark overlay
#     add_AI_disturbance_overlay(input_path, opacity)






# if (__name__ == '__main__'):
#     main()
