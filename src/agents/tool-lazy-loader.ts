import type { ToolProfileId } from "./tool-catalog.js";

/**
 * Detects the most appropriate tool profile based on the user's prompt and trigger.
 * This is a lightweight heuristic to reduce token usage by injecting fewer tool schemas.
 */
export function detectToolLazyProfile(params: {
  prompt: string;
  trigger?: string;
  isSubagent?: boolean;
}): ToolProfileId {
  const { prompt, trigger, isSubagent } = params;
  const lowerPrompt = prompt.toLowerCase();

  // Heartbeat/Cron/Memory triggersUsually need minimal or specific tools
  if (trigger === "heartbeat") {
    return "minimal";
  }
  if (trigger === "memory") {
    return "coding"; // memory flush often needs fs tools
  }
  if (trigger === "cron") {
    return "full"; // Cron tasks are unmanaged and unpredictable
  }

  // We can scale up if specific keywords are found.
  if (isSubagent) {
    if (isCodingTask(lowerPrompt)) return "coding";
    return "minimal";
  }

  // Coding/Filesystem intent takes precedence over messaging
  // because coding tasks often involve reading files before messaging.
  if (isCodingTask(lowerPrompt)) {
    return "coding";
  }

  // Messaging intent (routing, listing channels, etc.)
  if (isMessagingTask(lowerPrompt)) {
    return "messaging";
  }

  // Default to full for user prompts to ensure maximum capability
  return "full";
}

function isCodingTask(prompt: string): boolean {
  const keywords = [
    "bash", "shell", "terminal",
    "git", "diff", "patch", "apply_patch", "commit",
    "build", "test", "vitest", "jest", "pytest", "npm", "pnpm", "yarn",
    "refactor", "debug", "stack trace", "traceback", "exception", "typescript", "javascript", "python"
  ];
  return keywords.some(k => prompt.includes(k));
}

function isMessagingTask(prompt: string): boolean {
  const keywords = [
    "send message", "send a message", "reply", "chat", "channel", "group", "room", "telegram", "discord"
  ];
  return keywords.some(k => prompt.includes(k));
}
