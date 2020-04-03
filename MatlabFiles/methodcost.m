function [] = methodcost(im1, im2, uVector, v, windowSize)
%METHODCOST Plots comparison of cost function methods
%
%   Returns cost function results along specified path
%   uVector three element vector:
%   [lowersearchbound targetpoint uppersearchbound]
%   v- the x axis (vertical) search line position
%   windowSize - odd-numbered length of square window size
%   
[xdim, ydim, ~] = size(im1);
if (v > (xdim - windowSize))
    disp("v dimension exceeds image size")
end
maxDisparity = 2^10;
upoint = uVector(2);
[a, b] = centerdim([upoint v], windowSize);
testSample = im1(a, b);
searchMin = max([(1 + windowSize) (upoint - maxDisparity) uVector(1)]);
searchMax = min([(ydim - windowSize - 1) (upoint  + maxDisparity) uVector(3)]);
Jcorr = zeros(1, uVector(3) - uVector(1)); Jssd = Jcorr; Jsad = Jcorr;
ffcor = Jcorr; fftest = conj(fft2(testSample - mean(testSample, 'all')));
for ud = searchMin:searchMax
    [s, t] = centerdim([ud v], windowSize);
    otherSample = im2(s, t);
    Jcorr(ud - searchMin + 1) = corr2(testSample, otherSample);
    Jssd(ud - searchMin + 1) = sum((testSample - otherSample).^2, 'all');
    Jsad(ud - searchMin + 1) = sum(abs(testSample - otherSample), 'all');
    ffcor(ud - searchMin + 1) = sum(abs(fft2(otherSample - mean(otherSample, 'all')).*fftest), 'all');
end
Jssd = Jssd/max(Jssd);
Jsad = Jsad/max(Jsad);
xaxis = uVector(1):uVector(3);
figure
hold on
plot(xaxis, Jcorr)
plot(xaxis, Jssd)
plot(xaxis, Jsad)
ffcor = ffcor/max(ffcor);
plot(xaxis, ffcor)
xlim([uVector(1) uVector(3)])
grid on
legend("Mean-Normalized Correlation", "Sum of Squared Differences", "L1-Norm", 'fft multiply')
title("Comparing cost methods relative to point (x,y): " + string(v) + ", " + string(uVector(2)))
figure
subplot(2,1,1)
imshow(im1)
hold on
plot(uVector(2), v, 'r+', 'MarkerSize', 10)
subplot(2,1, 2)
imshow(im2)
hold on
searchline = uVector(1):uVector(3);
plot(searchline, v*(searchline./searchline), 'y', 'MarkerSize', 10)
end
