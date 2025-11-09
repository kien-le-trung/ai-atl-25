import { sql } from "drizzle-orm";
import { pgTable, text, varchar, timestamp, jsonb, integer } from "drizzle-orm/pg-core";
import { relations } from "drizzle-orm";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod";

// Person table - stores individual contacts
export const persons = pgTable("persons", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  name: text("name").notNull(),
  photoUrl: text("photo_url"),
  company: text("company"),
  school: text("school"),
  email: text("email"),
  experiences: text("experiences"),
  hobbies: text("hobbies"),
  lastLocation: text("last_location"),
  lastMeetingDate: timestamp("last_meeting_date"),
  lastTopic: text("last_topic"),
  createdAt: timestamp("created_at").defaultNow().notNull(),
});

// Conversation table - stores conversation sessions
export const conversations = pgTable("conversations", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  personId: varchar("person_id").notNull().references(() => persons.id, { onDelete: "cascade" }),
  location: text("location"),
  status: text("status").notNull().default("new"), // "new", "matched", "completed"
  transcript: text("transcript"),
  summary: text("summary"),
  sentiment: text("sentiment"), // "positive", "neutral", "negative"
  sentimentScore: integer("sentiment_score"), // 0-100
  talkTimeRatio: text("talk_time_ratio"), // e.g., "65/35"
  topics: text("topics").array(),
  vapiCallId: text("vapi_call_id"),
  vapiCallStatus: text("vapi_call_status"),
  vapiCallDuration: integer("vapi_call_duration"),
  vapiCallTranscript: text("vapi_call_transcript"),
  vapiCallEndedReason: text("vapi_call_ended_reason"),
  vapiCallStartedAt: timestamp("vapi_call_started_at"),
  vapiCallEndedAt: timestamp("vapi_call_ended_at"),
  createdAt: timestamp("created_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at").defaultNow().notNull(),
});

// Conversation details - structured extracted information
export const conversationDetails = pgTable("conversation_details", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  conversationId: varchar("conversation_id").notNull().references(() => conversations.id, { onDelete: "cascade" }),
  school: text("school"),
  company: text("company"),
  experiences: text("experiences"),
  hobbies: text("hobbies"),
  contacts: text("contacts"),
  extractedData: jsonb("extracted_data"), // Additional structured data
  createdAt: timestamp("created_at").defaultNow().notNull(),
});

// Follow-up actions - drafted emails and LinkedIn messages
export const followUpActions = pgTable("follow_up_actions", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  conversationId: varchar("conversation_id").notNull().references(() => conversations.id, { onDelete: "cascade" }),
  type: text("type").notNull(), // "email" or "linkedin"
  status: text("status").notNull().default("drafted"), // "drafted", "sent", "failed"
  recipientEmail: text("recipient_email"),
  recipientLinkedIn: text("recipient_linkedin"),
  subject: text("subject"),
  content: text("content").notNull(),
  metadata: jsonb("metadata"), // Additional data like search results
  createdAt: timestamp("created_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at").defaultNow().notNull(),
});

// Relations
export const personsRelations = relations(persons, ({ many }) => ({
  conversations: many(conversations),
}));

export const conversationsRelations = relations(conversations, ({ one, many }) => ({
  person: one(persons, {
    fields: [conversations.personId],
    references: [persons.id],
  }),
  details: many(conversationDetails),
  followUpActions: many(followUpActions),
}));

export const conversationDetailsRelations = relations(conversationDetails, ({ one }) => ({
  conversation: one(conversations, {
    fields: [conversationDetails.conversationId],
    references: [conversations.id],
  }),
}));

export const followUpActionsRelations = relations(followUpActions, ({ one }) => ({
  conversation: one(conversations, {
    fields: [followUpActions.conversationId],
    references: [conversations.id],
  }),
}));

// Insert schemas
export const insertPersonSchema = createInsertSchema(persons).omit({
  id: true,
  createdAt: true,
});

export const insertConversationSchema = createInsertSchema(conversations).omit({
  id: true,
  createdAt: true,
  updatedAt: true,
});

export const insertConversationDetailSchema = createInsertSchema(conversationDetails).omit({
  id: true,
  createdAt: true,
});

export const insertFollowUpActionSchema = createInsertSchema(followUpActions).omit({
  id: true,
  createdAt: true,
  updatedAt: true,
});

// Types
export type Person = typeof persons.$inferSelect;
export type InsertPerson = z.infer<typeof insertPersonSchema>;

export type Conversation = typeof conversations.$inferSelect;
export type InsertConversation = z.infer<typeof insertConversationSchema>;

export type ConversationDetail = typeof conversationDetails.$inferSelect;
export type InsertConversationDetail = z.infer<typeof insertConversationDetailSchema>;

export type FollowUpAction = typeof followUpActions.$inferSelect;
export type InsertFollowUpAction = z.infer<typeof insertFollowUpActionSchema>;

// Extended types with relations
export type ConversationWithPerson = Conversation & {
  person: Person;
  details?: ConversationDetail[];
};

export type PersonWithConversations = Person & {
  conversations: Conversation[];
};
