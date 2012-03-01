#!/usr/bin/env python
"""
reconsistutes shredded images.
author: Leah Xue
"""
import sys
import Image
import collections
import itertools
import operator

def chop(image):
    slices = []
    pixel_array = image.load()
    width, height = image.size
    for slice in xrange(0,width,32):
        print "slice: %d" % slice
        slice_stor = collections.defaultdict(dict)
        slice_stor = []
        for i in xrange(slice, slice+32):
            column = []
            for j in xrange(height):
                column.append(pixel_array[i,j])
            slice_stor.append(column)
        slices.append(slice_stor)
    return slices

def measure(slice_a, slice_b):
    """
    calculate euclidean distance between slice_a's right edge and slice_b's left edge
    """
    dist = 0
    for p_a, p_b in zip(slice_a[-1], slice_b[0]):
        # for each pixel, calculate euclidean distance between rgba values
        for i,j in zip(p_a, p_b):
            dist += (i-j)**2
    # sqrt whatever
    return dist

def noisy_order(dist_m, slices):
    address_table = {}
    for i in xrange(len(slices)):
        min_right, min_dist = min(dist_m[i].items(), key=operator.itemgetter(1))
        address_table[i] = min_right, min_dist

    invert_addressing = {}
    for i,j in address_table.iteritems():
        item, dist = j
        invert_addressing[item] = i

    # debugging
    # print address_table
    # print invert_addressing
    # this is a sketchy assumption -- and will break in many cases -- I assume that the leftmost strip is the one which no other strip claims to be right of.
    # break ties arbitrarily
    not_minimal_set = set(range(len(slices))) - set(invert_addressing.keys())
    leftmost = not_minimal_set.pop()
    output_order = [leftmost]
    cur, _ = address_table[leftmost]
    while cur not in output_order:
        output_order.append(cur)
        cur, _ = address_table[cur]
    return output_order

def cook(new_slice_order, image, size, shred_width=32):
    fixed = Image.new('RGBA', size)
    w, h = size
    for i, slice in enumerate(new_slice_order):
        x0, y0 = slice * shred_width, 0
        x1, y1 = slice * shred_width + shred_width, h 
        region = image.crop((x0,y0,x1,y1))
        fixed.paste(region, (shred_width * i, 0))
    return fixed

def reconstitute(image):
    slices = chop(image)
    dist_m = collections.defaultdict(dict)
    for one_slice, two_slice in itertools.permutations(slices, 2):
        i = slices.index(one_slice)
        j = slices.index(two_slice)
        dist_m[i][j] = measure(one_slice, two_slice)

    new_slice_order = noisy_order(dist_m, slices)
    print new_slice_order
    fixed_image = cook(new_slice_order, image, image.size)
    fixed_image.save("test.png")

def main():
    for infile in sys.argv[1:]:
        print "Opening %s" % infile
        image = Image.open(infile)
        reconstitute(image)

if __name__ == '__main__':
    main()

