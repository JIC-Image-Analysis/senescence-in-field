library(ggplot2)

data <- read.table('scratch/leaf_senescence_dates', header=T)
data$Date <- as.Date(data$Date)
qplot(data$Date, geom="histogram", bins=31, main="Leaf senescence date")

data <- read.table('scratch/peduncle_senescence_dates', header=T)
data$Date <- as.Date(data$Date)
qplot(data$Date, geom="histogram", bins=31, main="Peduncle senescence date")
