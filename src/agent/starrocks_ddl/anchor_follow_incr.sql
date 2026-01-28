CREATE TABLE `anchor_follow_incr` (
  `anchor_id` bigint(20) NULL COMMENT "",
  `today_follow` bigint(20) NULL COMMENT "",
  `before_follow` bigint(20) NULL COMMENT "",
  `follow_incr` bigint(20) NULL COMMENT "",
  `date_flag` int(11) NULL COMMENT ""
) ENGINE=OLAP 
DUPLICATE KEY(`anchor_id`, `today_follow`, `before_follow`)
DISTRIBUTED BY HASH(`anchor_id`) BUCKETS 100 
PROPERTIES (
"compression" = "LZ4",
"fast_schema_evolution" = "true",
"replicated_storage" = "true",
"replication_num" = "3"
);;
