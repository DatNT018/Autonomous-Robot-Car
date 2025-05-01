clc;
clear all;
close all;

lane = imread('blue_lane.png');
laneDouble = double(lane);

sigma = 2;

% gaussian lowpass filter
N = 25;
[X, Y] = meshgrid(-N/2:N/2-1, -N/2:N/2-1);
G = 1/(2*pi*sigma^2)*exp(-(X.^2 + Y.^2)/(2*sigma^2));
G = G/sum(G(:));

bluredImage = conv2(laneDouble(:,:,1), G, 'same');  

% laplacian filter
H = [-1 1; 1 -1];
laplacian = conv2(bluredImage, H, 'same');

logImage = laplacian;
logImage(abs(laplacian) < 0.04 * max(laplacian(:))) = 128;

edgeImage = zeros(size(bluredImage));
edgeImage(laplacian > 0) = 255;

zeroImage = zeros(size(bluredImage));
zeroImage(abs(laplacian) > 0.04 * max(laplacian(:))) = 255;

%plot
figure;
subplot(2,2,1);
imshow(uint8(bluredImage));
title('Blurred Image');

subplot(2,2,2);
imshow(uint8(logImage));
title('Laplacian Thresholding');

subplot(2,2,3);
imshow(uint8(edgeImage));
title('Edge Detection');

subplot(2,2,4);
imshow(uint8(zeroImage));
title('Laplacian Magnitude');
