library(ggfortify)
dataset <- read.csv('output/test_plots/data/out/plot_colours.csv', header=T)
df <- dataset[3:5]

# Plot the first two principal components
autoplot(prcomp(df), data=dataset, colour='date')

# Extract the second principal component
p <- prcomp(df)
dataset$senescence <- p$x[,2]

# Plot it
ggplot(dataset, aes(date, senescence)) + geom_violin(aes(fill=date))

# Plot with colours as point colour
dataset$hex = rgb(dataset$R, dataset$G, dataset$B, maxColorValue = 255)
autoplot(prcomp(df), data=dataset, colour=dataset$hex)
