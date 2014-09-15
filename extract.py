from skimage import io
from skimage import color
from skimage.transform import hough_line, hough_line_peaks
from skimage.transform import PiecewiseAffineTransform, warp
from skimage.filter import threshold_otsu
from skimage.feature import corner_harris, corner_subpix, corner_peaks
import numpy as np
import matplotlib.pyplot as plt
import os
import glob

DEBUG = True
HEIGHT = 400
WIDTH = 150

def calcIntersection(x1, y1, x2, y2, x3, y3, x4, y4):
    """ Calculate the intersection points between two lines """
    px = ((x1*y2 - y1*x2)*(x3-x4) - (x1-x2)*(x3*y4 - y3*x4)) / ((x1-x2)*(y3-y4) - (y1-y2)*(x3-x4))
    py = ((x1*y2 - y1*x2)*(y3-y4) - (y1-y2)*(x3*y4 - y3*x4)) / ((x1-x2)*(y3-y4) - (y1-y2)*(x3-x4))
    
    return (px, py)

def calc_distance(p1, p2):
    """ Calculate distance between two points """
    dist = 0
    for i in xrange(len(p1)):
        dist += (p1[i] - p2[i])*(p1[i] - p2[i])
    return dist

def search_closest_points(p, points):
    """ Search for queried point p the closest point in the set of points points """ 
    min_dist = 1000000000
    cp = None
    for i in xrange(len(points)):
        dist = calc_distance(p, points[i])
        if dist < min_dist:
            min_dist = dist
            cp = points[i]
    return cp

def search_closest_line(lines, ref_line):
    """ Search closest line from a set of line (represented by two points) to a reference line
    using a simple, naive assumption of the summation of both points' distance.
    """
    closest_line = [(0,0), (0,0)]
    min_dist = 1000000000
    for line in lines:
        dist = calc_distance(line[0], ref_line[0]) + calc_distance(line[1], ref_line[1])
        if dist < min_dist:
            min_dist = dist
            closest_line = line

    return closest_line

def extract_corner_hough(patch):
    """Extract four corner points using Hough transform 

    """
    # Find the lines that makes the boundary box using Hough Transform
    h, theta, d = hough_line(patch)

    # Divide the hough space for searching the different horizontal and vertical lines
    hcroph = h[:, 0:30]

    rows, cols = patch.shape
    # Vertical lines
    VLf = []
    for _, angle, dist in zip(*hough_line_peaks(h, theta, d, min_angle=9)):
        x0 = (dist - 0 * np.sin(angle)) / np.cos(angle)
        x1 = (dist - rows * np.sin(angle)) / np.cos(angle)
        VLf += [((x0, 0), (x1, rows))]

    # Horizontal lines
    HLf = []
    for _, angle, dist in zip(*hough_line_peaks(hcroph, theta, d, min_angle=9)):
        y0 = (dist - 0 * np.cos(angle)) / np.sin(angle)
        y1 = (dist - cols * np.cos(angle)) / np.sin(angle)
        HLf += [((0, y0), (cols, y1))]

    if DEBUG:
        plt.subplot(142)
        plt.title('hough line')
        plt.imshow(patch, cmap='gray')
        for i in xrange(len(VLf)):
            plt.plot((VLf[i][0][0], VLf[i][1][0]), (VLf[i][0][1], VLf[i][1][1]), 'r-')
        for i in xrange(len(HLf)):
            plt.plot((HLf[i][0][0], HLf[i][1][0]), (HLf[i][0][1], HLf[i][1][1]), 'r-')
        plt.axis([0, cols, rows, 0])

    VL = []
    VL += [search_closest_line(VLf, [(0, 0), (0, rows)])]
    VL += [search_closest_line(VLf, [(cols, 0), (cols, rows)])]

    HL = []
    HL += [search_closest_line(HLf, [(0, 0), (cols, 0)])]
    HL += [search_closest_line(HLf, [(0, rows), (cols, rows)])]

    if len(HL) < 2 or len(VL) < 2:
        print 'No line found'
        return []
    
    points = [VL[0], VL[-1], HL[0], HL[-1]]
    # Check for error
    for i in xrange(4):
        for j in xrange(i+1, 4):
            if points[i] == points[j]:
                print 'Error Line'
                return []

    # Calculate the intersection between points using determinants
    p1 = calcIntersection(VL[0][0][0], VL[0][0][1], VL[0][1][0], VL[0][1][1], HL[0][0][0], HL[0][0][1], HL[0][1][0], HL[0][1][1])
    p2 = calcIntersection(VL[0][0][0], VL[0][0][1], VL[0][1][0], VL[0][1][1], HL[1][0][0], HL[1][0][1], HL[1][1][0], HL[1][1][1])
    p3 = calcIntersection(VL[1][0][0], VL[1][0][1], VL[1][1][0], VL[1][1][1], HL[0][0][0], HL[0][0][1], HL[0][1][0], HL[0][1][1])
    p4 = calcIntersection(VL[1][0][0], VL[1][0][1], VL[1][1][0], VL[1][1][1], HL[1][0][0], HL[1][0][1], HL[1][1][0], HL[1][1][1])

    # Find the nearest point for each corner
    dim = patch.shape
    corners = [(0,0), (0, dim[0]), (dim[1], dim[0]), (dim[1], 0)]

    points = [p1, p2, p3, p4]
    dest_points = [[] for x in range(4)]
    for i in xrange(4):
        dest_points[i] = search_closest_points(corners[i], points)
        
    epsilon = 1e-10
    for i in xrange(4):
        for j in xrange(i+1, 4):
            if calc_distance(dest_points[i], dest_points[j]) < epsilon:
                print 'Error point'
                return []

    return dest_points

def extract_corner_harris(patch):
    """Extract four corner points using harris corner detection algorithm

    """
    # Find corner with harris corner detection
    coords = corner_peaks(corner_harris(patch, k=0.1), min_distance=5)
    coords_subpix = corner_subpix(patch, coords, window_size=13)

   # plt.subplot(121)
   # plt.imshow(gcrope, interpolation='nearest', cmap=plt.cm.gray)
   # plt.plot(coords[:, 1], coords[:, 0], '.b', markersize=3)
   # plt.plot(coords_subpix[:, 1], coords_subpix[:, 0], '+r', markersize=15)
   # ax.axis((0, 350, 350, 0))
   # plt.show()

   # for i in xrange(4):
   #     plt.plot(dest_points[i][1], dest_points[i][0], '*b', markersize=10)   
    
    # Find the nearest point for each corner
    dim = patch.shape
    corners = [(0,0), (dim[0], 0), (dim[0], dim[1]), (0, dim[1])]

    dest_points = [[] for x in range(4)]
    for i in xrange(4):
        dest_points[i] = search_closest_points(corners[i], coords_subpix)
        
    # Check for error
    try:
        epsilon = 1e-10
        for i in xrange(4):
            for j in xrange(i+1, 4):
                if calc_distance(dest_points[i], dest_points[j]) < epsilon:
                    print 'Error point'
                    return []
    except TypeError:
        return []

    # Reverse y,x position to x,y
    for i in xrange(4):
        dest_points[i][1], dest_points[i][0] = dest_points[i][0], dest_points[i][1]

    return dest_points

def remove_edge(patch):
    x = (patch.shape)[1]*9/10.
    patch[:, x:] = 0

    return patch

def extract_digits(fname):
    """ Extract the sub images of digits from the scanned image

    fname is the filename of the image
    """
    c1 = io.imread(fname)

    # Calculate the region of interest
    dim = c1.shape
    y0 = 350; y1 = y0+450;
    if dim[0] < 1100:
        y0 = dim[0]*300/1700; y1 = y0 + dim[0]*400/1700
    elif dim[0] > 1700 and dim[0] < 2400:
        y0 = 350; y1 = y0+450;
    else:
        y0 = dim[0]*350/1700; y1 = y0 + dim[0]*450/1700
    x0 = dim[1]*19/24

    # Cropped and convert to grayscale
    cropped = c1[y0:y1, x0:]
    gcrop = color.rgb2gray(cropped)

    # Threshold to create binary image
    thresh = threshold_otsu(gcrop)
    gcrope = gcrop < thresh

    # Remove unwanted edge
    gcrope = remove_edge(gcrope)

    if DEBUG:
        plt.subplot(141);
        plt.title('Cropped')
        plt.imshow(gcrop, cmap='gray')

    # Extract four corner points
    dest_points = extract_corner_hough(gcrope)
    #dest_points = extract_corner_harris(gcrope)
    src_points = [(0,0), (0, HEIGHT), (WIDTH, HEIGHT), (WIDTH, 0)]
    
    if dest_points == []:
        return False

    if DEBUG:
        plt.subplot(143)
        plt.title('Thresholded & corner points')
        plt.imshow(gcrope, cmap='gray')
        for p in dest_points:
            plt.plot(p[0], p[1], 'bo', markersize=10)
    
    #Transform to rescale and reorient the image
    dst = np.array(dest_points)
    src = np.array(src_points)
    
    tform = PiecewiseAffineTransform()
    tform.estimate(src, dst)
    warped = warp(gcrope, tform, output_shape=(HEIGHT, WIDTH))

    if DEBUG:
        plt.subplot(144)
        plt.title('Warped')
        plt.imshow(warped, cmap='gray')
        plt.show()

    # Prepare the directory
    if not os.path.exists('extracted'):
        os.makedirs('extracted')
        for i in xrange(10):
            os.makedirs('extracted/'+str(i))

    # Load the annotation for each digit
    fname_txt = fname[:-3]+'txt'
    f = open(fname_txt, 'r')
    f.readline()                        # Remove the header
    lines = f.readline().split(',')
    f.close()

    width = WIDTH / 3
    # Extract each digit
    for i in xrange(4):
        if len(lines[i]) < 3:
            hundred = '0'
        else:
            hundred = lines[i][0]
        counter[int(hundred)] += 1
        io.imsave('extracted/'+hundred+'/'+str(counter[int(hundred)])+'.png', warped[i*100:i*100+100, :width])
        
    for i in xrange(4):
        if len(lines[i]) == 3:
            hundred = lines[i][1]
        elif len(lines[i]) == 2:
            hundred = lines[i][0]
        else:
            hundred = '0'
        counter[int(hundred)] += 1
        io.imsave('extracted/'+hundred+'/'+str(counter[int(hundred)])+'.png', warped[i*100:i*100+100, width:2*width])

    for i in xrange(4):
        if len(lines[i]) == 1:
            hundred = lines[i][0]
        elif len(lines[i]) == 2:
            hundred = lines[i][1]
        elif len(lines[i]) == 3:
            hundred = lines[i][2]
        else:
            hundred = '0'
        counter[int(hundred)] += 1
        io.imsave('extracted/'+hundred+'/'+str(counter[int(hundred)])+'.png', warped[i*100:i*100+100, 2*width:3*width])

    return True

counter = [0]*10
success = 0; fail = 0;

# fname = 'select/87813_2.jpg'
# extract_digits(fname)

all_pics = glob.glob('select/*.jpg')
for pic in all_pics:
    print 'Extracting', pic, '...'
    if extract_digits(pic):
        success += 1
        print 'Success!!!'
    else:
        fail += 1
        print 'Fail.. :('

print 'total success:', success
print 'total fail:', fail
print 'statistic:', counter
