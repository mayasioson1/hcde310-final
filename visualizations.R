library(dplyr)
library(ggplot2)

# combine all csv files into one dataframe, save it to a new csv file
filenames <- list.files(path = "data/", pattern = "*.csv")
fullpath <- file.path("data", filenames)
contributions <- do.call("rbind", lapply(fullpath, FUN=function(files) {read.csv(files)}))

write.csv(contributions, "data/combined_contribs.csv", row.names = FALSE)

ggplot(data = contributions) +
  geom_point(mapping = aes(x = candidate_name, y = amount), alpha = 0.05) +
  scale_y_continuous(labels = scales::comma)

contribs_filtered <- contributions %>%
  filter(contributor_name != "UNITEMIZED TOTAL")
