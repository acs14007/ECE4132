function [normpoints, tform] = meannormalize(points)
% MEANNORMALIZE transforms a column of 2-d vectors to center about origin
%
%   % Parameters
    % points: N x 2 matrix
    %
    % Returns
    % normpoints : normalized points
    % tform : associated transform
    N = length(points)/2;
    mu = mean(points); % mu =[Xmu Ymu]
    Xnormed = points(:,1)/mu(1);
    Ynormed = points(:,2)/mu(2);
    scale = sum(Xnormed.^2 + Ynormed.^2)/N;
    tform = (eye(3) - [mu 0]')/scale;
    normpoints = [Xnormed Ynormed];
end