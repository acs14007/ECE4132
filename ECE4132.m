%% ECE 4132
clear;clc;close all
%% Section 1. Load images
% 
% Color images are loaded and converted to grey scale. It is assumed that
% the left and right images are the same size and taken facing the same
% plane at the same horizontal level
%
% left = imread('bb021_R_0.png');
% right = imread('bb021_R_1.png');
left = imread('test9P1.jpg');
right = imread('test9P2.jpg');
leftg = imresize(rgb2gray(left), (1/2));
rightg = imresize(rgb2gray(right), (1/2));
[xdim, ydim, ~] = size(leftg);
% %%%% Verify epipolar geometry of the images %%%%
%
% Large images will demand excessive RAM, downsize prior to execution
epipolarity(leftg, rightg)
% %%%%
%% Section 2. Disparity
%
% Pixel disparity is calculated by cutting a window from the right image
% and scanning across the left image to find the location of highest
% correlation.
%
% Speed is directly proportional to qSize. Recommended higher wSize to
% ensure accurate disparity calculations. wSize > 71
%
wSize = 91; % window size for correlation, odd numbered square
temp = zeros(ydim, 1);
qSize = 5; % this is the degree of output quantization
disparityMatrix = zeros(xdim, ydim);
% %%%% data collection for algorithm testing
% maxC = zeros(size(disparity));
% meanC = zeros(size(disparity));
% stdC = zeros(size(disparity));
% %%%%
maxDisparity = 128; % upper bound on disparity. By inspection,
for v = (1 + wSize):qSize:(xdim - wSize)
    % %% renew disparity memory for each row
    % uprev = (1 + wSize); 
    % %%
    for u2 = (1 + wSize):qSize:(ydim - wSize)
        [a, b] = centerdim([u2 v], wSize);
        testSample = rightg(a, b);
        searchMin = max([(1 + wSize) (u2 - maxDisparity)]);
        searchMax = min([(ydim - wSize - 1) (u2 + maxDisparity)]);
        % %% testing new method
%         points = num2cell([...
%             u2 v searchMin searchMax uprev]);
%         [disparityMatrix(u2, v), uprev] = nearbysearch(...
%             leftg, testSample, points, wSize);
        % %%
        % %% <old method>
        for u = searchMin:qSize:searchMax
            [s, t] = centerdim([u v], wSize);
            temp(u) = corr2(leftg(s, t), testSample);
        end
        [maxCorr, idx] = max(temp);
        [s2, t2] = centerdim([u2 v], qSize);
%         maxC(s2, t2) = maxCorr;
%         meanC(s2, t2) = mean(temp);
%         stdC(s2, t2) = std(temp);
        if maxCorr < (1/10)
            dispPixels = 0;
        else
            dispPixels = idx - u2;
        end
       disparityMatrix(s2, t2) = ones(qSize) * dispPixels;
       temp = temp.*0;
            % %% </old method>
    end
    disp('Scanned line # ' + string(v))
end
%% Section 3. Hardware calibration
%
% Image depth is found from distance and size parameters based on the
% stereo camera geometry and calculated disparity
%
% (distance in meters) = baseline * f / (disp + displacement)
%

% %%%%% Smartphone Camera %%%%%
% 8MP f/2.2
% 1.12-micron pixels
displacement = 0; %same camera so c0 = x1 -> no displacement
baseline = 6 * 2.54 /100; % convert inches to meter
% % 1/16
f = 2964; %(3.75/4.87) * 4000; % Calculated = 3080.1 Empirical 2960. 
cb = [... % 
    2969.6         0 0
         0    2960.4 0
    1931.3    1121.0 1]';
%
% %%%%% Samsung Gear 360 Camera %%%%%
% "Depth" 2.2 in
% "Resolution" 15.0 Megapixels
% Sensor Size 1/2.3"
% Apeture f/2.0
% Angle 180
% How to resolve into camera matrix??
%% Section 4. Depth Map
%Z = baseline * f / (disp + displacement)
Z = baseline * f * ...
    (abs(disparityMatrix(wSize:(xdim-wSize),wSize:(ydim-wSize)))+ displacement).^(-1);
minDist = floor(baseline * f /(displacement + maxDisparity));
maxDist = 50; % hard coding to 100 meter range %ceil(baseline * f /(displacement + 1));
depthmap(Z, [minDist maxDist])
%%
