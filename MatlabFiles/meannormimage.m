function [normim] = meannormimage(im)
% MEANNORMALIZE Attempts to set image to a mean of zero
%
%   % Parameters
    % im : image, typically uint8. gray or rgb
    %
    % Returns
    % normim : mean-normalized image. Returns same type as input image
    % 
normim = double(im) - mean2(double(im));
% if isa(im, 'uint8')
%     normim = uint8(normim);
% end
end