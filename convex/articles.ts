import { query, mutation } from "./_generated/server";
import { v } from "convex/values";

export const getByUrl = query({
  args: { url: v.string() },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("articles")
      .withIndex("by_url", (q) => q.eq("url", args.url))
      .first();
  },
});

export const insert = mutation({
  args: {
    url: v.string(),
    title: v.string(),
    summary: v.string(),
    fetched_at: v.number(),
  },
  handler: async (ctx, args) => {
    await ctx.db.insert("articles", args);
  },
});
