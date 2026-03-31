-- Ensure one content_item per topic/channel fan-out target.
ALTER TABLE content_items
  ADD CONSTRAINT uq_content_items_topic_channel UNIQUE (topic_id, channel_id);
