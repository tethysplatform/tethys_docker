# wps.des: custom-package-installer, title = custom-package-installer, abstract = custom-package-installer;
# wps.in: id = new_package, type = string, title = name of new package, minOccurs = 1, maxOccurs = 1;
# wps.out: output, text, the list of installed packages; 

# command to install my packages

install.packages(new_package, repos="http://cran.r-project.org")
packages <- installed.packages()
output = "packages_out"
write.table(c(row.names(packages)), output)