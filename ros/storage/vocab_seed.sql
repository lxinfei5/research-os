-- ResearchOS — controlled vocabulary seed. Extensible but GOVERNED: add values here,
-- not as free text. The URL gate (triggers.sql) rejects any source_ref whose platform or
-- source_kind is not listed below. Idempotent via INSERT OR IGNORE.

INSERT OR IGNORE INTO controlled_vocab (vocab_name, canonical_value, alias, status) VALUES
-- ── source_platform ──────────────────────────────────────────────────────
-- Public web / search
('source_platform','web','web_page','active'),
('source_platform','web','website','active'),
('source_platform','web_search','google','active'),
('source_platform','web_search','bing','active'),
('source_platform','web_search','sogou','active'),
('source_platform','web_search','searxng','active'),
('source_platform','web_search','zhipu','active'),
('source_platform','news_media','news','active'),
('source_platform','research_report',NULL,'active'),
('source_platform','paper','arxiv','active'),
-- Private media
('source_platform','x','X(Twitter)','active'),
('source_platform','x','twitter','active'),
('source_platform','douyin','抖音','active'),
('source_platform','xiaohongshu','小红书','active'),
('source_platform','xiaohongshu','rednote','active'),
('source_platform','wechat','微信','active'),
('source_platform','bilibili','b站','active'),
('source_platform','youtube',NULL,'active'),
-- Manual / misc
('source_platform','manual',NULL,'active'),
('source_platform','other',NULL,'active'),

-- ── source_kind ──────────────────────────────────────────────────────────
('source_kind','article',NULL,'active'),
('source_kind','web_page','web','active'),
('source_kind','search_result',NULL,'active'),
('source_kind','news',NULL,'active'),
('source_kind','report',NULL,'active'),
('source_kind','paper',NULL,'active'),
('source_kind','post','social_post','active'),
('source_kind','note',NULL,'active'),
('source_kind','video',NULL,'active'),
('source_kind','image','screenshot','active'),
('source_kind','forum','thread','active'),
('source_kind','chat',NULL,'active'),
('source_kind','other',NULL,'active');
