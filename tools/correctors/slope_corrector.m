function [new_image] = slope_corrector(image, slope)
    % To have memory-smaller DWI images, the format of each image is kept to int16. 
    % To have the actual float value obtained at the acquisition, each DWI slice 
    % (5th dimensional index for nifti-format) must be multiplied for a number
    % (called image scale or data slope) stored in a txt file (VisuCoreDataSlope.txt 
    % in Bruker after parsing).
    % 
    % This script take as input the DWI image, the file that should accompanies each DWI image and
    % provides the DWI with the actual DWI with the float values.  
    %
    % USAGE:
    % im = load_untouch_nii('image.nii.gz');  % very important to load
    % untouch to have the same header in the output.
    % slope = importdata('slopes.txt')
    % im_new = slope_corrector(im, slope)
    % save_nii(im_new, 'image_sloped.nii.gz');
    % based on the library
    % "Tools for NIfTI and ANALYZE image":
    % https://uk.mathworks.com/matlabcentral/fileexchange/8797-tools-for-nifti-and-analyze-image
    %
    % please add it to you path 
    % or uncomment next line after with the correct path:
    % addpath('/Users/sebastiano/sw_libraries/matlab_libraries/NIfTI_20140122')

    new_image = image;
    slope_size = size(slope, 1);
    dim = length(size(new_image.img));
    
    % adjust the type:
    new_image.hdr.dime.datatype = 64;
    new_image.img = double(new_image.img);

    % if the dim is 4
    if dim == 4
        
        % and DWI on the fourth coordinate   
        if slope_size == size(new_image.img, 4)
            for j=1:slope_size
                new_image.img(:, :, :, j) = new_image.img(:, :, :, j) * slope(j, 1); 
            end
        else
            error('Dimension of image does not correspond with the dimension of the slope.');
        end    
    
    % if the dim is 5
    elseif dim == 5
        
        % and DWI on the fourth coordinate
        if slope_size == size(new_image.img, 4)
           for j=1:slope_size
                new_image.img(:, :, :, j, :) = new_image.img(:, :, :, j, :) * slope(j, 1); 
           end
        % and DWI on the fifth coordinate   
        elseif slope_size == size(new_image.img, 5)    
            for j=1:slope_size
                new_image.img(:, :, :, :, j) = new_image.img(:, :, :, :, j) * slope(j, 1); 
            end
        else
            error('Dimension of image does not correspond with the dimension of the slope.');
        end
    else
        error('Dimension of matrix allowed is 4 or 5.');
    end
    
    % to be able to save_nii without a different header
    new_image.untouch = 0;  
     
end