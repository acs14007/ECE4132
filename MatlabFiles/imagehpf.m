function [hpf] = imagehpf(im, Clambda)
% IMAGEHPF High pass filter
%
%   Returns map of high pass filter. Operates on color matricies
%   individually. Executes basic histogram equalization on the output.
%   Converts output to uint8
%
%   :im         : input image
%   :Clambda    : lambda function to assing cutoff
%
%   :hpf        : high pass filtered output
%

%2D Fast Fourier Transform
[xdim, ydim, channels] = size(im);
imw = fft2(double(im));
%Shift zero-frequency to center of spectrum
imwshift=fftshift(imw);
%Gaussian Filter Response
%Cutoff Freq
if nargin == 1
    C=2*log(xdim*ydim);
elseif nargin == 2
    C = Clambda(xdim*ydim);
end
%2-D grid coordinates based on coordinates in vectors H and Y
[X,Y]=meshgrid(0:ydim-1, 0:xdim-1);

Cx = floor(ydim/2); % note the coordinate switch for nonsquare images
Cy = floor(xdim/2);
LowPassFilter=exp(-((X-Cx).^2+(Y-Cy).^2)./(2*C).^2);

%High pass Filter Definition
HighPassFilter=1-LowPassFilter; %HighPass Filter = 1-LowPassFilter
hpf = zeros(xdim, ydim, channels, 'uint8');
for ch = 1:channels
    ywshift=imwshift(:,:,ch).*HighPassFilter;
    yw=ifftshift(ywshift);
    ych = abs(ifft2(yw));
    % Basic histogram equaliziation on the filter output 
    minsub = 0;
    if min(min(ych)) > 1
        minsub = min(min(ych));
    end
    ych = (ych - minsub).*(255/(max(max(ych)) - minsub));
    hpf(:,:,ch) = uint8(ych);
end
end