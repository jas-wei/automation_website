from PIL import Image

def add_AI_disturbance_overlay(input_path, opacity):
    """
    this fuction overlays an AI disturbance image on top of your original image
    so that AI would have a harder time training on it

    Parameters
        input_path: filepath to image you want to protect
        output_path: filepath to where you want your altered iamge to go
        overlay_path: filepath to AI disturbance overlay filter
        opacity: adjust opacity of overlay image in between 0.00 - 1.00 (0% to 100%)

    Returns 
        None
    """
    # this path mgiht need to change later
    output_path = r'.\website\automation_script\__pycache__\output.png'
    overlay_path = r'.\website\automation_script\__pycache__\overlay.png'

    # Open the input image and convert it to RGBA mode (includes alpha channel for transparency)
    input_image = Image.open(input_path).convert("RGBA")
    overlay_image = Image.open(overlay_path).convert("RGBA")

    # Resize overlay to match the size of the input image
    # input_image.size provides dimentions for overlay_image to resize into
    # Image.Resampling.LANCZOS uses math to make the newly sized image high quality
    overlay_image = overlay_image.resize(input_image.size, Image.Resampling.LANCZOS)

    # Adjust opacity of the overlay image
    overlay_image = overlay_image.copy() #creates a copy so that og overlay is not altered
    alpha = overlay_image.split()[3]  # Extract the alpha channel from index 3 of RGBA collection
    alpha = alpha.point(lambda p: p * opacity)  # Modify the alpha channel to be new opacity
    overlay_image.putalpha(alpha) #apply new alpha channel to overlay image

    # Paste the overlay image onto the input image
    input_image.paste(overlay_image, overlay_image)

    # Save the resulting image
    input_image.save(output_path)
    input_image.show()


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
