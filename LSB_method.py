from PyQt4.QtCore import qAbs

__author__ = 'dreyus95'

from PIL import Image

class LSB_method():

    """
        A class that offers the functionality of a simple LSB method.
    """

    def hide_image(self,publicImgPath,hiddenImgPath,sizeOfHidden=4):
        """
            Method used to hide a frame inside a picture.

            - size of the hidden image is saved in the last 2 pixels
              of stego object

        :param publicImgPath: path to the image we use as a storage
        :param hiddenImgPath: path to the cropped frame that we want to hide
        :param sizeOfHidden: number of bits used for hidden frame inside original

        :return: COMBINED = stego object
        """

        data = Image.open(publicImgPath)
        hidden = Image.open(hiddenImgPath)

        # creating a new image used to store original+hidden frame
        combination = Image.new('RGB', (data.size[0], data.size[1]), "black")
        for x in range(data.size[0]):
            for y in range(data.size[1]):
                p = data.getpixel((x, y))
                combination.putpixel((x, y), p)

        # the magic of shifting bits that we can use between original and hidden frame
        shift = (8 - sizeOfHidden)
        visible_mask = 0xFF << sizeOfHidden
        hidden_mask = 0xFF >> shift

        # we know that hidden.size is ALWAYS smaller than data.size
        for x in range(hidden.size[0]):
            for y in range(hidden.size[1]):
                p = data.getpixel((x, y))
                q = hidden.getpixel((x, y))
                red = (p[0] & visible_mask) | ((q[0] >> shift) & hidden_mask)
                green = (p[1] & visible_mask) | ((q[1] >> shift) & hidden_mask)
                blue = (p[2] & visible_mask) | ((q[2] >> shift) & hidden_mask)
                combination.putpixel((x, y), (red, green, blue))

        # store the width and height in last pixels
        p = combination.getpixel((combination.size[0]-1, combination.size[1]-1))
        q = combination.getpixel((combination.size[0]-1, combination.size[1]-2))

        width = list(p)
        height = list(q)

        diff = hidden.size[0] % 3
        width[0], width[1], width[2] = hidden.size[0]/3, hidden.size[0]/3, hidden.size[0]/3+diff

        diff = hidden.size[1] % 3
        height[0], height[1], height[2] = hidden.size[1]/3, hidden.size[1]/3, hidden.size[1]/3+diff

        p = tuple(width)
        q = tuple(height)

        combination.putpixel((combination.size[0]-1,combination.size[1]-1), p)
        combination.putpixel((combination.size[0]-1,combination.size[1]-2), q)

        return combination



    def extract_hiddenImage(self,combinedImage,sizeOfHidden=4):
        """
            Method used for extracting a hidden frame out of the picture.

        :param combinedImage: stego object
        :param sizeOfHidden: number of bits used for hidden frame inside stego object

        :return: Hidden part of the stego object
        """
        p = combinedImage.getpixel((combinedImage.size[0]-1, combinedImage.size[1]-1))
        q = combinedImage.getpixel((combinedImage.size[0]-1, combinedImage.size[1]-2))

        width = p[0] + p[1] + p[2]
        height = q[0] + q[1] + q[2]
        img = Image.new('RGB', (width,height), "black")
        shift = (8 - sizeOfHidden)
        hidden_mask = 0xFF >> shift

        for x in range(width):
            for y in range(height):
                p = combinedImage.getpixel((x, y))
                red = (p[0] & hidden_mask) << shift
                green = (p[1] & hidden_mask) << shift
                blue = (p[2] & hidden_mask) << shift
                img.putpixel((x, y), (red, green, blue))

        return img

