CREATE TABLE `anchor_daily` (
  `id` varchar(255) NOT NULL COMMENT "",
  `date_flag` int(11) NOT NULL COMMENT "",
  `anchor_id` bigint(20) NOT NULL COMMENT "",
  `create_time` datetime NOT NULL COMMENT "",
  `favoriting_count` bigint(20) NULL COMMENT "",
  `follow_count` bigint(20) NULL COMMENT "",
  `following_count` bigint(20) NULL COMMENT "",
  `forward_count` bigint(20) NULL COMMENT "",
  `item_count` bigint(20) NULL COMMENT "",
  `like_count` bigint(20) NULL COMMENT "",
  `update_time` datetime NULL COMMENT "",
  `club_total_count` bigint(20) NULL COMMENT ""
) ENGINE=OLAP

CREATE TABLE `anchor_follow_incr` (
  `anchor_id` bigint(20) NULL COMMENT "",
  `today_follow` bigint(20) NULL COMMENT "",
  `before_follow` bigint(20) NULL COMMENT "",
  `follow_incr` bigint(20) NULL COMMENT "",
  `date_flag` int(11) NULL COMMENT ""
) ENGINE=OLAP

CREATE TABLE `anchor_video_item_gjz_test` (
  `id` bigint(20) NOT NULL COMMENT "",
  `publish_date_time` datetime NOT NULL COMMENT "",
  `anchor_id` bigint(20) NOT NULL COMMENT "",
  `duration` int(11) NULL COMMENT "",
  `follow_cnt` bigint(20) NULL COMMENT "",
  `like_cnt` bigint(20) NULL COMMENT "",
  `video_text` varchar(1000) NULL COMMENT "",
  `coment_cnt` bigint(20) NULL COMMENT "",
  `is_graphic` boolean NULL COMMENT "",
  `cart_video` boolean NULL COMMENT "",
  `product_id` varchar(20) NULL COMMENT "",
  `picture` varchar(2000) NULL COMMENT "",
  `share_cnt` bigint(20) NULL COMMENT "",
  `product_ids` varchar(65533) NULL COMMENT "",
  `is_delete` boolean NULL DEFAULT "false" COMMENT "",
  `product_ids_array` array<varchar(255)> NULL COMMENT "",
  `fans_profile_age` varchar(255) NULL COMMENT "",
  `fans_profile_city` varchar(255) NULL COMMENT "",
  `fans_profile_gender` varchar(255) NULL COMMENT "",
  `fans_profile_province` varchar(255) NULL COMMENT "",
  `keyword` varchar(65533) NULL COMMENT "",
  `update_time` int(11) NULL COMMENT "",
  INDEX idx_anchor_video_item_publish_time (`publish_date_time`) USING BITMAP COMMENT '',
  INDEX idx_cart_video_bitmap (`cart_video`) USING BITMAP COMMENT '',
  INDEX idx_item_product_id (`product_id`) USING BITMAP COMMENT '',
  INDEX idx_anchor_id (`anchor_id`) USING BITMAP COMMENT ''
) ENGINE=OLAP

CREATE TABLE `date_video_data` (
  `date_flag` date NOT NULL COMMENT "",
  `video_id` varchar(20) NOT NULL COMMENT "",
  `sales_low` bigint(20) NULL COMMENT "",
  `sales_high` bigint(20) NULL COMMENT "",
  `product_id` varchar(20) NULL COMMENT "",
  `anchor_id` bigint(20) NULL COMMENT "",
  `publish_date` date NULL COMMENT "",
  `digg` int(11) NULL DEFAULT "0" COMMENT "",
  `comment` int(11) NULL DEFAULT "0" COMMENT "",
  `share` int(11) NULL DEFAULT "0" COMMENT "",
  `collect` int(11) NULL DEFAULT "0" COMMENT "",
  `is_delete` tinyint(4) NULL DEFAULT "0" COMMENT "",
  `is_top` int(11) NULL DEFAULT "0" COMMENT "",
  `create_time` datetime NULL COMMENT "",
  INDEX idx_create_time (`create_time`) USING BITMAP COMMENT ''
) ENGINE=OLAP

CREATE TABLE `jl_user` (
  `anchor_id` bigint(20) NOT NULL COMMENT "",
  `user_name` varchar(255) NULL COMMENT "",
  `user_head_logo` varchar(255) NULL COMMENT "",
  `first_tag_name` varchar(100) NULL COMMENT "",
  `second_tag_name` varchar(100) NULL COMMENT "",
  `follow_count` bigint(20) NULL COMMENT "",
  `follow_incr` bigint(20) NULL COMMENT "",
  `city` varchar(50) NULL COMMENT "",
  `province` varchar(50) NULL COMMENT "",
  `birth_year` int(11) NULL COMMENT "",
  `is_gov_media_vip` boolean NULL COMMENT "",
  `user_gender` varchar(10) NULL COMMENT "",
  `enterprise_verify` varchar(255) NULL COMMENT "",
  `custom_verify` varchar(255) NULL COMMENT "",
  `with_fusion_shop_entry` boolean NULL COMMENT "",
  `aweme_id` varchar(50) NULL COMMENT "",
  `hava_contact` boolean NULL COMMENT "",
  `sec_uid` varchar(255) NULL COMMENT "",
  `shop_id` bigint(20) NULL COMMENT "所属店铺",
  `level` int(11) NULL COMMENT "带货等级",
  `star_atlas` boolean NULL COMMENT "",
  `shop_types_array` array<varchar(255)> NULL COMMENT "",
  `score` decimal(10, 2) NULL COMMENT "",
  `is_delete` boolean NULL COMMENT "",
  `special_state` int(11) NULL COMMENT "",
  `update_time` int(11) NULL COMMENT "",
  `enterprise_type` varchar(65533) NULL COMMENT "",
  `insitution_id` varchar(100) NULL COMMENT "mcn",
  `esc_shop_id` varchar(50) NULL COMMENT "",
  `user_introduction` varchar(65533) NULL COMMENT "",
  `fans_club_number` bigint(20) NULL COMMENT "",
  `like_count` bigint(20) NULL COMMENT "",
  `ip_text` varchar(100) NULL COMMENT "",
  INDEX idx_jl_user_anchor (`anchor_id`) USING BITMAP COMMENT '',
  INDEX idx_user_name (`user_name`) USING GIN("imp_lib" = "clucene", "parser" = "standard") COMMENT '',
  INDEX idx_aweme_id (`aweme_id`) USING GIN("imp_lib" = "clucene", "parser" = "standard") COMMENT ''
) ENGINE=OLAP

CREATE TABLE `live_base` (
  `id` bigint(20) NOT NULL COMMENT "",
  `live_create_time` datetime NOT NULL COMMENT "",
  `anchor_id` bigint(20) NOT NULL COMMENT "",
  `cover_url` varchar(1024) NULL COMMENT "",
  `finish_time` int(11) NULL COMMENT "",
  `is_show` boolean NULL COMMENT "",
  `title` varchar(255) NULL COMMENT "",
  `top_user` bigint(20) NULL COMMENT "",
  `total_user` bigint(20) NULL COMMENT "",
  `contain_cart` int(11) NULL COMMENT "",
  `follow_count` bigint(20) NULL COMMENT "",
  `like_count` bigint(20) NULL COMMENT "",
  `windmill_id` bigint(20) NULL COMMENT "",
  `windmill_title` varchar(255) NULL COMMENT "",
  `windmill_type` varchar(255) NULL COMMENT "",
  `windmill_url` varchar(2000) NULL COMMENT "",
  `windmill_create_time` datetime NULL COMMENT "",
  `update_time` int(11) NULL COMMENT "",
  `exposed_num` bigint(20) NULL COMMENT "",
  `rtmp_pull_url` varchar(1000) NULL COMMENT "RTMP流地址",
  INDEX idx_contain_cart (`contain_cart`) USING BITMAP COMMENT ''
) ENGINE=OLAP

CREATE TABLE `live_product_sale` (
  `room_id` bigint(20) NOT NULL COMMENT "",
  `product_id` bigint(20) NOT NULL COMMENT "",
  `date_flag` date NOT NULL COMMENT "",
  `anchor_id` bigint(20) NULL COMMENT "",
  `number` int(11) NULL COMMENT "",
  `min_price` decimal(14, 2) NULL COMMENT ""
) ENGINE=OLAP

CREATE MATERIALIZED VIEW `live_base_view` (`id`, `live_create_time`, `anchor_id`, `cover_url`, `finish_time`, `is_show`, `title`, `top_user`, `total_user`, `contain_cart`, `follow_count`, `like_count`, `windmill_id`, `windmill_title`, `windmill_type`, `windmill_url`, `windmill_create_time`, `update_time`, `exposed_num`, `city`, `province`, `user_follow_count`, `user_name`, `user_head_logo`, `user_gender`, `first_tag_name`, `second_tag_name`, `product_num`, `sales_volume`, `saleroom`, `promotion_source`, `first_cid`, `second_cid`, `other`,
  INDEX idx_sales_volume (`sales_volume`) USING BITMAP COMMENT '',
  INDEX idx (`title`) USING GIN("imp_lib" = "clucene", "parser" = "chinese") COMMENT '')
PARTITION BY (`live_create_time`)
DISTRIBUTED BY RANDOM
REFRESH MANUAL
PROPERTIES (
"replicated_storage" = "false",
"session.enable_spill" = "true",
"partition_ttl" = "181 DAY",
"replication_num" = "3",
"storage_medium" = "HDD"
)
AS SELECT `t1`.`id`, `t1`.`live_create_time`, `t1`.`anchor_id`, `t1`.`cover_url`, `t1`.`finish_time`, `t1`.`is_show`, `t1`.`title`, `t1`.`top_user`, `t1`.`total_user`, `t1`.`contain_cart`, `t1`.`follow_count`, `t1`.`like_count`, `t1`.`windmill_id`, `t1`.`windmill_title`, `t1`.`windmill_type`, `t1`.`windmill_url`, `t1`.`windmill_create_time`, `t1`.`update_time`, `t1`.`exposed_num`, `t2`.`city`, `t2`.`province`, `t2`.`follow_count` AS `user_follow_count`, `t2`.`user_name`, `t2`.`user_head_logo`, `t2`.`user_gender`, `t2`.`first_tag_name`, `t2`.`second_tag_name`, `t3`.`product_num`, `t3`.`sales` AS `sales_volume`, `t3`.`saleroom`, `t4`.`distinct_promotion_sources` AS `promotion_source`, `t4`.`distinct_first_cids` AS `first_cid`, `t4`.`distinct_second_cids` AS `second_cid`, `t5`.`other`
FROM `donggua`.`live_base` AS `t1` LEFT OUTER JOIN `donggua`.`jl_user` AS `t2` ON `t1`.`anchor_id` = `t2`.`anchor_id` LEFT OUTER JOIN `donggua`.`live_sales_view` AS `t3` ON `t1`.`id` = `t3`.`room_id` LEFT OUTER JOIN `donggua`.`jl_user_shop_type_view` AS `t4` ON `t1`.`anchor_id` = `t4`.`anchor_id` LEFT OUTER JOIN `donggua`.`live_info_traffic` AS `t5` ON `t1`.`id` = `t5`.`_id`
