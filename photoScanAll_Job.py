#-------------------------------------------------------------------------------
# Name:        Agisoft autonomus process 1.2 version
# Purpose:      Make all process from Workflow menu to only one process
#
# Author:      Miguel Blanco
#
# Created:     29/10/2015
# Copyright:   MiguelBlanco
# Licence:     
#-------------------------------------------------------------------------------

import os
import PhotoScan
from PySide import QtGui, QtCore
from datetime import datetime

startTime = datetime.now()
print ("Start script at....")
print (startTime)


global doc
doc = PhotoScan.app.document


#prompting for path to photos
path_photos = PhotoScan.app.getExistingDirectory("http://www.gisdron.com         --      Specify input photo folder:")
path_export = PhotoScan.app.getExistingDirectory("http://www.gisdron.com         --      Specify EXPORT folder:")

# Processing parameters

# 1- Aling photos
accuracy = PhotoScan.Accuracy.HighAccuracy  #align photos accuracy
preselection = PhotoScan.Preselection.GenericPreselection  # Pair preselection
keypoints = 40000 # align photos key point limit
tiepoints = 10000 # align photos tie point limit

#  2- Built dense cloud
quality = PhotoScan.Quality.HighQuality # build dense cloud quality  HighQuality,   MediumQuality
filtering = PhotoScan.FilterMode.AggressiveFiltering #depth filtering

# 3- Built Mesh
surface = PhotoScan.SurfaceType.HeightField # build mesh surface type  (HeightField,  Arbitrary)
source = PhotoScan.PointsSource.DensePoints # build mesh source
face_num = PhotoScan.FaceCount.MediumFaceCount # build mesh polygon count,  MediumFaceCount,  HighFaceCount
interpolation = PhotoScan.Interpolation.EnabledInterpolation # build mesh interpolation

# 4- Built Texture
mapping = PhotoScan.MappingMode.GenericMapping # build texture mapping
blending = PhotoScan.BlendingMode.MosaicBlending # blending mode
atlas_size = 4096  # 8192
color_corr = False


print("Script started")

# Creating new chunk
doc.addChunk()
chunk = doc.chunks[-1]
chunk.label = "New Chunk by Avyon.com"

#loading images
image_list = os.listdir(path_photos)
photo_list = list()
for photo in image_list:
	if ("jpg" or "jpeg" or "JPG" or "JPEG") in photo.lower():
		photo_list.append(path_photos + "\\" + photo)
chunk.addPhotos(photo_list)

# Process 1.  Align photos
chunk.matchPhotos(accuracy = accuracy, preselection = preselection, filter_mask = False, keypoint_limit = keypoints, tiepoint_limit = tiepoints)
chunk.alignCameras()

#  Process 2.  Optimize alignment
#chunk.optimizeCameras()
print ("optimise cameras initialisation...")
chunk.optimizeCameras(fit_f=True, fit_cxcy=True, fit_aspect=True, fit_skew=True, fit_k1k2k3=True,
fit_p1p2=True, fit_k4=False)
print ("optimise cameras finish...")
print ("--------------------------")
print ("Building dense cloud")


#building dense cloud
PhotoScan.app.gpu_mask = 1  #GPU devices binary mask
PhotoScan.app.cpu_cores_inactive = 2  #CPU cores inactive
chunk.buildDenseCloud(quality = quality, filter = filtering)

#building mesh
chunk.buildModel(surface = surface, source = source, interpolation = interpolation, face_count = face_num)

#build texture
chunk.buildUV(mapping = mapping, count = 1)
chunk.buildTexture(blending = blending , color_correction = color_corr, size = atlas_size)

PhotoScan.app.update()

#export


# Export DEM
# chunk.exportDem(path, format=Ã¢â‚¬â„¢tifÃ¢â‚¬â„¢[, projection ][, region ][, dx ][, dy ][, blockw ][, blockh ], nodata=-32767, crop_borders=True, write_kml=False, write_world=False)
chunk.exportDem(path_export + "\\DEM.tif", format="tif")  #   [, projection ][, region ][, dx ][, dy ][, blockw ][, blockh ], nodata=-
#   Continuation de parametres a voir  =   32767, crop_borders=True, write_kml=False, write_world=False)

#  Export OrthoPhoto
chunk.exportOrthophoto(path_export + "\\Ortho.tif")  #  , blending=MosaicBlending, color_correction=False) # [, projection
#   Continuation de parametres a voir  =  ][, region ][, dx ][, dy ][, blockw ][, blockh ], write_kml=False, write_world=False)

#  Export Reppport
chunk.exportReport(path_export + "\\report.pdf")


doc.save(path_export + "\\Photoscan.psz")

print ("Script finished at....  ")
print (datetime.now() - startTime)

print("Script finished")


#  PhotoScan.app.addMenuItem("Custom menu/Process 1", main)
