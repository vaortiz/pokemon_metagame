library(readxl)
library(readr)
library(tidyverse)
all_tours %>% 
  filter(Wins>6) %>% 
  .[,c(5:52)]->df

all_tours %>% 
  filter(Wins>6) %>% View

jaccard <- function(a, b) {
  a <- unlist(a)
  b <- unlist(b)
  intersection <- length(intersect(a, b))
  union <- length(union(a, b))
  return(1 - intersection / union)
}

outer(1:nrow(df), 1:nrow(df), Vectorize(function(i, j) jaccard(df[i, ], df[j, ])))->mat_jacc

library(cluster)
library(factoextra)
fviz_nbclust(hcut, method = "silhouette")
silhouette(mat_jacc, dist.method = "euclidean")

fviz_nbclust(mat_jacc, hcut, method = "gap_stat", k.max = 50)


library(Rtsne)
tsne_result <- Rtsne(as.dist(mat_jacc), is_distance = TRUE)
tsne_result$theta
plot(tsne_result$Y, col = "blue", pch = 16, main = "t-SNE de Matriz de Distancias")
library(plotly)
data <- data.frame(X = tsne_result$Y[, 1], Y = tsne_result$Y[, 2], Etiqueta=c(1:472))
ts<-select(data,1,2)

library(NbClust)
res.nbclust <- NbClust(ts, distance = "euclidean",
                       min.nc = 15, max.nc = 50, 
                       method = "average", index ="all") 
res.nbclust$Best.nc

library(plotly)
plot_ly(data, x = ~X, y = ~Y, text = ~Etiqueta, mode = "markers", marker = list(size = 10)) %>%
  layout(title = "t-SNE de Matriz de Distancias", xaxis = list(title = "Dimensión 1"), yaxis = list(title = "Dimensión 2"))
library(dbscan)
dbscan_result <- dbscan(ts, eps = 1.165, minPts = 1) 
cluster<-dbscan_result$cluster

cbind(df,cluster) %>% select(1,9,17,25,33,41,49) %>% gather(key = "columna", value = "nombre", -cluster) %>%
  group_by(cluster, nombre) %>%
  summarise(repeticiones = n())%>%
  arrange(cluster, desc(repeticiones)) %>% View

cluster %>% table %>% order
cluster %>% table
fviz_cluster(list(data = ts, cluster = cluster),
             ellipse.type = "convex", # Concentration ellipse
             repel = F, # Avoid label overplotting (slow)
             show.clust.cent = FALSE, ggtheme = theme_minimal() +
               theme(legend.position = "none"))

all_tours %>% 
  filter(Wins>6) %>% cbind(cluster)->sum1

write_excel_csv(sum1, "cluster1.csv")

carac_final <- read_delim("cluster1.csv", 
                          delim = ";", escape_double = FALSE, trim_ws = TRUE)

carac_final %>% 
  filter(cluster!="Other")->carac_sig
