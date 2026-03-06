import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
  articles: defineTable({
    url: v.string(),
    title: v.string(),
    summary: v.string(),
    fetched_at: v.number(),
  }).index("by_url", ["url"]),
});
