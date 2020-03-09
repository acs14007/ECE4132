function [color] = joinrgb(r, g, b)
%JOINRGB Concatenates color matrix to return rgb image
%   %% Inputs %%
%   r, g, b: matricies with numbers in range 0,255
%   enter scalar 0 if a color is omitted. Function will create a properly sized zero matrix
%   %% Returns $$
%   uint8 color image
%

if length(r) > 1
	blank = zeros(size(r));
elseif length(g) > 1
	blank = zeros(size(g));
elseif length(b) > 1
	blank = zeros(size(b));
else
	blank = 0
	% this constitutes an error %
end
if length(r) > 1
	red = uint8(r);
else
	red = uint8(blank);
end
if length(g) > 1
	green = uint8(g);
else
	green = uint8(blank);
end
if length(b) > 1
	blue = uint8(b);
else
	blue = uint8(blank);
end
color = cat(3, red, green, blue);
end

