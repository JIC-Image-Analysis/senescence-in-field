library(ggfortify)
dataset <- read.csv('output/test_plots/data/out/plot_colours.csv', header=T)
df <- dataset[3:5]

# Plot the first two principal components
autoplot(prcomp(df), data=dataset, colour='date')

# Extract the second principal component
p <- prcomp(df)
dataset$senescence <- p$x[,2]
dataset$brightness <- p$x[,1]

# Plot it
ggplot(dataset, aes(date, senescence)) + geom_violin(aes(fill=date))

# Plot with colours as point colour
dataset$hex = rgb(dataset$R, dataset$G, dataset$B, maxColorValue = 255)
autoplot(prcomp(df), data=dataset, colour=dataset$hex)

ggplot(dataset, aes(date, brightness)) + geom_violin(aes(fill=date))


fast_senescing <- c('55_24', '50_14', '54_18', '16_17', '47_14')
slow_senescing <- c('8_6', '49_6', '29_17', '9_6', '21_1')

all_interesting <- c(fast_senescing, slow_senescing)

selected <- subset(dataset, plot %in% all_interesting)
