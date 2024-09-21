from dataclasses import dataclass
import drawsvg as draw
from math import floor

IMG_WIDTH = 800
IMG_HEIGHT = 600

# Fraction of the image's height that contains the refracted wavefronts.
# Measured as a normalised coordinate from top left corner
SLIT_HEIGHT = 0.7

# Distance from the centre of the refraction grating to the centre of a slit
# horizontally, as a fraction of the image width
DISTANCE_FROM_CENTRE_TO_SLIT = 0.2

# Distance between wavefronts as a fraction of the image height
WAVEFRONT_SPACING_HEIGHT = 0.05

GRATING_COLOUR = "black"
BACKGROUND_COLOUR = "white"

GRATING_WIDTH = 10
WAVEFRONT_WIDTH = 1


@dataclass
class NormalisedPoint:
    u: float
    v: float

    def rasterise_height(self, IMG_HEIGHT):
        return floor(IMG_HEIGHT * self.v)

    def rasterise_width(self, IMG_WIDTH):
        return floor(IMG_WIDTH * self.u)


centreLeftSlit = NormalisedPoint(3, 4)


def rasterise_height(normalisedHeight):
    return floor(IMG_HEIGHT * normalisedHeight)


def rasterise_width(normalisedWidth):
    return floor(IMG_WIDTH * normalisedWidth)


if __name__ == "__main__":

    # Get a vector drawing with origin in bottom left
    d = draw.Drawing(IMG_WIDTH, IMG_HEIGHT, origin=(0, 0))

    # Draw the background
    # TODO
    d.append(draw.Rectangle(0, 0, IMG_WIDTH, IMG_HEIGHT, fill=BACKGROUND_COLOUR))

    # Compute the grating width as a normalised coordinate (as it is parameterised
    # by height)
    wavefrontSpacingWidth = WAVEFRONT_SPACING_HEIGHT * IMG_WIDTH / IMG_HEIGHT

    # Draw the grating
    leftGratingLeftPoint = NormalisedPoint(0, SLIT_HEIGHT)
    leftGratingRightPoint = NormalisedPoint(
        0.5 - DISTANCE_FROM_CENTRE_TO_SLIT - wavefrontSpacingWidth / 2,
        SLIT_HEIGHT,
    )
    leftGrating = draw.Line(
        leftGratingLeftPoint.rasterise_width(IMG_WIDTH),
        leftGratingLeftPoint.rasterise_height(IMG_HEIGHT),
        leftGratingRightPoint.rasterise_width(IMG_WIDTH),
        leftGratingRightPoint.rasterise_height(IMG_HEIGHT),
        stroke=GRATING_COLOUR,
        stroke_width=GRATING_WIDTH,
    )
    d.append(leftGrating)

    centreGratingLeftPoint = NormalisedPoint(
        0.5 - DISTANCE_FROM_CENTRE_TO_SLIT + wavefrontSpacingWidth / 2, SLIT_HEIGHT
    )
    centreGratingRightPoint = NormalisedPoint(
        0.5 + DISTANCE_FROM_CENTRE_TO_SLIT - wavefrontSpacingWidth / 2, SLIT_HEIGHT
    )
    centreGrating = draw.Line(
        centreGratingLeftPoint.rasterise_width(IMG_WIDTH),
        centreGratingLeftPoint.rasterise_height(IMG_HEIGHT),
        centreGratingRightPoint.rasterise_width(IMG_WIDTH),
        centreGratingRightPoint.rasterise_height(IMG_HEIGHT),
        stroke=GRATING_COLOUR,
        stroke_width=GRATING_WIDTH,
    )
    d.append(centreGrating)

    rightGratingLeftPoint = NormalisedPoint(
        0.5 + DISTANCE_FROM_CENTRE_TO_SLIT + wavefrontSpacingWidth / 2, SLIT_HEIGHT
    )
    rightGratingRightPoint = NormalisedPoint(1, SLIT_HEIGHT)
    rightGrating = draw.Line(
        rightGratingLeftPoint.rasterise_width(IMG_WIDTH),
        rightGratingLeftPoint.rasterise_height(IMG_HEIGHT),
        rightGratingRightPoint.rasterise_width(IMG_WIDTH),
        rightGratingRightPoint.rasterise_height(IMG_HEIGHT),
        stroke=GRATING_COLOUR,
        stroke_width=GRATING_WIDTH,
    )
    d.append(rightGrating)

    # Draw the wavefronts behind the grating
    currentHeight = SLIT_HEIGHT + WAVEFRONT_SPACING_HEIGHT
    while currentHeight < 1.0:
        wavefrontLeftPoint = NormalisedPoint(0, currentHeight)
        wavefrontRightPoint = NormalisedPoint(1, currentHeight)
        wavefront = draw.Line(
        wavefrontLeftPoint.rasterise_width(IMG_WIDTH),
        wavefrontLeftPoint.rasterise_height(IMG_HEIGHT),
        wavefrontRightPoint.rasterise_width(IMG_WIDTH),
        wavefrontRightPoint.rasterise_height(IMG_HEIGHT),
        stroke=GRATING_COLOUR,
        stroke_width=WAVEFRONT_WIDTH,
        )
        d.append(wavefront)
        currentHeight += WAVEFRONT_SPACING_HEIGHT

    # Get the point that the refraction gratings are centred on,
    # with the origin in the centre of the image
    # Normalised coordinates

    # leftGratingNormalised = NormalisedPoint(0.5-DISTANCE_FROM_CENTRE_TO_SLIT, HEIGHT_BEHIND_SLIT)

    # Draw a circle centred on the left grating
    # TODO

    d.save_png("double-slit.png")
