library(readr)
library(dplyr)
library(ggplot2)
library(rnaturalearth)
library(rnaturalearthdata)

###################################
old <- read_tsv('lb_1.tsv', na=c('')) 
gcodes <- unique(old$Glottocode)

languages <- read_tsv('lb_release.tsv', na=c('')) %>% 
  mutate(new=ifelse(Glottocode %in% gcodes, 0, 1))

################################################
#####             Maps                     #####
################################################
languages$Longitude<-sapply(languages$Longitude,function(x) ifelse(x<(-25),x + 360,x))
world <- map_data('world', interior=F, wrap=c(-25,335), ylim=c(-54,79))

map_lb <- ggplot() +
  geom_polygon(
    data=world,
    aes(x=long,y=lat,group=group),
    colour="#F2DDC1",linewidth=0.2, fill="#F2DDC1"
  ) + 
  geom_jitter(
    data=languages,
    aes(Longitude, Latitude, fill=Count, alpha=ifelse(new==1, 0.7, 0.4)),
    height=3, width=2, size=4, shape=21
  ) +
  scale_fill_viridis_c(option="D", trans = "log", breaks=c(100, 250, 500, 1000), name="Concepts") +
  scale_x_continuous(name=NULL, breaks=NULL) +
  scale_y_continuous(name=NULL, breaks=NULL) +
  theme_bw() +
  guides(alpha = 'none') +
  theme(legend.position="right") 

map_lb
ggsave('map_lb.png', map_lb, scale=1, width=2000, height=1200, units="px")
