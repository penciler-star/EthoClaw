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

  // Heartbeat/Cron/Memory triggers usually need minimal tools
  if (trigger === "heartbeat" || trigger === "cron" || trigger === "memory") {
    return "minimal";
  }

  // Subagents often perform specialized tasks, but "minimal" is a safe base.
  // We can scale up if specific keywords are found.
  if (isSubagent) {
    if (isCodingTask(lowerPrompt)) return "coding";
    return "minimal";
  }

  // Messaging intent (routing, listing channels, etc.)
  if (isMessagingTask(lowerPrompt)) {
    return "messaging";
  }

  // Coding/Filesystem intent
  if (isCodingTask(lowerPrompt)) {
    return "coding";
  }

  // Default to full for user prompts to ensure maximum capability,
  // unless we want to be more aggressive with Ethoclaw.
  return "full";
}

function isCodingTask(prompt: string): boolean {
  const keywords = [
    "run", "exec", "bash", "shell", "terminal",
    "read", "write", "edit", "file", "path", "dir", "folder",
    "grep", "search", "find", "list", "ls",
    "git", "diff", "patch", "apply", "commit",
    "build", "test", "npm", "pnpm", "yarn",
    "refactor", "debug", "fix", "code", "typescript", "javascript", "python"
  ];
  return keywords.some(k => prompt.includes(k));
}

function isMessagingTask(prompt: string): boolean {
  const keywords = [
    "send", "message", "reply", "chat", "channel", "group", "room",
    "list", "search", "find" // shared with coding, but in context of messaging
  ];
  // Check for specific messaging keywords that don't overlap too much with coding
  const strongKeywords = ["send", "message", "reply", "channel", "group"];
  return strongKeywords.some(k => prompt.includes(k));
}
