# Translate between different coordinate/labelling systems

# Code ordering - IMAGE_PLOT, e.g. 55_24
# Where images start numbering at 0

import math


def image_plot_to_intermediate(image, plot):

    rowpos = 60 * int(math.floor((29 - plot) / 5))
    rowadj = (29 - plot) % 5

    colpos = 360 * int(math.floor((image - 1) / 12))
    coladj = 5 * ((image - 1) % 12)

    return rowpos + rowadj + colpos + coladj


def test_image_plot_to_intermediate():

    assert image_plot_to_intermediate(1, 29) == 0
    assert image_plot_to_intermediate(1, 25) == 4
    assert image_plot_to_intermediate(2, 29) == 5
    assert image_plot_to_intermediate(12, 25) == 59
    # assert image_plot_to_intermediate(13, 29) == 60

    assert image_plot_to_intermediate(1, 24) == 60
    assert image_plot_to_intermediate(1, 19) == 120
    assert image_plot_to_intermediate(1, 1) == 303

    assert image_plot_to_intermediate(2, 24) == 65
    assert image_plot_to_intermediate(12, 0) == 359

    assert image_plot_to_intermediate(13, 29) == 360
    assert image_plot_to_intermediate(13, 24) == 420

# def code_label_to_field_label(code_label):

#     pass


def image_plot_to_rack_plot(n_image, n_plot):

    intermediate = image_plot_to_intermediate(n_image, n_plot)

    print(intermediate)

    plot = 1 + intermediate % 20
    rack = 1 + int(math.floor(intermediate / 20))

    return rack, plot


def test_image_plot_to_rack_plot():

    assert image_plot_to_rack_plot(1, 1) == (16, 4)  # C0370
    assert image_plot_to_rack_plot(1, 29) == (1, 1)
    assert image_plot_to_rack_plot(2, 29) == (1, 6)


# def test_code_label_to_field_label():

#     n_image = 55
#     n_plot = 24

#     code_label = "{}_{}".format(n_image, n_plot)

#     field_ordering = code_label_to_field_label(code_label)

#     assert field_ordering == "C1979"
#     assert field_identifier = "C1979"

#     8, 6, "C0339"


# def test_code_label_to_rack_plot():

#     n_image = 55
#     n_plot = 24

#     code_label = "{}_{}".format(n_image, n_plot)

#     rack, plot = code_label_to_rack_plot(code_label)


