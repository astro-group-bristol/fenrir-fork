import numpy as np
import numpy.ma as mask
import matplotlib.pyplot as pl
import matplotlib
import csv
import sys

def rIsco(a):
	z1 = 1 + (((1-(a*a))**(1./3.))*(((1+a)**(1./3.))+((1-a)**(1./3.))))
	z2 = ((3*(a*a))+(z1*z1))**0.5
	rOut = 3+z2-(((3-z1)*(3+z1+(2.*z2)))**0.5)
	return rOut

def grSigma(r,a,theta):
	return (r**2.) + ((a*np.cos(theta))**2.)

def grDelta(r,a):
	return (r**2.) - (2.*r) + (a**2.)

def aFunct(r,a,theta):
	aFunctOut = (((r*r)+(a*a))**2.)-(a*a)*grDelta(r,a)*(np.sin(theta)**2.)
	return aFunctOut
"""
def grArea(r,theta,dr,a,dtheta):
	rTerm = (grSigma(r,a,theta)/grDelta(r,a)) + (grSigma(r,a,theta)*((dtheta/dr)**2.))
	phiTerm = (r**2.) + (a**2.) + (2.*r*((a*np.sin(theta))**2.)/grSigma(r,a,theta))
	areaOut = (2.*np.pi)*np.sqrt(rTerm*phiTerm)*dr
	return areaOut
"""
def grArea(r,theta,dr,a,dtheta):
	rTerm = np.sqrt((grSigma(r,a,theta)/grDelta(r,a)) + (grSigma(r,a,theta)*((dtheta/dr)**2.)*(np.sin(theta)**2.)))
	phiTerm = np.sqrt((aFunct(r,a,theta)/grSigma(r,a,theta)))#*(np.sin(theta)**2.))
	areaOut = (2.*np.pi)*phiTerm*rTerm*dr
	return areaOut

inFile = 'test_new_v2_th4.npy'#'test_even.npy'#'./test_new_v2_4_0.npy'
outFile = 'test_new_v2_th4_hist.npy'#'test_even_hist.npy'#'./test_hist_4_0.npy'
nBins = 150
specIndex = 2.
#Unpacking data (x, y, gRatio, time, radius, theta, phi)
data = np.load(inFile)
x = data[0]
y = data[1]
gRatio = data[2]
time = data[3]
radius = data[4]
theta = data[5]
phi = data[6]
scaleHeight = data[7]
projectedRadius = data[8]
gamma = data[9]
diskHitSwitch = data[10]
print np.min(x)/np.pi
print np.max(x)/np.pi
a = 0.998
rIn = rIsco(a)
rOut = 500.
print rIsco(a)

#iRcut = np.where(np.logical_and(projectedRadius > rIn,projectedRadius < rOut, diskHitSwitch > 0.5))
iRcut = np.where(np.logical_and((np.logical_and(np.logical_and(projectedRadius[:-1] > rIn,projectedRadius[:-1] < rOut), diskHitSwitch[:-1] > 0)),(gRatio[:-1] < 100.)))

specEnergy = (gRatio)[iRcut]#[weirdCut])#[np.isfinite(gRatio[iRcut])]
specRadius = (projectedRadius)[iRcut]#[weirdCut]#[np.isfinite(gRatio[iRcut])]
specTheta = (theta)[iRcut]#[weirdCut]
specPhi = (phi)[iRcut]#[weirdCut]
specGamma = (gamma)[iRcut]#[weirdCut]
specDelta = np.pi - x[iRcut]

binLimArray = np.logspace(np.log10(rIn),np.log10(rOut),nBins,endpoint=False)
#binLimArray = np.linspace(rIn,rOut,nBins,endpoint=False)
specBin = np.zeros(nBins-1)
drArray = np.zeros(nBins-1)
dThetaArray = np.zeros(nBins-1)
numArray = np.zeros(nBins-1)
fluxArray = np.zeros(nBins-1)
dDelta = np.zeros(nBins-1)
binDelta = np.zeros(nBins-1)

l = 1
#print specHist[1]
while (l < nBins):
	rMinBin = binLimArray[l-1]
	rMaxBin = binLimArray[l]
	specBin[l-1] = (rMinBin+rMaxBin)/2.
	drArray[l-1] = rMaxBin-rMinBin
	iInBin = np.where(np.logical_and(specRadius > rMinBin, specRadius < rMaxBin))
	radInBin = specRadius[iInBin]
	#drArray[l-1] = np.max(radInBin)-np.min(radInBin)
	thetaInBin = specTheta[iInBin]
	gammaInBin = specGamma[iInBin]
	energyInBin = specEnergy[iInBin]
	deltaInBin = specDelta[iInBin]
	numArray[l-1] = len(radInBin)
	if (numArray[l-1] > 0):
		#drArray[l-1] = np.max(radInBin)-np.min(radInBin)
		dThetaArray[l-1] = np.max(thetaInBin)-np.min(thetaInBin)
		dDelta[l-1] = np.max(deltaInBin) - np.min(deltaInBin)
		binDelta[l-1] = np.mean(deltaInBin)
		grAreaInBin = grArea(radInBin,thetaInBin,drArray[l-1],a,dThetaArray[l-1])
		fluxInBin = (1./(gammaInBin*grAreaInBin))*np.sin(deltaInBin)*(energyInBin**(specIndex))#*np.sin(deltaInBin)
		fluxArray[l-1] = np.sum(fluxInBin)*drArray[l-1]
	else:
		fluxInBin = 0.
		fluxArray[l-1] = 0.
	l+=1


#pl.figure(figsize=(10.,10.))
pl.plot(specBin,fluxArray/np.sum(fluxArray), color = 'k')#, marker = 'o')
#pl.plot(specRadius,specArea)
#pl.plot(specRadius,2.*np.pi*specRadius*dRray[iRcut])
pl.axvline(rIn, color = 'g')
#pl.xlabel('r')
#pl.ylabel('F')
pl.yscale('log')
pl.xscale('log')
pl.xlim([1.,500.])
#pl.ylim([10.**-4.,10**-1.])
pl.show()
#outArray = np.array([[specBin,fluxArray,numArray],binLimArray])
#np.save(outFile, outArray)
#pl.savefig('./test.png')
