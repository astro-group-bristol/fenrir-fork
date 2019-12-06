import numpy as np
import numpy.ma as mask
import matplotlib.pyplot as pl
import matplotlib
import csv
import sys

"""
This script will take in a series of disk images (one for each zoom level) and one emissivity profile. These are
found via the parameter indices and the paths given to the script from the command line. It outputs a lineprofile
that will act as the convolution kernel for the reflection spectrum that is generated in XSPEC with a modified version
of RELXILL.

The input layout is: 
python3 create_lineprof_lp_auto.py $spin $spinIndex $inclinationIndex $heightIndex $diskThicknessIndex $diskFilePath $lpFilePath $outDirPath

spin = black hole spin value
spinIndex = index of the current spin value
inclinationIndex = index of the current inclination value
heightIndex = index of the current LP height value
diskThicknessIndex = index of the current asymtotic disk thickness value
diskDirPath = path to directory that holds the disk images that will be used
lpDirPath = path to the directory that holds the emissivity profile file that will be used
outDirPath = path to the directory that will contain the output line profile file

It is assumed that the disk files, the emissivity file, and the output line profile file will all be of the .npy format.
"""


def writeDataToTextFile(fileName, dataToWrite, numberDataColumns=1):
	if numberDataColumns <= 0:
		raise ValueError('You must have a positive number of data columns to write')
	if type(fileName) != str:
		raise TypeError('File name must be specified with a path string')

	outputToFile = open(fileName,'w')

	if numberDataColumns == 1:
		for i in range(len(dataToWrite)):
			outputToFile.write(str(dataToWrite[i] + '\n'))
	else:
		for i in range(numberDataColumns):
			currentRow = ''
			for j in range(len(dataToWrite[0])):
				currentRow += currentRow + str(dataToWrite[i][j]) + ' '
				outputToFile.write(currentRow[:-1] + '\n')
	outputToFile.close()

def rIsco(a):
	"""Calculates the inner-most stable circular orbit (or rIsco, in gravitational
	radii Rg) for a given dimensionless spin value. |a| <= 1

	Example: rIsco(0) => 6.0 """

	if type(a) not in [int, float]:
		raise TypeError('Spin must be either a int or float type between -1 and 1, inclusive.')
	
	z1 = 1 + (((1-(a*a))**(1./3.))*(((1+a)**(1./3.))+((1-a)**(1./3.))))
	z2 = ((3*(a*a))+(z1*z1))**0.5
	
	if (a < 0) and (a >= -1):
		rIscoOut = 3+z2+(((3-z1)*(3+z1+(2.*z2)))**0.5)
	elif (a >= 0) and (a <= 1):
		rIscoOut = 3+z2-(((3-z1)*(3+z1+(2.*z2)))**0.5)
	else:
		raise ValueError('Spin value must be between -1 and 1, inclusive.')
	
	return rIscoOut

a = float(sys.argv[1])
nEnergyBins = 4096

diskDirectoryPath = sys.argv[2]
lpDirectoryPath = sys.argv[3]
outDirectoryPath = sys.argv[4]
caseNum = sys.argv[5]
diskNum = sys.argv[6]
diskFiles = [diskDirectoryPath + 'yorp7_'+caseNum+'_cat'+str(catNum)+'_'+diskNum+'.npy' for catNum in range(1,4)]
lpFile = lpDirectoryPath + 'yorp1_em_test_hist_cat'+diskNum + '_' + caseNum + '.npy'
outFile = outDirectoryPath + 'line_offhd_'+caseNum+'_'+diskNum+'.npy'
outText = outDirectoryPath + 'line_offhd_'+caseNum+'_'+diskNum+'.txt'

#Inner and outer cylindrical radii to be used for each disk image level
rInVals = [rIsco(a),10.,30.]
rOutVals = [10.,30.,100.]

#Solid angle correction factors based on size of disk images
solidAngCorrect = [(1./49.),(1./9.),1.]

#energyBins = np.linspace(0.002, 2.002, nEnergyBins+1)#10.**np.linspace(np.log10(0.00035), np.log10(2000.), nEnergyBins+1)
energyBins = 10.**np.linspace(np.log10(0.00035), np.log10(2000.), nEnergyBins+1)
deltaE = energyBins[1:]-energyBins[:-1]

#From RELXILL:
#define N_ENER_CONV  4096  // number of bins for the convolution, not that it needs to follow 2^N because of the FFT
#define EMIN_RELXILL 0.00035  // minimal energy of the convolution (in keV)
#define EMAX_RELXILL 2000.0 // minimal energy of the convolution (in keV)
midEnergy = (energyBins[1:] + energyBins[:-1])/2.

#Loading in emissivity file. Format: emmisivity array = np.array([[binLimArray[:-1],fluxArray,binDelta],a,hCorona])
lpData = np.load(lpFile)
lpRadii = lpData[0][0]
lpFlux = lpData[0][1]

#Creating array that will store line profile data (flux, where each index is an energy range)
lineProfile = np.zeros(nEnergyBins)

#Going over each disk file to calculate individual contributions to the line profile flux
for i in range(len(diskFiles)):
	diskFile = diskFiles[i]
	rIn = rInVals[i]
	rOut = rOutVals[i]
	correction = solidAngCorrect[i]

	#Unpacking data from disk transform data
	diskData = np.load(diskFile)
	x = diskData[0]
	y = diskData[1]
	gRatio = diskData[2]
	time = diskData[3]
	radius = diskData[4]
	theta = diskData[5]
	phi = diskData[6]
	scaleHeight = diskData[7]
	projectedRadius = diskData[8]

	#Creating index array for disk data within range between rIn and rOut
	iRcut = np.where(np.logical_and(projectedRadius >= rIn,projectedRadius < rOut))

	#Creating arrays with radius cut from iRcut
	specRadius = projectedRadius[iRcut]
	specEnergy = gRatio[iRcut]


	#For each photon in disk file, finding corresponding lpFlux from its cylindrical radius (specRadius) using binary search
	radIndices = np.searchsorted(lpRadii,specRadius,sorter=None)
	photonLPFlux = np.array([lpFlux[radIndices[j]] for j in len(radIndices)])
	
	#Creating line profile via histogram
	indivFlux = (specEnergy**3.)*photonLPFlux*correction
	lineProfile = lineProfile + (np.histogram(specEnergy, bins = energyBins, weights = indivFlux))[0]


lineProfile = lineProfile*deltaE
writeDataToTextFile(outFile,lineProfile)
