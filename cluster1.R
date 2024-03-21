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

###La caracterización fue en excel######

carac_final <- read_delim("cluster1.csv", 
                          delim = ";", escape_double = FALSE, trim_ws = TRUE)

carac_final %>% 
  filter(cluster!="Other")->carac_sig

carac_sig %>% select(5,13,21,29,37,45) %>% pivot_longer(everything()) %>% select(value) %>% unique %>% as.vector %>% .$value %>% sort %>% writeClipboard()

bind_rows(carac_sig, all_tours) %>% View


carac_sig$cluster %>% table

carac_sig %>% 
  filter(cluster=="Articuno Offense") %>% 
  select(5,13,21,29,37,45) %>% pivot_longer(everything()) %>% select(value) %>% unique


carac_sig %>% 
  filter(cluster=="Articuno Offense") %>% View



library(tidyr)

###### HABEMOS FACT TABLE POKEMON ##########

cbind(carac_sig %>% 
        select(grep("^\\d+_", names(carac_sig), value = TRUE)) %>% 
        split.default(rep(1:(345 %/% 8), each = 8, length.out = 48)) %>% 
        lapply(function(mat) {
          colnames(mat) <- c("Pokémon","Objeto","Habilidad","Teratipo","Mov1","Mov2","Mov3","Mov4")
          return(mat)
        }) %>% do.call(rbind, .) , carac_sig %>% 
        select(c(Torneo, Nombre, cluster)) %>%
        .[rep(row.names(.), times = 6), ] 
) %>%  arrange(cluster, Nombre) -> fact_pokemon

fact_pokemon$cluster %>% table

######### EJEMPLO DE GRAFICOS Y TABLAS NECESARIAS PARA EL DASHBOARD ##########

fact_pokemon %>% 
  group_by(cluster) %>% 
  summarise(Usage = n()/6) %>% 
  arrange(desc(Usage))

### CON ARTICUNO OFFENSE SE PUEDE HACER UN GRAFICO DE % DE USO ###

fact_pokemon %>%
  filter(cluster == "Articuno Offense") %>%
  group_by(Pokémon) %>%
  summarise(Usage = n_distinct(Nombre) / n_distinct(filter(fact_pokemon, cluster == "Articuno Offense")$Nombre) * 100) %>% 
  arrange(desc(Usage))

#CON CADA POKE DEL % DE USO SE PUEDE HACER UN GRAFICO DE % DE USO DE OBJETOS HABILIDADES ETC ###

fact_pokemon %>%
  filter(cluster == "Articuno Offense") %>% 
  filter(Pokémon == "Articuno") %>% 
  group_by(Objeto) %>%
  summarise(Objetos= n()/n_distinct(filter(fact_pokemon, cluster == "Articuno Offense")$Nombre) * 100) %>% 
  arrange(desc(Objetos))

fact_pokemon %>%
  filter(cluster == "Articuno Offense") %>% 
  filter(Pokémon == "Articuno") %>% 
  group_by(Habilidad) %>%
  summarise(Habilidades= n()/n_distinct(filter(fact_pokemon, cluster == "Articuno Offense")$Nombre) * 100) %>% 
  arrange(desc(Habilidades))

fact_pokemon %>%
  filter(cluster == "Articuno Offense") %>% 
  filter(Pokémon == "Articuno") %>% 
  group_by(Teratipo) %>%
  summarise(Teratipos= n()/n_distinct(filter(fact_pokemon, cluster == "Articuno Offense")$Nombre) * 100) %>% 
  arrange(desc(Teratipos))

fact_pokemon %>%
  filter(cluster == "Articuno Offense") %>% 
  filter(Pokémon == "Articuno") %>% 
  select(Mov1, Mov2, Mov3, Mov4) %>% 
  pivot_longer(everything(), values_to = "Move") %>% 
  group_by(Move) %>%
  summarise(Moves= n()/n_distinct(filter(fact_pokemon, cluster == "Articuno Offense")$Nombre) * 100) %>% 
  arrange(desc(Moves))
