library(readxl)
no_ofi <- read_excel("~/GitHub/pokemon_metagame/no_ofi.xlsx")

reemplazar_ogerpon <- function(pokemon, objeto) {
  case_when(
    objeto == "Wellspring Mask" ~ paste0(pokemon, "-Wellspring"),
    objeto == "Hearthflame Mask" ~ paste0(pokemon, "-Hearthflame"),
    objeto == "Cornerstone Mask" ~ paste0(pokemon, "-Cornerstone"),
    TRUE ~ pokemon
  )
}
no_ofi %>%   mutate(across(ends_with("_Pokémon"), ~ mapply(reemplazar_ogerpon, ., no_ofi[[paste0(str_replace(cur_column(), "_Pokémon", "_Objeto"))]]))) ->no_ofi 


reemplazar_resultado <- function(resultado, nombre) {
  case_when(
    resultado == nombre ~ "Win",
    is.na(resultado) ~ NA_character_,
    resultado == "-1" ~ "DROP",
    TRUE ~ "Loss"
  )
}

# Aplica la funci?n a cada par de columnas Resultado y Nombre
for (i in 1:13) {
  nombre_resultado <- paste0("Resultado_", i)
  
  no_ofi <- no_ofi %>%
    mutate(!!nombre_resultado := mapply(reemplazar_resultado, !!sym(nombre_resultado), no_ofi$Nombre))
}


liverpool <- read_excel("~/GitHub/pokemon_metagame/torneos.xlsx", 
                        sheet = "liverpool")


portland <- read_excel("~/GitHub/pokemon_metagame/torneos.xlsx", 
                       sheet = "Portland")
charlotte <- read_excel("~/GitHub/pokemon_metagame/torneos.xlsx", 
                        sheet = "charlotte")

melbourne <- read_excel("~/GitHub/pokemon_metagame/torneos.xlsx", 
                        sheet = "melbourne")

knoxville <- read_excel("~/GitHub/pokemon_metagame/torneos.xlsx", 
                        sheet = "knoxville")
dortmund <- read_excel("~/GitHub/pokemon_metagame/dortmund.xlsx")

goianias <- read_excel("~/GitHub/pokemon_metagame/goianias.xlsx")

utrecht <- read_excel("~/GitHub/pokemon_metagame/utrecht.xlsx")

liverpool$Nombre<-iconv(liverpool$Nombre, to = "ISO-8859-1", sub = "byte")
charlotte$Nombre<-iconv(charlotte$Nombre, to = "ISO-8859-1", sub = "byte")
portland$Nombre<-iconv(portland$Nombre, to = "ISO-8859-1", sub = "byte")

ofis<-bind_rows(goianias, utrecht, dortmund, charlotte,knoxville, melbourne, liverpool, portland )

bind_rows(select(ofis, -c(Equipo,Enfrentamientos)), no_ofi) %>% 
  select(-Wins, -Losses, everything(), Wins, Losses) -> all_tours

write_excel_csv(all_tours, file = "all_tours_final.csv")
