"""This python script is used to generate a list of detecotr boxes with 
   a box number, a theta angle, a list of detector IDs and a phi angle.

   The box number is arbitary, while the detector ID corresponds to the
   real detector ID. Theta is the angle made to the incoming beam and
   phi is the angle in the x-z plane.
   
   Further details at: https://github.com/mantidproject/documents/blob/master/Project-Management/ILL/Instrument_Definitions/IN6/IN6_Geometry.md
"""
from __future__ import print_function

lamp_theta_angle_list = [10.33, 11.11, 11.89, 12.67, 13.73, 14.51, 15.29, 16.07, 17.13, 17.13, 17.13, 17.91, 17.91, 17.91, 18.69, 18.69, 18.69, 19.47, 20.53, 20.53, 20.53, 21.31, 21.31, 21.31, 22.09, 22.09, 22.09, 22.87, 23.93, 23.93, 23.93, 24.71, 24.71, 24.71, 25.49, 25.49, 25.49, 26.27, 27.33, 27.33, 27.33, 28.11, 28.11, 28.11, 28.89, 28.89, 28.89, 29.67, 30.73, 30.73, 30.73, 31.51, 31.51, 31.51, 32.29, 32.29, 32.29, 33.07, 34.13, 34.13, 34.13, 34.91, 34.91, 34.91, 35.69, 35.69, 35.69, 36.47, 37.53, 37.53, 37.53, 38.31, 38.31, 38.31, 39.09, 39.09, 39.09, 39.87, 40.93, 40.93, 40.93, 41.71, 41.71, 41.71, 42.49, 42.49, 42.49, 43.27, 44.33, 44.33, 44.33, 45.11, 45.11, 45.11, 45.89, 45.89, 45.89, 46.67, 46.67, 46.67, 47.73, 47.73, 47.73, 48.51, 48.51, 48.51, 49.29, 49.29, 49.29, 50.07, 50.07, 50.07, 51.13, 51.13, 51.13, 51.91, 51.91, 51.91, 52.69, 52.69, 52.69, 53.47, 53.47, 53.47, 54.53, 54.53, 54.53, 55.31, 55.31, 55.31, 56.09, 56.09, 56.09, 56.87, 56.87, 56.87, 57.93, 57.93, 57.93, 58.71, 58.71, 58.71, 59.49, 59.49, 59.49, 60.27, 60.27, 60.27, 61.33, 61.33, 61.33, 62.11, 62.11, 62.11, 62.89, 62.89, 62.89, 63.67, 63.67, 63.67, 64.73, 64.73, 64.73, 65.51, 65.51, 65.51, 66.29, 66.29, 66.29, 67.07, 67.07, 67.07, 68.13, 68.13, 68.13, 68.91, 68.91, 68.91, 69.69, 69.69, 69.69, 70.47, 70.47, 70.47, 71.53, 71.53, 71.53, 72.31, 72.31, 72.31, 73.09, 73.09, 73.09, 73.87, 73.87, 73.87, 74.93, 74.93, 74.93, 75.71, 75.71, 75.71, 76.49, 76.49, 76.49, 77.27, 77.27, 77.27, 78.33, 78.33, 78.33, 79.11, 79.11, 79.11, 79.89, 79.89, 79.89, 80.67, 80.67, 80.67, 81.73, 81.73, 81.73, 82.51, 82.51, 82.51, 83.29, 83.29, 83.29, 84.07, 84.07, 84.07, 85.13, 85.13, 85.13, 85.91, 85.91, 85.91, 86.69, 86.69, 86.69, 87.47, 87.47, 87.47, 88.53, 88.53, 88.53, 89.31, 89.31, 89.31, 90.09, 90.09, 90.09, 90.87, 90.87, 90.87, 91.93, 91.93, 91.93, 92.71, 92.71, 92.71, 93.49, 93.49, 93.49, 94.27, 94.27, 94.27, 95.33, 95.33, 95.33, 96.11, 96.11, 96.11, 96.89, 96.89, 96.89, 97.67, 97.67, 97.67, 98.73, 98.73, 98.73, 99.51, 99.51, 99.51, 100.29, 100.29, 100.29, 101.07, 101.07, 101.07, 102.93, 102.93, 102.93, 103.71, 103.71, 103.71, 104.49, 104.49, 104.49, 105.57, 105.57, 105.57, 106.35, 106.35, 106.35, 107.13, 107.13, 107.13, 108.21, 108.21, 108.21, 108.99, 108.99, 108.99, 109.77, 109.77, 109.77, 110.85, 110.85, 110.85, 111.63, 111.63, 111.63, 112.41, 112.41, 112.41, 113.49, 113.49, 113.49, 114.27, 114.27, 114.27, 115.05, 115.05, 115.05]

fixed_theta_angle_list = [10.33, 11.11, 11.89, 12.67, 13.73, 14.51, 15.29, 16.07, 17.13, 17.13, 17.13, 17.91, 17.91, 17.91, 18.69, 18.69, 18.69, 19.47, 20.53, 20.53, 20.53, 21.31, 21.31, 21.31, 22.09, 22.09, 22.09, 22.87, 23.93, 23.93, 23.93, 24.71, 24.71, 24.71, 25.49, 25.49, 25.49, 26.27, 27.33, 27.33, 27.33, 28.11, 28.11, 28.11, 28.89, 28.89, 28.89, 29.67, 30.73, 30.73, 30.73, 31.51, 31.51, 31.51, 32.29, 32.29, 32.29, 33.07, 34.13, 34.13, 34.13, 34.91, 34.91, 34.91, 35.69, 35.69, 35.69, 36.47, 37.53, 37.53, 37.53, 38.31, 38.31, 38.31, 39.09, 39.09, 39.09, 39.87, 40.93, 40.93, 40.93, 41.71, 41.71, 41.71, 42.49, 42.49, 42.49, 43.27, 44.33, 44.33, 44.33, 45.11, 45.11, 45.11, 45.89, 45.89, 45.89, 46.67, 46.67, 46.67, 47.73, 47.73, 47.73, 48.51, 48.51, 48.51, 49.29, 49.29, 49.29, 50.07, 50.07, 50.07, 51.13, 51.13, 51.13, 51.91, 51.91, 51.91, 52.69, 52.69, 52.69, 53.47, 53.47, 53.47, 54.53, 54.53, 54.53, 55.31, 55.31, 55.31, 56.09, 56.09, 56.09, 56.87, 56.87, 56.87, 57.93, 57.93, 57.93, 58.71, 58.71, 58.71, 59.49, 59.49, 59.49, 60.27, 60.27, 60.27, 61.33, 61.33, 61.33, 62.11, 62.11, 62.11, 62.89, 62.89, 62.89, 63.67, 63.67, 63.67, 64.73, 64.73, 64.73, 65.51, 65.51, 65.51, 66.29, 66.29, 66.29, 67.07, 67.07, 67.07, 68.13, 68.13, 68.13, 68.91, 68.91, 68.91, 69.69, 69.69, 69.69, 70.47, 70.47, 70.47, 71.53, 71.53, 71.53, 72.31, 72.31, 72.31, 73.09, 73.09, 73.09, 73.87, 73.87, 73.87, 74.93, 74.93, 74.93, 75.71, 75.71, 75.71, 76.49, 76.49, 76.49, 77.27, 77.27, 77.27, 78.33, 78.33, 78.33, 79.11, 79.11, 79.11, 79.89, 79.89, 79.89, 80.67, 80.67, 80.67, 81.73, 81.73, 81.73, 82.51, 82.51, 82.51, 83.29, 83.29, 83.29, 84.07, 84.07, 84.07, 85.13, 85.13, 85.13, 85.91, 85.91, 85.91, 86.69, 86.69, 86.69, 87.47, 87.47, 87.47, 88.53, 88.53, 88.53, 89.31, 89.31, 89.31, 90.09, 90.09, 90.09, 90.87, 90.87, 90.87, 91.93, 91.93, 91.93, 92.71, 92.71, 92.71, 93.49, 93.49, 93.49, 94.27, 94.27, 94.27, 95.33, 95.33, 95.33, 96.11, 96.11, 96.11, 96.89, 96.89, 96.89, 97.67, 97.67, 97.67, 98.73, 98.73, 98.73, 99.51, 99.51, 99.51, 100.29, 100.29, 100.29, 101.07, 101.07, 101.07, 102.15, 102.15, 102.15, 102.93, 102.93, 102.93, 103.71, 103.71, 103.71, 104.79, 104.79, 104.79, 105.57, 105.57, 105.57, 106.35, 106.35, 106.35, 107.43, 107.43, 107.43, 108.21, 108.21, 108.21, 108.99, 108.99, 108.99, 110.07, 110.07, 110.07, 110.85, 110.85, 110.85, 111.63, 111.63, 111.63, 112.71, 112.71, 112.71, 113.49, 113.49, 113.49, 114.27, 114.27, 114.27]

# phi angles for lower, middle and upper detectors
lower_angle = -11.5
middle_angle = 0
upper_angle = 11.5

def write_line(box, angle, detector_ids, height_angle):
    f.write(str(box) + '\t\t' + str(angle) + '\t' + str(detector_ids).replace(' ', '').replace('[', '').replace(']', ' ').ljust(16) + '\t' + str(height_angle) + '\n')


def find_average_angle_for_box_and_slice(detectors, number_of_detectors_middle, number_of_detectors_upper_lower):
    """ Finds the centre theta angle for the detector boxes. Then removes
        these detectors from the list.
    """
    
    angles_for_middle_box = detectors[0:number_of_detectors_middle]
    middle_box_angle = sum(angles_for_middle_box)/len(angles_for_middle_box)
    
    angles_for_upper_lower_box = detectors[0:number_of_detectors_upper_lower]
    if len(angles_for_upper_lower_box) > 0:
        upper_lower_box_angle = sum(angles_for_upper_lower_box)/len(angles_for_upper_lower_box)
    else:
        upper_lower_box_angle = 0
    
    detectors = detectors[max(number_of_detectors_middle, number_of_detectors_upper_lower):]
    return middle_box_angle, upper_lower_box_angle, detectors
    

if __name__ == '__main__':
    output_filename = 'in6_detector_box_list.txt'
        
    # Sort detector list
    detectors = fixed_theta_angle_list
    #detectors = lamp_theta_angle_list
    detectors = list(set(detectors))
    detectors = sorted(detectors, key=float)

    box = 1 # box number start
    number_of_boxs = 32
    d_id = 4 # detector id start, others are monitors

    f = open(output_filename, 'w')
    f.write('Box # \tTheta \tDetector ID \t\tPhi \n')

    for i in range(number_of_boxs):
        """There are 4 different regimes for the theta angle, 
            corresponding to how many detectors are in each box, and
            if they exist for upper, lower and/or middle boxes.
        """

        angle = detectors[0]

        if angle < 17:
            # Middle
            number_of_detectors_middle = 4
            number_of_detectors_upper_lower = 0
            middle_box_angle, upper_lower_box_angle, detectors = find_average_angle_for_box_and_slice(detectors, number_of_detectors_middle, number_of_detectors_upper_lower)
            write_line(box, middle_box_angle, [d_id, d_id + 1, d_id + 2, d_id + 3], middle_angle)
            box += 1
            d_id += 4
        elif 17 < angle < 44:
            number_of_detectors_middle = 4
            number_of_detectors_upper_lower = 3
            middle_box_angle, upper_lower_box_angle, detectors = find_average_angle_for_box_and_slice(detectors, number_of_detectors_middle, number_of_detectors_upper_lower)

            # Upper
            write_line(box, upper_lower_box_angle, [d_id, d_id + 3, d_id + 6], upper_angle)
            box += 1
            d_id += 1
            # Middle
            write_line(box, middle_box_angle, [d_id, d_id + 3, d_id + 6, d_id + 8], middle_angle)
            box += 1
            d_id += 1
            # Lower
            write_line(box, upper_lower_box_angle, [d_id, d_id + 3, d_id + 6], lower_angle)
            box += 1
            d_id += 1
            
            d_id += 7
        elif 44 < angle < 102: # 4 upper/lower/middle
            number_of_detectors_middle = 4
            number_of_detectors_upper_lower = 4
            middle_box_angle, upper_lower_box_angle, detectors = find_average_angle_for_box_and_slice(detectors, number_of_detectors_middle, number_of_detectors_upper_lower)

            # Upper
            write_line(box, upper_lower_box_angle, [d_id, d_id + 3, d_id + 6, d_id + 9], upper_angle)
            box += 1
            d_id += 1
            # Middle
            write_line(box, middle_box_angle, [d_id, d_id + 3, d_id + 6, d_id + 9], middle_angle)
            box += 1
            d_id += 1
            # Lower
            write_line(box, upper_lower_box_angle, [d_id, d_id + 3, d_id + 6, d_id + 9], lower_angle)
            box += 1
            d_id += 1
            
            d_id += 9
        elif angle > 102: # 3 upper/lower/middle
            number_of_detectors_middle = 3
            number_of_detectors_upper_lower = 3
            middle_box_angle, upper_lower_box_angle, detectors = find_average_angle_for_box_and_slice(detectors, number_of_detectors_middle, number_of_detectors_upper_lower)

            # Upper
            write_line(box, upper_lower_box_angle, [d_id, d_id + 3, d_id + 6], upper_angle)
            box += 1
            d_id += 1
            # Middle
            write_line(box, middle_box_angle, [d_id, d_id + 3, d_id + 6], middle_angle)
            box += 1
            d_id += 1
            # Lower
            write_line(box, upper_lower_box_angle, [d_id, d_id + 3, d_id + 6], lower_angle)
            box += 1
            d_id += 1
            
            d_id += 6
            
    print("Detector list written to:", output_filename)



