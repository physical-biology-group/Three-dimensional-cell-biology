arguments = getArgument();

data = split(arguments,'#');
print(arguments)
folder = data[0]+"//"
print(folder)
Prefix = data[1]
Suffix = data[7]
tstart=1
zP= data[2]
zPlanes = parseInt(zP);
ov = data[3]
overlap = parseInt(ov);
tp = data[4]
timePoints = parseInt(tp);
gX = data[5]
gridSizeX = parseInt(gX);
gY = data[6]
gridSizeY = parseInt(gY);
output = data[8]

// macro text
File.makeDirectory(folder+"zProjections\\");
zPro = folder+"zProjections\\"
File.makeDirectory(folder+"Stitched\\");
stiched = folder+"Stitched\\"
tiles = gridSizeX*gridSizeX+1
for(t = tstart; t < timePoints + tstart; t++){
                if(t < 10)
                {
                                vt = '0' + '0' + t;
                }
                else if(t < 100)
                {
                                vt = '0' + t;
                }
                else
                {
                                vt = t;
                }


/*for (t = 50; t < timePoints+50; t++){
	if (t < 10) {
		if (timePoints < 100) {
			vt = '1'+'0'+t;
		}
		else {
			vt = '0'+'0'+t;
		}
	}
	else {
		if (timePoints < 100) {
			vt = '1'+t;
		}
		else { 
			if (t < 100) {
				vt = '0'+t;
			}
			else {
				vt = t;
			}
		}
}*/	
	if (tiles <= 10){
		for (m = 1; m < tiles; m++){
			vm = m;
			for (z = 1; z < zPlanes+1; z++){
				if (z < 10){
					vz = '0'+z;
				}
				else {
					vz = z;
				}
				Image = folder+Prefix+'t'+vt+'z'+vz+'m'+vm+Suffix;
				open(Image);
			}
		run("Images to Stack", "name=Stack title=[] use");
		run("Z Project...", "projection=[Average Intensity]");
		run("Enhance Local Contrast (CLAHE)", "blocksize=49 histogram=256 maximum=5 mask=*None*"); 
		run("Subtract Background...", "rolling=700 light sliding disable");
		run("8-bit");
		saveAs("Tiff", zPro+Prefix+vt+'m'+vm+"zpro.tif");
		close();
		close();
		}
	}
	if (tiles > 10){
		for (m = 1; m < tiles; m++){
			if (m < 10){
				vm = '0'+m;
			}
			else {
				vm = m;
			}
			for (z = 1; z < zPlanes+1; z++){
				if (z < 10){
					vz = '0'+z;
				}
				else {
					vz = z;
				}
				Image = folder+Prefix+'t'+vt+'z'+vz+'m'+vm+Suffix;
				open(Image);
			}
			run("Images to Stack", "name=Stack title=[] use");
			run("Z Project...", "projection=[Average Intensity]");
			//run("Enhance Local Contrast (CLAHE)", "blocksize=49 histogram=256 maximum=5 mask=*None*"); 
			run("Subtract Background...", "rolling=700 light sliding disable");
			run("8-bit");
			saveAs("Tiff", zPro+Prefix+vt+'m'+vm+"zpro.tif");
			close();
			close();
			}
		}
	if (tiles <= 10){
		run("Grid/Collection stitching", "type=[Grid: row-by-row] order=[Right & Down                ] grid_size_x="+gridSizeX+" grid_size_y="+gridSizeY+" tile_overlap="+overlap+" first_file_index_i=1 directory="+zPro+" file_names="+Prefix+vt+"m{i}zpro.tif output_textfile_name=TileConfiguration.txt fusion_method=[Linear Blending] regression_threshold=0.30 max/avg_displacement_threshold=2.50 absolute_displacement_threshold=3.50 compute_overlap subpixel_accuracy computation_parameters=[Save computation time (but use more RAM)] image_output=[Fuse and display]");
	}
	else {
		run("Grid/Collection stitching", "type=[Grid: row-by-row] order=[Right & Down                ] grid_size_x="+gridSizeX+" grid_size_y="+gridSizeY+" tile_overlap="+overlap+" first_file_index_i=1 directory="+zPro+" file_names="+Prefix+vt+"m{ii}zpro.tif output_textfile_name=TileConfiguration.txt fusion_method=[Linear Blending] regression_threshold=0.30 max/avg_displacement_threshold=2.50 absolute_displacement_threshold=3.50 compute_overlap subpixel_accuracy computation_parameters=[Save computation time (but use more RAM)] image_output=[Fuse and display]");
	}
	selectWindow("Fused");
	saveAs("Tiff", stiched+Prefix+vt+"stiched.tif");
	print('stiched image ', vt, ' of ', timePoints);
	close();
}
for (t = tstart; t < timePoints + tstart; t++){
                if(t < 10)
                {
                                vt = '0' + '0' + t;
                }
                else if(t < 100)
                {
                                vt = '0' + t;
                }
                else
                {
                                vt = t;
	}
	open(stiched+Prefix+vt+"stiched.tif");
}
run("Images to Stack", "name=Stack title=[] use");
saveAs("Tiff", output);
close();
run("Quit");




