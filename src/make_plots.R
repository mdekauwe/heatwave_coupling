library(ggplot2)
library(cowplot)

theme_set(theme_cowplot(font_size=12)) # reduce default font size
fname = "/Users/mdekauwe/Desktop/x.csv"
df <- read.csv(file=fname, header=TRUE, sep=",")

ax1 <- ggplot(df) +
  geom_point(aes(x=SW, y=Qle), colour="blue", alpha=0.06) +
  geom_point(aes(x=SW, y=Qh), colour="red", alpha=0.06) +
  geom_smooth(method="loess", size=1.5, aes(x=SW, y=Qh), colour="red",
             fill ="salmon") +
  geom_smooth(method="loess", size=1.5, aes(x=SW, y=Qle), colour="blue",
              fill ="lightblue") +
  labs(x=bquote('SW down'~(W~m^-2)), y=bquote('Daily Fluxes'~(W~m^-2))) +
  theme(panel.grid.major=element_blank(),
        panel.grid.minor = element_blank())


ax2 <- ggplot(df) +
  geom_point(aes(x=Tair, y=Qle), colour="blue", alpha=0.06) +
  geom_point(aes(x=Tair, y=Qh), colour="red", alpha=0.06) +
  geom_smooth(method="loess", size=1.5, aes(x=Tair, y=Qh),
              colour="red", fill ="salmon") +
  geom_smooth(method="loess", size=1.5, aes(x=Tair, y=Qle), colour="blue",
              fill ="lightblue") +
  labs(x="Temperature (°C)", y=element_blank()) +
  theme(panel.grid.major=element_blank(),
        panel.grid.minor = element_blank())

plt <- plot_grid(ax1, ax2, labels="AUTO", align='h', hjust=0)

save_plot("/Users/mdekauwe/Desktop/plot.png", plt,
          ncol = 2, nrow = 1, base_aspect_ratio = 1.3)
