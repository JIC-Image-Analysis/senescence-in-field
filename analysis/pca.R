library(ggplot2)
library(ggfortify)

args <- commandArgs(trailingOnly=TRUE)
colors <- read.table(args[1], header=T, sep=',')
colors$hex <- rgb(colors$red, colors$green, colors$blue, maxColorValue=255)

df = colors[c(1, 2, 3)]
fig = autoplot(prcomp(df), colour=colors$hex)
fig = fig + geom_text(aes(label=colors$identifier), hjust=-0.1)  # Label the points.
#autoplot(prcomp(df), data=colors, colour='name')

ggsave(args[2])
