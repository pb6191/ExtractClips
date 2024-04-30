# %%

# %% load modules

from pathlib import Path
import numpy as np
import pandas as pd
from PIL import Image

pd.set_option(
    "display.max_rows",
    8,
    "display.max_columns",
    None,
    "display.width",
    None,
    "display.expand_frame_repr",
    True,
    "display.max_colwidth",
    None,
)

np.set_printoptions(
    edgeitems=5,
    linewidth=233,
    precision=4,
    sign=" ",
    suppress=True,
    threshold=50,
    formatter=None,
)


# %%


images = Path("extractedImgs")
images = list(images.glob("*.jpg"))

image = images[0]

# %%

# Open an image file
with Image.open(image) as img:
    # Define the area to crop (left, top, right, bottom)
    # These coordinates should be adjusted to your specific needs
    area = (10, 10, 1500, 1000)  # Example coordinates
    cropped_img = img.crop(area)

    # reduce quality
    # img.save("_test.jpg", quality=80)

    new_width = int(img.width // 2)
    new_height = int(img.height // 2)

    # Resize the image
    resized_img = img.resize((new_width, new_height), Image.LANCZOS)

    # Save the resized image
    resized_img.save("_test.jpg")

    # Optionally, display the resized image
    resized_img.show()

    # # Save the cropped image
    # cropped_img.save("_test.jpg")

    # # Optionally, display the cropped image
    # cropped_img.show()

# %%
