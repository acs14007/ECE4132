function [] = samplematches(im1, im2, method,...
    vVector, uVector, windowSize)
%UNTITLED3 Summary of this function goes here
%   Detailed explanation goes here
[xdim, ydim, ~] = size(im1);
if (vVector(end) > (xdim - windowSize))
    disp("v dimension exceeds image size")
end
uSize = length(uVector); vSize = length(vVector);
matchValues = zeros(uSize*vSize, ydim);
lcell = num2cell(zeros(uSize*vSize, 1)); maxDisparity = 2^10;
for v = 1:vSize
    for u = 1:uSize
        upoint = uVector(u); vpoint = vVector(v);
        [a, b] = centerdim([upoint vpoint], windowSize);
        testSample = im1(a, b);
        searchMin = max([(1 + windowSize) (upoint - maxDisparity)]);
        searchMax = min([(ydim - windowSize - 1) (upoint  + maxDisparity)]);
        for ud = searchMin:searchMax
            [s, t] = centerdim([ud vpoint], windowSize);
            otherSample = im2(s, t);
            if method == "corr"
                J = corr2(testSample, otherSample);
            elseif method == "ssd"
                J = sum((testSample - otherSample).^2, 'all');
            elseif method == "sad"
                J = sum(abs(testSample - otherSample), 'all');
            end
            matchValues(u*(v + 1) - 1, ud) = J;
        end
        lcell{u*(v + 1) - 1} = num2str(vpoint) + ", " + num2str(upoint);
    end
end
xaxis = 1:ydim;
figure
hold on
for x = 1:(uSize*vSize)
    plot(xaxis, matchValues(x, :), "DisplayName", lcell{x})
end
legend show
xlim([max(windowSize, uVector(1)-windowSize) ...
    min(uVector(end)+windowSize, ydim-windowSize)])
grid on
title(method)
end

