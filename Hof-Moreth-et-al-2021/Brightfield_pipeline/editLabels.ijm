image = getArgument();

open(image)
title = getTitle();
name = replace(title, ".tif", "")
selectWindow(title);
folder = getDirectory("image")
print("creating output folder")
File.makeDirectory(folder+"results_"+name+"\\");
output = folder+"results_"+name+"\\"
run("Label Edition");
//setTool("multipoint");
waitForUser('Merge labels if necessary. Therefore selct the labels by pressing shift and ckilckin on the image. \n To remove the selctions press Alt and click on the image. After merging press "Close", close the window with the cross and klick on "ok" to proceed');
print("saving output")
saveAs("Tiff", folder+name+"edited.tif");
for (i=1; i<nSlices+1; i++) {
	setSlice(i);
	run("Region Morphometry");
	wait(1000);
	saveAs("Results", output+i+"-Morphometry.csv");
}
setSlice(1);
run("Region Morphometry");
saveAs("Results", output+"1-Morphometry.csv");
wait(1000);
run("Close All");
run("Quit");