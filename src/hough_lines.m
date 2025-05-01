clc;
clear all;
close all;

lane = imread('blue_lane.png');

if size(lane, 3) > 1
    laneGray = rgb2gray(lane);
else
    laneGray = lane;
end

laneGray = imgaussfilt(laneGray, 2);

% Canny Edge Detection 
binary_image = edge(laneGray, 'Canny', [0.1 0.3]);


figure, imshow(binary_image), title('Binary Image from Canny Edge Detection');

% Hough Transform
a = -90:1:89; 
[H, T, R] = hough(binary_image, 'Rho', 1, 'Theta', a);

thresh = 0.3 * max(H(:)); 
P = houghpeaks(H, 10, 'Threshold', thresh);

if isempty(P)
    P = [1 1; 1 1];
end

min_line_length = 100; 
fill_gap_between_lines = 50;
lines = houghlines(binary_image, T, R, P, 'MinLength', min_line_length, 'FillGap', fill_gap_between_lines);

figure, imshow(lane); 
hold on;

for k = 1:length(lines)
    xy = [lines(k).point1; lines(k).point2];
    plot(xy(:,1), xy(:,2), 'LineWidth', 2, 'Color', 'green');
end

title('final detected lines');
hold off;