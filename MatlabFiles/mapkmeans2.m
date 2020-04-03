function [mapped] = mapkmeans2(im, keys, mapcolor)
%MAPKMEANS2 returns pixels mapped to nearest centroid
%
%   returns uint8 of size im. Optional third argument required to map
%   colors, otherwise maps key integer to pixels. Function to be vectorized
%   at some point. Currently runs on a for loop. Should be feasible to do a
%   tensor with dimensions = x, y, 3, #ofkeys
%
[M, N, L] = size(im); nkeys = size(keys, 1);
% keymats = zeros(M, N, L, nkeys, 'single');
% r = ones(M, N, L, 1); b = r; g = r;
% for x = 1:L
%     r = keys(x, 1); g = keys(x, 2); b = keys(x, 3);
%     keymats(:, :, :, x) = keys(:, :, :)
%     
% end
imColumn = reshape(single(im), M*N, L);
pixelrepmat = ones(nkeys, L, 'single');
if nargin > 2
    if strcmp(mapcolor, 'Color')
        mapfcn =@(x) uint8(keys(x, :));
        L = 3;
    else
        mapfcn =@(x) uint8(x); % Currently no other options
    end
else
    mapfcn =@(x) uint8(x);
end
% mapping must be initialized after L is reassigned based on the color flag
mapvector = zeros(M*N, L);
for pixel = 1:M*N
    p = pixelrepmat.*imColumn(pixel,:);
    difsq = sum((p - keys).^2,2);
    [~, matchedKey] = min(difsq);
    mapvector(pixel, :) = mapfcn(matchedKey);
end
mapped = uint8(floor(reshape(mapvector, M, N, L)));
end

