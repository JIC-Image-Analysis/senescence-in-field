library(ggplot2)
library(ggfortify)

args <- commandArgs(trailingOnly=TRUE)
colors <- read.table(args[1], header=T, sep=',')
colors$hex <- rgb(colors$red, colors$green, colors$blue, maxColorValue=255)

df = colors[c(1, 2, 3)]
autoplot(prcomp(df), colour=colors$hex)
#autoplot(prcomp(df), data=colors, colour='name')

ggsave(args[2])
