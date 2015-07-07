# wps.des: installed-packages, title = installed-packages, abstract = installed-packages;
# wps.in: input, integer; 
# wps.out: output, text, the table of installed packages; 

# fetch the installed packages
packages <- installed.packages()
output = "packages_out"
write.table(row.names(packages), output)
