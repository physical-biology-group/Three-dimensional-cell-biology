arguments = getArgument();
data = split(arguments,'#');

image = data[0]
filter = data[1]
saving = data[2]

wait(1000);
// macro text
open(image)
title = getTitle();
selectWindow(title);
folder = getDirectory("image")
print("creating output folder")
File.makeDirectory(folder+"results_"+title+"\\");
output = folder+"results_"+title+"\\"
//process image
if (filter == "bilateral") {
	print("applying bilateral filter");
	run("8-bit");
	run("Bilateral Filter", "spatial=10 range=50");
	selectWindow(title);
	close();
	title = getTitle();
}
if (filter == "sigma") {
	print("applying sigma filter");
	for (i=1; i<nSlices+1; i++) {
		setSlice(i);
		run("Sigma Filter Plus", "radius=10 use=2 minimum=0.2");
	}
}
if (filter == "median") {
	print("applying median filter");
	run("Median...", "radius=5 stack");
}
selectWindow(title);
run("Subtract Background...", "rolling=500 light sliding stack");
run("Invert", "stack");
print("starting morphological segmentation");
run("Morphological Segmentation");
selectWindow("Morphological Segmentation");
wait(1000);
call("inra.ijpb.plugins.MorphologicalSegmentation.setInputImageType", "border");
print("border type set");
call("inra.ijpb.plugins.MorphologicalSegmentation.segment", "tolerance=15", "calculateDams=true", "connectivity=6");
print("segment");
call("inra.ijpb.plugins.MorphologicalSegmentation.setDisplayFormat", "Catchment basins");
waitForUser('If the segmentation does not start automatically, enter a value in the field "Tolerance" (usually 10 to 15) and press run.\n Repeat until the segmentation is satisfactory, then press ok. Several labels can be merged in the next step.');
call("inra.ijpb.plugins.MorphologicalSegmentation.createResultImage");
selectWindow("Morphological Segmentation");
close();

// save output and close windows
selectWindow(title);
close();
title = getTitle();
selectWindow(title);
run("Remove Border Labels", "left right top bottom");
print("saving intermediate image");
if (saving == "yes") {
	saveAs("Tiff", image+"_intermediate.tif");
}
run("Label Edition");
//setTool("multipoint");
waitForUser('Merge labels if necessary. Therefore select the labels by pressing shift and click in on the image. \n To remove the selctions press Alt and click on the image. After merging press "Close", close the window with the cross and klick on "ok" to proceed');
saveAs("Tiff", image+"_segmented.tif");
for (i=1; i<nSlices+1; i++) {
	setSlice(i);
	run("Region Morphometry");
	wait(1000);
	saveAs("Results", output+i+"-Morphometry.csv");
}
wait(1000);
run("Close All");
run("Quit");


