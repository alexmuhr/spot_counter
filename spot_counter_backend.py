import cv2
from skimage.io import imread as skimread
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

def spot_scan(file):
    try:
        img_dir = os.path.dirname(file) # Determine directory of image file. Use to save outputs later.

        ##### LOAD IMAGE FILE AND CROP A D45 mm AREA FROM CENTER #####

        img = skimread(file) # Read image file

        # Determine image size for centered crop
        height = img.shape[0]
        width = img.shape[1]
        center_y = int(height/2)
        center_x = int(width/2)
        img_center = (center_x, center_y)
        mask_radius = 4252

        # Create D45mm circular mask at center of image
        mask = np.zeros((height,width), np.uint8)
        cv2.circle(mask, img_center, mask_radius, (255, 255, 255), -1)
        masked_img = cv2.bitwise_and(img, img, mask=mask)

        # Threshold and find contours
        thresh_mask = cv2.threshold(mask, 1, 255, cv2.THRESH_BINARY)[1]
        mask_contours = cv2.findContours(thresh_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        x,y,w,h = cv2.boundingRect(mask_contours[0])

        # Crop masked data
        crop_img = masked_img[y:y+h,x:x+w]

        #convert black edge pixels to white so that edge does not get captured by threshold
        crop_img[np.where(crop_img==[0])] = 255

        ##### APPLY THRESHOLDING TO IMAGE THEN FIND AND RECORD MICROFEATURES #####

        # Apply thresholding to the cropped image
        thresh_img = cv2.threshold(crop_img, 145, 255, cv2.THRESH_BINARY_INV)[1]

        # Create contours
        (_,cnts,_) = cv2.findContours(thresh_img.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        cnt_data = {"Area":[], "Location":[]} # Initialize contour data

        #determine if contour area is large enough to be interesting
        for contour in cnts:
            area = cv2.contourArea(contour)*0.000028
            (x, y), radius = cv2.minEnclosingCircle(contour)
            center = (int(x), int(y))
            radius = int(radius)
            cnt_data["Area"].append(area)
            cnt_data["Location"].append(center)
            if area < 0.002:
                continue
            else:
                # If mf large enough draw a circle around the contour
                cv2.circle(crop_img, center, radius, (0, 0, 255), 10)

        # Create dataframe from cnt_data
        cnt_data = pd.DataFrame(cnt_data)

        # Resize and save image with circled microfeatures
        out_img_file = img_dir + "/highlighted_spots.jpg" # Concatenate directory/filename for output image
        resize_img = cv2.resize(crop_img, (800, 800))
        cv2.imwrite(out_img_file, resize_img)
        #cv2.imshow("original", resize_img)
        #cv2.waitKey(0)

        ##### CREATE A HISTOGRAM OF MICROFEATURE SIZE #####

        # create microfeature histogram
        bins = [0.002, 0.0025, 0.003, 0.004, 0.006, 0.008, 0.012, 0.018, 0.025, 0.050, 0.1, 10]
        bars = [0.0025, 0.003, 0.004, 0.006, 0.008, 0.012, 0.018, 0.025, 0.050, 0.1, 'More']
        # Use hist method to sort data into bins
        n, bins, patches = plt.hist(x=list(cnt_data["Area"]), bins=bins, color='#0504aa', alpha=0.7, rwidth=0.85)
        bar_height = n.tolist() # Convert array of bin counts to list
        y_pos = np.arange(len(bars)) # y_pos determines # of bars
        plt.bar(y_pos, bar_height, align='center', alpha=0.5)
        plt.xticks(y_pos, bars, rotation = 30)
        plt.ylabel('Count')
        plt.xlabel('Microfeature Size ($mm^2$)')
        plt.title('Microfeature Distribution')
        maxmf = max(list(cnt_data['Area'])) # Determine size of largest MF
        text_y = max(bar_height) / 2 # Variable to place text at mid height of chart
        plt.text(7, text_y , 'largest feature\n%s mm2' % str(round(maxmf,4)))
        out_plt_file = img_dir + "/histogram.jpg"
        plt.savefig(out_plt_file)
        #plt.show()

        ##### CREATE A SUMMARY REPORT IN EXCEL #####

        # Create summary statistics
        nsmall = bar_height[0] + bar_height[1] + bar_height[2] + bar_height[3] + bar_height[4] # 0.002 to 0.008
        nmed = bar_height[5] + bar_height[6] # 0.008 to 0.018
        nlarge = bar_height[7] + bar_height[8] + bar_height[9] + bar_height[10] # 0.018 to 10
        mf_coverage = sum(cnt_data["Area"].values)/(1590)*100
        # Determine pass or fail
        if nsmall < 380:
            tsmall = "pass"
        else:
            tsmall = "fail"
        if nmed < 250:
            tmed = "pass"
        else:
            tmed = "fail"
        if nlarge < 160:
            tlarge = "pass"
        else:
            tlarge = "fail"
        if maxmf < 0.1:
            tmax = "pass"
        else:
            tmax = "fail"
        # Set indexes and columns
        index = ["Count 0.002 - 0.008 mm2", "Count 0.008 - 0.018 mm2", "Count 0.018 - 0.1 mm2", "Largest Spot", "Spot Coverage %"]
        summary = {"Key Data":[nsmall, nmed, nlarge, round(maxmf,4), round(mf_coverage,4)], "Pass / Fail":[tsmall, tmed, tlarge, tmax, ""]}
        summary = pd.DataFrame(data = summary, index = index)
        # Send summary dataframe to excel then add a tab for cnt_data
        out_xls_file = img_dir + "/spot_data.xlsx"
        writer = pd.ExcelWriter(out_xls_file, engine = 'openpyxl')
        summary.to_excel(writer, sheet_name = "Summary")
        cnt_data.to_excel(writer, sheet_name = "Spot Data")
        writer.save()
        writer.close()
        return 0, summary
    except Exception as e:
        return 1, ("scan error\n" + str(e))
