# Smart Pivot Project — Semiconductor Supply Chain Network Pipeline
# HOW TO RUN: Open in RStudio, hit Ctrl+Shift+S to source

# Install once if needed:
# install.packages(c("tidyverse", "readxl", "jsonlite", "igraph"))

library(tidyverse)
library(readxl)
library(jsonlite)
library(igraph)

`%||%` <- function(a, b) if (!is.null(a)) a else b

RAW  <- "C:/Users/sahas/Desktop/Research Portfolio/Semiconducter Network Analsysis/Github Project Repository/Data/Raw"
PROC <- "C:/Users/sahas/Desktop/Research Portfolio/Semiconducter Network Analsysis/Github Project Repository/Data/Processed"
dir.create(PROC, recursive = TRUE, showWarnings = FALSE)

cat("Raw:  ", RAW,  "\n")
cat("Out:  ", PROC, "\n\n")

# STEP 1 - GEOCODING
cat("[1/7] Geocoding lookup...\n")

ne_raw <- read_json(file.path(RAW, "ne_centroids.geojson"))

geo <- map_dfr(ne_raw$features, function(feat) {
  p <- feat$properties
  tibble(
    iso3   = p$ADM0_A3   %||% NA_character_,
    name   = p$NAME      %||% NA_character_,
    lon    = p$LABEL_X   %||% NA_real_,
    lat    = p$LABEL_Y   %||% NA_real_,
    region = p$REGION_UN %||% NA_character_
  )
}) %>%
  filter(!is.na(iso3), !is.na(lon), !is.na(lat)) %>%
  distinct(iso3, .keep_all = TRUE)

if (!"HKG" %in% geo$iso3) {
  geo <- add_row(geo, iso3="HKG", name="Hong Kong", lon=114.17, lat=22.32, region="Asia")
  cat("  HKG added manually\n")
}
cat("  OK -", nrow(geo), "territories\n")

# STEP 2 - OECD TiVA
cat("[2/7] OECD TiVA C26 DVA scores...\n")

agg_codes <- c("OECD","EU15","EU27_2020","EU28","EU28XEU15","NAFTA",
               "APEC","ASEAN","G20","A5_A7","S2","S2_S8",
               "E","F","W_O","WXD","WXOECD","EA19")

tiva <- read_csv(file.path(RAW, "oecd_tiva_C26.csv"), show_col_types = FALSE) %>%
  rename(iso3 = REF_AREA, year = TIME_PERIOD, dva = OBS_VALUE) %>%
  filter(year == "2020", !iso3 %in% agg_codes, !is.na(dva), dva > 0) %>%
  select(iso3, dva_usd_m = dva) %>%
  mutate(dva_norm = dva_usd_m / max(dva_usd_m))

cat("  OK -", nrow(tiva), "countries\n")
tiva %>% arrange(desc(dva_usd_m)) %>% slice(1:6) %>%
  mutate(dva_bn = round(dva_usd_m / 1000, 1)) %>%
  select(iso3, dva_bn) %>% print()

# STEP 3 - COMTRADE FUNCTIONS
cat("[3/7] Comtrade functions...\n")

read_comtrade <- function(filename) {
  read_csv(file.path(RAW, filename),
           show_col_types = FALSE,
           locale = locale(encoding = "latin1")) %>%
    filter(partnerISO == "W00",
           !is.na(primaryValue), primaryValue > 0,
           !reporterISO %in% c("W00","S19","S13","S14","S99","EU0")) %>%
    select(iso3 = reporterISO, flow = flowCode, value = primaryValue)
}

build_edges <- function(df, lid, lname, n_exp=15, n_imp=20, min_wt=0.01) {
  exporters <- df %>%
    filter(flow == "X") %>%
    group_by(iso3) %>% summarise(val = sum(value), .groups = "drop") %>%
    mutate(share = val / sum(val)) %>%
    arrange(desc(val)) %>% slice(1:n_exp)

  importers <- df %>%
    filter(flow == "M") %>%
    group_by(iso3) %>% summarise(val = sum(value), .groups = "drop") %>%
    mutate(share = val / sum(val)) %>%
    arrange(desc(val)) %>% slice(1:n_imp)

  cross_join(
    exporters %>% select(from = iso3, e = share),
    importers %>% select(to   = iso3, i = share)
  ) %>%
    filter(from != to) %>%
    mutate(
      weight_norm = (e * i) / max(e * i),
      layer_id    = lid,
      layer_name  = lname
    ) %>%
    filter(weight_norm >= min_wt) %>%
    select(from, to, weight_norm, layer_id, layer_name)
}

cat("  OK\n")

# STEP 4 - BUILD ALL EDGES
cat("[4/7] Building edges for all 6 layers...\n")

l1 <- tribble(
  ~from,  ~to,    ~weight_norm,
  "CHN",  "USA",  1.00,
  "CHN",  "KOR",  0.85,
  "CHN",  "TWN",  0.80,
  "CHN",  "DEU",  0.70,
  "CHN",  "JPN",  0.65,
  "CHN",  "CAN",  0.50,
  "CHN",  "GBR",  0.35,
  "CHN",  "FRA",  0.28,
  "CAN",  "USA",  0.55,
  "DEU",  "USA",  0.30,
  "DEU",  "NLD",  0.20,
  "JPN",  "USA",  0.18,
  "JPN",  "KOR",  0.14,
  "RUS",  "CHN",  0.08
) %>% mutate(layer_id = 1L, layer_name = "Raw Extraction")
cat("  L1:", nrow(l1), "edges\n")

l2 <- tribble(
  ~from,  ~to,    ~weight_norm,
  "JPN",  "TWN",  1.00,
  "JPN",  "KOR",  0.92,
  "JPN",  "USA",  0.68,
  "JPN",  "CHN",  0.55,
  "JPN",  "SGP",  0.42,
  "JPN",  "MYS",  0.30,
  "JPN",  "DEU",  0.22,
  "JPN",  "PHL",  0.20,
  "DEU",  "TWN",  0.52,
  "DEU",  "KOR",  0.46,
  "DEU",  "USA",  0.40,
  "DEU",  "JPN",  0.28,
  "DEU",  "CHN",  0.25,
  "USA",  "TWN",  0.45,
  "USA",  "KOR",  0.38,
  "USA",  "JPN",  0.25,
  "USA",  "SGP",  0.20,
  "KOR",  "TWN",  0.35,
  "KOR",  "CHN",  0.22,
  "BEL",  "TWN",  0.18,
  "BEL",  "KOR",  0.16
) %>% mutate(layer_id = 2L, layer_name = "Refined Materials")
cat("  L2:", nrow(l2), "edges\n")

cat("  L3: Equipment...\n")
l3 <- read_comtrade("comtrade_hs8486_2022.csv") %>%
      build_edges(3L, "Equipment")
cat("     ", nrow(l3), "edges\n")

cat("  L4: Design & IP...\n")
l4 <- read_comtrade("comtrade_hs852351_852352_852359_2022.csv") %>%
      build_edges(4L, "Design & IP")
cat("     ", nrow(l4), "edges\n")

cat("  L5: Fabrication...\n")
l5 <- read_comtrade("comtrade_hs8542_2022.csv") %>%
      build_edges(5L, "Fabrication", n_exp=15, n_imp=20)
cat("     ", nrow(l5), "edges\n")

cat("  L6: Assembly & Packaging...\n")
l6 <- read_comtrade("comtrade_hs8541.csv") %>%
      build_edges(6L, "Assembly & Packaging", n_exp=15, n_imp=20)
cat("     ", nrow(l6), "edges\n")

# STEP 5 - PASSIVE CONSUMER FILTER
cat("[5/7] Passive consumer filter...\n")

all_edges <- bind_rows(l1, l2, l3, l4, l5, l6) %>%
  filter(!is.na(from), !is.na(to), from != "", to != "")

all_ids <- union(all_edges$from, all_edges$to)

degree_tbl <- tibble(iso3 = all_ids) %>%
  mutate(
    out_deg = map_int(iso3, ~ sum(all_edges$from == .x)),
    in_deg  = map_int(iso3, ~ sum(all_edges$to   == .x))
  )

passive <- degree_tbl %>%
  filter(in_deg >= 2, out_deg == 0) %>%
  pull(iso3)

cat("  Removed:", if (length(passive) > 0) paste(passive, collapse=", ") else "none", "\n")

edges_f <- all_edges %>%
  filter(!from %in% passive, !to %in% passive)

cat("  OK -", nrow(edges_f), "edges remaining\n")

# STEP 6 - BETWEENNESS CENTRALITY
cat("[6/7] Betweenness centrality per layer...\n")

bc_long <- map_dfr(1:6, function(lid) {
  e <- edges_f %>% filter(layer_id == lid)
  if (nrow(e) == 0) return(tibble())
  g <- graph_from_data_frame(
    d = e %>% select(from, to, weight = weight_norm),
    directed = TRUE
  )
  bc <- betweenness(g, directed=TRUE,
                    weights=1 / E(g)$weight,
                    normalized=TRUE)
  tibble(iso3=names(bc), layer_id=lid,
         layer_name=unique(e$layer_name), bc=bc)
})

cat("  Top node per layer:\n")
bc_long %>%
  group_by(layer_id, layer_name) %>%
  slice_max(bc, n=1) %>%
  mutate(bc = round(bc, 4)) %>%
  select(layer_name, iso3, bc) %>% print()

bc_wide <- bc_long %>%
  select(iso3, layer_id, bc) %>%
  pivot_wider(names_from=layer_id, values_from=bc,
              names_prefix="bc_l", values_fill=0)

for (i in 1:6) {
  col <- paste0("bc_l", i)
  if (!col %in% names(bc_wide)) bc_wide[[col]] <- 0
}

# STEP 7 - WRITE OUTPUT
cat("[7/7] Writing JSON files...\n")

active_ids <- union(edges_f$from, edges_f$to)

nodes_final <- tibble(id = active_ids) %>%
  left_join(geo %>% select(id=iso3, label=name,
                            longitude=lon, latitude=lat, region), by="id") %>%
  left_join(tiva %>% select(id=iso3, dva_usd_m, dva_norm), by="id") %>%
  left_join(degree_tbl %>% select(id=iso3, out_deg, in_deg), by="id") %>%
  left_join(bc_wide %>% rename(id=iso3), by="id") %>%
  filter(!is.na(longitude)) %>%
  mutate(
    across(c(dva_usd_m, dva_norm,
             bc_l1, bc_l2, bc_l3, bc_l4, bc_l5, bc_l6),
           ~ replace_na(.x, 0)),
    bc_max = pmax(bc_l1, bc_l2, bc_l3, bc_l4, bc_l5, bc_l6),
    node_role = case_when(
      out_deg > in_deg * 1.5  ~ "exporter",
      in_deg  > out_deg * 1.5 ~ "importer",
      TRUE                    ~ "hub"
    )
  )

edges_final <- edges_f %>%
  filter(from %in% nodes_final$id, to %in% nodes_final$id) %>%
  left_join(tiva %>% select(iso3, src_dva=dva_norm), by=c("from"="iso3")) %>%
  mutate(
    final_weight = if_else(!is.na(src_dva) & src_dva > 0,
                           weight_norm * 0.6 + src_dva * 0.4,
                           weight_norm),
    final_weight = final_weight / max(final_weight)
  ) %>%
  select(source=from, target=to,
         weight=weight_norm, final_weight,
         layer_id, layer_name)

meta <- list(
  generated_at = format(Sys.time(), "%Y-%m-%dT%H:%M:%SZ"),
  n_nodes      = nrow(nodes_final),
  n_edges      = nrow(edges_final),
  layers = list(
    list(id=1, name="Raw Extraction",       color="#FF6B6B", source="USGS MCS 2026"),
    list(id=2, name="Refined Materials",    color="#FFA040", source="SEMI/SIA/BCG structural"),
    list(id=3, name="Equipment",            color="#FFD700", source="UN Comtrade HS 8486"),
    list(id=4, name="Design & IP",          color="#00CED1", source="UN Comtrade HS 852351-9"),
    list(id=5, name="Fabrication",          color="#9B59F5", source="UN Comtrade HS 8542"),
    list(id=6, name="Assembly & Packaging", color="#57E389", source="UN Comtrade HS 8541")
  ),
  disclaimer = "Edge weights are biproportional inferences from country-level trade aggregates. Working paper only."
)

write_json(nodes_final, file.path(PROC, "nodes.json"),
           pretty=TRUE, auto_unbox=TRUE, na="null")
write_json(edges_final, file.path(PROC, "edges.json"),
           pretty=TRUE, auto_unbox=TRUE, na="null")
write_json(meta, file.path(PROC, "meta.json"),
           pretty=TRUE, auto_unbox=TRUE)

# SUMMARY
cat("\n==========================================\n")
cat("PIPELINE COMPLETE\n")
cat("==========================================\n")
cat("nodes.json ->", nrow(nodes_final), "nodes\n")
cat("edges.json ->", nrow(edges_final), "edges\n\n")
cat("Node roles:\n");  print(table(nodes_final$node_role))
cat("\nEdges by layer:\n"); print(table(edges_final$layer_name))
cat("\nTop 10 nodes by betweenness:\n")
nodes_final %>%
  arrange(desc(bc_max)) %>% slice(1:10) %>%
  select(id, label, bc_max, node_role) %>%
  mutate(bc_max = round(bc_max, 4)) %>% print()
cat("\nFiles written to:", PROC, "\n")
