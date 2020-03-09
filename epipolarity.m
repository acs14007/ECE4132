function [] = epipolarity(im1, im2)
%EPIPOLAR Demonstrate epipolar lines
%   Uses vision toolbox to find epipolar lines dynamically
%   Code sequence copied from Mathworks vision toolbox documentation.
%   Useful for verifying the geometry between two images
[x, y] = size(im1);
if x*y > 4 * 10^6
    disp("image too large to match features")
else
    p1 = detectHarrisFeatures(im1);
    p2 = detectHarrisFeatures(im2);
    [f1, valid1] = extractFeatures(im1, p1);
    [f2, valid2] = extractFeatures(im2, p2);
    pairs = matchFeatures(f1, f2);
    matchp1 = valid1(pairs(:,1),:);
    matchp2 = valid2(pairs(:,2),:);
    figure
    showMatchedFeatures(im1, im2, matchp1, matchp2)  
end

%
%% Commented out attempt to build by hand
%
% c1 = det(im1);
% [vSize, uSize] = size(im1);
% wSize = 100;
% [pairs, ~] = size(c1);
% c2 = zeros(pairs, 2);
% for x = 1:pairs
%     cors = zeros(vSize, uSize);
%     [sc1, tc1] = centerdim([c1(x,1) c1(x,2)], wSize);
%     im1sample = im1(sc1, tc1);
%     for v = (wSize + 1):(vSize-wSize)
%         for u = (vSize +1):(uSize-wSize)
%             [s, t] = centerdim([u v], wSize);
%             cors = corr2(im1sample, im2(s, t));
%         end
%     end
%     % expecting a single maximum per x loop
%     m = max(cors); [mx, my] = find(cors == m);
%     c2(x,:) = [mx my];
% end
% figure
% imshow(im1)
% hold on
% plot(c1(:,1), c1(:,2), 'r', 'markersize', 20)
% figure
% imshow(im2)
% hold on
% plot(c2(:,1), c2(:,2), 'r', 'markersize', 20)
end
