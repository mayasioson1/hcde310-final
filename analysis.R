library(dplyr)
library(ggplot2)

# combine all csv files into one dataframe, save it to a new csv file
filenames <- list.files(path = "data/", pattern = "*.csv")
fullpath <- file.path("data", filenames)
contributions <- do.call("rbind", lapply(fullpath, FUN=function(files) {read.csv(files)}))
# write.csv(contributions, "data/combined_contribs.csv", row.names = FALSE)

contribs_filtered <- contributions %>%
  filter(contributor_name != "UNITEMIZED TOTAL")

republicans <- contribs_filtered %>%
  filter(candidate_name == "trump" | candidate_name == "weld" | candidate_name == "walsh")

democrats <- contribs_filtered %>%
  filter(candidate_name != "trump" & candidate_name != "weld" & candidate_name != "walsh")
