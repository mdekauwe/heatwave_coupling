library(ggplot2)
library(cowplot)

fname = "data/ozflux_fluxes.csv"
df <- read.csv(file=fname, header=TRUE, sep=",")
df <- subset(df, PFT!="NA")

pfts <- unique(df$PFT)

colours = c("red", "green", "blue", "yellow", "pink")

i <- 1
for (pft in pfts) {

  print(pft)
  theme_set(theme_cowplot(font_size=12))
  ax1 <- ggplot(df) +
    #geom_point(aes(x=SW, y=Qle), colour=colours[i], alpha=0.06) +
    geom_smooth(method="loess", size=1.5, aes(x=SW, y=Qle), colour=colours[i],
                fill=colours[i]) +
    labs(x=bquote('SW down'~(W~m^-2)), y=bquote('Qle'~(W~m^-2))) +
    theme(panel.grid.major=element_blank(),
          panel.grid.minor = element_blank())

  ax2 <- ggplot(df) +
    #geom_point(aes(x=SW, y=Qh), colour=colours[i], alpha=0.06) +
    geom_smooth(method="loess", size=1.5, aes(x=SW, y=Qh), colour=colours[i],
               fill=colours[i]) +
    labs(x=bquote('SW down'~(W~m^-2)), y=bquote('Qh'~(W~m^-2))) +
    theme(panel.grid.major=element_blank(),
          panel.grid.minor = element_blank())

  i <- i + 1
}

plt <- plot_grid(ax1, ax2, labels="AUTO", align='h', hjust=0)
save_plot("/Users/mdekauwe/Desktop/by_pft.png", plt,
          ncol=2, nrow=1, base_aspect_ratio=1.3)
