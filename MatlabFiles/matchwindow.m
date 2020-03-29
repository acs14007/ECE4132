function [foundPoint, cost, avgf] = matchwindow(template, w, varargin)
%MATCHWINDOW Calculates cost function over entire input template
%
%   Searches whole template to find window
%   Plots template and indicates location of match
%   Returns location of match and map of cost function values
%   
%   Additionally, measures frequency and returns E[S(w)]
%
[xdim, ydim] = size(template);
[xw, yw] = size(w);
if xdim*ydim > 500^2
    disp('matchwindow searches every pixel. Consider reducing input size')
end
if xw ~= yw
    disp('matchwindow function expects odd-numbered square windows')
    wSize = xdim;
else
    wSize = xw;
end
if nargin == 3
    cfn = varargin{1};
    if cfn == "fft"
        cfunction =@(x) sum(fft2(meannormimage(x)).*conj(fft2(meannormimage(w))), ...
            'all')/(xw*yw);
        MaxOrMin = 'max';
    elseif cfn == "sad"
        cfunction =@(x) sum(abs(x - w), 'all');
        MaxOrMin = 'min';
    else
        cfunction =@(x) corr2(x, w);
        MaxOrMin = 'max';
    end
elseif nargin == 4
    % ignores 3rd argument and takes 4th as a lambda function
    y = varargin{2};
    cfunction =@(x) y(x);
    MaxOrMin = 'max';
else
    cfunction =@(x) corr2(x, w);
    MaxOrMin = 'max';
end
cost = zeros(xdim, ydim);
avgf = zeros(xw, yw); n = 0;
for v = (1 + wSize):(xdim - wSize)
    for u = (1 + wSize):(ydim - wSize)
        [s, t] = centerdim([u v], wSize);
        cost(v, u) = cfunction(template(s,t));
        nf =  fft2(meannormimage(double(template(s,t))));%  - mean2(double(template(s, t))));
        %avgf = avgf + fft2(double(template(s,t)) - mean2(double(template(s, t))));
        avgf = avgf + (nf.*conj(nf));
        n = n + 1;
    end
    disp('Scanned line # ' + string(v))
end
avgf = avgf/ n;

if MaxOrMin == 'max'
    [~, linindex] = max(cost, [], 'all', 'linear');
else
    [~, linindex] = min(cost, [], 'all', 'linear');
end
[r, c] = ind2sub([xdim ydim 1], linindex);
foundPoint = [r c];
figure
imshow(template)
hold on
scatter(c, r, 'o', 'y')
% resize after to omit edges for display
cost = cost((1 + wSize):(xdim - wSize), (1 + wSize):(ydim - wSize));
end
