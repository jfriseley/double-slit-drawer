from dataclasses import dataclass
import drawsvg as draw
from math import floor

IMG_WIDTH = 800
IMG_HEIGHT = 600

# Fraction of the image's height that contains the refracted wavefronts.
# Measured as a normalised coordinate from top left corner
SLIT_HEIGHT = 0.7



# Distance between wavefronts as a fraction of the image height

WAVEFRONT_SPACING_WIDTH = 0.05

# How many wavefronts from the centre of the image to the centre of a slit
WAVEFRONTS_FROM_CENTER_TO_SLIT : int= 5


GRATING_COLOUR ='white'
WAVEFRONT_COLOUR = 'white'
BACKGROUND_COLOUR = 'blue'

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


def rasterise_height(normalisedHeight):
    return floor(IMG_HEIGHT * normalisedHeight)


def rasterise_width(normalisedWidth):
    return floor(IMG_WIDTH * normalisedWidth)


if __name__ == "__main__":

    # Get a vector drawing with origin in top left
    d = draw.Drawing(IMG_WIDTH, IMG_HEIGHT, origin=(0, 0))

    # Draw the background
    d.append(draw.Rectangle(0, 0, IMG_WIDTH, IMG_HEIGHT, fill=BACKGROUND_COLOUR))

    # Compute the grating width as a normalised coordinate (as it is parameterised
    # by height)
    wavefrontSpacingHeight = WAVEFRONT_SPACING_WIDTH * IMG_HEIGHT / IMG_WIDTH

    # Distance from the centre of the refraction grating to the centre of a slit
    # We want the length of the centre grating to be a multiple of wavefront spacing width
    # TODO
    # Gap between gratings needs to be 2*WAVEFRONT_SPACING_WIDTH
    distanceFromCentreToSlit = WAVEFRONTS_FROM_CENTER_TO_SLIT*WAVEFRONT_SPACING_WIDTH

    # Draw the wavefronts behind the grating
    currentHeight = SLIT_HEIGHT + WAVEFRONT_SPACING_WIDTH
    while currentHeight < 1.0:
        wavefrontLeftPoint = NormalisedPoint(0, currentHeight)
        wavefrontRightPoint = NormalisedPoint(1, currentHeight)
        wavefront = draw.Line(
            wavefrontLeftPoint.rasterise_width(IMG_WIDTH),
            wavefrontLeftPoint.rasterise_height(IMG_HEIGHT),
            wavefrontRightPoint.rasterise_width(IMG_WIDTH),
            wavefrontRightPoint.rasterise_height(IMG_HEIGHT),
            stroke=WAVEFRONT_COLOUR,
            stroke_width=WAVEFRONT_WIDTH,
        )
        d.append(wavefront)
        currentHeight += WAVEFRONT_SPACING_WIDTH

    # Draw circles centred on the slits
    for slitCentre_u in [
        0.5 - distanceFromCentreToSlit,
        0.5 + distanceFromCentreToSlit,
    ]:
        slitCentre = NormalisedPoint(slitCentre_u, SLIT_HEIGHT)
        # Convert wavefront spacing to raster
        wavefrontSpacingRaster = floor(IMG_WIDTH * WAVEFRONT_SPACING_WIDTH)
        for i in range(100):

            d.append(
                draw.ArcLine(
                    slitCentre.rasterise_width(IMG_WIDTH),
                    slitCentre.rasterise_height(IMG_HEIGHT),
                    i * wavefrontSpacingRaster,
                    0,
                    180,
                    stroke=WAVEFRONT_COLOUR,
                    stroke_width=WAVEFRONT_WIDTH,
                    fill_opacity=0,
                )
            )

    # Draw the grating
    leftGratingLeftPoint = NormalisedPoint(0, SLIT_HEIGHT)
    leftGratingRightPoint = NormalisedPoint(
        0.5 - distanceFromCentreToSlit - WAVEFRONT_SPACING_WIDTH/2,
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
        0.5 - distanceFromCentreToSlit + WAVEFRONT_SPACING_WIDTH/2, SLIT_HEIGHT
    )
    centreGratingRightPoint = NormalisedPoint(
        0.5 + distanceFromCentreToSlit - WAVEFRONT_SPACING_WIDTH/2, SLIT_HEIGHT
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
        0.5 + distanceFromCentreToSlit + WAVEFRONT_SPACING_WIDTH/2, SLIT_HEIGHT
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

    d.save_png("double-slit.png")
    d.save_svg("double-slit.svg")
